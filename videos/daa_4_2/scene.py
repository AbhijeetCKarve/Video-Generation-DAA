"""Video 4.2 - P, NP, NP-Hard & NP-Complete. Rendered by build.py (needs SCHEDULE / ENVELOPE env vars)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from lesson import *  # noqa: E402,F401,F403

PURPLE = UNIT_COLORS["IV"]
DARK = "#0F172A"


def titled_card(title, color, lines, w, h, title_size=30, line_size=24, line_color=TEXT):
    body = VGroup(label(title, title_size, color, "BOLD"), *[label(t, line_size, line_color) for t in lines]
                  ).arrange(DOWN, buff=0.18)
    box = card(w, h, edge=color)
    return VGroup(box, body.move_to(box))


def flow(chips, buff=0.5):
    row = VGroup(*chips).arrange(RIGHT, buff=buff)
    arrows = VGroup(*[Arrow(row[i].get_right(), row[i + 1].get_left(), buff=0.08, color=MUTED, stroke_width=4,
                            max_tip_length_to_length_ratio=0.35) for i in range(len(chips) - 1)])
    return VGroup(row, arrows)


def small_graph(center, r=1.1):
    """Five vertices on a circle, all edges faint, for the hook."""
    pts = [center + np.array([r * np.sin(2 * np.pi * k / 5), r * np.cos(2 * np.pi * k / 5), 0]) for k in range(5)]
    edges = VGroup(*[Line(pts[a], pts[b], color=PANEL_EDGE, stroke_width=2) for a in range(5) for b in range(a + 1, 5)])
    dots = VGroup(*[VGroup(Circle(0.22, color=TEXT, fill_color=PANEL, fill_opacity=1, stroke_width=3).move_to(q),
                           label(str(k + 1), 18, TEXT, "BOLD").move_to(q)) for k, q in enumerate(pts)])
    g = VGroup(edges, dots)
    g.pts = pts
    return g


class Venn(VGroup):
    """P inside NP, NP-hard overlapping NP; the overlap is NP-complete."""

    def __init__(self, center, scale=1.0, **kw):
        super().__init__(**kw)
        c = np.array([*center[:2], 0])
        self.np_ = Ellipse(width=6.6 * scale, height=4.4 * scale, color=PURPLE, stroke_width=4, fill_color=PURPLE,
                           fill_opacity=0.10).move_to(c + LEFT * 1.3 * scale)
        self.hard = Ellipse(width=6.0 * scale, height=4.0 * scale, color=KILL, stroke_width=4, fill_color=KILL,
                            fill_opacity=0.10).move_to(c + RIGHT * 2.3 * scale)
        self.p = Circle(1.15 * scale, color=SAFE, stroke_width=4, fill_color=SAFE, fill_opacity=0.15).move_to(
            c + LEFT * 3.0 * scale + DOWN * 0.1 * scale)
        self.lab_np = label("NP", int(34 * scale), PURPLE, "BOLD").move_to(c + LEFT * 2.0 * scale + UP * 1.6 * scale)
        self.lab_hard = label("NP-hard", int(34 * scale), KILL, "BOLD").move_to(c + RIGHT * 3.4 * scale + UP * 1.4 * scale)
        self.lab_p = label("P", int(34 * scale), SAFE, "BOLD").move_to(self.p.get_center() + UP * 0.45 * scale)
        self.lab_npc = label("NP-complete", int(26 * scale), GOLD, "BOLD").move_to(c + RIGHT * 0.5 * scale + UP * 0.7 * scale)
        self.ex_p = label("shortest path", int(18 * scale), SAFE).move_to(self.p.get_center() + DOWN * 0.25 * scale)
        self.ex_npc = VGroup(label("SAT", int(18 * scale), GOLD), label("Hamiltonian cycle", int(18 * scale), GOLD)
                             ).arrange(DOWN, buff=0.08).move_to(c + RIGHT * 0.5 * scale + DOWN * 0.1 * scale)
        self.ex_hard = label("halting problem", int(18 * scale), KILL).move_to(c + RIGHT * 3.6 * scale + DOWN * 0.3 * scale)
        self.add(self.np_, self.hard, self.p, self.lab_np, self.lab_hard, self.lab_p, self.lab_npc, self.ex_p,
                 self.ex_npc, self.ex_hard)


class Video(Lesson):
    NEXT = ("4.3  Polynomial-time", "reductions")

    # ------------------------------------------------------------ hook
    def b_hook_q(self, b):
        g = small_graph(STAGE + LEFT * 4.0 + UP * 0.3)
        self.show(g, run_time=0.6)
        q1 = VGroup(label("Does it have a Hamiltonian cycle?", 30, TEXT, "BOLD"), chip("yes / no", GOLD, 22, DARK)
                    ).arrange(RIGHT, buff=0.4)
        q2 = VGroup(label("What is the shortest tour?", 30, TEXT, "BOLD"), chip("the best answer", ACCENT, 22)
                    ).arrange(RIGHT, buff=0.4)
        qs = VGroup(q1, q2).arrange(DOWN, buff=0.6, aligned_edge=LEFT).move_to(STAGE + RIGHT * 1.9 + UP * 0.3)
        self.stage.add(qs)
        self.go(FadeIn(q1[0], shift=RIGHT * 0.3), run_time=0.5)
        self.go(FadeIn(q2[0], shift=RIGHT * 0.3), run_time=0.5)
        self.at(b, 1)
        self.go(GrowFromCenter(q1[1]), run_time=0.4)
        self.sfx("pop")
        self.until(b["phrases"][1]["start"] + self.phrase_len(b, 1) * 0.55)
        self.go(GrowFromCenter(q2[1]), run_time=0.4)
        self.sfx("pop")

    def b_hook_names(self, b):
        self.clear(run_time=0.4)
        names = VGroup(chip("P", SAFE, 44), chip("NP", PURPLE, 44), chip("NP-hard", KILL, 44), chip("NP-complete", GOLD, 44, DARK)
                       ).arrange(RIGHT, buff=0.5).move_to(STAGE + UP * 0.6)
        self.stage.add(names)
        self.go(LaggedStart(*[GrowFromCenter(n) for n in names], lag_ratio=0.35), run_time=1.6)
        self.sfx("pop")
        self.at(b, 1)
        sub = label("four names every DAA exam asks about", 28, MUTED).move_to(STAGE + DOWN * 0.9)
        self.show(sub, run_time=0.5)

    def b_hook_big(self, b):
        self.clear(run_time=0.4)
        q = VGroup(label("P", 110, SAFE, "BOLD"), label("=", 90, GOLD, "BOLD"), label("NP", 110, PURPLE, "BOLD"),
                   label("?", 110, GOLD, "BOLD")).arrange(RIGHT, buff=0.4).move_to(STAGE + UP * 0.7)
        self.show(q, anim=GrowFromCenter, run_time=0.7)
        self.sfx("whoosh")
        self.at(b, 1)
        prize = chip("$ 1,000,000 prize", GOLD, 36, DARK).move_to(STAGE + DOWN * 1.2)
        self.show(prize, anim=GrowFromCenter, run_time=0.5)
        self.sfx("chime")

    def b_syllabus(self, b):
        self.syllabus(b, ["Decision vs optimisation problems", "P and NP, NP-hard and NP-complete",
                          "The P vs NP question"], unit_text="UNIT IV  ·  COMPLEXITY")

    def b_exam(self, b):
        self.exam_star(b)

    # ------------------------------------------------------------ decision vs optimisation
    def b_d_opt(self, b):
        self.unsay()
        self.clear(run_time=0.4)
        c = titled_card("OPTIMISATION PROBLEM", ACCENT, ["asks for the best answer"], 6.0, 1.5)
        c.move_to(STAGE + LEFT * 3.3 + UP * 2.0)
        self.show(c, run_time=0.6)
        self.at(b, 1)
        ex = VGroup(*[chip(t, ACCENT, 24) for t in ["the shortest tour", "the maximum profit", "the fewest colours"]])
        ex.arrange(DOWN, buff=0.22).next_to(c, DOWN, buff=0.4)
        self.stage.add(ex)
        self.go(LaggedStart(*[FadeIn(e, shift=UP * 0.2) for e in ex], lag_ratio=0.4), run_time=1.3)
        self.sfx("pop")
        self.d_left, self.d_left_ex = c, ex

    def b_d_dec(self, b):
        c = titled_card("DECISION PROBLEM", GOLD, ["asks only yes or no"], 6.0, 1.5)
        c.move_to(STAGE + RIGHT * 3.3 + UP * 2.0)
        self.show(c, run_time=0.6)
        self.at(b, 1)
        ex = VGroup(*[chip(t, GOLD, 24, DARK) for t in ["a tour of length ≤ k ?", "a packing with profit ≥ r ?",
                                                        "colourable with k colours ?"]])
        ex.arrange(DOWN, buff=0.22).next_to(c, DOWN, buff=0.4)
        self.stage.add(ex)
        self.go(LaggedStart(*[FadeIn(e, shift=UP * 0.2) for e in ex], lag_ratio=0.4), run_time=1.6)
        self.sfx("pop")
        self.d_right, self.d_right_ex = c, ex

    def b_d_link(self, b):
        y = self.d_left_ex[1].get_center()[1]
        arr = Arrow(np.array([1.1, y, 0]), np.array([-1.4, y, 0]), buff=0.0, color=SAFE, stroke_width=6,
                    max_tip_length_to_length_ratio=0.2)
        lab = label("decision version in polynomial time  ⇒  optimisation version too", 24, SAFE, "BOLD").move_to(STAGE + DOWN * 1.95)
        self.show(arr, lab, run_time=0.6)
        self.sfx("pop")
        self.at(b, 1)
        how = chip("ask  'at most k ?'  for different k: a polynomial number of questions (binary search)", PANEL_EDGE, 22)
        how.move_to(STAGE + DOWN * 2.7)
        self.show(how, run_time=0.5)

    def b_d_why(self, b):
        self.clear(run_time=0.4)
        c = chip("from now on: decision problems only", GOLD, 34, DARK).move_to(STAGE + UP * 0.6)
        self.show(c, anim=GrowFromCenter, run_time=0.6)
        self.sfx("pop")
        self.at(b, 1)
        sub = label("P, NP, NP-hard, NP-complete are classes of yes / no problems", 26, MUTED).move_to(STAGE + DOWN * 0.6)
        self.show(sub, run_time=0.5)

    # ------------------------------------------------------------ P and NP
    def class_card(self, name, color, lines, pos, w=6.2, h=3.0):
        body = VGroup(label(name, 56, color, "BOLD"), *[label(t, 23, TEXT) for t in lines]).arrange(DOWN, buff=0.15)
        box = card(w, h, edge=color)
        return VGroup(box, body.move_to(box)).move_to(pos)

    def b_p_def(self, b):
        self.clear(run_time=0.4)
        self.pc = self.class_card("P", SAFE, ["decision problems solved by a", "deterministic algorithm", "in polynomial time"],
                                  STAGE + LEFT * 3.3 + UP * 1.2)
        self.show(self.pc, run_time=0.6)
        self.sfx("pop")
        self.at(b, 1)
        ex = VGroup(*[chip(t, SAFE, 22) for t in ["shortest path", "minimum spanning tree", "is n prime ?"]])
        ex.arrange(DOWN, buff=0.18).next_to(self.pc, DOWN, buff=0.3)
        self.stage.add(ex)
        self.go(LaggedStart(*[FadeIn(e, shift=UP * 0.2) for e in ex], lag_ratio=0.4), run_time=1.2)

    def b_np_def(self, b):
        self.npc = self.class_card("NP", PURPLE, ["decision problems solved by a", "non-deterministic algorithm", "in polynomial time"],
                                   STAGE + RIGHT * 3.3 + UP * 1.2)
        self.show(self.npc, run_time=0.6)
        self.sfx("pop")
        self.at(b, 1)
        fl = flow([chip("guess", GOLD, 22, DARK), chip("verify in polynomial time", SAFE, 22)]).next_to(self.npc, DOWN, buff=0.3)
        self.show(fl, run_time=0.6)
        self.np_flow = fl

    def b_np_ex(self, b):
        names = ["Hamiltonian cycle", "decision knapsack", "graph colouring", "SAT"]
        cs = [chip(t, PURPLE, 20) for t in names]
        ex = VGroup(VGroup(cs[0], cs[1]).arrange(RIGHT, buff=0.15), VGroup(cs[2], cs[3]).arrange(RIGHT, buff=0.15)
                    ).arrange(DOWN, buff=0.15).next_to(self.np_flow, DOWN, buff=0.25)
        ex.set_x(self.npc.get_x())
        self.stage.add(ex)
        self.go(LaggedStart(*[FadeIn(e, shift=UP * 0.2) for e in cs], lag_ratio=0.3), run_time=1.3)
        self.sfx("pop")
        self.at(b, 1)
        cert = VGroup(label("certificate: a cycle, a packing, a colouring, an assignment", 19, MUTED),
                      label("→  checked in polynomial time", 19, SAFE)).arrange(DOWN, buff=0.06).next_to(ex, DOWN, buff=0.2)
        cert.set_x(self.npc.get_x())
        self.show(cert, run_time=0.5)

    def b_p_in_np(self, b):
        self.clear(run_time=0.4)
        npc = Ellipse(width=6.0, height=4.2, color=PURPLE, stroke_width=4, fill_color=PURPLE, fill_opacity=0.10).move_to(STAGE + LEFT * 2.6)
        pc = Circle(1.3, color=SAFE, stroke_width=4, fill_color=SAFE, fill_opacity=0.15).move_to(STAGE + LEFT * 3.6 + DOWN * 0.2)
        ln = label("NP", 40, PURPLE, "BOLD").move_to(STAGE + LEFT * 1.4 + UP * 1.0)
        lp = label("P", 40, SAFE, "BOLD").move_to(pc.get_center())
        self.show(npc, ln, run_time=0.5)
        self.show(pc, lp, anim=GrowFromCenter, run_time=0.5)
        self.sfx("pop")
        why = VGroup(label("a deterministic algorithm", 24, TEXT), label("= a non-deterministic one", 24, TEXT),
                     label("that never uses Choice", 24, GOLD, "BOLD")).arrange(DOWN, buff=0.1).move_to(STAGE + RIGHT * 3.4 + UP * 0.9)
        self.show(why, run_time=0.5)
        self.at(b, 1)
        sub = label("P  ⊆  NP", 48, TEXT, "BOLD").move_to(STAGE + RIGHT * 3.4 + DOWN * 1.0)
        self.show(sub, anim=GrowFromCenter, run_time=0.5)
        self.sfx("chime")

    def b_pvsnp(self, b):
        self.clear(run_time=0.4)
        q = VGroup(label("NP  ⊆  P  ?", 60, TEXT, "BOLD"), label("is every NP problem also in P?", 28, MUTED)
                   ).arrange(DOWN, buff=0.2).move_to(STAGE + UP * 1.1)
        self.show(q, anim=GrowFromCenter, run_time=0.6)
        self.sfx("whoosh")
        unk = chip("nobody knows", KILL, 30).move_to(STAGE + DOWN * 0.4)
        self.show(unk, run_time=0.5)
        self.at(b, 1)
        bel = VGroup(label("most computer scientists believe  P ≠ NP", 26, TEXT), label("but there is no proof", 26, GOLD, "BOLD")
                     ).arrange(DOWN, buff=0.1).move_to(STAGE + DOWN * 1.7)
        self.show(bel, run_time=0.5)

    # ------------------------------------------------------------ SAT and reductions
    def b_sat(self, b):
        self.clear(run_time=0.4)
        head = chip("SATISFIABILITY  (SAT)", GOLD, 32, DARK).move_to(STAGE + UP * 2.2)
        self.show(head, anim=GrowFromCenter, run_time=0.5)
        self.sfx("pop")
        self.at(b, 1)
        d = VGroup(label("given a Boolean formula,", 28, TEXT),
                   label("is there a true / false assignment to its variables", 28, TEXT),
                   label("that makes the whole formula true?", 28, TEXT, "BOLD")).arrange(DOWN, buff=0.12)
        box = card(d.width + 0.8, d.height + 0.6, edge=GOLD)
        self.sat_card = VGroup(box, d.move_to(box)).move_to(STAGE + UP * 0.5)
        self.show(self.sat_card, run_time=0.6, shift=UP * 0.2)

    def b_sat_ex(self, b):
        self.go(self.sat_card.animate.scale(0.75).move_to(STAGE + UP * 1.9), run_time=0.4)
        f = VGroup(label("( x₁  ∨  x₂ )", 36, TEXT, "BOLD"), label("∧", 36, MUTED), label("( ¬x₁  ∨  x₃ )", 36, TEXT, "BOLD")
                   ).arrange(RIGHT, buff=0.3).move_to(STAGE + UP * 0.3)
        self.show(f, run_time=0.5)
        asg = VGroup(chip("x₁ = true", SAFE, 24), chip("x₃ = true", SAFE, 24), label("→", 30, MUTED), chip("formula = true", GOLD, 24, DARK)
                     ).arrange(RIGHT, buff=0.3).move_to(STAGE + DOWN * 0.7)
        self.stage.add(asg)
        self.go(LaggedStart(*[FadeIn(a, shift=UP * 0.2) for a in asg], lag_ratio=0.3), run_time=1.2)
        self.sfx("chime")
        self.at(b, 1)
        n = VGroup(label("n variables  →  2ⁿ assignments", 24, KILL), label("checking one: easy", 24, SAFE), label("⇒  SAT ∈ NP", 28, PURPLE, "BOLD")
                   ).arrange(RIGHT, buff=0.5).move_to(STAGE + DOWN * 2.0)
        self.stage.add(n)
        self.go(LaggedStart(*[FadeIn(x, shift=UP * 0.2) for x in n], lag_ratio=0.4), run_time=1.2)
        self.sfx("pop")

    def b_reduce(self, b):
        self.clear(run_time=0.4)
        head = VGroup(label("REDUCIBILITY", 34, GOLD, "BOLD"), label("L₁ ∝ L₂   (L₁ reduces to L₂)", 28, TEXT)).arrange(DOWN, buff=0.1)
        head.move_to(STAGE + UP * 2.2)
        self.show(head, anim=FadeIn, run_time=0.5)
        self.at(b, 1)
        i1 = titled_card("instance of L₁", ACCENT, ["any input"], 3.6, 1.5, 24, 20)
        tr = titled_card("polynomial-time", GOLD, ["deterministic transform"], 3.8, 1.5, 24, 20)
        i2 = titled_card("instance of L₂", PURPLE, ["same yes / no answer"], 3.6, 1.5, 24, 20)
        row = VGroup(i1, tr, i2).arrange(RIGHT, buff=0.7).move_to(STAGE + DOWN * 0.2)
        arrows = VGroup(*[Arrow(row[i].get_right(), row[i + 1].get_left(), buff=0.08, color=MUTED, stroke_width=5,
                                max_tip_length_to_length_ratio=0.3) for i in range(2)])
        self.stage.add(row, arrows)
        self.go(LaggedStart(FadeIn(i1), GrowArrow(arrows[0]), FadeIn(tr), GrowArrow(arrows[1]), FadeIn(i2), lag_ratio=0.3), run_time=1.8)
        self.sfx("pop")
        self.red_row = row

    def b_reduce_mean(self, b):
        c1 = chip("L₂ in polynomial time  ⇒  L₁ in polynomial time", SAFE, 24).move_to(STAGE + DOWN * 1.6)
        self.show(c1, run_time=0.5)
        c2 = chip("L₂ is at least as hard as L₁", KILL, 24).next_to(c1, DOWN, buff=0.25)
        self.show(c2, run_time=0.5)
        self.at(b, 1)
        nxt = label("reductions in full: video 4.3", 22, MUTED).next_to(c2, DOWN, buff=0.25)
        self.show(nxt, run_time=0.4)

    # ------------------------------------------------------------ NP-hard and NP-complete
    def b_nph_def(self, b):
        self.clear(run_time=0.4)
        self.hc = self.class_card("NP-hard", KILL, ["L is NP-hard if", "SAT  ∝  L"], STAGE + LEFT * 3.3 + UP * 1.1)
        self.show(self.hc, run_time=0.6)
        self.sfx("pop")
        self.at(b, 1)
        eq = VGroup(label("equivalently: every problem in NP reduces to L", 22, MUTED),
                    label("at least as hard as everything in NP", 24, KILL, "BOLD")).arrange(DOWN, buff=0.1)
        eq.next_to(self.hc, DOWN, buff=0.35)
        self.show(eq, run_time=0.5)

    def b_npc_def(self, b):
        self.cc = self.class_card("NP-complete", GOLD, ["L is NP-complete if", "NP-hard  and  in NP"], STAGE + RIGHT * 3.3 + UP * 1.1)
        self.show(self.cc, run_time=0.6)
        self.sfx("pop")
        self.at(b, 1)
        eq = label("the hardest problems inside NP", 24, GOLD, "BOLD").next_to(self.cc, DOWN, buff=0.35)
        self.show(eq, run_time=0.5)

    def b_cook(self, b):
        self.clear(run_time=0.4)
        head = chip("COOK'S THEOREM  (1971)", GOLD, 32, DARK).move_to(STAGE + UP * 2.2)
        self.show(head, anim=GrowFromCenter, run_time=0.5)
        self.sfx("pop")
        st = VGroup(label("SAT  ∈  P", 48, SAFE, "BOLD"), label("⟺", 44, MUTED), label("P  =  NP", 48, PURPLE, "BOLD")
                    ).arrange(RIGHT, buff=0.5).move_to(STAGE + UP * 0.5)
        self.show(st, anim=GrowFromCenter, run_time=0.6)
        self.sfx("whoosh")
        self.at(b, 1)
        first = chip("SAT: the first NP-complete problem", KILL, 26).move_to(STAGE + DOWN * 1.0)
        self.show(first, run_time=0.5)
        rest = label("every other one is proved by a reduction from SAT", 24, MUTED).move_to(STAGE + DOWN * 1.9)
        self.show(rest, run_time=0.5)

    def b_examples(self, b):
        self.clear(run_time=0.4)
        head = label("NP-COMPLETE PROBLEMS", 34, GOLD, "BOLD").move_to(STAGE + UP * 2.2)
        self.show(head, anim=GrowFromCenter, run_time=0.4)
        names = ["SAT", "3-SAT", "Hamiltonian cycle", "vertex cover", "clique", "graph colouring", "decision knapsack"]
        chips_ = VGroup(*[chip(t, GOLD, 26, DARK) for t in names])
        rows = VGroup(VGroup(*chips_[:4]).arrange(RIGHT, buff=0.35), VGroup(*chips_[4:]).arrange(RIGHT, buff=0.35)
                      ).arrange(DOWN, buff=0.4).move_to(STAGE + UP * 0.4)
        self.stage.add(rows)
        self.go(LaggedStart(*[GrowFromCenter(c) for c in chips_], lag_ratio=0.25), run_time=2.0)
        self.sfx("pop")
        self.at(b, 1)
        nxt = chip("proofs: video 4.4", ACCENT, 24).move_to(STAGE + DOWN * 1.5)
        self.show(nxt, run_time=0.5)

    def b_nph_only(self, b):
        self.clear(run_time=0.4)
        head = label("NP-HARD BUT NOT NP-COMPLETE", 34, KILL, "BOLD").move_to(STAGE + UP * 2.2)
        self.show(head, anim=GrowFromCenter, run_time=0.4)
        why = label("not in NP at all", 26, MUTED).next_to(head, DOWN, buff=0.2)
        self.show(why, run_time=0.4)
        self.at(b, 1)
        c1 = titled_card("Halting problem", KILL, ["no algorithm decides it", "yet SAT reduces to it"], 5.6, 2.0)
        c2 = titled_card("Optimisation versions", KILL, ["e.g. the shortest tour (TSP)", "NP-hard, not a decision problem"], 5.6, 2.0)
        VGroup(c1, c2).arrange(RIGHT, buff=0.5).move_to(STAGE + DOWN * 0.5)
        self.show(c1, run_time=0.6)
        self.until(b["phrases"][1]["start"] + self.phrase_len(b, 1) * 0.6)
        self.show(c2, run_time=0.6)
        self.sfx("pop")

    # ------------------------------------------------------------ the picture
    def b_venn(self, b):
        self.clear(run_time=0.4)
        v = Venn(STAGE + DOWN * 0.3)
        self.venn = v
        self.stage.add(v)
        self.go(FadeIn(v.np_), FadeIn(v.lab_np), run_time=0.5)
        self.go(GrowFromCenter(v.p), FadeIn(v.lab_p), FadeIn(v.ex_p), run_time=0.5)
        self.sfx("pop")
        self.until(b["phrases"][0]["start"] + self.phrase_len(b, 0) * 0.7)
        self.go(FadeIn(v.hard), FadeIn(v.lab_hard), run_time=0.6)
        self.sfx("pop")
        self.at(b, 1)
        self.go(FadeIn(v.lab_npc), FadeIn(v.ex_npc), run_time=0.5)
        self.sfx("chime")
        self.until(b["phrases"][1]["start"] + self.phrase_len(b, 1) * 0.55)
        self.go(FadeIn(v.ex_hard), run_time=0.5)

    def b_collapse(self, b):
        v = self.venn
        note = chip("one polynomial algorithm for one NP-complete problem …", GOLD, 24, DARK).move_to(STAGE + UP * 2.6)
        self.show(note, run_time=0.5)
        self.at(b, 1)
        target = v.p.copy().set_stroke(PURPLE).set_fill(PURPLE, 0.15)
        merged = label("P = NP", 34, PURPLE, "BOLD").move_to(v.p.get_center() + UP * 0.45)
        self.go(Transform(v.np_, target), Transform(v.lab_np, merged), FadeOut(v.lab_p), FadeOut(v.lab_npc),
                v.ex_npc.animate.move_to(v.p.get_center() + DOWN * 0.3), FadeOut(v.ex_p), run_time=1.2)
        self.sfx("whoosh")
        res = chip("… and the whole picture collapses: P = NP", KILL, 26).move_to(STAGE + DOWN * 2.8)
        self.show(res, anim=GrowFromCenter, run_time=0.5)
        self.sfx("kill")

    def b_prize(self, b):
        self.clear(run_time=0.4)
        head = label("A MILLENNIUM PRIZE PROBLEM", 34, GOLD, "BOLD").move_to(STAGE + UP * 1.5)
        self.show(head, anim=GrowFromCenter, run_time=0.5)
        self.at(b, 1)
        prize = chip("$ 1,000,000", GOLD, 56, DARK).move_to(STAGE + UP * 0.1)
        self.show(prize, anim=GrowFromCenter, run_time=0.6)
        self.sfx("chime")
        who = VGroup(label("Clay Mathematics Institute", 28, TEXT), label("unclaimed since 2000", 26, MUTED)).arrange(DOWN, buff=0.1)
        who.move_to(STAGE + DOWN * 1.4)
        self.show(who, run_time=0.5)

    # ------------------------------------------------------------ practice, tips, recap
    def b_p_intro(self, b):
        self.question_card(b, ["Which are in NP?  Which are also in P?", "path of length ≤ k ?   ·   Hamiltonian cycle ?",
                               "is this array sorted ?"])

    def b_p_pause(self, b):
        self.pause_screen(b, "Pause and decide")

    def b_p_answer(self, b):
        self.pause_over()
        self.clear(run_time=0.4)
        rows = [("path of length ≤ k ?", "NP ✓", "P ✓  (Dijkstra)", SAFE),
                ("is this array sorted ?", "NP ✓", "P ✓  (one linear scan)", SAFE),
                ("Hamiltonian cycle ?", "NP ✓", "P ?   (NP-complete)", KILL)]
        g = VGroup()
        for t, a, c, col in rows:
            r = VGroup(label(t, 28, TEXT, "BOLD"), chip(a, PURPLE, 24), chip(c, col, 24))
            g.add(r)
        for r in g:
            r[0].set_x(STAGE[0] - 6.2, LEFT)
            r[1].set_x(STAGE[0] - 0.6)
            r[2].set_x(STAGE[0] + 0.9, LEFT)
        ys = [1.5, 0.4, -0.7]
        for r, y in zip(g, ys):
            r.set_y(STAGE[1] + y)
        self.stage.add(g)
        for r in g:
            self.go(FadeIn(r[0], shift=RIGHT * 0.2), run_time=0.4)
        self.go(LaggedStart(*[GrowFromCenter(r[1]) for r in g], lag_ratio=0.3), run_time=0.9)
        self.sfx("pop")
        self.go(GrowFromCenter(g[0][2]), GrowFromCenter(g[1][2]), run_time=0.5)
        self.sfx("chime")
        self.at(b, 1)
        self.go(GrowFromCenter(g[2][2]), run_time=0.5)
        self.sfx("kill")
        note = label("nobody knows whether Hamiltonian cycle is in P", 24, MUTED).move_to(STAGE + DOWN * 2.0)
        self.show(note, run_time=0.5)

    def b_tip1(self, b):
        self.tip(b, 1, "Four definitions in one breath", "P · NP · NP-hard (SAT ∝ L) · NP-complete (NP-hard and in NP)")

    def b_tip2(self, b):
        self.tip(b, 2, "Draw the diagram, one example per region", "shortest path · Hamiltonian cycle · halting problem")

    def b_tip3(self, b):
        self.tip(b, 3, "State Cook's theorem and what P = NP means", "a polynomial algorithm for one NP-complete problem ⇒ all of NP")

    def b_recap(self, b):
        self.recap(b, ["Decision problems only",
                       "P: deterministic polynomial.  NP: guess and verify",
                       "NP-hard: as hard as SAT.  NP-complete: NP-hard and in NP",
                       "P vs NP is still open"])
