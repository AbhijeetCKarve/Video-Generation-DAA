"""Vertical (9:16) scenes for the 30-second hook-first promo. Rendered at 1080x1920; the lesson clips in the
middle are cut in by short_build.py. Content stays above y = -4 so the burned-in captions have the bottom band.

    manim -qh --fps 30 -r 1080,1920 --media_dir projects/branding/build-short videos/brand/short.py HookScene ProblemScene PromiseScene CTAScene
"""
import sys
from pathlib import Path

import numpy as np
from manim import DOWN, LEFT, RIGHT, UP, Dot, FadeIn, GrowFromCenter, LaggedStart, Scene, VGroup, config

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from kit import ACCENT, BG, GOLD, KILL, MUTED, PANEL, SAFE, TEXT, UNIT_COLORS, chip, label  # noqa: E402

config.pixel_width, config.pixel_height = 1080, 1920
config.frame_height, config.frame_width = 14.2222, 8.0
config.background_color = BG
RED = "#FF0000"


class Timed(Scene):
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


def lines(texts, size, color=TEXT, weight="BOLD", buff=0.12):
    return VGroup(*[label(t, size, c if isinstance(c, str) else color, weight)
                    for t, c in [(x if isinstance(x, tuple) else (x, None)) for x in texts]]).arrange(DOWN, buff=buff)


class HookScene(Timed):
    LENGTH = 4.6

    def construct(self):
        rng = np.random.default_rng(7)
        dots = VGroup(*[Dot(radius=0.04, color=ACCENT, fill_opacity=0.55).move_to([x, y, 0])
                        for x, y in zip(rng.uniform(-3.7, 3.7, 200), rng.uniform(-3.8, 5.6, 200))])
        l1 = label("200 CITIES.", 92, GOLD, "BOLD").move_to(UP * 3.6)
        l2 = label("VANS LEAVE AT 8.", 64, TEXT, "BOLD").move_to(UP * 2.2)
        l3 = label("THE BEST ROUTE?", 64, TEXT, "BOLD").move_to(UP * 0.9)
        l4 = VGroup(chip("NO COMPUTER CAN", KILL, 34, TEXT, pad=0.3), chip("FIND IT IN TIME", KILL, 34, TEXT, pad=0.3)).arrange(DOWN, buff=0.12).move_to(DOWN * 0.9)
        self.at(0.0, LaggedStart(*[GrowFromCenter(d) for d in dots], lag_ratio=0.004), run_time=0.9)
        self.t = 0.9
        self.at(0.5, FadeIn(l1, shift=UP * 0.3), run_time=0.4)
        self.at(1.5, FadeIn(l2, shift=UP * 0.3), run_time=0.4)
        self.at(2.5, FadeIn(l3, shift=UP * 0.3), run_time=0.4)
        self.at(3.3, GrowFromCenter(l4), run_time=0.4)
        self.finish()


class ProblemScene(Timed):
    LENGTH = 5.0

    def construct(self):
        a = lines(["Students don't fail", "algorithms because", "the ideas are hard."], 62).move_to(UP * 3.3)
        a[2].set_color(MUTED)
        b = lines(["They fail because", "the textbook", ("skips the steps.", GOLD)], 62).move_to(DOWN * 0.6)
        self.at(0.2, FadeIn(a, shift=UP * 0.3), run_time=0.5)
        self.at(2.3, FadeIn(b, shift=UP * 0.3), run_time=0.5)
        self.finish()


class PromiseScene(Timed):
    LENGTH = 5.2

    def construct(self):
        l1 = label("EVERY STEP.", 76, TEXT, "BOLD").move_to(UP * 3.8)
        l2 = label("ON SCREEN.", 76, TEXT, "BOLD").move_to(UP * 2.6)
        l3 = lines(["IN THE WORDS THE", "EXAMINER EXPECTS."], 46, GOLD).move_to(UP * 1.0)
        row = VGroup(chip("10 LECTURES", ACCENT, 30), chip("3.1 → 4.5", UNIT_COLORS["IV"], 30),
                     chip("FREE", SAFE, 30)).arrange(RIGHT, buff=0.22).move_to(DOWN * 0.6)
        self.at(0.2, FadeIn(l1, shift=UP * 0.3), run_time=0.4)
        self.at(1.0, FadeIn(l2, shift=UP * 0.3), run_time=0.4)
        self.at(1.9, FadeIn(l3, shift=UP * 0.3), run_time=0.5)
        self.at(3.3, LaggedStart(*[GrowFromCenter(c) for c in row], lag_ratio=0.3), run_time=0.7)
        self.finish()


class CTAScene(Timed):
    LENGTH = 4.6

    def construct(self):
        tag = chip("DAA SERIES", GOLD, 30, BG).move_to(UP * 4.3)
        name = label("Abhijeet Karve", 60, TEXT, "BOLD").move_to(UP * 3.1)
        sub = lines(["Design & Analysis", "of Algorithms"], 40, MUTED, "NORMAL", 0.08).move_to(UP * 1.6)
        btn = chip("▶   Watch the playlist", RED, 38, TEXT, pad=0.4).move_to(DOWN * 0.1)
        hint = label("link below", 38, MUTED).move_to(DOWN * 1.3)
        self.at(0.2, FadeIn(tag, shift=DOWN * 0.2), run_time=0.4)
        self.at(0.5, FadeIn(name, shift=UP * 0.3), run_time=0.5)
        self.at(1.0, FadeIn(sub, shift=UP * 0.2), run_time=0.4)
        self.at(1.7, GrowFromCenter(btn), run_time=0.5)
        self.at(2.5, FadeIn(hint, shift=UP * 0.2), run_time=0.4)
        self.finish()
