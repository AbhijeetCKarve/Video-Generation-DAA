"""Shared scene scaffolding for the DAA lessons (3.3 onwards): timing against the narration
schedule, stage management, the on-camera cameos, and the screens every video has
(welcome, syllabus, exam star, practice pause, tips, recap, next video, end card).

A video's scene.py does `from lesson import *`, subclasses Lesson, sets NEXT, and writes
one b_<key> method per beat. The schedule, envelope and variant come from the environment
(see production.py), exactly as before.
"""
import json
import os
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from manim import *  # noqa: E402,F401,F403
from kit import *    # noqa: E402,F401,F403

S = json.loads(Path(os.environ["SCHEDULE"]).read_text())
ENV = np.load(os.environ["ENVELOPE"])
SFX_LOG = os.environ.get("SFX_LOG")
config.background_color = BG

VARIANT = os.environ.get("VARIANT", "")
FACE = VARIANT == "face"          # your camera in a circle where the mascot stands, all the way through
CAMEO = VARIANT == "cameo"        # you on camera in a few short shots (S["cameos"]), no mascot
CAMEOS = {c.get("beat", "end"): c for c in S.get("cameos", [])}
MASCOT = not CAMEO                # Algo on screen; without him the content sits in the middle
MASCOT_POS = np.array([-5.75, -1.05, 0])
FACE_POS = np.array([-6.07, -1.05, 0])
STAGE = np.array([0.9 if MASCOT else 0.0, 0.15, 0])


class Lesson(Scene):
    NEXT = ("", "")                 # the next video's title, two lines

    # ------------------------------------------------------------ timing helpers
    def now(self):
        return self.renderer.time

    def until(self, t):
        dt = t - self.now()
        if dt > 1 / 30:
            self.wait(dt)

    def at(self, b, i):
        self.until(b["phrases"][min(i, len(b["phrases"]) - 1)]["start"])

    def phrase_len(self, b, i):
        ph = b["phrases"][min(i, len(b["phrases"]) - 1)]
        return ph["end"] - ph["start"]

    def sfx(self, kind, delay=0.0):
        self.sfx_events.append((round(self.now() + delay, 3), kind))

    def go(self, *anims, run_time=None):
        anims = [a for a in anims if a is not None] + self.pending
        self.pending = []
        if anims:
            if run_time:
                self.play(*anims, run_time=run_time)
            else:
                self.play(*anims)

    # ------------------------------------------------------------ stage management
    def clear(self, *keep, run_time=0.5):
        gone = [m for m in self.stage if m not in keep]
        self.stage = VGroup(*keep)
        if gone:
            self.go(*[FadeOut(m) for m in gone], run_time=run_time)

    def show(self, *mobs, anim=FadeIn, run_time=0.6, **kw):
        for m in mobs:
            self.stage.add(m)
        self.go(*[anim(m, **kw) for m in mobs], run_time=run_time)

    def drop(self, *mobs, run_time=0.4):
        """Fade out a few stage objects, keep the rest."""
        for m in mobs:
            self.stage.remove(m)
        self.go(*[FadeOut(m) for m in mobs], run_time=run_time)

    def grow_tree(self, tree, events, b, phrase, n, per=0.5, on_event=None):
        """Advance a Tree by n events of `events` during phrase `phrase`, pacing them to the narration."""
        self.at(b, phrase)
        span = self.phrase_len(b, phrase)
        step = max(0.28, min(per, span / max(n, 1)))
        for _ in range(n):
            i = tree.ev_i
            kind = events[i][0]
            main = tree.mark_back(i) if kind == "back" else tree.grow(i)   # grow() creates the node first
            extra = on_event(i, kind) if on_event else []                  # ...so on_event can refer to it
            self.go(main, *extra, run_time=step)
            self.sfx("back" if kind == "back" else "place" if kind == "place" else "kill", -step)
            tree.ev_i += 1

    # ------------------------------------------------------------ the mascot (if any)
    def react(self, mood):
        m = self.mascot
        if not self.mascot_on:
            return
        if mood == "excited":
            self.pending += [m.set_mood("happy"), m.bounce()]
        elif mood == "warm":
            self.pending += [m.set_mood("happy")]
        elif mood == "curious":
            self.pending += [m.set_mood("thinking"), m.tilt()]
        elif mood == "emphatic":
            self.pending += [m.set_mood("neutral"), m.point()]
        else:
            self.pending += [m.set_mood("neutral")]

    def say(self, text, hold=None):
        """Speech bubble from the mascot; removed at the next bubble or explicitly."""
        self.unsay()
        if FACE or not MASCOT:           # you say it yourself on camera / nobody to say it
            return
        self.bubble_mob = self.mascot.bubble(text)
        self.go(FadeIn(self.bubble_mob, shift=UP * 0.15), run_time=0.3)

    def unsay(self):
        if getattr(self, "bubble_mob", None) is not None:
            self.go(FadeOut(self.bubble_mob), run_time=0.25)
            self.bubble_mob = None

    # ------------------------------------------------------------ cameos (you on camera, laid in at the mix)
    def cameo_in(self, shot):
        """The ring your face appears in; the mascot steps off-screen while you are on."""
        self.unsay()
        self.until(shot["start"])
        self.face_ring = FaceSpot(accent=UNIT_COLORS[S["unit"]], radius=S["face_px"] / 2 / 135).move_to(
            np.array([*shot["pos"], 0]))
        anims = [GrowFromCenter(self.face_ring)]
        if self.mascot_on:
            anims.append(self.mascot.animate.move_to(MASCOT_POS + LEFT * 4))
        self.go(*anims, run_time=0.4)
        self.sfx("whoosh", -0.3)

    def cameo_out(self, shot):
        self.until(shot["end"] - 0.3)
        anims = [ShrinkToCenter(self.face_ring)]
        if self.mascot_on:
            anims.append(self.mascot.animate.move_to(MASCOT_POS))
        self.go(*anims, run_time=0.3)

    # ------------------------------------------------------------ main loop
    def construct(self):
        self.sfx_events, self.pending, self.stage = [], [], VGroup()
        self.mascot_on = False
        thumb = ImageMobject(str(Path(os.environ["SCHEDULE"]).parents[1] / "output" / "thumbnail.png"))
        thumb.scale_to_fit_width(config.frame_width)
        self.add(thumb)
        self.until(S["intro"] - 0.5)
        self.play(FadeOut(thumb), run_time=0.5)
        self.header = Header(S["unit"], S["code"])
        self.header_on = False
        if FACE:
            self.mascot = FaceSpot(accent=UNIT_COLORS[S["unit"]], radius=0.926).move_to(FACE_POS)
        elif not MASCOT:
            self.mascot = NoMascot()
        else:
            self.mascot = Mascot(accent=UNIT_COLORS[S["unit"]], height=1.9).move_to(MASCOT_POS + LEFT * 4)
            self.mascot.attach(self.now, ENV)
            self.add(self.mascot)
        for b in S["beats"]:
            if CAMEO and CAMEOS.get(b["key"], {}).get("kind") == "line":   # your face comes in just before
                self.cameo_in(CAMEOS[b["key"]])
            self.until(b["start"])
            if b["section"] and self.header_on:
                self.pending.append(self.header.set_section(b["section"]))
            self.react(b["mood"])
            getattr(self, "b_" + b["key"])(b)
            self.go()
            if self.now() > b["end"] + 0.2:
                print(f"OVERRUN {b['key']}: ended {self.now():.2f}s, window closed {b['end']:.2f}s")
        self.until(S["end_card"])
        self.end_card()
        self.until(S["total"])
        if SFX_LOG:
            Path(SFX_LOG).write_text(json.dumps(self.sfx_events))

    # ------------------------------------------------------------ screens every video has
    def b_hook_mascot(self, b):
        """The welcome line: you on camera (cameo/face) or Algo arriving (mascot)."""
        self.clear(run_time=0.5)
        if not CAMEO:
            self.mascot_on = True
            if FACE:
                self.go(GrowFromCenter(self.mascot), run_time=0.6)
            else:
                self.go(self.mascot.animate.move_to(MASCOT_POS), run_time=0.8)
            self.sfx("whoosh")
            self.go(self.mascot.wave(), run_time=1.0)
        series = label("DAA SERIES", 34, MUTED, "BOLD")
        by = label("by Abhijeet Karve", 54, TEXT, "BOLD")
        g = VGroup(series, by).arrange(DOWN, buff=0.25).move_to(STAGE + UP * 0.4)
        self.show(g, anim=FadeIn, run_time=0.6, shift=UP * 0.2)
        self.at(b, 1)
        if not CAMEO:
            self.say("Hi, students!" if VARIANT == "real" else "Hi! I'm Algo")
        guide = label("your guide, step by step", 30, ACCENT).next_to(g, DOWN, buff=0.4)
        self.show(guide, run_time=0.5)

    def syllabus(self, b, topics, unit_text="UNIT III  ·  BACKTRACKING"):
        self.unsay()
        if CAMEO and "hook_mascot" in CAMEOS:
            self.cameo_out(CAMEOS["hook_mascot"])
        self.clear(run_time=0.4)
        self.header_on = True
        self.header.set_section("Today's plan")
        self.add(self.header)
        self.go(FadeIn(self.header, shift=DOWN * 0.2), run_time=0.5)
        unit = chip(unit_text, UNIT_COLORS[S["unit"]], 34).move_to(STAGE + UP * 2.0)
        self.show(unit, anim=GrowFromCenter, run_time=0.5)
        self.unit_chip = unit
        self.at(b, 1)
        rows = VGroup(*[VGroup(chip(str(i + 1), ACCENT, 28), label(t, 36, TEXT, "BOLD")).arrange(RIGHT, buff=0.3)
                        for i, t in enumerate(topics)])
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.32).move_to(STAGE + DOWN * 0.45)
        self.stage.add(rows)
        self.go(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.3) for r in rows], lag_ratio=0.5), run_time=2.2)
        self.sfx("pop")

    def exam_star(self, b, text="Tips at the end!"):
        star = chip("★  Exam favourite", GOLD, 26, "#0F172A").next_to(self.unit_chip, RIGHT, buff=0.3)
        self.show(star, anim=GrowFromCenter, run_time=0.5)
        self.sfx("pop")
        self.at(b, 1)
        self.say(text)

    def question_card(self, b, lines):
        """'Your turn' header + the question in a gold card."""
        self.clear(run_time=0.4)
        head = label("YOUR TURN", 34, GOLD, "BOLD").move_to(STAGE + UP * 1.7)
        self.show(head, anim=GrowFromCenter, run_time=0.4)
        self.sfx("pop")
        self.at(b, 1)
        q = VGroup(*[label(t, 40, TEXT, "BOLD") for t in lines]).arrange(DOWN, buff=0.2)
        box = card(q.width + 0.9, q.height + 0.7, edge=GOLD)
        self.question = VGroup(box, q.move_to(box)).move_to(STAGE + DOWN * 0.1)
        self.show(self.question, run_time=0.6, shift=UP * 0.2)

    def pause_screen(self, b, text="Pause and draw the tree"):
        bars = VGroup(*[RoundedRectangle(width=0.35, height=1.1, corner_radius=0.1, fill_color=TEXT, fill_opacity=1,
                                         stroke_width=0) for _ in range(2)]).arrange(RIGHT, buff=0.3)
        pause = VGroup(Circle(0.95, color=TEXT, stroke_width=6), bars).move_to(STAGE + DOWN * 0.9 + LEFT * 2.5)
        txt = label(text, 30, TEXT, "BOLD").next_to(pause, RIGHT, buff=0.4)
        self.go(self.question.animate.scale(0.75).move_to(STAGE + UP * 1.3), run_time=0.4)
        self.show(pause, txt, run_time=0.5)
        self.say("Your turn!")
        self.at(b, 1)
        self.say("I'll wait!")
        if CAMEO and "p_pause" in CAMEOS:     # ...and you wait on camera while they draw
            self.cameo_in(CAMEOS["p_pause"])

    def pause_over(self):
        self.unsay()
        if CAMEO and "p_pause" in CAMEOS:
            self.cameo_out(CAMEOS["p_pause"])

    def tip(self, b, n, text, sub):
        if n == 1:
            self.clear(run_time=0.4)
        row = VGroup(chip(str(n), GOLD, 30, "#0F172A"),
                     VGroup(label(text, 30, TEXT, "BOLD"), label(sub, 22, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
                     ).arrange(RIGHT, buff=0.35)
        row.move_to(STAGE + UP * (1.7 - 1.35 * (n - 1))).align_to(STAGE + LEFT * 3.6, LEFT)
        self.stage.add(row)
        self.go(FadeIn(row, shift=RIGHT * 0.3), run_time=0.5)
        self.sfx("pop")

    def recap(self, b, items):
        self.clear(run_time=0.4)
        rows = VGroup(*[VGroup(label("✓", 34, SAFE, "BOLD"), label(t, 30, TEXT)).arrange(RIGHT, buff=0.3) for t in items])
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4).move_to(STAGE)
        self.stage.add(rows)
        for i, r in enumerate(rows):
            self.at(b, i + 1)
            self.go(FadeIn(r, shift=RIGHT * 0.3), run_time=0.5)

    def b_next(self, b):
        self.clear(run_time=0.4)
        nxt = VGroup(label("NEXT VIDEO", 26, MUTED, "BOLD"), *[label(t, 44, TEXT, "BOLD") for t in self.NEXT]
                     ).arrange(DOWN, buff=0.15)
        box = card(nxt.width + 1.0, nxt.height + 0.8, edge=UNIT_COLORS[S["unit"]])
        g = VGroup(box, nxt.move_to(box)).move_to(STAGE)
        self.show(g, anim=FadeIn, run_time=0.6, shift=UP * 0.2)
        self.at(b, 1)
        self.go(self.mascot.wave(), self.mascot.set_mood("happy"), run_time=1.0)

    def end_card(self):
        """Upper part only: the lower half stays free for YouTube's end-screen boxes."""
        self.unsay()
        self.clear(run_time=0.5)
        thanks = label("Thanks for watching", 56, TEXT, "BOLD")
        by = VGroup(label("CREATED BY", 24, MUTED, "BOLD"), label("Abhijeet Karve", 44, GOLD, "BOLD")).arrange(DOWN, buff=0.1)
        g = VGroup(thanks, by).arrange(DOWN, buff=0.4).move_to(STAGE + UP * 1.7)
        self.show(g, run_time=0.8, shift=UP * 0.2)
        if CAMEO and "end" in CAMEOS:         # you, next to your name, for the end screen
            self.cameo_in(CAMEOS["end"])
