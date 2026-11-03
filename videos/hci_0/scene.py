"""HCI introductory session (ETCS334). Rendered by build.py (needs SCHEDULE / ENVELOPE env vars)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from lesson import *  # noqa: E402,F401,F403

PINK = UNIT_COLORS["HCI"]
PURPLE = UNIT_COLORS["IV"]
DARK = "#0F172A"


def chips(items, color, size=22, text_color=None, buff=0.22):
    return VGroup(*[chip(t, color, size, text_color or (DARK if color in (GOLD, SAFE) else TEXT)) for t in items]).arrange(RIGHT, buff=buff)


def flow(items, color, size=22, buff=0.35):
    row = chips(items, color, size, buff=buff)
    arrows = VGroup(*[Arrow(row[i].get_right(), row[i + 1].get_left(), buff=0.06, color=MUTED, stroke_width=3,
                            max_tip_length_to_length_ratio=0.4) for i in range(len(items) - 1)])
    g = VGroup(row, arrows)
    g.is_flow = True
    return g


def titled_card(title, color, lines, w, h, title_size=26, line_size=21, line_color=TEXT):
    body = VGroup(label(title, title_size, color, "BOLD"), *[label(t, line_size, line_color) for t in lines]).arrange(DOWN, buff=0.12)
    if body.width > w - 0.3:
        body.scale_to_fit_width(w - 0.3)
    box = card(w, h, edge=color)
    return VGroup(box, body.move_to(box))


def phone_frame(center, w=2.6, h=5.0, color=PANEL_EDGE):
    return RoundedRectangle(width=w, height=h, corner_radius=0.35, color=color, stroke_width=4, fill_color=PANEL, fill_opacity=1).move_to(center)


def door(center, handle, label_text, color):
    """A door: a flat plate (push) or a pull handle; the sign on it."""
    d = RoundedRectangle(width=1.6, height=3.4, corner_radius=0.08, color=color, stroke_width=4, fill_color="#3b2f2f", fill_opacity=1).move_to(center)
    g = VGroup(d)
    if handle:
        g.add(RoundedRectangle(width=0.14, height=0.9, corner_radius=0.07, color=GOLD, fill_color=GOLD, fill_opacity=1, stroke_width=0).move_to(center + RIGHT * 0.5))
    else:
        g.add(Rectangle(width=0.5, height=0.5, color=TEXT, fill_color="#94A3B8", fill_opacity=1, stroke_width=1).move_to(center + RIGHT * 0.4))
    if label_text:
        g.add(VGroup(Rectangle(width=0.9, height=0.34, color=TEXT, fill_color=TEXT, fill_opacity=1, stroke_width=0),
                     label(label_text, 16, DARK, "BOLD")).move_to(center + UP * 1.15))
    return g


class Video(Lesson):
    NEXT = ("Lecture 1", "Foundations of HCI: the human")

    def screen(self, head_text, color, sub=None):
        self.clear(run_time=0.4)
        head = chip(head_text, color, 26, DARK if color in (GOLD, SAFE) else TEXT).move_to(STAGE + UP * 2.55)
        self.show(head, anim=GrowFromCenter, run_time=0.5)
        self.sfx("pop")
        self.y = 1.75
        if sub:
            t = label(sub, 30, TEXT, "BOLD").move_to(STAGE + UP * self.y)
            if t.width > 13.0:
                t.scale_to_fit_width(13.0)
            self.show(t, run_time=0.4)
            self.y -= 0.85
        return head

    def row(self, mob, gap=0.62, run_time=0.9):
        mob.move_to(STAGE + UP * self.y)
        if mob.width > 13.4:
            mob.scale_to_fit_width(13.4)
        self.stage.add(mob)
        parts = (list(mob[0]) + [mob[1]]) if getattr(mob, "is_flow", False) else list(mob)
        if len(parts) > 1:
            self.go(LaggedStart(*[FadeIn(p, shift=UP * 0.15) for p in parts], lag_ratio=0.25), run_time=run_time)
        else:
            self.go(FadeIn(mob, shift=UP * 0.15), run_time=0.5)
        self.y -= gap

    def punch(self, text, color=GOLD, size=30, y=-2.4):
        c = chip(text, color, size, DARK if color in (GOLD, SAFE) else TEXT).move_to(STAGE + UP * y)
        if c.width > 13.2:
            c.scale_to_fit_width(13.2)
        self.show(c, anim=GrowFromCenter, run_time=0.5)
        self.sfx("chime")
        return c

    # ------------------------------------------------------------ hook
    def b_hook_angry(self, b):
        p1 = phone_frame(STAGE + LEFT * 4.2 + UP * 0.2, color=KILL)
        wrong = VGroup(RoundedRectangle(width=1.9, height=0.5, corner_radius=0.1, color=SAFE, fill_color=SAFE, fill_opacity=0.3).move_to(p1.get_center() + UP * 0.9),
                       RoundedRectangle(width=1.9, height=0.5, corner_radius=0.1, color=KILL, fill_color=KILL, fill_opacity=0.9).move_to(p1.get_center() + UP * 0.2),
                       label("Delete all", 16, TEXT, "BOLD").move_to(p1.get_center() + UP * 0.2), label("Save", 16, TEXT).move_to(p1.get_center() + UP * 0.9))
        p2 = phone_frame(STAGE + UP * 0.2, color=KILL)
        form = VGroup(*[RoundedRectangle(width=1.9, height=0.4, corner_radius=0.08, color=PANEL_EDGE, fill_color="#2a3140", fill_opacity=1).move_to(p2.get_center() + UP * (1.3 - i * 0.6)) for i in range(4)],
                      chip("Session expired. Start again.", KILL, 13).move_to(p2.get_center() + DOWN * 1.5))
        kiosk = VGroup(RoundedRectangle(width=3.0, height=4.2, corner_radius=0.2, color=KILL, stroke_width=4, fill_color=PANEL, fill_opacity=1).move_to(STAGE + RIGHT * 4.2 + UP * 0.2),
                       Rectangle(width=2.2, height=1.4, color=ACCENT, fill_color="#0b2a4a", fill_opacity=1).move_to(STAGE + RIGHT * 4.2 + UP * 1.2),
                       label("INSERT COINS", 16, TEXT, "BOLD").move_to(STAGE + RIGHT * 4.2 + UP * 1.2),
                       label("₹50 ... gone", 20, KILL, "BOLD").move_to(STAGE + RIGHT * 4.2 + DOWN * 0.6))
        self.show(p1, wrong, run_time=0.6)
        self.show(p2, form, run_time=0.6)
        self.show(kiosk, run_time=0.6)
        self.sfx("kill")
        self.at(b, 1)
        self.punch("the hardware was fine. the design failed you", KILL, 30, -2.7)

    def b_hook_subject(self, b):
        self.clear(run_time=0.4)
        q = VGroup(label("joy", 56, SAFE, "BOLD"), label("or", 36, MUTED), label("torture", 56, KILL, "BOLD")).arrange(RIGHT, buff=0.5).move_to(STAGE + UP * 1.6)
        self.show(q, anim=GrowFromCenter, run_time=0.6)
        self.sfx("pop")
        self.at(b, 1)
        big = label("HCI", 120, PINK, "BOLD").move_to(STAGE + DOWN * 0.3)
        full = label("Human Computer Interface", 36, TEXT, "BOLD").next_to(big, DOWN, buff=0.1)
        self.show(big, anim=GrowFromCenter, run_time=0.7)
        self.sfx("whoosh")
        self.show(full, run_time=0.4)
        el = chip("Programme Elective VI  ·  ETCS334", GOLD, 24, DARK).move_to(STAGE + DOWN * 2.6)
        self.show(el, run_time=0.4)

    def b_hook_promise(self, b):
        self.clear(run_time=0.4)
        t = chip("the next 13 minutes", PINK, 30).move_to(STAGE + UP * 2.1)
        self.show(t, anim=GrowFromCenter, run_time=0.5)
        items = VGroup(*[VGroup(chip(str(i + 1), ACCENT, 26), label(x, 32, TEXT, "BOLD")).arrange(RIGHT, buff=0.3) for i, x in enumerate(
            ["What HCI is, through things you use every day", "What you will build in this course", "How you will be marked", "Why it is the most useful elective"])])
        items.arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(STAGE + DOWN * 0.3)
        self.stage.add(items)
        self.go(FadeIn(items[0], shift=RIGHT * 0.3), run_time=0.5)
        self.at(b, 1)
        self.go(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.3) for r in items[1:]], lag_ratio=0.4), run_time=1.5)
        self.sfx("pop")

    def b_syllabus(self, b):
        self.syllabus(b, ["What HCI is", "Five ideas you can use tomorrow", "What you will build", "How marks work, and why to enrol"],
                      unit_text="ETCS334  ·  HCI")

    def b_exam(self, b):
        self.exam_star(b, text="A one-minute test, at the end", star="★  Test at the end")

    # ------------------------------------------------------------ what HCI is
    def b_w_meet(self, b):
        self.unsay()
        self.screen("WHAT HCI IS", PINK)
        human = VGroup(Circle(0.35, color=TEXT, fill_color=TEXT, fill_opacity=1, stroke_width=0).shift(UP * 0.7),
                       RoundedRectangle(width=1.1, height=1.3, corner_radius=0.3, color=TEXT, fill_color=TEXT, fill_opacity=1, stroke_width=0).shift(DOWN * 0.35),
                       label("human", 22, MUTED).shift(DOWN * 1.5)).move_to(STAGE + LEFT * 4.5 + UP * 0.4)
        iface = VGroup(RoundedRectangle(width=3.4, height=2.4, corner_radius=0.2, color=PINK, stroke_width=4, fill_color=PANEL, fill_opacity=1),
                       VGroup(*[chip(t, PINK, 16) for t in ["screen", "buttons", "voice", "gestures"]]).arrange_in_grid(rows=2, buff=0.15),
                       label("the interface", 22, PINK, "BOLD").shift(DOWN * 1.5)).move_to(STAGE + UP * 0.4)
        machine = VGroup(RoundedRectangle(width=1.6, height=1.9, corner_radius=0.15, color=ACCENT, stroke_width=4, fill_color="#0b2a4a", fill_opacity=1),
                         VGroup(*[Rectangle(width=1.1, height=0.12, color=ACCENT, fill_color=ACCENT, fill_opacity=0.8, stroke_width=0).shift(UP * (0.5 - 0.3 * i)) for i in range(4)]),
                         label("machine", 22, MUTED).shift(DOWN * 1.5)).move_to(STAGE + RIGHT * 4.5 + UP * 0.4)
        a1 = DoubleArrow(human.get_right() + RIGHT * 0.1, iface.get_left() + LEFT * 0.1, color=MUTED, stroke_width=4, buff=0.1, max_tip_length_to_length_ratio=0.15)
        a2 = DoubleArrow(iface.get_right() + RIGHT * 0.1, machine.get_left() + LEFT * 0.1, color=MUTED, stroke_width=4, buff=0.1, max_tip_length_to_length_ratio=0.15)
        self.show(human, machine, run_time=0.5)
        self.show(iface, anim=GrowFromCenter, run_time=0.6)
        self.show(a1, a2, run_time=0.4)
        self.at(b, 1)
        self.punch("does this design fit the way humans actually think and behave?", GOLD, 28, -2.4)

    def b_w_three(self, b):
        self.screen("THREE FIELDS, ONE SUBJECT", PINK)
        c = STAGE + DOWN * 0.3
        circles = VGroup(Circle(1.9, color=ACCENT, fill_color=ACCENT, fill_opacity=0.18, stroke_width=4).move_to(c + LEFT * 1.3 + UP * 0.6),
                         Circle(1.9, color=GOLD, fill_color=GOLD, fill_opacity=0.18, stroke_width=4).move_to(c + RIGHT * 1.3 + UP * 0.6),
                         Circle(1.9, color=SAFE, fill_color=SAFE, fill_opacity=0.18, stroke_width=4).move_to(c + DOWN * 1.4))
        labels = VGroup(VGroup(label("Computer science", 24, ACCENT, "BOLD"), label("builds the system", 18, MUTED)).arrange(DOWN, buff=0.05).move_to(c + LEFT * 2.6 + UP * 1.2),
                        VGroup(label("Psychology", 24, GOLD, "BOLD"), label("explains the user", 18, MUTED)).arrange(DOWN, buff=0.05).move_to(c + RIGHT * 2.6 + UP * 1.2),
                        VGroup(label("Design", 24, SAFE, "BOLD"), label("shapes what the user sees", 18, MUTED)).arrange(DOWN, buff=0.05).move_to(c + DOWN * 2.3))
        self.show(circles[0], labels[0], run_time=0.5)
        self.at(b, 1)
        self.show(circles[1], labels[1], run_time=0.5)
        self.show(circles[2], labels[2], run_time=0.5)
        hci = label("HCI", 40, PINK, "BOLD").move_to(c + UP * 0.1)
        self.show(hci, anim=GrowFromCenter, run_time=0.5)
        self.sfx("chime")

    def b_w_blame(self, b):
        self.screen("THE SHIFT IN THINKING", PINK)
        old = VGroup(label("user error", 60, MUTED, "BOLD")).move_to(STAGE + UP * 0.9)
        self.show(old, run_time=0.5)
        self.at(b, 1)
        strike = Line(old.get_left() + LEFT * 0.2, old.get_right() + RIGHT * 0.2, color=KILL, stroke_width=8)
        self.show(strike, anim=Create, run_time=0.4)
        self.sfx("kill")
        new = label("design error", 72, GOLD, "BOLD").move_to(STAGE + DOWN * 0.8)
        self.show(new, anim=GrowFromCenter, run_time=0.6)
        self.sfx("chime")
        n = label("the heart of the subject", 24, MUTED).move_to(STAGE + DOWN * 2.2)
        self.show(n, run_time=0.4)

    # ------------------------------------------------------------ five ideas
    def idea(self, n, title):
        self.screen(f"IDEA {n}  ·  {title.upper()}", GOLD)

    def b_i_door(self, b):
        self.idea(1, "affordances and signifiers")
        d1 = door(STAGE + LEFT * 4.0 + UP * 0.3, False, "", SAFE)
        d2 = door(STAGE + LEFT * 1.3 + UP * 0.3, True, "", SAFE)
        l1 = label("flat plate: push", 22, SAFE, "BOLD").next_to(d1, DOWN, buff=0.25)
        l2 = label("handle: pull", 22, SAFE, "BOLD").next_to(d2, DOWN, buff=0.25)
        self.show(d1, l1, run_time=0.5)
        self.show(d2, l2, run_time=0.5)
        self.at(b, 1)
        d3 = door(STAGE + RIGHT * 2.6 + UP * 0.3, True, "PUSH", KILL)
        l3 = label("handle, but push: a Norman door", 22, KILL, "BOLD").next_to(d3, DOWN, buff=0.25)
        self.show(d3, l3, run_time=0.6)
        self.sfx("kill")
        ouch = label("✗", 60, KILL, "BOLD").next_to(d3, RIGHT, buff=0.4)
        self.show(ouch, anim=GrowFromCenter, run_time=0.3)
        n = label("your apps are full of them", 24, MUTED).move_to(STAGE + DOWN * 2.6)
        self.show(n, run_time=0.4)

    def b_i_chat(self, b):
        self.clear(run_time=0.4)
        self.idea(1, "signifiers in a chat app")
        ph = phone_frame(STAGE + LEFT * 3.6 + DOWN * 0.5, 3.0, 4.8)
        c = ph.get_center()
        bub = VGroup(RoundedRectangle(width=2.0, height=0.7, corner_radius=0.2, color=SAFE, fill_color="#14532d", fill_opacity=1, stroke_width=0).move_to(c + UP * 1.2 + RIGHT * 0.3),
                     label("See you at 5", 15, TEXT).move_to(c + UP * 1.3 + RIGHT * 0.3), label("✓✓", 15, ACCENT, "BOLD").move_to(c + UP * 1.0 + RIGHT * 1.0))
        bar = VGroup(RoundedRectangle(width=1.7, height=0.5, corner_radius=0.25, color=PANEL_EDGE, fill_color="#2a3140", fill_opacity=1).move_to(c + DOWN * 2.0 + LEFT * 0.35),
                     label("Message", 13, MUTED).move_to(c + DOWN * 2.0 + LEFT * 0.35),
                     Circle(0.26, color=SAFE, fill_color=SAFE, fill_opacity=1, stroke_width=0).move_to(c + DOWN * 2.0 + RIGHT * 0.95), label("➤", 16, DARK, "BOLD").move_to(c + DOWN * 2.0 + RIGHT * 0.95),
                     label("🎤", 18).move_to(c + DOWN * 2.0 + RIGHT * 0.45) if False else Circle(0.16, color=MUTED, fill_color=MUTED, fill_opacity=1, stroke_width=0).move_to(c + DOWN * 2.0 + RIGHT * 0.5))
        self.show(ph, bub, bar, run_time=0.7)
        notes = VGroup(VGroup(label("➤  paper plane", 24, TEXT, "BOLD"), label("signifies send", 20, MUTED)).arrange(RIGHT, buff=0.3),
                       VGroup(label("●  microphone", 24, TEXT, "BOLD"), label("signifies record", 20, MUTED)).arrange(RIGHT, buff=0.3),
                       VGroup(label("✓✓  blue ticks", 24, ACCENT, "BOLD"), label("feedback: delivered, read", 20, MUTED)).arrange(RIGHT, buff=0.3)
                       ).arrange(DOWN, aligned_edge=LEFT, buff=0.35).move_to(STAGE + RIGHT * 2.8 + UP * 0.8)
        self.stage.add(notes)
        self.go(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.3) for r in notes], lag_ratio=0.4), run_time=1.4)
        self.at(b, 1)
        pr = chips(["visibility", "feedback", "signifiers"], GOLD, 24).move_to(STAGE + RIGHT * 2.8 + DOWN * 1.2)
        self.show(pr, run_time=0.6)
        self.sfx("pop")
        n = label("3 of Norman's 6 principles, in one screen", 22, MUTED).move_to(STAGE + RIGHT * 2.8 + DOWN * 2.0)
        self.show(n, run_time=0.4)

    def b_i_fitts(self, b):
        self.idea(2, "Fitts' law")
        f = VGroup(label("time to reach a target  ∝  distance  /  size", 28, TEXT, "BOLD")).move_to(STAGE + RIGHT * 2.2 + UP * 1.6)
        self.show(f, run_time=0.5)
        ph = phone_frame(STAGE + LEFT * 4.2 + DOWN * 0.8, 2.4, 4.4)
        c = ph.get_center()
        zones = VGroup(RoundedRectangle(width=2.3, height=1.4, corner_radius=0.2, color=SAFE, fill_color=SAFE, fill_opacity=0.5, stroke_width=0).move_to(c + DOWN * 1.4),
                       RoundedRectangle(width=2.3, height=1.3, corner_radius=0.2, color=GOLD, fill_color=GOLD, fill_opacity=0.4, stroke_width=0).move_to(c + UP * 0.05),
                       RoundedRectangle(width=2.3, height=1.2, corner_radius=0.2, color=KILL, fill_color=KILL, fill_opacity=0.4, stroke_width=0).move_to(c + UP * 1.4))
        zl = VGroup(label("easy", 16, DARK, "BOLD").move_to(zones[0]), label("stretch", 16, DARK, "BOLD").move_to(zones[1]), label("hard", 16, TEXT, "BOLD").move_to(zones[2]))
        self.at(b, 1)
        self.show(ph, zones, zl, run_time=0.7)
        self.sfx("pop")
        notes = VGroup(VGroup(chip("most used buttons", SAFE, 22), label("at the bottom, under your thumb", 22, TEXT)).arrange(RIGHT, buff=0.3),
                       VGroup(chip("the ad's close button", KILL, 22), label("tiny, on purpose", 22, TEXT)).arrange(RIGHT, buff=0.3)
                       ).arrange(DOWN, aligned_edge=LEFT, buff=0.5).move_to(STAGE + RIGHT * 2.6 + DOWN * 0.3)
        self.stage.add(notes)
        self.go(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.3) for r in notes], lag_ratio=0.5), run_time=1.2)
        ad = VGroup(RoundedRectangle(width=3.2, height=1.0, corner_radius=0.1, color=PANEL_EDGE, fill_color="#2a3140", fill_opacity=1), label("AD: Win a phone!", 18, GOLD, "BOLD"),
                    label("×", 11, MUTED).shift(RIGHT * 1.45 + UP * 0.38)).move_to(STAGE + RIGHT * 2.6 + DOWN * 2.2)
        self.show(ad, run_time=0.5)

    def b_i_hick(self, b):
        self.idea(3, "Hick's law")
        f = label("more choices  →  longer to decide", 28, TEXT, "BOLD").move_to(STAGE + UP * 1.7)
        self.show(f, run_time=0.5)
        self.at(b, 1)
        r1 = RoundedRectangle(width=2.2, height=4.0, corner_radius=0.3, color=KILL, stroke_width=4, fill_color="#1f2937", fill_opacity=1).move_to(STAGE + LEFT * 3.6 + DOWN * 1.0)
        btns = VGroup(*[Circle(0.12, color=TEXT, fill_color="#9ca3af", fill_opacity=1, stroke_width=0).move_to(r1.get_center() + np.array([-0.75 + 0.375 * (i % 5), 1.6 - 0.36 * (i // 5), 0])) for i in range(50)])
        r2 = RoundedRectangle(width=1.6, height=4.0, corner_radius=0.5, color=SAFE, stroke_width=4, fill_color="#1f2937", fill_opacity=1).move_to(STAGE + RIGHT * 0.8 + DOWN * 1.0)
        b6 = VGroup(*[Circle(0.3, color=TEXT, fill_color="#e5e7eb", fill_opacity=1, stroke_width=0).move_to(r2.get_center() + np.array([-0.4 + 0.8 * (i % 2), 1.2 - 0.8 * (i // 2), 0])) for i in range(6)])
        self.show(r1, btns, run_time=0.7)
        l1 = label("50 buttons", 22, KILL, "BOLD").next_to(r1, DOWN, buff=0.2)
        self.show(l1, run_time=0.3)
        self.show(r2, b6, run_time=0.6)
        l2 = label("6 buttons", 22, SAFE, "BOLD").next_to(r2, DOWN, buff=0.2)
        self.show(l2, run_time=0.3)
        self.sfx("pop")
        n = VGroup(label("same job,", 24, MUTED), label("very different feeling", 24, TEXT, "BOLD"), label("fewer visible choices → faster users", 22, GOLD)).arrange(DOWN, buff=0.15)
        n.move_to(STAGE + RIGHT * 4.3 + DOWN * 1.0)
        self.show(n, run_time=0.5)

    def b_i_gulf(self, b):
        self.idea(4, "the gulf of execution")
        goal = chip("goal: 2 minutes on high", SAFE, 26).move_to(STAGE + LEFT * 4.2 + UP * 1.2)
        act = chip("action: which button?", KILL, 26).move_to(STAGE + RIGHT * 4.2 + UP * 1.2)
        gap = DashedLine(goal.get_right() + RIGHT * 0.1, act.get_left() + LEFT * 0.1, color=MUTED, stroke_width=3, dash_length=0.15)
        gl = label("the gulf", 22, MUTED).next_to(gap, UP, buff=0.1)
        self.show(goal, run_time=0.4)
        self.show(gap, gl, act, run_time=0.6)
        self.at(b, 1)
        panel = VGroup(RoundedRectangle(width=5.2, height=2.6, corner_radius=0.2, color=KILL, stroke_width=3, fill_color="#1f2937", fill_opacity=1))
        names = ["Popcorn", "Defrost", "Reheat", "Sensor", "Potato", "Clock", "Timer", "Power", "+30s", "Beverage", "Pizza", "Melt"]
        for i, nm in enumerate(names):
            panel.add(VGroup(RoundedRectangle(width=1.15, height=0.5, corner_radius=0.08, color=PANEL_EDGE, fill_color="#374151", fill_opacity=1, stroke_width=1),
                             label(nm, 13, TEXT)).move_to(panel[0].get_center() + np.array([-1.8 + 1.2 * (i % 4), 0.85 - 0.75 * (i // 4), 0])))
        panel.move_to(STAGE + LEFT * 3.0 + DOWN * 1.0)
        good = VGroup(RoundedRectangle(width=3.6, height=2.6, corner_radius=0.2, color=SAFE, stroke_width=3, fill_color="#1f2937", fill_opacity=1),
                      label("2:00", 54, TEXT, "BOLD").shift(UP * 0.4), VGroup(chip("+30 s", PANEL_EDGE, 16), chip("START", SAFE, 18)).arrange(RIGHT, buff=0.3).shift(DOWN * 0.7)
                      ).move_to(STAGE + RIGHT * 3.6 + DOWN * 1.0)
        self.show(panel, run_time=0.6)
        self.sfx("kill")
        self.show(good, run_time=0.6)
        self.sfx("chime")
        self.show(label("12 buttons", 20, KILL, "BOLD").next_to(panel, DOWN, buff=0.15), label("good design closes the gulf", 20, SAFE, "BOLD").next_to(good, DOWN, buff=0.15), run_time=0.4)

    def b_i_dark(self, b):
        self.idea(5, "dark patterns")
        t1 = VGroup(RoundedRectangle(width=4.0, height=1.5, corner_radius=0.15, color=KILL, stroke_width=3, fill_color="#1f2937", fill_opacity=1),
                    VGroup(label("Offer ends in", 18, MUTED), label("00:59", 40, KILL, "BOLD"), label("resets when you reload", 15, GOLD)).arrange(DOWN, buff=0.05))
        t2 = VGroup(RoundedRectangle(width=4.0, height=1.5, corner_radius=0.15, color=KILL, stroke_width=3, fill_color="#1f2937", fill_opacity=1),
                    VGroup(VGroup(Square(0.32, color=TEXT, fill_color=ACCENT, fill_opacity=1, stroke_width=2), label("✓", 18, TEXT, "BOLD")).shift(LEFT * 1.4),
                           label("Travel insurance  ₹299", 20, TEXT).shift(RIGHT * 0.3), label("pre-ticked for you", 15, GOLD).shift(DOWN * 0.5)))
        t3 = VGroup(RoundedRectangle(width=4.0, height=1.5, corner_radius=0.15, color=KILL, stroke_width=3, fill_color="#1f2937", fill_opacity=1),
                    VGroup(chip("YES, UPGRADE ME", SAFE, 18), label("no thanks", 13, "#4b5563")).arrange(DOWN, buff=0.15))
        for t in (t1, t2, t3):
            t[1].move_to(t[0])
        cards = VGroup(t1, t2, t3).arrange(RIGHT, buff=0.4).move_to(STAGE + UP * 0.5)
        self.stage.add(cards)
        self.go(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cards], lag_ratio=0.4), run_time=1.6)
        self.sfx("kill")
        self.at(b, 1)
        self.punch("built to trick you: learn to spot them, refuse to build them", KILL, 28, -1.6)

    # ------------------------------------------------------------ practice
    def b_p_intro(self, b):
        self.question_card(b, ["One app that annoys you:", "name the exact moment it goes wrong.", "signifier?  size?  too many choices?  a gulf?"])

    def b_p_pause(self, b):
        self.pause_screen(b, "Pause and think of one")

    def b_p_answer(self, b):
        self.pause_over()
        self.screen("YOU JUST DID A HEURISTIC EVALUATION", GOLD)
        fl = flow(["missing signifier", "button too small", "too many choices", "a gulf"], KILL, 22, 0.3).move_to(STAGE + UP * 0.9)
        self.show(fl[0], run_time=0.8)
        self.at(b, 1)
        m = chips(["Nielsen's 10 heuristics", "severity ratings", "cognitive walkthrough"], GOLD, 24).move_to(STAGE + DOWN * 0.6)
        self.show(m, run_time=0.8)
        self.sfx("pop")
        n = label("instinct → method", 30, TEXT, "BOLD").move_to(STAGE + DOWN * 1.9)
        self.show(n, run_time=0.4)

    # ------------------------------------------------------------ what you will build
    def b_b_lab(self, b):
        self.screen("WHAT YOU WILL BUILD", SAFE)
        bar = VGroup(Rectangle(width=3.6, height=1.0, color=ACCENT, fill_color=ACCENT, fill_opacity=1, stroke_width=0),
                     Rectangle(width=7.2, height=1.0, color=SAFE, fill_color=SAFE, fill_opacity=1, stroke_width=0)).arrange(RIGHT, buff=0).move_to(STAGE + UP * 0.8)
        t = VGroup(label("1 h lecture", 22, TEXT, "BOLD").move_to(bar[0]), label("2 h laboratory, every week", 22, DARK, "BOLD").move_to(bar[1]))
        self.show(bar, t, run_time=0.7)
        self.at(b, 1)
        no = VGroup(label("sit and memorise", 40, MUTED, "BOLD")).move_to(STAGE + DOWN * 0.9)
        self.show(no, run_time=0.4)
        self.show(Line(no.get_left(), no.get_right(), color=KILL, stroke_width=6), anim=Create, run_time=0.3)
        self.punch("you will design", SAFE, 40, -2.2)

    def build_step(self, n, title, items, extra=None):
        self.screen(f"YOU WILL BUILD  ·  STEP {n}", SAFE, title)
        self.row(chips(items, ACCENT, 22), gap=0.8)
        if extra:
            self.at(self._b, 1)
            self.row(chips(extra, GOLD, 22), gap=0.8)

    def b_b_research(self, b):
        self._b = b
        self.screen("YOU WILL BUILD  ·  STEP 1", SAFE, "Study real users")
        self.row(flow(["interview 5 people", "personas", "journey map"], ACCENT, 22, 0.4), gap=0.9)
        self.at(b, 1)
        self.row(chips(["keystroke-level model: predict an expert's task time"], GOLD, 22), gap=0.8)

    def b_b_proto(self, b):
        self.screen("YOU WILL BUILD  ·  STEP 2", SAFE, "Structure and prototype")
        self.row(flow(["card sorting", "wireframes, 3+ screens", "clickable Figma prototype"], ACCENT, 22, 0.4), gap=0.9)
        self.at(b, 1)
        self.row(chips(["Shneiderman's golden rules", "a real design system"], GOLD, 22), gap=0.8)

    def b_b_test(self, b):
        self.screen("YOU WILL BUILD  ·  STEP 3", SAFE, "Test it with real users")
        self.row(chips(["think-aloud usability test"], ACCENT, 24), gap=0.9)
        grid = VGroup(*[VGroup(label(k, 18, MUTED), label(v, 30, TEXT, "BOLD")).arrange(DOWN, buff=0.05) for k, v in
                        [("task success rate", "80 %"), ("time on task", "42 s"), ("error rate", "0.4"), ("SUS", "72")]]).arrange(RIGHT, buff=0.9).move_to(STAGE + DOWN * 0.6)
        self.show(grid, run_time=0.8)
        ex = label("(example numbers)", 16, MUTED).next_to(grid, DOWN, buff=0.15)
        self.show(ex, run_time=0.2)
        self.at(b, 1)
        self.punch("numbers, not opinions", GOLD, 32, -2.3)

    def b_b_access(self, b):
        self.screen("YOU WILL BUILD  ·  STEP 4", SAFE, "Audit a public website for accessibility")
        self.row(chips(["WAVE", "Lighthouse", "NVDA screen reader", "WCAG 2.2"], ACCENT, 22), gap=0.9)
        self.at(b, 1)
        issues = chips(["no alt text ✗", "low contrast ✗", "no keyboard access ✗", "missing ARIA labels ✗"], KILL, 20)
        self.row(issues, gap=0.9)
        self.punch("how many sites a blind user simply cannot use", GOLD, 26, -1.9)

    def b_b_mini(self, b):
        self.screen("YOU WILL BUILD  ·  THE MINI PROJECT", GOLD, "A complete user-centred design of something you choose")
        self.at(b, 1)
        topics = ["accessible e-governance app", "campus navigation app", "chatbot for student queries", "voice interface for visually impaired users", "banking app without dark patterns"]
        cs = [chip(t, PURPLE, 22) for t in topics]
        grid = VGroup(VGroup(*cs[:3]).arrange(RIGHT, buff=0.3), VGroup(*cs[3:]).arrange(RIGHT, buff=0.3)).arrange(DOWN, buff=0.35).move_to(STAGE + DOWN * 0.2)
        if grid.width > 13.2:
            grid.scale_to_fit_width(13.2)
        self.stage.add(grid)
        self.go(LaggedStart(*[GrowFromCenter(c) for c in cs], lag_ratio=0.2), run_time=1.8)
        self.sfx("pop")

    # ------------------------------------------------------------ units in brief
    def units(self, b, first):
        if first:
            self.screen("THE THEORY BEHIND EVERY STEP", PINK)
            self.unit_cards = VGroup(*[titled_card(f"UNIT {r}", c, lines, 3.1, 2.6, 26, 19) for r, c, lines in
                                       [("I", SAFE, ["the human:", "perception, memory, error", "Norman's principles"]),
                                        ("II", GOLD, ["interaction design", "design thinking", "visual design, prototyping"]),
                                        ("III", ACCENT, ["usability engineering", "user research, task analysis", "heuristic evaluation"]),
                                        ("IV", PURPLE, ["usability testing", "accessibility, ethics", "designing for AI"])]]).arrange(RIGHT, buff=0.3).move_to(STAGE + UP * 0.2)
            self.stage.add(self.unit_cards)
            self.go(FadeIn(self.unit_cards[0], shift=UP * 0.2), run_time=0.5)
            self.at(b, 1)
            self.go(FadeIn(self.unit_cards[1], shift=UP * 0.2), run_time=0.5)
        else:
            self.go(FadeIn(self.unit_cards[2], shift=UP * 0.2), run_time=0.5)
            self.at(b, 1)
            self.go(FadeIn(self.unit_cards[3], shift=UP * 0.2), run_time=0.5)
            self.sfx("pop")
            n = label("15 hours of theory, 30 hours of laboratory", 22, MUTED).move_to(STAGE + DOWN * 2.0)
            self.show(n, run_time=0.4)

    def b_t_units12(self, b):
        self.units(b, True)

    def b_t_units34(self, b):
        self.units(b, False)

    # ------------------------------------------------------------ marks
    def b_m_scheme(self, b):
        self.screen("MARKS  ·  50 IN TOTAL", PINK)
        no = chip("no written end exam", KILL, 30).move_to(STAGE + UP * 1.5)
        self.show(no, anim=GrowFromCenter, run_time=0.5)
        self.sfx("pop")
        self.at(b, 1)
        cs = VGroup(titled_card("Continuous assessment  ·  25", ACCENT, ["active learning  10", "task based learning  10", "presentation  5"], 6.0, 2.3, 24, 20),
                    titled_card("End oral exam  ·  25", GOLD, ["based on your laboratory work", "and the mini project"], 6.0, 2.3, 24, 20)).arrange(RIGHT, buff=0.5).move_to(STAGE + DOWN * 0.6)
        self.stage.add(cs)
        self.go(FadeIn(cs[0], shift=UP * 0.2), run_time=0.5)
        self.until(b["phrases"][1]["start"] + self.phrase_len(b, 1) * 0.55)
        self.go(FadeIn(cs[1], shift=UP * 0.2), run_time=0.5)

    def b_m_fair(self, b):
        self.screen("A FAIR WAY TO BE MARKED", PINK)
        fl = flow(["do the assignments", "a portfolio", "the oral: a conversation about your designs"], GOLD, 22, 0.4).move_to(STAGE + UP * 0.6)
        if fl.width > 13.0:
            fl.scale_to_fit_width(13.0)
        self.show(fl[0][0], run_time=0.4)
        self.at(b, 1)
        self.show(fl[1][0], fl[0][1], run_time=0.5)
        self.show(fl[1][1], fl[0][2], run_time=0.5)
        self.sfx("chime")
        self.punch("you are marked on what you build", SAFE, 30, -1.4)

    # ------------------------------------------------------------ why enrol
    def reason(self, n, title, lines, color):
        if n == 1:
            self.screen("WHY PICK THIS ELECTIVE", PINK)
            self.reasons = VGroup()
        c = titled_card(f"{n}  ·  {title}", color, lines, 6.3, 2.0, 26, 20)
        pos = [STAGE + LEFT * 3.3 + UP * 1.0, STAGE + RIGHT * 3.3 + UP * 1.0, STAGE + LEFT * 3.3 + DOWN * 1.4, STAGE + RIGHT * 3.3 + DOWN * 1.4][n - 1]
        c.move_to(pos)
        self.show(c, run_time=0.6, shift=UP * 0.2)
        self.sfx("pop")
        return c

    def b_r_career(self, b):
        self.reason(1, "Career", ["every product company has UX roles;", "developers who understand users ship better software"], ACCENT)
        self.at(b, 1)
        self.punch("HCI makes you both", GOLD, 24, -2.9)

    def b_r_ai(self, b):
        self.reason(2, "AI changed the interface", ["chatbots, voice assistants, copilots", "need design more than ever"], PURPLE)

    def b_r_portfolio(self, b):
        self.reason(3, "A portfolio", ["a Figma prototype, a usability report,", "an accessibility audit: show them in an interview"], SAFE)

    def b_r_fun(self, b):
        self.reason(4, "It is fun", ["argue about buttons, test your friends,", "break websites, see the world differently"], GOLD)
        self.at(b, 1)
        self.punch("once you see bad design, you cannot unsee it", GOLD, 24, -2.9)

    # ------------------------------------------------------------ tips, recap, close
    def b_tip1(self, b):
        self.tip(b, 1, "The one-minute test, tonight", "any app, one task you have never done: count the taps, note every hesitation")

    def b_tip2(self, b):
        self.tip(b, 2, "Install Figma this week", "free education plan for students; we start wireframing early")

    def b_tip3(self, b):
        self.tip(b, 3, "Keep a design diary from day one", "every bad interface you meet, one line each: gold for your mini project")

    def b_recap(self, b):
        self.recap(b, ["HCI designs the meeting point of humans and machines", "It blames the design, not the user",
                       "You research, prototype, test and audit real interfaces", "You are marked on what you build, not a written paper"])

    def b_next(self, b):
        self.clear(run_time=0.4)
        en = VGroup(label("ENROL", 90, PINK, "BOLD"), chip("ETCS334  ·  Human Computer Interface  ·  Programme Elective VI", GOLD, 26, DARK),
                    label("bring a problem you want to fix", 30, TEXT)).arrange(DOWN, buff=0.35).move_to(STAGE + UP * 0.4)
        self.show(en, anim=GrowFromCenter, run_time=0.7)
        self.sfx("chime")
        self.at(b, 1)
        nxt = VGroup(label("FIRST LECTURE", 22, MUTED, "BOLD"), label("Foundations of HCI: the human", 30, TEXT, "BOLD")).arrange(DOWN, buff=0.1)
        box = card(nxt.width + 0.8, nxt.height + 0.5, edge=PINK)
        g = VGroup(box, nxt.move_to(box)).move_to(STAGE + DOWN * 2.3)
        self.show(g, run_time=0.5, shift=UP * 0.2)
