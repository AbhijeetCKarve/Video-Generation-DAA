"""Video 4.1 - Polynomial vs Non-Polynomial & Non-Deterministic Algorithms.
Rendered by build.py (needs SCHEDULE / ENVELOPE env vars)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from lesson import *  # noqa: E402,F401,F403

PURPLE = UNIT_COLORS["IV"]
DARK = "#0F172A"

NSEARCH = ["Algorithm NSearch(A, n, x)",
           "{",
           "  j := Choice(1, n);",
           "  if (A[j] = x) then",
           "  {",
           "    write(j);  Success();",
           "  }",
           "  write(0);  Failure();",
           "}"]
NSORT = ["Algorithm NSort(A, n)",
         "// Sort n positive integers.",
         "{",
         "  for i := 1 to n do B[i] := 0;",
         "  for i := 1 to n do",
         "  {",
         "    j := Choice(1, n);",
         "    if (B[j] <> 0) then Failure();",
         "    B[j] := A[i];",
         "  }",
         "  for i := 1 to n - 1 do",
         "    if (B[i] > B[i+1]) then Failure();",
         "  write(B[1:n]);  Success();",
         "}"]
DKP = ["Algorithm DKP(p, w, n, m, r)",
       "{",
       "  W := 0;  P := 0;",
       "  for i := 1 to n do",
       "  {",
       "    x[i] := Choice(0, 1);",
       "    W := W + x[i] * w[i];",
       "    P := P + x[i] * p[i];",
       "  }",
       "  if ((W > m) or (P < r)) then Failure();",
       "  else Success();",
       "}"]
NHAM = ["Algorithm NHamiltonian(G, n)",
        "{",
        "  for i := 1 to n do v[i] := Choice(1, n);",
        "  if (a vertex repeats in v[1:n]) then Failure();",
        "  for i := 1 to n - 1 do",
        "    if ((v[i], v[i+1]) is not an edge) then Failure();",
        "  if ((v[n], v[1]) is not an edge) then Failure();",
        "  write(v[1:n]);  Success();",
        "}"]


def titled_card(title, color, lines, w, h, title_size=30, line_size=24, line_color=TEXT):
    """A panel with a coloured heading and a few lines of text under it."""
    body = VGroup(label(title, title_size, color, "BOLD"), *[label(t, line_size, line_color) for t in lines]
                  ).arrange(DOWN, buff=0.18)
    box = card(w, h, edge=color)
    return VGroup(box, body.move_to(box))


def cell_row(vals, pos, name=None, size=0.62, color=TEXT):
    """An array drawn as boxes with 1-based indices under them; .cells[i] is (box, text)."""
    g = VGroup()
    for i, v in enumerate(vals):
        q = pos + RIGHT * i * size
        g.add(VGroup(Square(size, stroke_color=PANEL_EDGE, stroke_width=2, fill_color=PANEL, fill_opacity=1).move_to(q),
                     label(str(v), 24, color).move_to(q)))
    idx = VGroup(*[label(str(i + 1), 16, MUTED).next_to(g[i], DOWN, buff=0.08) for i in range(len(vals))])
    out = VGroup(g, idx)
    if name:
        out.add(label(name, 26, MUTED, "BOLD").next_to(g, LEFT, buff=0.35))
    out.cells = g
    return out


def flow(chips, buff=0.5):
    """Chips in a row joined by arrows."""
    row = VGroup(*chips).arrange(RIGHT, buff=buff)
    arrows = VGroup(*[Arrow(row[i].get_right(), row[i + 1].get_left(), buff=0.08, color=MUTED, stroke_width=4,
                            max_tip_length_to_length_ratio=0.35) for i in range(len(chips) - 1)])
    return VGroup(row, arrows)


class Video(Lesson):
    NEXT = ("4.2  P, NP, NP-Hard", "& NP-Complete")

    # ------------------------------------------------------------ hook
    def b_hook_fast(self, b):
        pc = chip("1,000,000,000 steps / second", ACCENT, 34).move_to(STAGE + UP * 1.9)
        self.show(pc, anim=GrowFromCenter, run_time=0.6)
        self.sfx("pop")
        self.at(b, 1)
        row = flow([chip("sort 1,000,000 numbers", PANEL_EDGE, 28), chip("0.02 s", SAFE, 30)], buff=0.6)
        row.move_to(STAGE + UP * 0.3)
        self.show(row, run_time=0.6)
        self.sfx("chime")

    def b_hook_slow(self, b):
        row = flow([chip("every tour of 25 cities", PANEL_EDGE, 28), chip("10,000,000 years", KILL, 30)], buff=0.6)
        row.move_to(STAGE + DOWN * 1.2)
        self.show(row[0][0], row[1], run_time=0.5)
        self.at(b, 1)
        self.show(row[0][1], anim=GrowFromCenter, run_time=0.5)
        self.sfx("kill")
        self.go(row[0][1].animate.scale(1.25), run_time=0.4)

    def b_hook_name(self, b):
        self.clear(run_time=0.4)
        title = label("GROWTH RATE", 80, GOLD, "BOLD").move_to(STAGE + UP * 0.7)
        self.show(title, anim=GrowFromCenter, run_time=0.7)
        self.sfx("whoosh")
        self.at(b, 1)
        sub = chip("the first idea of complexity theory", PURPLE, 28).move_to(STAGE + DOWN * 0.8)
        self.show(sub, run_time=0.5)

    def b_syllabus(self, b):
        self.syllabus(b, ["Polynomial vs exponential growth", "Tractable vs intractable problems",
                          "Deterministic vs non-deterministic algorithms"], unit_text="UNIT IV  ·  COMPLEXITY")

    def b_exam(self, b):
        self.exam_star(b)

    # ------------------------------------------------------------ growth rates
    def b_g_poly(self, b):
        self.unsay()
        self.clear(run_time=0.4)
        c = titled_card("POLYNOMIAL TIME", SAFE, ["running time  ≤  c · nᵏ", "for some constant k"], 6.2, 2.4)
        c.move_to(STAGE + LEFT * 3.3 + UP * 1.2)
        self.show(c, run_time=0.6)
        self.at(b, 1)
        ex = VGroup(*[chip(t, SAFE, 26) for t in ["n", "n log n", "n²", "n³", "…", "nᵏ"]]).arrange(RIGHT, buff=0.2)
        ex.next_to(c, DOWN, buff=0.45)
        self.stage.add(ex)
        self.go(LaggedStart(*[FadeIn(e, shift=UP * 0.2) for e in ex], lag_ratio=0.3), run_time=1.6)
        self.sfx("pop")

    def b_g_exp(self, b):
        c = titled_card("EXPONENTIAL TIME", KILL, ["n sits in the exponent", "grows much, much faster"], 6.2, 2.4)
        c.move_to(STAGE + RIGHT * 3.3 + UP * 1.2)
        self.show(c, run_time=0.6)
        self.at(b, 1)
        ex = VGroup(*[chip(t, KILL, 26) for t in ["2ⁿ", "n!", "nⁿ"]]).arrange(RIGHT, buff=0.2).next_to(c, DOWN, buff=0.45)
        self.stage.add(ex)
        self.go(LaggedStart(*[FadeIn(e, shift=UP * 0.2) for e in ex], lag_ratio=0.3), run_time=1.0)
        self.sfx("pop")

    def b_g_table(self, b):
        self.clear(run_time=0.4)
        head = chip("1 step = 1 nanosecond   (a billion steps a second)", ACCENT, 24).move_to(STAGE + UP * 2.75)
        cols = ["", "n = 10", "n = 20", "n = 50", "n = 100"]
        rows = [("n²", ["100 ns", "400 ns", "2.5 µs", "10 µs"], SAFE),
                ("n³", ["1 µs", "8 µs", "125 µs", "1 ms"], SAFE),
                ("2ⁿ", ["1 µs", "1 ms", "13 days", "40 trillion years"], KILL),
                ("n!", ["3.6 ms", "77 years", "10⁴⁸ years", "10¹⁴¹ years"], KILL)]
        xs = [-4.7, -2.7, -0.7, 1.4, 3.8]
        ys = [1.7, 0.9, 0.1, -0.7, -1.5]
        box = card(10.8, 4.3).move_to(STAGE + UP * 0.1)
        hdr = VGroup(*[label(c, 24, MUTED, "BOLD").move_to(STAGE + np.array([x, ys[0], 0])) for c, x in zip(cols, xs)])
        sep = Line(STAGE + np.array([-5.2, 1.3, 0]), STAGE + np.array([5.2, 1.3, 0]), color=PANEL_EDGE, stroke_width=2)
        grid, self.tcell = VGroup(), {}
        for r, (nm, vals, col) in enumerate(rows):
            line = VGroup(label(nm, 32, col, "BOLD").move_to(STAGE + np.array([xs[0], ys[r + 1], 0])))
            for c, v in enumerate(vals):
                t = label(v, 24, TEXT).move_to(STAGE + np.array([xs[c + 1], ys[r + 1], 0]))
                self.tcell[(r, c)] = t
                line.add(t)
            grid.add(line)
        self.show(head, box, hdr, sep, run_time=0.5)
        self.stage.add(grid)
        self.go(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in grid], lag_ratio=0.4), run_time=1.8)
        self.at(b, 1)
        r1 = SurroundingRectangle(self.tcell[(1, 3)], color=GOLD, buff=0.12, stroke_width=4)
        self.show(r1, anim=Create, run_time=0.4)
        self.sfx("pop")
        self.until(b["phrases"][1]["start"] + self.phrase_len(b, 1) * 0.5)
        r2 = SurroundingRectangle(self.tcell[(2, 3)], color=KILL, buff=0.12, stroke_width=4)
        self.show(r2, anim=Create, run_time=0.4)
        self.sfx("kill")
        self.go(self.tcell[(2, 3)].animate.set_color(KILL), run_time=0.3)

    def b_g_point(self, b):
        self.clear(run_time=0.4)
        head = chip("a computer 1000× faster", GOLD, 32, DARK).move_to(STAGE + UP * 2.1)
        self.show(head, anim=GrowFromCenter, run_time=0.5)
        self.sfx("pop")
        self.at(b, 1)
        r1 = VGroup(label("n³", 40, SAFE, "BOLD"), label("handles", 28, MUTED), label("n  →  10 n", 36, TEXT, "BOLD"),
                    label("ten times the input", 24, SAFE)).arrange(RIGHT, buff=0.4)
        r2 = VGroup(label("2ⁿ", 40, KILL, "BOLD"), label("handles", 28, MUTED), label("n  →  n + 10", 36, TEXT, "BOLD"),
                    label("only ten more items", 24, KILL)).arrange(RIGHT, buff=0.4)
        rows = VGroup(r1, r2).arrange(DOWN, buff=0.6, aligned_edge=LEFT).move_to(STAGE + DOWN * 0.3)
        self.stage.add(rows)
        self.go(FadeIn(r1, shift=RIGHT * 0.3), run_time=0.5)
        self.until(b["phrases"][1]["start"] + self.phrase_len(b, 1) * 0.5)
        self.go(FadeIn(r2, shift=RIGHT * 0.3), run_time=0.5)
        self.sfx("kill")
        why = label("1000 = 10³  and  1000 ≈ 2¹⁰", 22, MUTED).move_to(STAGE + DOWN * 2.3)
        self.show(why, run_time=0.4)

    # ------------------------------------------------------------ tractable vs intractable
    def b_t_def(self, b):
        self.clear(run_time=0.4)
        l = titled_card("TRACTABLE", SAFE, ["a polynomial-time algorithm exists"], 6.0, 1.5)
        r = titled_card("INTRACTABLE", KILL, ["no polynomial-time algorithm is known"], 6.3, 1.5)
        l.move_to(STAGE + LEFT * 3.3 + UP * 2.0)
        r.move_to(STAGE + RIGHT * 3.3 + UP * 2.0)
        self.show(l, run_time=0.6)
        self.at(b, 1)
        self.show(r, run_time=0.6)
        self.t_left, self.t_right = l, r

    def b_t_examples(self, b):
        ex = VGroup(*[chip(t, SAFE, 26) for t in ["Sorting", "Searching", "Shortest paths", "Minimum spanning tree"]])
        ex.arrange(DOWN, buff=0.22).next_to(self.t_left, DOWN, buff=0.4)
        self.stage.add(ex)
        self.go(LaggedStart(*[FadeIn(e, shift=UP * 0.2) for e in ex], lag_ratio=0.35), run_time=1.5)
        self.sfx("pop")
        self.at(b, 1)
        hard = VGroup(*[chip(t, KILL, 26) for t in ["Travelling salesperson", "Hamiltonian cycle", "Graph coloring",
                                                     "0/1 Knapsack"]])
        hard.arrange(DOWN, buff=0.22).next_to(self.t_right, DOWN, buff=0.4)
        self.stage.add(hard)
        self.go(LaggedStart(*[FadeIn(e, shift=UP * 0.2) for e in hard], lag_ratio=0.35), run_time=1.8)
        self.sfx("kill")
        self.t_hard = hard

    def b_t_unit3(self, b):
        tag = chip("UNIT III", UNIT_COLORS["III"], 22).next_to(self.t_right, UP, buff=0.12).align_to(self.t_right, LEFT)
        self.show(tag, anim=GrowFromCenter, run_time=0.4)
        self.sfx("pop")
        self.at(b, 1)
        note = VGroup(label("backtracking / branch & bound:", 22, MUTED), label("worst case still exponential", 24, KILL, "BOLD")
                      ).arrange(DOWN, buff=0.08).next_to(self.t_hard, DOWN, buff=0.35)
        self.show(note, run_time=0.5)

    def b_t_open(self, b):
        self.clear(run_time=0.4)
        q = VGroup(label("P", 110, SAFE, "BOLD"), label("=?", 70, GOLD, "BOLD"), label("NP", 110, PURPLE, "BOLD")
                   ).arrange(RIGHT, buff=0.5).move_to(STAGE + UP * 0.6)
        self.show(q, anim=GrowFromCenter, run_time=0.7)
        self.sfx("whoosh")
        lines = VGroup(label("no proof that a polynomial algorithm is impossible", 24, MUTED),
                       label("no polynomial algorithm found either", 24, MUTED)).arrange(DOWN, buff=0.1)
        lines.move_to(STAGE + DOWN * 1.3)
        self.show(lines, run_time=0.5)
        self.at(b, 1)
        nxt = chip("the open question  →  next video", ACCENT, 26).move_to(STAGE + DOWN * 2.4)
        self.show(nxt, anim=GrowFromCenter, run_time=0.5)
        self.sfx("pop")

    # ------------------------------------------------------------ deterministic vs non-deterministic
    def b_d_det(self, b):
        self.clear(run_time=0.4)
        head = chip("DETERMINISTIC", ACCENT, 30).move_to(STAGE + UP * 2.3)
        self.show(head, anim=GrowFromCenter, run_time=0.5)
        steps = VGroup(*[VGroup(Circle(0.42, color=ACCENT, fill_color=PANEL, fill_opacity=1, stroke_width=3),
                                label(f"step {i + 1}", 18, TEXT)) for i in range(5)]).arrange(RIGHT, buff=1.0)
        steps.move_to(STAGE + UP * 0.6)
        arrows = VGroup(*[Arrow(steps[i].get_right(), steps[i + 1].get_left(), buff=0.05, color=MUTED, stroke_width=4,
                                max_tip_length_to_length_ratio=0.3) for i in range(4)])
        self.stage.add(steps, arrows)
        self.go(LaggedStart(*[AnimationGroup(FadeIn(steps[i]), *( [GrowArrow(arrows[i - 1])] if i else []))
                              for i in range(5)], lag_ratio=0.4), run_time=1.6)
        one = label("one outcome per step", 26, TEXT, "BOLD").move_to(STAGE + DOWN * 0.7)
        self.show(one, run_time=0.4)
        self.at(b, 1)
        same = chip("same input  →  same path, every time", PANEL_EDGE, 24).move_to(STAGE + DOWN * 1.6)
        self.show(same, run_time=0.5)

    def b_n_idea(self, b):
        self.clear(run_time=0.4)
        head = chip("NON-DETERMINISTIC", GOLD, 30, DARK).move_to(STAGE + UP * 2.3)
        self.show(head, anim=GrowFromCenter, run_time=0.5)
        self.sfx("pop")
        start = VGroup(Circle(0.42, color=ACCENT, fill_color=PANEL, fill_opacity=1, stroke_width=3), label("start", 18, TEXT)
                       ).move_to(STAGE + LEFT * 4.6 + UP * 0.2)
        ch = VGroup(RoundedRectangle(width=1.9, height=0.8, corner_radius=0.2, color=GOLD, fill_color=PANEL, fill_opacity=1,
                                     stroke_width=3), label("Choice(S)", 22, GOLD, "BOLD")).move_to(STAGE + LEFT * 1.9 + UP * 0.2)
        outs = VGroup(*[VGroup(Circle(0.36, color=MUTED, fill_color=PANEL, fill_opacity=1, stroke_width=3),
                               label(t, 20, TEXT)).move_to(STAGE + RIGHT * 1.2 + UP * (0.2 + dy))
                        for t, dy in zip(["a", "b", "c"], [1.4, 0.0, -1.4])])
        ends = VGroup(chip("Failure", KILL, 22).move_to(STAGE + RIGHT * 4.3 + UP * 1.6),
                      chip("Success", SAFE, 22).move_to(STAGE + RIGHT * 4.3 + UP * 0.2),
                      chip("Failure", KILL, 22).move_to(STAGE + RIGHT * 4.3 + DOWN * 1.2))
        a0 = Arrow(start.get_right(), ch.get_left(), buff=0.05, color=MUTED, stroke_width=4, max_tip_length_to_length_ratio=0.3)
        a1 = VGroup(*[Arrow(ch.get_right(), o.get_left(), buff=0.05, color=MUTED, stroke_width=4,
                            max_tip_length_to_length_ratio=0.3) for o in outs])
        a2 = VGroup(*[Arrow(o.get_right(), e.get_left(), buff=0.05, color=MUTED, stroke_width=4,
                            max_tip_length_to_length_ratio=0.3) for o, e in zip(outs, ends)])
        self.stage.add(start, ch, outs, ends, a0, a1, a2)
        self.go(FadeIn(start), GrowArrow(a0), FadeIn(ch), run_time=0.6)
        self.go(LaggedStart(*[AnimationGroup(GrowArrow(a1[i]), FadeIn(outs[i])) for i in range(3)], lag_ratio=0.3), run_time=0.9)
        self.go(LaggedStart(*[AnimationGroup(GrowArrow(a2[i]), FadeIn(ends[i])) for i in range(3)], lag_ratio=0.3), run_time=0.9)
        self.at(b, 1)
        lucky = VGroup(a0.copy().set_color(GOLD), a1[1].copy().set_color(GOLD), a2[1].copy().set_color(GOLD))
        self.stage.add(lucky)
        self.go(Create(lucky), outs[1][0].animate.set_stroke(GOLD, 5), run_time=0.8)
        self.sfx("chime")
        note = label("if any pick can lead to Success, that pick is made", 24, GOLD).move_to(STAGE + DOWN * 2.4)
        self.show(note, run_time=0.5)

    def b_n_funcs(self, b):
        self.clear(run_time=0.4)
        cards = VGroup(titled_card("Choice(S)", GOLD, ["picks an element", "of the set S"], 3.9, 2.0),
                       titled_card("Failure()", KILL, ["signals an", "unsuccessful completion"], 3.9, 2.0),
                       titled_card("Success()", SAFE, ["signals a", "successful completion"], 3.9, 2.0)
                       ).arrange(RIGHT, buff=0.4).move_to(STAGE + UP * 0.6)
        self.stage.add(cards)
        for i, c in enumerate(cards):
            self.at(b, 0) if i == 0 else None
            self.go(FadeIn(c, shift=UP * 0.2), run_time=0.5)
            self.sfx("pop")
            if i < 2:
                self.until(b["phrases"][0]["start"] + self.phrase_len(b, 0) * (i + 1) / 3)
        self.at(b, 1)
        t = chip("each takes O(1) time", ACCENT, 28).move_to(STAGE + DOWN * 1.4)
        self.show(t, anim=GrowFromCenter, run_time=0.5)

    def b_n_rule(self, b):
        self.clear(run_time=0.4)
        head = label("THE RULE", 34, GOLD, "BOLD").move_to(STAGE + UP * 2.2)
        self.show(head, anim=GrowFromCenter, run_time=0.4)
        r1 = VGroup(label("If some sequence of choices leads to Success,", 30, TEXT),
                    label("the algorithm makes exactly those choices.", 30, TEXT, "BOLD")).arrange(DOWN, buff=0.12)
        box1 = card(r1.width + 0.8, r1.height + 0.6, edge=SAFE)
        c1 = VGroup(box1, r1.move_to(box1)).move_to(STAGE + UP * 0.7)
        self.show(c1, run_time=0.6, shift=UP * 0.2)
        self.at(b, 1)
        r2 = VGroup(label("It fails only when", 28, TEXT), label("no sequence of choices can succeed.", 28, KILL, "BOLD")
                    ).arrange(DOWN, buff=0.1)
        box2 = card(r2.width + 0.8, r2.height + 0.55, edge=KILL)
        c2 = VGroup(box2, r2.move_to(box2)).move_to(STAGE + DOWN * 1.3)
        self.show(c2, run_time=0.6, shift=UP * 0.2)
        self.sfx("pop")

    def code_panel(self, lines, pos, max_h=5.6):
        code = CodePanel(lines, font_size=21)
        code.scale_to_fit_height(min(code.height, max_h)).move_to(pos)
        return code

    def b_n_search(self, b):
        self.clear(run_time=0.4)
        self.code = self.code_panel(NSEARCH, STAGE + LEFT * 3.0 + DOWN * 0.1)
        self.show(self.code, run_time=0.6)
        self.go(self.code.highlight(0))
        A = cell_row([7, 3, 9, 4, 6, 2], STAGE + RIGHT * 1.9 + UP * 1.0, name="A")
        x = VGroup(label("x =", 26, MUTED, "BOLD"), label("4", 26, TEXT)).arrange(RIGHT, buff=0.2).next_to(A, DOWN, buff=0.7)
        self.show(A, x, run_time=0.5)
        self.go(self.code.highlight(2))
        j = VGroup(Arrow(ORIGIN, DOWN * 0.7, color=GOLD, stroke_width=5, max_tip_length_to_length_ratio=0.35),
                   label("j", 24, GOLD, "BOLD")).arrange(UP, buff=0.05).next_to(A.cells[3], UP, buff=0.1)
        self.show(j, run_time=0.4)
        self.sfx("pop")
        self.at(b, 1)
        self.go(self.code.highlight(3), A.cells[3][0].animate.set_fill(GOLD).set_stroke(GOLD), A.cells[3][1].animate.set_color(DARK))
        self.go(self.code.highlight(5))
        ok = chip("Success: j = 4", SAFE, 24).next_to(x, DOWN, buff=0.45)
        self.show(ok, anim=GrowFromCenter, run_time=0.4)
        self.sfx("chime")
        self.until(b["phrases"][1]["start"] + self.phrase_len(b, 1) * 0.75)
        self.go(self.code.highlight(7, KILL))
        self.n_anchor = ok

    def b_n_search2(self, b):
        d = chip("deterministic:  O(n)", ACCENT, 26).move_to(STAGE + RIGHT * 2.3 + DOWN * 1.9)
        self.show(d, run_time=0.5)
        self.at(b, 1)
        nd = chip("non-deterministic:  O(1)", GOLD, 26, DARK).next_to(d, DOWN, buff=0.25)
        self.show(nd, anim=GrowFromCenter, run_time=0.5)
        self.sfx("chime")
        sub = label("one guess + one comparison", 20, MUTED).next_to(nd, DOWN, buff=0.15)
        self.show(sub, run_time=0.4)

    def b_n_sort(self, b):
        self.clear(run_time=0.4)
        self.code = self.code_panel(NSORT, STAGE + LEFT * 3.5 + DOWN * 0.1)
        self.show(self.code, run_time=0.6)
        self.go(self.code.highlight(0))
        A = cell_row([5, 2, 8, 1], STAGE + RIGHT * 2.8 + UP * 1.6, name="A")
        B = cell_row(["", "", "", ""], STAGE + RIGHT * 2.8 + UP * 0.1, name="B")
        self.show(A, B, run_time=0.5)
        self.go(self.code.highlight(6))
        span = self.phrase_len(b, 0)
        t0 = b["phrases"][0]["start"]
        for k, (i, j) in enumerate([(0, 2), (1, 1), (2, 3), (3, 0)]):     # A[i] goes to its sorted slot j
            self.until(t0 + span * (0.45 + 0.13 * k))
            tag = label(f"j = {j + 1}", 18, GOLD, "BOLD").next_to(B.cells[j], UP, buff=0.08)
            self.stage.add(tag)
            self.go(self.code.highlight(8), TransformFromCopy(A.cells[i][1], B.cells[j][1].become(
                label(str(A.cells[i][1].text), 24, TEXT).move_to(B.cells[j]))), FadeIn(tag), run_time=0.45)
            self.sfx("place", -0.3)
            self.pending.append(FadeOut(tag))
        self.at(b, 1)
        self.go(self.code.highlight(11))
        chk = SurroundingRectangle(B.cells, color=SAFE, buff=0.08, stroke_width=4)
        self.show(chk, anim=Create, run_time=0.5)
        self.until(b["phrases"][1]["start"] + self.phrase_len(b, 1) * 0.6)
        self.go(self.code.highlight(12))
        ok = chip("B = 1 2 5 8 : Success", SAFE, 24).next_to(B, DOWN, buff=0.6)
        self.show(ok, anim=GrowFromCenter, run_time=0.4)
        self.sfx("chime")

    def b_n_sort2(self, b):
        d = chip("deterministic:  O(n log n)", ACCENT, 24).move_to(STAGE + RIGHT * 3.4 + DOWN * 2.0)
        nd = chip("non-deterministic:  O(n)", GOLD, 24, DARK).next_to(d, DOWN, buff=0.25)
        self.show(nd, anim=GrowFromCenter, run_time=0.5)
        self.sfx("chime")
        self.at(b, 1)
        self.show(d, run_time=0.5)

    def b_n_interp(self, b):
        self.clear(run_time=0.4)
        root = Dot(color=GOLD, radius=0.1)
        leaves = VGroup(*[Dot(color=ACCENT, radius=0.08).move_to(RIGHT * 1.3 + UP * (0.9 - 0.45 * i)) for i in range(5)])
        fan = VGroup(root, leaves, *[Line(root.get_center(), l.get_center(), color=MUTED, stroke_width=2) for l in leaves])
        par = VGroup(label("UNLIMITED PARALLELISM", 24, ACCENT, "BOLD"), fan,
                     label("every choice tried at the same time", 20, MUTED)).arrange(DOWN, buff=0.25)
        box1 = card(5.6, 3.3)
        c1 = VGroup(box1, par.move_to(box1))
        guess = VGroup(Circle(0.55, color=GOLD, stroke_width=4), label("?", 40, GOLD, "BOLD"))
        luck = VGroup(label("LUCKY GUESSER", 24, GOLD, "BOLD"), guess,
                      label("the guess is then verified", 20, MUTED)).arrange(DOWN, buff=0.25)
        box2 = card(5.6, 3.3)
        c2 = VGroup(box2, luck.move_to(box2))
        cards = VGroup(c1, c2).arrange(RIGHT, buff=0.5).move_to(STAGE + UP * 0.6)
        self.show(c1, run_time=0.6)
        self.at(b, 1)
        self.show(c2, run_time=0.6)
        self.until(b["phrases"][1]["start"] + self.phrase_len(b, 1) * 0.55)
        fl = flow([chip("guess", GOLD, 28, DARK), chip("verify", SAFE, 28), chip("polynomial time", ACCENT, 28)])
        fl.move_to(STAGE + DOWN * 2.1)
        self.stage.add(fl)
        self.go(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in fl[0]], lag_ratio=0.4), FadeIn(fl[1]), run_time=1.2)
        self.sfx("pop")

    def b_n_knap(self, b):
        self.clear(run_time=0.4)
        q = VGroup(label("0/1 Knapsack, as a yes / no question:", 24, MUTED),
                   label("items with weight ≤ m and profit ≥ r ?", 28, TEXT, "BOLD")).arrange(DOWN, buff=0.12)
        qbox = card(q.width + 0.7, q.height + 0.5, edge=GOLD)
        qc = VGroup(qbox, q.move_to(qbox)).move_to(STAGE + RIGHT * 2.4 + UP * 1.7)
        self.show(qc, run_time=0.6, shift=UP * 0.2)
        self.code = self.code_panel(DKP, STAGE + LEFT * 3.3 + DOWN * 0.3)
        self.show(self.code, run_time=0.6)
        self.go(self.code.highlight(0))
        self.at(b, 1)
        self.go(self.code.highlight(5))
        xs = VGroup(*[VGroup(label(f"x{i + 1}", 20, MUTED), chip(v, GOLD, 24, DARK)).arrange(DOWN, buff=0.1)
                      for i, v in enumerate(["1", "1", "0", "1"])]).arrange(RIGHT, buff=0.4).move_to(STAGE + RIGHT * 2.4 + UP * 0.2)
        self.stage.add(xs)
        self.go(LaggedStart(*[FadeIn(x, shift=UP * 0.2) for x in xs], lag_ratio=0.3), run_time=1.0)
        self.sfx("pop")
        self.go(self.code.highlight(6))
        self.go(self.code.highlight(7))
        self.until(b["phrases"][1]["start"] + self.phrase_len(b, 1) * 0.65)
        self.go(self.code.highlight(9))
        chk = chip("add up, compare: O(n)", SAFE, 26).move_to(STAGE + RIGHT * 2.4 + DOWN * 1.2)
        self.show(chk, anim=GrowFromCenter, run_time=0.5)
        self.sfx("chime")
        self.go(self.code.highlight(10, SAFE))

    def b_n_point(self, b):
        self.clear(run_time=0.4)
        c1 = titled_card("FINDING the answer", KILL, ["try the choices:", "exponential (2ⁿ, n!)"], 5.6, 2.3)
        c2 = titled_card("CHECKING an answer", SAFE, ["add up, compare, verify:", "polynomial"], 5.6, 2.3)
        VGroup(c1, c2).arrange(RIGHT, buff=0.5).move_to(STAGE + UP * 0.6)
        self.show(c1, run_time=0.6)
        self.at(b, 1)
        self.show(c2, run_time=0.6)
        self.sfx("chime")
        note = label("the pattern behind every hard problem of Unit III", 26, GOLD).move_to(STAGE + DOWN * 1.6)
        self.show(note, run_time=0.5)

    def b_n_class(self, b):
        self.clear(run_time=0.4)
        big = label("NP", 120, PURPLE, "BOLD").move_to(STAGE + UP * 1.4)
        self.show(big, anim=GrowFromCenter, run_time=0.7)
        self.sfx("whoosh")
        full = label("Non-deterministic Polynomial time", 32, TEXT, "BOLD").next_to(big, DOWN, buff=0.2)
        self.show(full, run_time=0.5)
        self.at(b, 1)
        d = VGroup(label("a yes / no problem is in NP when", 26, MUTED),
                   label("a non-deterministic algorithm solves it in polynomial time", 26, TEXT, "BOLD")).arrange(DOWN, buff=0.1)
        dbox = card(d.width + 0.8, d.height + 0.5, edge=PURPLE)
        dc = VGroup(dbox, d.move_to(dbox)).move_to(STAGE + DOWN * 1.1)
        self.show(dc, run_time=0.6, shift=UP * 0.2)
        fl = flow([chip("guess the answer", GOLD, 24, DARK), chip("verify it fast", SAFE, 24)]).move_to(STAGE + DOWN * 2.5)
        self.show(fl, run_time=0.5)
        self.sfx("pop")

    # ------------------------------------------------------------ practice, tips, recap
    def b_p_intro(self, b):
        self.question_card(b, ["Write a non-deterministic algorithm:", "does G (n vertices) have a Hamiltonian cycle?",
                               "in polynomial time"])

    def b_p_pause(self, b):
        self.pause_screen(b, "Pause and write it down")

    def b_p_answer(self, b):
        self.pause_over()
        self.clear(run_time=0.4)
        self.code = CodePanel(NHAM, font_size=21)
        self.code.scale_to_fit_width(min(self.code.width, 9.6)).move_to(STAGE + UP * 0.95)
        self.show(self.code, run_time=0.6)
        self.go(self.code.highlight(2))
        g = chip("GUESS: n choices", GOLD, 24, DARK)
        v = chip("VERIFY: polynomial", SAFE, 24)
        row = VGroup(g, v).arrange(RIGHT, buff=0.5).move_to(STAGE + DOWN * 1.65)
        self.show(g, anim=GrowFromCenter, run_time=0.4)
        self.sfx("pop")
        self.at(b, 1)
        self.go(self.code.highlight(3))
        self.show(v, anim=GrowFromCenter, run_time=0.4)
        self.go(self.code.highlight(5))
        self.go(self.code.highlight(6))
        self.until(b["phrases"][1]["start"] + self.phrase_len(b, 1) * 0.7)
        self.go(self.code.highlight(7, SAFE))
        res = chip("Hamiltonian cycle  ∈  NP", PURPLE, 30).move_to(STAGE + DOWN * 2.55)
        self.show(res, anim=GrowFromCenter, run_time=0.5)
        self.sfx("chime")

    def b_tip1(self, b):
        self.tip(b, 1, "Define polynomial time: O(nᵏ)", "and give the growth table: n³ against 2ⁿ")

    def b_tip2(self, b):
        self.tip(b, 2, "Name Choice, Failure, Success + the rule", "it fails only when no sequence of choices succeeds")

    def b_tip3(self, b):
        self.tip(b, 3, "Example: NSearch O(1) or NSort O(n)", "write the algorithm and state its time")

    def b_recap(self, b):
        self.recap(b, ["Polynomial time: tractable.  Exponential: not",
                       "Unit III's hard problems: no known polynomial algorithm",
                       "Non-deterministic: guess with Choice, verify in polynomial time"])
