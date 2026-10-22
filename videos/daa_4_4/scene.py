"""Video 4.4 - Proving NP-Completeness: 3-SAT, Clique & Vertex Cover. Rendered by build.py."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from lesson import *  # noqa: E402,F401,F403

PURPLE = UNIT_COLORS["IV"]
DARK = "#0F172A"
# (x1 v -x2 v x3) ^ (-x1 v x2 v x3) ^ (x1 v x2 v -x3)
F = [[(1, True), (2, False), (3, True)], [(1, False), (2, True), (3, True)], [(1, True), (2, True), (3, False)]]
SUB = {1: "₁", 2: "₂", 3: "₃"}
G5_EDGES = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (0, 4)]       # K4 on 1-4 plus 1-5
G5_BAR = [(1, 4), (2, 4), (3, 4)]
PEOPLE = ["Asha", "Bala", "Chetan", "Dev", "Esha", "Farah", "Gopal"]
CLIQUE5 = [0, 1, 2, 3, 4]
SOCIAL_EXTRA = [(4, 5), (5, 6), (2, 6)]


def lit(v, pos):
    return ("" if pos else "¬") + "x" + SUB[v]


def clause_text(cl):
    return "( " + "  ∨  ".join(lit(v, p) for v, p in cl) + " )"


def ring(center, r, n, start=np.pi / 2):
    return [center + np.array([r * np.cos(start - 2 * np.pi * k / n), r * np.sin(start - 2 * np.pi * k / n), 0]) for k in range(n)]


def node(pos, text, r=0.3, color=TEXT, fill=PANEL, size=20, text_color=TEXT):
    return VGroup(Circle(r, color=color, fill_color=fill, fill_opacity=1, stroke_width=3).move_to(pos),
                  label(text, size, text_color, "BOLD").move_to(pos))


def edge(a, b, color=MUTED, width=3, buff=0.32):
    ln = Line(a, b, color=color, stroke_width=width, buff=buff)
    ln.set_z_index(-1)
    return ln


def titled_card(title, color, lines, w, h, title_size=28, line_size=22, line_color=TEXT):
    body = VGroup(label(title, title_size, color, "BOLD"), *[label(t, line_size, line_color) for t in lines]
                  ).arrange(DOWN, buff=0.15)
    box = card(w, h, edge=color)
    return VGroup(box, body.move_to(box))


def flow(chips, buff=0.5, color=MUTED):
    row = VGroup(*chips).arrange(RIGHT, buff=buff)
    arrows = VGroup(*[Arrow(row[i].get_right(), row[i + 1].get_left(), buff=0.08, color=color, stroke_width=4,
                            max_tip_length_to_length_ratio=0.35) for i in range(len(chips) - 1)])
    return VGroup(row, arrows)


def paint(nodes, idx, color):
    """Animations that fill the given nodes with a colour (dark text on top)."""
    return [a for i in idx for a in (nodes[i][0].animate.set_fill(color).set_stroke(color), nodes[i][1].animate.set_color(DARK))]


class Video(Lesson):
    NEXT = ("4.5  Approximation algorithms", "& applications in AI, big data, crypto")

    # ------------------------------------------------------------ small helpers
    def step_tag(self, n, text):
        tag = VGroup(chip(f"STEP {n}", PURPLE if n == 1 else KILL, 22), label(text, 24, TEXT, "BOLD")).arrange(RIGHT, buff=0.3)
        tag.move_to(STAGE + UP * 2.55).align_to(STAGE + LEFT * 6.4, LEFT)
        self.show(tag, anim=FadeIn, run_time=0.4, shift=RIGHT * 0.2)
        self.sfx("pop")
        return tag

    def stamp(self, text, pos=None):
        s = chip(text, GOLD, 32, DARK).move_to(pos if pos is not None else STAGE + DOWN * 2.6)
        self.show(s, anim=GrowFromCenter, run_time=0.5)
        self.sfx("chime")
        return s

    def formula(self, pos, size=28, gap=0.35):
        """The example 3-SAT formula as three clause boxes joined by ∧; .clauses holds the boxes."""
        boxes = VGroup()
        for cl in F:
            t = label(clause_text(cl), size, TEXT, "BOLD")
            b = RoundedRectangle(width=t.width + 0.4, height=t.height + 0.35, corner_radius=0.12, color=PANEL_EDGE,
                                 fill_color=PANEL, fill_opacity=1, stroke_width=2)
            boxes.add(VGroup(b, t.move_to(b)))
        parts = VGroup()
        for i, bx in enumerate(boxes):
            if i:
                parts.add(label("∧", size, MUTED, "BOLD"))
            parts.add(bx)
        parts.arrange(RIGHT, buff=gap).move_to(pos)
        parts.clauses = boxes
        return parts

    def social(self, center, r=1.9):
        pts = ring(center, r, 7)
        E = [(a, b) for a in CLIQUE5 for b in CLIQUE5 if a < b] + SOCIAL_EXTRA
        es = VGroup(*[edge(pts[a], pts[b], MUTED, 2, 0.36) for a, b in E])
        nodes = VGroup(*[node(p, PEOPLE[k], 0.36, TEXT, PANEL, 15) for k, p in enumerate(pts)])
        g = VGroup(es, nodes)
        g.pts, g.edges, g.nodes, g.E = pts, es, nodes, E
        return g

    def g5(self, center, edges, r=1.3):
        pts = ring(center, r, 5)
        es = VGroup(*[edge(pts[a], pts[b], MUTED, 4, 0.32) for a, b in edges])
        nodes = VGroup(*[node(p, str(k + 1), 0.3, TEXT, PANEL, 20) for k, p in enumerate(pts)])
        g = VGroup(es, nodes)
        g.pts, g.edges, g.nodes = pts, es, nodes
        return g

    # ------------------------------------------------------------ hook
    def b_hook_clique(self, b):
        g = self.social(STAGE + LEFT * 3.4 + UP * 0.1)
        self.show(g, run_time=0.8)
        q = label("five people who all follow each other?", 30, TEXT, "BOLD").move_to(STAGE + RIGHT * 3.3 + UP * 1.2)
        self.show(q, run_time=0.5)
        self.at(b, 1)
        clique_edges = [e for e, (a, b_) in zip(g.edges, g.E) if a in CLIQUE5 and b_ in CLIQUE5]
        self.go(*[e.animate.set_color(GOLD).set_stroke(width=5) for e in clique_edges], *paint(g.nodes, CLIQUE5, GOLD), run_time=0.8)
        self.sfx("chime")
        c = VGroup(chip("CLIQUE", GOLD, 36, DARK), chip("NP-complete", KILL, 26)).arrange(DOWN, buff=0.3).move_to(STAGE + RIGHT * 3.3 + DOWN * 0.6)
        self.show(c, anim=GrowFromCenter, run_time=0.5)
        self.sfx("pop")

    def b_hook_chain(self, b):
        self.clear(run_time=0.4)
        ch = flow([chip("SAT", KILL, 32), chip("3-SAT", PURPLE, 32), chip("Clique", PURPLE, 32), chip("Vertex cover", PURPLE, 32)],
                  buff=0.7, color=GOLD).move_to(STAGE + UP * 0.6)
        self.stage.add(ch)
        self.go(LaggedStart(*[AnimationGroup(FadeIn(ch[0][i]), *([GrowArrow(ch[1][i - 1])] if i else []))
                              for i in range(4)], lag_ratio=0.4), run_time=1.8)
        self.sfx("pop")
        today = chip("today: three proofs", GOLD, 24, DARK).next_to(ch, UP, buff=0.5)
        self.show(today, run_time=0.4)
        self.at(b, 1)
        note = label("each proof is one reduction from the previous problem", 26, MUTED).move_to(STAGE + DOWN * 1.0)
        self.show(note, run_time=0.5)

    def b_hook_name(self, b):
        self.clear(run_time=0.4)
        title = VGroup(label("PROVING", 44, MUTED, "BOLD"), label("NP-COMPLETENESS", 76, GOLD, "BOLD")).arrange(DOWN, buff=0.1)
        title.move_to(STAGE + UP * 0.8)
        self.show(title, anim=GrowFromCenter, run_time=0.7)
        self.sfx("whoosh")
        self.at(b, 1)
        sub = chip("the same two-step template, every time", PURPLE, 28).move_to(STAGE + DOWN * 1.0)
        self.show(sub, run_time=0.5)

    def b_syllabus(self, b):
        self.syllabus(b, ["The two-step template", "3-SAT is NP-complete", "3-SAT → Clique", "Clique → Vertex cover"],
                      unit_text="UNIT IV  ·  COMPLEXITY")

    def b_exam(self, b):
        self.exam_star(b)

    # ------------------------------------------------------------ the template
    def b_t_steps(self, b):
        self.unsay()
        self.clear(run_time=0.4)
        s1 = titled_card("STEP 1 :  X ∈ NP", PURPLE, ["give a certificate", "check it in polynomial time"], 6.7, 2.3, 30, 22)
        s2 = titled_card("STEP 2 :  X is NP-hard", KILL, ["take a known NP-complete problem K", "reduce it to X :   K ∝ X"], 6.7, 2.3, 30, 22)
        VGroup(s1, s2).arrange(RIGHT, buff=0.3).move_to(STAGE + UP * 0.6)
        self.show(s1, run_time=0.6)
        self.sfx("pop")
        self.at(b, 1)
        self.show(s2, run_time=0.6)
        self.sfx("pop")
        res = chip("STEP 1 + STEP 2   ⇒   X is NP-complete", GOLD, 28, DARK).move_to(STAGE + DOWN * 1.5)
        self.show(res, anim=GrowFromCenter, run_time=0.5)

    def b_t_why(self, b):
        self.clear(run_time=0.4)
        c1 = VGroup(label("NP-hard  +  in NP   =   NP-complete", 32, TEXT, "BOLD"), label("the definition from video 4.2", 22, MUTED)).arrange(DOWN, buff=0.1)
        c1.move_to(STAGE + UP * 1.0)
        self.show(c1, run_time=0.6)
        self.at(b, 1)
        c2 = VGroup(label("KNOWN HARD  ∝  X", 32, KILL, "BOLD"), label("the direction rule from video 4.3", 22, MUTED)).arrange(DOWN, buff=0.1)
        c2.move_to(STAGE + DOWN * 1.0)
        self.show(c2, run_time=0.6)
        self.sfx("pop")

    def b_t_start(self, b):
        self.clear(run_time=0.4)
        root = VGroup(chip("SAT", KILL, 40), label("NP-complete by Cook's theorem", 24, MUTED)).arrange(DOWN, buff=0.2).move_to(STAGE + UP * 1.6)
        self.show(root, anim=GrowFromCenter, run_time=0.6)
        self.sfx("pop")
        self.at(b, 1)
        kids = VGroup(*[chip(t, PURPLE, 24) for t in ["3-SAT", "Clique", "Vertex cover", "…"]]).arrange(RIGHT, buff=0.6).move_to(STAGE + DOWN * 1.0)
        arrows = VGroup(*[Arrow(root.get_bottom(), k.get_top(), buff=0.15, color=GOLD, stroke_width=4, max_tip_length_to_length_ratio=0.2) for k in kids])
        self.stage.add(kids, arrows)
        self.go(LaggedStart(*[AnimationGroup(GrowArrow(a), FadeIn(k)) for a, k in zip(arrows, kids)], lag_ratio=0.3), run_time=1.4)
        note = label("every proof borrows from SAT, directly or through a chain", 22, MUTED).move_to(STAGE + DOWN * 2.2)
        self.show(note, run_time=0.4)

    # ------------------------------------------------------------ 3-SAT
    def b_s_def(self, b):
        self.clear(run_time=0.4)
        head = chip("3-SAT", GOLD, 36, DARK).move_to(STAGE + UP * 2.3)
        self.show(head, anim=GrowFromCenter, run_time=0.5)
        self.f = self.formula(STAGE + UP * 0.8)
        self.show(self.f, run_time=0.7)
        self.sfx("pop")
        notes = VGroup(label("CNF: an AND of clauses", 24, TEXT), label("each clause: an OR of exactly 3 literals", 24, TEXT)).arrange(DOWN, buff=0.1)
        notes.move_to(STAGE + DOWN * 0.6)
        self.show(notes, run_time=0.5)
        self.at(b, 1)
        q = chip("is it satisfiable ?", PURPLE, 28).move_to(STAGE + DOWN * 1.9)
        self.show(q, anim=GrowFromCenter, run_time=0.5)

    def b_s_innp(self, b):
        self.clear(self.f, run_time=0.4)
        self.step_tag(1, "3-SAT  ∈  NP")
        self.at(b, 1)
        cert = chip("certificate:   x₁ = T,  x₂ = T,  x₃ = T", GOLD, 26, DARK).move_to(STAGE + DOWN * 0.6)
        self.show(cert, run_time=0.5)
        ticks = VGroup(*[label("✓", 36, SAFE, "BOLD").next_to(c, DOWN, buff=0.15) for c in self.f.clauses])
        self.stage.add(ticks)
        self.go(LaggedStart(*[GrowFromCenter(t) for t in ticks], lag_ratio=0.4), run_time=1.0)
        self.sfx("chime")
        lin = label("check every clause: linear time", 24, SAFE).move_to(STAGE + DOWN * 1.6)
        self.show(lin, run_time=0.4)

    def b_s_reduce(self, b):
        self.clear(run_time=0.4)
        self.step_tag(2, "SAT  ∝  3-SAT")
        rule = label("translate every clause into clauses of exactly 3 literals", 24, MUTED).move_to(STAGE + UP * 1.6)
        self.show(rule, run_time=0.4)
        self.at(b, 1)
        long_ = chip("( a ∨ b ∨ c ∨ d )", ACCENT, 30).move_to(STAGE + LEFT * 3.6 + UP * 0.4)
        split = VGroup(chip("( a ∨ b ∨ y )", SAFE, 28), label("∧", 28, MUTED, "BOLD"), chip("( ¬y ∨ c ∨ d )", SAFE, 28)
                       ).arrange(RIGHT, buff=0.25).move_to(STAGE + RIGHT * 2.6 + UP * 0.4)
        arr = Arrow(long_.get_right(), split.get_left(), buff=0.15, color=GOLD, stroke_width=6, max_tip_length_to_length_ratio=0.3)
        self.show(long_, run_time=0.4)
        self.show(arr, anim=GrowArrow, run_time=0.3)
        self.show(split, run_time=0.5)
        self.sfx("pop")
        note = label("a long clause is split with a fresh variable y", 22, MUTED).move_to(STAGE + DOWN * 0.5)
        self.show(note, run_time=0.4)

    def b_s_short(self, b):
        short = chip("( a ∨ b )", ACCENT, 30).move_to(STAGE + LEFT * 3.6 + DOWN * 1.3)
        pad = VGroup(chip("( a ∨ b ∨ y )", SAFE, 28), label("∧", 28, MUTED, "BOLD"), chip("( a ∨ b ∨ ¬y )", SAFE, 28)
                     ).arrange(RIGHT, buff=0.25).move_to(STAGE + RIGHT * 2.6 + DOWN * 1.3)
        arr = Arrow(short.get_right(), pad.get_left(), buff=0.15, color=GOLD, stroke_width=6, max_tip_length_to_length_ratio=0.3)
        self.show(short, run_time=0.4)
        self.show(arr, anim=GrowArrow, run_time=0.3)
        self.show(pad, run_time=0.5)
        self.sfx("pop")
        self.at(b, 1)
        res = VGroup(chip("satisfiable  ⇔  satisfiable", SAFE, 22), chip("linear size", SAFE, 22)).arrange(RIGHT, buff=0.4).move_to(STAGE + DOWN * 2.2)
        self.show(res, run_time=0.5)
        self.until(b["phrases"][1]["start"] + self.phrase_len(b, 1) * 0.75)
        self.stamp("3-SAT is NP-COMPLETE", STAGE + DOWN * 3.0)

    # ------------------------------------------------------------ clique
    def b_c_def(self, b):
        self.clear(run_time=0.4)
        head = chip("CLIQUE", GOLD, 36, DARK).move_to(STAGE + RIGHT * 3.3 + UP * 2.0)
        self.show(head, anim=GrowFromCenter, run_time=0.5)
        g = self.social(STAGE + LEFT * 3.4 + DOWN * 0.2, 1.8)
        self.show(g, run_time=0.7)
        d = VGroup(label("given a graph and k:", 24, MUTED), label("k vertices, all pairwise connected ?", 28, TEXT, "BOLD")).arrange(DOWN, buff=0.1)
        d.move_to(STAGE + RIGHT * 3.3 + UP * 0.6)
        self.show(d, run_time=0.5)
        self.at(b, 1)
        clique_edges = [e for e, (a, b_) in zip(g.edges, g.E) if a in CLIQUE5 and b_ in CLIQUE5]
        self.go(*[e.animate.set_color(GOLD).set_stroke(width=5) for e in clique_edges], *paint(g.nodes, CLIQUE5, GOLD), run_time=0.8)
        self.sfx("chime")
        ex = chip("five people who all follow each other: k = 5", GOLD, 22, DARK).move_to(STAGE + RIGHT * 3.3 + DOWN * 0.9)
        self.show(ex, run_time=0.5)
        self.c_graph = g

    def b_c_innp(self, b):
        self.clear(self.c_graph, run_time=0.4)
        self.step_tag(1, "CLIQUE  ∈  NP")
        self.at(b, 1)
        cert = chip("certificate: the k vertices", GOLD, 26, DARK).move_to(STAGE + RIGHT * 3.3 + UP * 0.6)
        self.show(cert, run_time=0.5)
        chk = VGroup(label("check the  k choose 2  edges between them", 24, TEXT), label("polynomial", 26, SAFE, "BOLD")).arrange(DOWN, buff=0.1)
        chk.move_to(STAGE + RIGHT * 3.3 + DOWN * 0.8)
        self.show(chk, run_time=0.5)
        self.sfx("chime")

    def literal_graph(self, center):
        """9 vertices in 3 columns (one per clause), labelled with their literals; edges added later."""
        cols = [center + RIGHT * dx for dx in (-3.6, 0.0, 3.6)]
        pts, nodes, labels = [], VGroup(), VGroup()
        for ci, cl in enumerate(F):
            for li, (v, p) in enumerate(cl):
                q = cols[ci] + UP * (1.15 - 1.15 * li)
                pts.append(q)
                nodes.add(node(q, lit(v, p), 0.36, TEXT, PANEL, 20))
            labels.add(label(f"C{ci + 1}", 22, MUTED, "BOLD").move_to(cols[ci] + UP * 2.0))
        E = []
        for i in range(9):
            for j in range(i + 1, 9):
                ci, cj = i // 3, j // 3
                (v, p), (w, q) = F[ci][i % 3], F[cj][j % 3]
                if ci != cj and not (v == w and p != q):
                    E.append((i, j))
        g = VGroup(nodes, labels)
        g.pts, g.nodes, g.E = pts, nodes, E
        return g

    def b_c_build(self, b):
        self.clear(run_time=0.4)
        self.step_tag(2, "3-SAT  ∝  CLIQUE")
        f = self.formula(STAGE + UP * 1.7, 22, 0.25)
        self.show(f, run_time=0.5)
        self.at(b, 1)
        g = self.literal_graph(STAGE + DOWN * 0.9)
        self.stage.add(g)
        self.go(LaggedStart(*[FadeIn(n, scale=0.5) for n in g.nodes], lag_ratio=0.1), FadeIn(g[1]), run_time=1.4)
        self.sfx("pop")
        note = chip("one vertex per literal of every clause:  3k vertices", PURPLE, 22).move_to(STAGE + DOWN * 3.1)
        self.show(note, run_time=0.4)
        self.lg, self.lg_note, self.lg_f = g, note, f

    def b_c_edges(self, b):
        g = self.lg
        es = VGroup(*[edge(g.pts[i], g.pts[j], MUTED, 2, 0.38) for i, j in g.E])
        g.edges = es
        self.stage.add(es)
        self.go(LaggedStart(*[Create(e) for e in es], lag_ratio=0.08), run_time=2.2)
        self.sfx("pop")
        rule = VGroup(label("edge  =  different clauses  and  not opposites", 22, TEXT), label("never  x  with  ¬x", 22, KILL, "BOLD")
                      ).arrange(DOWN, buff=0.08).move_to(self.lg_note)
        self.go(FadeOut(self.lg_note), FadeIn(rule), run_time=0.4)
        self.stage.remove(self.lg_note)
        self.stage.add(rule)
        self.lg_note = rule
        self.at(b, 1)
        q = chip("clique of size k = 3 ?", GOLD, 22, DARK).move_to(STAGE + RIGHT * 5.5 + DOWN * 3.1)
        self.show(q, anim=GrowFromCenter, run_time=0.5)
        self.sfx("pop")

    def b_c_example(self, b):
        g = self.lg
        tri = [2, 5, 6]                                           # x3 (C1), x3 (C2), x1 (C3)
        self.at(b, 1)
        tri_edges = [e for e, (i, j) in zip(g.edges, g.E) if i in tri and j in tri]
        self.go(*[e.animate.set_color(GOLD).set_stroke(width=7) for e in tri_edges], *paint(g.nodes, tri, GOLD), run_time=0.9)
        self.sfx("chime")
        asg = chip("x₁ = T,  x₃ = T   ⇒   formula true", SAFE, 22).move_to(self.lg_note)
        self.go(FadeOut(self.lg_note), FadeIn(asg), run_time=0.4)
        self.stage.remove(self.lg_note)
        self.stage.add(asg)
        self.lg_note = asg

    def b_c_why(self, b):
        self.clear(run_time=0.4)
        head = label("WHY IT WORKS", 32, GOLD, "BOLD").move_to(STAGE + UP * 2.3)
        self.show(head, anim=GrowFromCenter, run_time=0.4)
        c1 = titled_card("clique of size k  ⇒  satisfiable", SAFE, ["one literal from every clause,", "no x with ¬x: set them all true"], 6.2, 1.9, 26, 22)
        c2 = titled_card("satisfiable  ⇒  clique of size k", SAFE, ["one true literal per clause;", "those k vertices are pairwise joined"], 6.2, 1.9, 26, 22)
        c1.move_to(STAGE + UP * 0.8)
        c2.move_to(STAGE + DOWN * 1.3)
        self.show(c1, run_time=0.6)
        self.sfx("pop")
        self.at(b, 1)
        self.show(c2, run_time=0.6)
        self.sfx("pop")
        yes = chip("yes  ⇔  yes", GOLD, 26, DARK).move_to(STAGE + DOWN * 2.7)
        self.show(yes, anim=GrowFromCenter, run_time=0.4)

    def b_c_done(self, b):
        self.clear(run_time=0.4)
        c = chip("3k vertices,  fewer than 9k² edges:  polynomial", SAFE, 28).move_to(STAGE + UP * 0.8)
        self.show(c, run_time=0.5)
        self.at(b, 1)
        self.stamp("CLIQUE is NP-COMPLETE", STAGE + DOWN * 0.6)

    # ------------------------------------------------------------ vertex cover
    def b_v_def(self, b):
        self.clear(run_time=0.4)
        head = chip("VERTEX COVER", GOLD, 36, DARK).move_to(STAGE + RIGHT * 3.3 + UP * 2.0)
        self.show(head, anim=GrowFromCenter, run_time=0.5)
        g = self.g5(STAGE + LEFT * 3.4 + DOWN * 0.2, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 2)], 1.6)
        self.show(g, run_time=0.7)
        d = VGroup(label("given a graph and k:", 24, MUTED), label("k vertices that touch every edge ?", 28, TEXT, "BOLD")).arrange(DOWN, buff=0.1)
        d.move_to(STAGE + RIGHT * 3.3 + UP * 0.6)
        self.show(d, run_time=0.5)
        self.at(b, 1)
        self.go(*paint(g.nodes, [0, 2, 3], KILL), *[e.animate.set_color(KILL) for e in g.edges], run_time=0.8)
        self.sfx("chime")
        ex = chip("the guards at junctions: k = 3", KILL, 22).move_to(STAGE + RIGHT * 3.3 + DOWN * 0.9)
        self.show(ex, run_time=0.5)
        self.v_graph = g

    def b_v_innp(self, b):
        self.clear(self.v_graph, run_time=0.4)
        self.step_tag(1, "VERTEX COVER  ∈  NP")
        self.at(b, 1)
        cert = chip("certificate: the k vertices", GOLD, 26, DARK).move_to(STAGE + RIGHT * 3.3 + UP * 0.6)
        self.show(cert, run_time=0.5)
        chk = VGroup(label("check that every edge touches one of them", 24, TEXT), label("polynomial", 26, SAFE, "BOLD")).arrange(DOWN, buff=0.1)
        chk.move_to(STAGE + RIGHT * 3.3 + DOWN * 0.8)
        self.show(chk, run_time=0.5)
        self.sfx("chime")

    def b_v_build(self, b):
        self.clear(run_time=0.4)
        self.step_tag(2, "CLIQUE  ∝  VERTEX COVER")
        g = self.g5(STAGE + LEFT * 3.6 + DOWN * 0.4, G5_EDGES, 1.45)
        gb = self.g5(STAGE + RIGHT * 3.6 + DOWN * 0.4, G5_BAR, 1.45)
        lg = label("G", 30, TEXT, "BOLD").next_to(g, UP, buff=0.3)
        lgb = label("Ḡ  (the complement)", 30, TEXT, "BOLD").next_to(gb, UP, buff=0.3)
        self.show(g, lg, run_time=0.6)
        arr = Arrow(g.get_right() + RIGHT * 0.2, gb.get_left() + LEFT * 0.2, buff=0.1, color=GOLD, stroke_width=6, max_tip_length_to_length_ratio=0.2)
        lab = label("Ḡ has an edge exactly where G has none", 22, MUTED).move_to(STAGE + DOWN * 3.15)
        self.show(arr, anim=GrowArrow, run_time=0.4)
        self.show(gb, lgb, lab, run_time=0.6)
        self.sfx("pop")
        self.at(b, 1)
        q = chip("cover of size n − k ?", GOLD, 24, DARK).move_to(STAGE + DOWN * 2.45)
        self.show(q, anim=GrowFromCenter, run_time=0.5)
        self.sfx("pop")
        self.vg, self.vgb, self.vq = g, gb, q

    def b_v_example(self, b):
        g, gb = self.vg, self.vgb
        self.go(*paint(g.nodes, [0, 1, 2, 3], GOLD), *[e.animate.set_color(GOLD).set_stroke(width=5) for e in g.edges[:6]], run_time=0.8)
        self.sfx("chime")
        c1 = chip("clique of size 4", GOLD, 22, DARK).next_to(g, DOWN, buff=0.3)
        self.drop(self.vq, run_time=0.3)
        self.show(c1, run_time=0.4)
        self.at(b, 1)
        self.go(*[e.animate.set_color(KILL).set_stroke(width=5) for e in gb.edges], run_time=0.5)
        self.go(*paint(gb.nodes, [4], KILL), run_time=0.5)
        self.sfx("place")
        c2 = chip("cover of size 1  =  5 − 4", KILL, 22).next_to(gb, DOWN, buff=0.3)
        self.show(c2, run_time=0.4)

    def b_v_why(self, b):
        self.clear(run_time=0.4)
        head = label("WHY IT WORKS", 32, GOLD, "BOLD").move_to(STAGE + UP * 2.3)
        self.show(head, anim=GrowFromCenter, run_time=0.4)
        c1 = titled_card("clique of size k in G  ⇒  cover of size n − k in Ḡ", SAFE,
                         ["no complement edges inside the clique,", "so every Ḡ edge touches the other n − k vertices"], 9.0, 1.9, 26, 22)
        c2 = titled_card("cover of size n − k in Ḡ  ⇒  clique of size k in G", SAFE,
                         ["the vertices outside the cover have no Ḡ edges,", "so they are pairwise joined in G"], 9.0, 1.9, 26, 22)
        c1.move_to(STAGE + UP * 0.8)
        c2.move_to(STAGE + DOWN * 1.3)
        self.show(c1, run_time=0.6)
        self.sfx("pop")
        self.at(b, 1)
        self.show(c2, run_time=0.6)
        self.sfx("pop")
        yes = chip("yes  ⇔  yes", GOLD, 26, DARK).move_to(STAGE + DOWN * 2.7)
        self.show(yes, anim=GrowFromCenter, run_time=0.4)

    def b_v_done(self, b):
        self.clear(run_time=0.4)
        c = chip("same n vertices,  fewer than n² edges:  polynomial", SAFE, 28).move_to(STAGE + UP * 0.8)
        self.show(c, run_time=0.5)
        self.at(b, 1)
        self.stamp("VERTEX COVER is NP-COMPLETE", STAGE + DOWN * 0.6)

    # ------------------------------------------------------------ how they relate
    def b_r_triangle(self, b):
        self.clear(run_time=0.4)
        head = label("THREE PROBLEMS, ONE TRIANGLE", 32, GOLD, "BOLD").move_to(STAGE + UP * 2.4)
        self.show(head, anim=GrowFromCenter, run_time=0.4)
        pts = ring(STAGE + DOWN * 0.4, 1.9, 3)
        cs = [chip("clique in G", GOLD, 26, DARK).move_to(pts[0]), chip("independent set in Ḡ", SAFE, 26).move_to(pts[1] + RIGHT * 1.4),
              chip("V − (vertex cover of Ḡ)", KILL, 26).move_to(pts[2] + LEFT * 1.6)]
        self.at(b, 1)
        self.stage.add(*cs)
        self.go(LaggedStart(*[GrowFromCenter(c) for c in cs], lag_ratio=0.4), run_time=1.3)
        self.sfx("pop")
        eqs = VGroup(*[label("=", 36, MUTED, "BOLD").move_to((cs[i].get_center() + cs[j].get_center()) / 2) for i, j in ((0, 1), (1, 2), (0, 2))])
        self.show(eqs, run_time=0.5)
        note = label("the same set of vertices: any one of them solves the others", 24, TEXT).move_to(STAGE + DOWN * 2.8)
        self.show(note, run_time=0.5)

    def b_r_chain(self, b):
        self.clear(run_time=0.4)
        ch = flow([chip("SAT", KILL, 32), chip("3-SAT", PANEL_EDGE, 32), chip("Clique", PANEL_EDGE, 32), chip("Vertex cover", PANEL_EDGE, 32)],
                  buff=0.9, color=GOLD).move_to(STAGE + UP * 0.6)
        self.show(ch, run_time=0.8)
        cook = label("Cook's theorem", 20, MUTED).next_to(ch[0][0], UP, buff=0.2)
        self.show(cook, run_time=0.3)
        self.at(b, 1)
        for i in range(3):
            dot = Dot(color=KILL, radius=0.14).move_to(ch[1][i].get_start())
            self.add(dot)
            self.play(MoveAlongPath(dot, Line(ch[1][i].get_start(), ch[1][i].get_end())), run_time=0.5)
            self.remove(dot)
            self.go(ch[0][i + 1][0].animate.set_fill(KILL).set_stroke(KILL), run_time=0.3)
            self.sfx("kill", -0.2)
        note = label("hardness flows down the arrows, from Cook's theorem to everything", 24, TEXT).move_to(STAGE + DOWN * 1.2)
        self.show(note, run_time=0.5)

    def b_r_use(self, b):
        self.clear(run_time=0.4)
        c = chip("in the exam, any of these can be your known NP-complete problem", ACCENT, 26).move_to(STAGE + UP * 0.9)
        self.show(c, run_time=0.5)
        self.at(b, 1)
        tip = VGroup(label("pick the one that looks most like your new problem", 28, GOLD, "BOLD"), label("that makes the translation short", 24, MUTED)
                     ).arrange(DOWN, buff=0.1).move_to(STAGE + DOWN * 0.8)
        self.show(tip, run_time=0.5)
        self.sfx("chime")

    # ------------------------------------------------------------ practice, tips, recap
    def b_p_intro(self, b):
        self.question_card(b, ["Independent set: k vertices, no edges among them.", "Prove it is NP-complete.", "(known problem: clique)"])

    def b_p_pause(self, b):
        self.pause_screen(b, "Pause and write the two steps")

    def b_p_answer(self, b):
        self.pause_over()
        self.clear(run_time=0.4)
        s1 = titled_card("STEP 1 :  in NP", PURPLE, ["certificate: the k vertices", "check that no pair is an edge: polynomial"], 8.6, 1.9, 28, 24)
        s2 = titled_card("STEP 2 :  NP-hard,   CLIQUE  ∝  INDEPENDENT SET", KILL, ["a clique of size k in G  =  an independent set of size k in Ḡ",
                                                                                  "translation: the complement graph, the same k"], 10.4, 1.9, 28, 24)
        s1.move_to(STAGE + UP * 1.5)
        s2.move_to(STAGE + DOWN * 0.7)
        self.show(s1, run_time=0.6)
        self.sfx("pop")
        self.at(b, 1)
        self.show(s2, run_time=0.6)
        self.sfx("pop")
        self.until(b["phrases"][1]["start"] + self.phrase_len(b, 1) * 0.75)
        self.stamp("INDEPENDENT SET is NP-COMPLETE", STAGE + DOWN * 2.5)

    def b_tip1(self, b):
        self.tip(b, 1, "Two headings, always: 'in NP' and 'NP-hard'", "proving only the reduction loses marks")

    def b_tip2(self, b):
        self.tip(b, 2, "The reduction needs four things", "known problem · translation · yes ⇔ yes · polynomial size")

    def b_tip3(self, b):
        self.tip(b, 3, "Memorise the two pictures", "the literal graph (3-SAT → Clique) and the complement graph (Clique → VC)")

    def b_recap(self, b):
        self.recap(b, ["NP-complete:  in NP  +  a reduction from a known one",
                       "3-SAT: split the clauses.   Clique: the literal graph",
                       "Vertex cover: the complement graph",
                       "Clique, independent set, vertex cover: one triangle"])
