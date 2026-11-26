"""49-second brand promo for the DAA series: four text scenes (the clip montage between them is cut by build.py).

    manim -qh --fps 30 --media_dir projects/branding/build videos/brand/promo.py IntroScene PromiseScene ProgressScene OutroScene
"""
import sys
from pathlib import Path

from manim import (DOWN, LEFT, RIGHT, UP, FadeIn, FadeOut, GrowFromCenter, Scene, VGroup, config, Write, rate_functions)

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from kit import ACCENT, BG, GOLD, KILL, MUTED, PANEL, SAFE, TEXT, UNIT_COLORS, card, chip, label  # noqa: E402

config.background_color = BG
RED = "#FF0000"


class Timed(Scene):
    """Animations are placed at absolute seconds so the cut points in build.py stay exact."""
    LENGTH = 4.0

    def __init__(self, **kw):
        super().__init__(**kw)
        self.t = 0.0

    def at(self, when, *anims, run_time=0.5):
        if when > self.t:
            self.wait(when - self.t)
            self.t = when
        self.play(*anims, run_time=run_time)
        self.t += run_time

    def finish(self):
        if self.LENGTH > self.t:
            self.wait(self.LENGTH - self.t)


class IntroScene(Timed):
    LENGTH = 4.4

    def construct(self):
        tag = chip("DAA SERIES  ·  DES PUNE UNIVERSITY", GOLD, 22, BG).move_to(UP * 2.2)
        t1 = label("Design & Analysis", 72, TEXT, "BOLD")
        t2 = label("of Algorithms", 72, TEXT, "BOLD")
        title = VGroup(t1, t2).arrange(DOWN, buff=0.15).move_to(UP * 0.35)
        sub = label("every algorithm, step by step", 34, MUTED).next_to(title, DOWN, buff=0.5)
        by = VGroup(label("with", 28, MUTED), label("Abhijeet Karve", 40, GOLD, "BOLD")).arrange(RIGHT, buff=0.25)
        by.next_to(sub, DOWN, buff=0.45)
        self.at(0.2, FadeIn(tag, shift=DOWN * 0.2), run_time=0.4)
        self.at(0.6, FadeIn(title, shift=UP * 0.3), run_time=0.6)
        self.at(1.6, FadeIn(sub, shift=UP * 0.2), run_time=0.5)
        self.at(2.5, FadeIn(by, shift=UP * 0.2), run_time=0.5)
        self.finish()


ROWS = [("A real problem first", "the hook that makes the idea matter"),
        ("Every step traced on screen", "tables, trees and graphs, animated"),
        ("Proofs you can write in the exam", "short, exact, in the words the examiner expects"),
        ("A practice question, with a pause", "work it out before the answer appears"),
        ("Exam tips and a recap", "what to write, in what order")]


class PromiseScene(Timed):
    LENGTH = 12.0

    def construct(self):
        head = label("EVERY VIDEO, THE SAME PROMISE", 40, TEXT, "BOLD").move_to(UP * 2.9)
        rows = VGroup()
        for i, (big, small) in enumerate(ROWS):
            num = chip(str(i + 1), ACCENT, 26)
            txt = VGroup(label(big, 36, TEXT, "BOLD"), label(small, 24, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
            rows.add(VGroup(num, txt).arrange(RIGHT, buff=0.4, aligned_edge=UP))
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.32).move_to(DOWN * 0.45)
        for r in rows:
            r[0].align_to(r[1][0], UP).shift(DOWN * 0.02)
        self.at(0.3, FadeIn(head, shift=UP * 0.2), run_time=0.5)
        for i, r in enumerate(rows):
            self.at(1.2 + 1.8 * i, FadeIn(r, shift=RIGHT * 0.3), run_time=0.45)
        self.finish()


UNITS = [("III", "Unit III", "Backtracking, Branch & Bound", "5 videos", True),
         ("IV", "Unit IV", "NP-completeness, approximation", "5 videos", True),
         ("V", "Unit V", "Network flow & more", "coming next", False)]


class ProgressScene(Timed):
    LENGTH = 8.6

    def construct(self):
        head = label("WHERE THE SERIES IS", 40, TEXT, "BOLD").move_to(UP * 2.9)
        cards = VGroup()
        for unit, name, topic, count, done in UNITS:
            colour = UNIT_COLORS[unit]
            box = card(12.4, 1.25)
            tag = chip(name.upper(), colour, 22).move_to(box.get_left() + RIGHT * 1.25)
            text = label(topic, 31, TEXT, "BOLD").next_to(tag, RIGHT, buff=0.4)
            right = chip(("✓  " if done else "") + count, SAFE if done else colour, 22).move_to(box.get_right() + LEFT * 1.35)
            cards.add(VGroup(box, tag, text, right))
        cards.arrange(DOWN, buff=0.28).move_to(DOWN * 0.1)
        foot = chip("plus lab demos: the same programs written and run in C++ and Java", PANEL, 24, TEXT).move_to(DOWN * 2.9)
        self.at(0.3, FadeIn(head, shift=UP * 0.2), run_time=0.5)
        for i, c in enumerate(cards):
            self.at(1.0 + 1.6 * i, FadeIn(c, shift=RIGHT * 0.3), run_time=0.45)
        self.at(5.8, FadeIn(foot, shift=UP * 0.2), run_time=0.5)
        self.finish()


class OutroScene(Timed):
    LENGTH = 8.2

    def construct(self):
        tag = chip("DAA SERIES", GOLD, 24, BG).move_to(UP * 2.6)
        name = label("Abhijeet Karve", 64, TEXT, "BOLD").move_to(UP * 1.4)
        line = label("Design & Analysis of Algorithms  ·  ETCS329  ·  DES Pune University", 28, MUTED).move_to(UP * 0.55)
        btn = chip("▶   Watch the playlist on YouTube", RED, 34, TEXT, pad=0.35).move_to(DOWN * 0.75)
        hint = label("link in the post  ·  free for every student", 28, MUTED).move_to(DOWN * 1.75)
        self.at(0.2, FadeIn(tag, shift=DOWN * 0.2), run_time=0.4)
        self.at(0.6, FadeIn(name, shift=UP * 0.3), run_time=0.6)
        self.at(1.3, FadeIn(line, shift=UP * 0.2), run_time=0.5)
        self.at(2.2, GrowFromCenter(btn), run_time=0.6)
        self.at(3.0, FadeIn(hint, shift=UP * 0.2), run_time=0.5)
        self.finish()
