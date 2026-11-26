"""Vertical 30-second promo, all native: every scene fills the 1080x1920 frame, hard cuts on the bar of a
104-bpm track (one bar = 2.3077 s). Captions are burned in later, so nothing sits below y = -4.6.

    manim -qh --fps 30 -r 1080,1920 --media_dir projects/branding/build-short2 videos/brand/short2.py \
        HookScene ProblemScene StepBacktrack StepBranch StepTSP StepNP StepApprox PromiseScene CTAScene
"""
import sys
from pathlib import Path

import numpy as np
from manim import (DOWN, LEFT, ORIGIN, PI, RIGHT, UP, AnimationGroup, Circle, Create, FadeIn, FadeOut, GrowFromCenter,
                   Indicate, LaggedStart, Line, Scene, Transform, VGroup, VMobject, config, rate_functions)

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from kit import ACCENT, BG, BACK, GOLD, KILL, MUTED, PANEL, PANEL_EDGE, SAFE, TEXT, UNIT_COLORS, Board, card, chip, label  # noqa: E402

config.pixel_width, config.pixel_height = 1080, 1920
config.frame_height, config.frame_width = 14.2222, 8.0
config.background_color = BG
BAR = 60 / 104 * 4           # 2.3077 s
BEAT = BAR / 4
RED = "#FF0000"
PURPLE, REDU = UNIT_COLORS["IV"], UNIT_COLORS["III"]


class Timed(Scene):
    BARS = 2

    def __init__(self, **kw):
        super().__init__(**kw)
        self.t = 0.0

    @property
    def length(self):
        return self.BARS * BAR

    def at(self, when, *anims, run_time=0.3):
        if when > self.t + 1e-6:
            self.wait(when - self.t)
            self.t = when
        self.play(*anims, run_time=run_time)
        self.t += run_time

    def punch(self, when, *mobs, run_time=0.28):
        """Words land with a snap: scale in with a slight overshoot."""
        self.at(when, *[GrowFromCenter(m, rate_func=rate_functions.ease_out_back) for m in mobs], run_time=run_time)

    def finish(self):
        if self.length > self.t:
            self.wait(self.length - self.t)


def big(text, size, color=TEXT, y=0.0):
    return label(text, size, color, "BOLD").move_to(UP * y)


# ------------------------------------------------------------------ 1. hook: 200 cities, routes thrash, impossible
class HookScene(Timed):
    BARS = 2.5

    def construct(self):
        rng = np.random.default_rng(3)
        pts = np.column_stack([rng.uniform(-3.7, 3.7, 160), rng.uniform(-4.2, 5.8, 160), np.zeros(160)])
        dots = VGroup(*[Circle(radius=0.045, color=ACCENT, fill_opacity=0.7, stroke_width=0).move_to(p) for p in pts])
        self.play(LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.003), run_time=0.45)
        self.t = 0.45
        route = VMobject(stroke_color=ACCENT, stroke_width=3, stroke_opacity=0.8)
        route.set_points_as_corners(pts[rng.permutation(160)[:18]])
        self.add(route)
        l1 = big("200 CITIES.", 84, GOLD, 4.3)
        l2 = big("VANS LEAVE AT 8.", 62, TEXT, 3.0)
        l3 = big("THE BEST ROUTE?", 58, TEXT, 1.7)
        stamp = chip("IMPOSSIBLE IN TIME", KILL, 44, TEXT, pad=0.34).rotate(-4 * PI / 180).move_to(DOWN * 0.5)
        words = {BEAT * 1: l1, BEAT * 3: l2, BEAT * 5: l3}
        k = 0
        while self.t < BEAT * 7 - 0.05:                       # the route keeps re-trying a new order
            due = [w for tt, w in words.items() if tt <= self.t + 0.2 and w not in self.mobjects]
            new = VMobject(stroke_color=ACCENT if k < 10 else KILL, stroke_width=3, stroke_opacity=0.85)
            new.set_points_as_corners(pts[rng.permutation(160)[:18]])
            anims = [Transform(route, new)] + [GrowFromCenter(w, rate_func=rate_functions.ease_out_back) for w in due]
            self.play(*anims, run_time=0.2)
            self.t += 0.2
            k += 1
        self.punch(BEAT * 7, stamp, run_time=0.25)
        self.finish()


# ------------------------------------------------------------------ 2. the problem
class ProblemScene(Timed):
    BARS = 2.5

    def construct(self):
        a1, a2, a3 = big("STUDENTS", 92, TEXT, 4.4), big("DON'T FAIL", 92, TEXT, 3.2), big("BECAUSE IT'S HARD.", 50, MUTED, 2.1)
        self.punch(0.0, a1)
        self.punch(0.25, a2)
        self.punch(BEAT * 1, a3)
        b1, b2, b3 = big("THEY FAIL", 92, TEXT, 4.4), big("BECAUSE THE TEXTBOOK", 46, MUTED, 3.3), big("SKIPS", 110, GOLD, 1.9)
        b4 = big("THE STEPS.", 84, GOLD, 0.6)
        self.at(BAR + BEAT, FadeOut(VGroup(a1, a2, a3)), run_time=0.12)
        self.punch(BAR + BEAT + 0.12, b1)
        self.punch(BAR + BEAT + 0.4, b2)
        self.punch(BAR + BEAT * 3, b3, b4, run_time=0.3)
        self.finish()


# ------------------------------------------------------------------ 3. five steps, one bar each
class Step(Timed):
    BARS = 1
    TITLE, COLOUR = "", ACCENT

    def title(self):
        self.punch(0.0, chip(self.TITLE, self.COLOUR, 48, TEXT, pad=0.3).move_to(UP * 5.4), run_time=0.25)


class StepBacktrack(Step):
    TITLE, COLOUR = "BACKTRACKING", REDU

    def construct(self):
        self.title()
        b = Board(6, size=6.4, labels=False).move_to(UP * 0.4)
        self.add(b)
        seq = [("place", 0, 0), ("place", 1, 2), ("place", 2, 4), ("kill", 3, 1), ("kill", 3, 3), ("remove", 2),
               ("place", 2, 5), ("place", 3, 1), ("place", 4, 3)]
        t = 0.3
        for ev in seq:
            if ev[0] == "place":
                an, _ = b.place(ev[1], ev[2])
                self.at(t, an, run_time=0.2)
            elif ev[0] == "kill":
                self.at(t, b.kill(ev[1], ev[2]), run_time=0.2)
            else:
                self.at(t, b.remove(ev[1]), run_time=0.2)
            t += 0.2
        self.finish()


def node(txt, color=TEXT, fill=PANEL, r=0.34, size=30):
    c = Circle(radius=r, color=color, fill_color=fill, fill_opacity=1, stroke_width=3)
    return VGroup(c, label(txt, size, TEXT, "BOLD").move_to(c))


class StepBranch(Step):
    TITLE, COLOUR = "BRANCH & BOUND", REDU

    def construct(self):
        self.title()
        root = node("10", GOLD).move_to(UP * 3.2)
        kids = [node(v).move_to([x, 1.2, 0]) for v, x in (("16", -2.4), ("10", 0), ("21", 2.4))]
        grand = [node(v).move_to([x, -0.9, 0]) for v, x in (("12", -1.3), ("15", 0), ("25", 1.3))]
        e1 = [Line(root.get_bottom(), k.get_top(), stroke_width=3, color=PANEL_EDGE) for k in kids]
        e2 = [Line(kids[1].get_bottom(), g.get_top(), stroke_width=3, color=PANEL_EDGE) for g in grand]
        self.at(0.25, GrowFromCenter(root), run_time=0.2)
        self.at(0.5, *[Create(e) for e in e1], *[GrowFromCenter(k) for k in kids], run_time=0.35)
        self.at(1.0, kids[1][0].animate.set_stroke(GOLD, 6), run_time=0.2)
        self.at(1.25, *[Create(e) for e in e2], *[GrowFromCenter(g) for g in grand], run_time=0.35)
        self.at(1.7, grand[0][0].animate.set_stroke(GOLD, 6), GrowFromCenter(chip("least cost first", GOLD, 34, BG).move_to(DOWN * 2.6)), run_time=0.25)
        self.finish()


class StepTSP(Step):
    TITLE, COLOUR = "TSP", REDU

    def construct(self):
        self.title()
        rows = [["∞", "10", "20", "0", "1"], ["13", "∞", "14", "2", "0"], ["1", "3", "∞", "0", "2"],
                ["16", "3", "15", "∞", "0"], ["12", "0", "3", "12", "∞"]]
        before = [["∞", "20", "30", "10", "11"], ["15", "∞", "16", "4", "2"], ["3", "5", "∞", "2", "4"],
                  ["19", "6", "18", "∞", "3"], ["16", "4", "7", "16", "∞"]]
        cell = 1.2
        grid = VGroup()
        for r in range(5):
            for c in range(5):
                box = card(cell, cell, PANEL, PANEL_EDGE).move_to([(c - 2) * cell, 2.8 - r * cell, 0])
                grid.add(VGroup(box, label(before[r][c], 40, TEXT, "BOLD").move_to(box)))
        self.at(0.25, FadeIn(grid), run_time=0.25)
        for r in range(5):
            tr = [Transform(grid[r * 5 + c][1], label(rows[r][c], 40, GOLD if rows[r][c] == "0" and before[r][c] != "0" else TEXT, "BOLD").move_to(grid[r * 5 + c][0])) for c in range(5)]
            self.at(0.6 + 0.22 * r, *tr, run_time=0.18)
        self.at(1.85, GrowFromCenter(chip("reduced cost  ĉ = 21", GOLD, 36, BG).move_to(DOWN * 3.4)), run_time=0.25)
        self.finish()


class StepNP(Step):
    TITLE, COLOUR = "NP-COMPLETE", PURPLE

    def construct(self):
        self.title()
        cols = [("x₁", "¬x₂", "x₃"), ("¬x₁", "x₂", "x₃"), ("x₁", "x₂", "¬x₃")]
        nodes = [[node(t, TEXT, PANEL, 0.4, 28).move_to([(i - 1) * 2.7, 3.0 - j * 1.6, 0]) for j, t in enumerate(col)] for i, col in enumerate(cols)]
        heads = [chip(f"C{i + 1}", PURPLE, 26).move_to([(i - 1) * 2.7, 4.3, 0]) for i in range(3)]
        self.at(0.25, *[GrowFromCenter(n) for col in nodes for n in col], *[GrowFromCenter(h) for h in heads], run_time=0.3)
        edges = []
        for i in range(3):
            for j in range(i + 1, 3):
                for a in nodes[i]:
                    for b in nodes[j]:
                        ta, tb = a[1].text, b[1].text
                        if ta.replace("¬", "") != tb.replace("¬", "") or ta == tb:
                            edges.append(Line(a[0].get_center(), b[0].get_center(), stroke_width=1.8, color=MUTED, stroke_opacity=0.6, z_index=-1))
        self.at(0.7, LaggedStart(*[Create(e) for e in edges], lag_ratio=0.02), run_time=0.8)
        tri = [nodes[0][2], nodes[1][2], nodes[2][0]]
        gold = VGroup(*[Line(tri[i][0].get_center(), tri[j][0].get_center(), stroke_width=7, color=GOLD) for i, j in ((0, 1), (1, 2), (0, 2))])
        self.at(1.6, Create(gold), *[n[0].animate.set_stroke(GOLD, 6) for n in tri], run_time=0.3)
        self.at(1.95, GrowFromCenter(chip("a clique of size 3  →  satisfiable", GOLD, 30, BG).move_to(DOWN * 2.2)), run_time=0.25)
        self.finish()


class StepApprox(Step):
    TITLE, COLOUR = "APPROXIMATION", PURPLE

    def construct(self):
        self.title()
        pos = {1: (-3, 3.2), 2: (-1, 3.2), 3: (1, 3.2), 4: (3, 3.2), 7: (3, 0.6), 5: (-1, 0.6), 6: (1, 0.6)}
        pos = {k: (x, y) for k, (x, y) in pos.items()}
        E = [(1, 2), (2, 3), (3, 4), (3, 5), (4, 5), (4, 6), (4, 7), (5, 6)]
        V = {k: node(str(k)).move_to([x, y, 0]) for k, (x, y) in pos.items()}
        L = {e: Line(V[e[0]][0].get_center(), V[e[1]][0].get_center(), stroke_width=4, color=PANEL_EDGE, z_index=-1) for e in E}
        self.at(0.25, *[Create(l) for l in L.values()], *[GrowFromCenter(v) for v in V.values()], run_time=0.35)
        t = 0.7
        gone = set()
        for pick in ((2, 3), (5, 6), (4, 7)):
            touch = [e for e in E if e not in gone and (set(e) & set(pick))]
            self.at(t, L[pick].animate.set_stroke(GOLD, 8), *[V[v][0].animate.set_fill(GOLD).set_stroke(GOLD) for v in pick],
                    *[V[v][1].animate.set_color(BG) for v in pick], run_time=0.2)
            self.at(t + 0.22, *[FadeOut(L[e]) for e in touch if e != pick], L[pick].animate.set_stroke(GOLD, 8, opacity=0.35), run_time=0.15)
            gone |= set(touch)
            t += 0.42
        self.at(t, GrowFromCenter(chip("cover of 6  ≤  2 × optimal", GOLD, 34, BG).move_to(DOWN * 1.4)), run_time=0.25)
        self.finish()


# ------------------------------------------------------------------ 4. promise
class PromiseScene(Timed):
    BARS = 2

    def construct(self):
        l1, l2 = big("EVERY STEP.", 88, TEXT, 4.4), big("ON SCREEN.", 88, TEXT, 3.1)
        l3, l4 = big("IN THE", 44, MUTED, 2.0), big("EXAMINER'S WORDS.", 50, GOLD, 1.1)
        row = VGroup(chip("10 LECTURES", ACCENT, 32), chip("3.1 → 4.5", PURPLE, 32), chip("FREE", SAFE, 32)).arrange(RIGHT, buff=0.22).move_to(DOWN * 0.7)
        tail = big("7 to 11 minutes each", 36, MUTED, -1.9)
        self.punch(0.0, l1)
        self.punch(BEAT, l2)
        self.punch(BEAT * 2, l3, l4)
        self.at(BAR, LaggedStart(*[GrowFromCenter(c, rate_func=rate_functions.ease_out_back) for c in row], lag_ratio=0.35), run_time=0.6)
        self.punch(BAR + BEAT * 2, tail)
        self.finish()


# ------------------------------------------------------------------ 5. sign-off
class CTAScene(Timed):
    BARS = 1.5

    def construct(self):
        tag = chip("DAA SERIES", GOLD, 32, BG).move_to(UP * 4.8)
        name = big("Abhijeet Karve", 66, TEXT, 3.5)
        sub = VGroup(label("Design & Analysis", 40, MUTED), label("of Algorithms", 40, MUTED)).arrange(DOWN, buff=0.08).move_to(UP * 2.1)
        btn = chip("▶   Watch the playlist", RED, 42, TEXT, pad=0.42).move_to(UP * 0.2)
        hint = big("link below  ↓", 40, MUTED, -1.0)
        self.punch(0.0, tag)
        self.punch(0.3, name)
        self.punch(0.7, sub)
        self.punch(BEAT * 2, btn, run_time=0.3)
        self.punch(BEAT * 3, hint)
        self.at(BAR + BEAT, Indicate(btn, scale_factor=1.06, color=RED), run_time=0.5)
        self.finish()
