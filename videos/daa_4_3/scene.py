"""Video 4.3 - Polynomial-Time Reductions. Rendered by build.py (needs SCHEDULE / ENVELOPE env vars)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from lesson import *  # noqa: E402,F401,F403

PURPLE = UNIT_COLORS["IV"]
DARK = "#0F172A"
EXAMS = ["Maths", "Physics", "DAA", "DBMS", "English"]
CONFLICTS = [(0, 1), (0, 2), (1, 3), (2, 3), (2, 4), (3, 4)]
SLOT = [0, 1, 1, 0, 2]                                   # a 3-slot timetable (facts.py: 2 slots impossible)
SLOT_COLOURS = [SAFE, GOLD, ACCENT]
VAN_EDGES = [(0, 1), (1, 2), (2, 3), (3, 0)]
PENTA_EDGES = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
GUESTS = ["Asha", "Bala", "Chetan", "Dev", "Esha"]
NOTES = [100, 200, 200, 50, 20, 10]


def ring(center, r, n, start=np.pi / 2):
    """n points on a circle, the first at the top, clockwise."""
    return [center + np.array([r * np.cos(start - 2 * np.pi * k / n), r * np.sin(start - 2 * np.pi * k / n), 0]) for k in range(n)]


def node(pos, text, r=0.3, color=TEXT, fill=PANEL, size=20, text_color=TEXT):
    return VGroup(Circle(r, color=color, fill_color=fill, fill_opacity=1, stroke_width=3).move_to(pos),
                  label(text, size, text_color, "BOLD").move_to(pos))


def box_node(pos, text, color=PANEL_EDGE, fill=PANEL, size=20, text_color=TEXT):
    t = label(text, size, text_color, "BOLD")
    b = RoundedRectangle(width=t.width + 0.5, height=0.6, corner_radius=0.15, color=color, fill_color=fill, fill_opacity=1,
                         stroke_width=3)
    return VGroup(b, t).move_to(pos)


def edge(a, b, color=MUTED, width=3, buff=0.32, dashed=False):
    if dashed:
        return DashedLine(a, b, color=color, stroke_width=width, buff=buff, dash_length=0.12)
    return Line(a, b, color=color, stroke_width=width, buff=buff)


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


def big_arrow(a, b, color=GOLD, width=8):
    return Arrow(a, b, buff=0.1, color=color, stroke_width=width, max_tip_length_to_length_ratio=0.25)


class Video(Lesson):
    NEXT = ("4.4  Proving NP-completeness:", "3-SAT, Vertex Cover & Clique")

    # ------------------------------------------------------------ hook
    def b_hook_real(self, b):
        pts = ring(STAGE + LEFT * 3.4 + UP * 0.1, 1.9, 5)
        nodes = VGroup(*[box_node(p, e) for p, e in zip(pts, EXAMS)])
        lines = VGroup(*[edge(pts[i], pts[j], buff=0.0) for i, j in CONFLICTS])
        for ln in lines:
            ln.set_z_index(-1)
        self.show(nodes, run_time=0.7, lag_ratio=0.15)
        self.sfx("pop")
        self.stage.add(lines)
        self.go(LaggedStart(*[Create(ln) for ln in lines], lag_ratio=0.2), run_time=1.2)
        key = label("edge = some student takes both", 20, MUTED).next_to(nodes, DOWN, buff=0.35)
        self.show(key, run_time=0.4)
        self.exam_key = key
        self.at(b, 1)
        q = VGroup(label("How few slots?", 40, GOLD, "BOLD"), chip("exam timetabling", ACCENT, 26)).arrange(DOWN, buff=0.35)
        q.move_to(STAGE + RIGHT * 3.4 + UP * 0.3)
        self.show(q, anim=GrowFromCenter, run_time=0.5)
        self.sfx("pop")
        self.exam_nodes, self.exam_lines, self.exam_q = nodes, lines, q

    def b_hook_turn(self, b):
        coloured = [box_node(n.get_center(), e, SLOT_COLOURS[s], SLOT_COLOURS[s], 20, DARK)
                    for n, e, s in zip(self.exam_nodes, EXAMS, SLOT)]
        self.go(LaggedStart(*[Transform(n, c) for n, c in zip(self.exam_nodes, coloured)], lag_ratio=0.25), run_time=1.5)
        self.sfx("place")
        legend = VGroup(*[chip(f"slot {i + 1}", c, 20, DARK) for i, c in enumerate(SLOT_COLOURS)]).arrange(RIGHT, buff=0.2)
        legend.next_to(self.exam_nodes, DOWN, buff=0.35)
        self.drop(self.exam_key, run_time=0.2)
        self.show(legend, run_time=0.4)
        self.at(b, 1)
        q2 = VGroup(label("colourable with k colours?", 32, TEXT, "BOLD"), chip("graph colouring", PURPLE, 26)).arrange(DOWN, buff=0.3)
        q2.move_to(STAGE + RIGHT * 3.4 + UP * 0.6)
        self.go(FadeOut(self.exam_q), FadeIn(q2, shift=UP * 0.2), run_time=0.5)
        self.stage.remove(self.exam_q)
        self.stage.add(q2)
        red = chip("you just did a REDUCTION", GOLD, 28, DARK).move_to(STAGE + RIGHT * 3.4 + DOWN * 1.3)
        self.show(red, anim=GrowFromCenter, run_time=0.5)
        self.sfx("chime")

    def b_hook_name(self, b):
        self.clear(run_time=0.4)
        title = label("REDUCTIONS", 80, GOLD, "BOLD").move_to(STAGE + UP * 0.8)
        self.show(title, anim=GrowFromCenter, run_time=0.7)
        self.sfx("whoosh")
        c1 = chip("solve a new problem with an old algorithm", SAFE, 26).move_to(STAGE + DOWN * 0.6)
        self.show(c1, run_time=0.5)
        self.at(b, 1)
        c2 = chip("prove that a problem is hard", KILL, 26).move_to(STAGE + DOWN * 1.4)
        self.show(c2, run_time=0.5)

    def b_syllabus(self, b):
        self.syllabus(b, ["What a reduction is", "The direction rule", "Three everyday reductions", "How reductions prove NP-hardness"],
                      unit_text="UNIT IV  ·  COMPLEXITY")

    def b_exam(self, b):
        self.exam_star(b)

    # ------------------------------------------------------------ the idea
    def b_i_translate(self, b):
        self.unsay()
        self.clear(run_time=0.4)
        a = titled_card("PROBLEM A", ACCENT, ["a question you", "cannot solve yet"], 3.6, 1.7)
        t = titled_card("TRANSLATOR", GOLD, ["the reduction", "(polynomial time)"], 3.6, 1.7)
        bb = titled_card("PROBLEM B", SAFE, ["has a known", "solver"], 3.6, 1.7)
        row = VGroup(a, t, bb).arrange(RIGHT, buff=0.8).move_to(STAGE + UP * 0.8)
        arrows = VGroup(*[big_arrow(row[i].get_right(), row[i + 1].get_left(), MUTED, 6) for i in range(2)])
        self.stage.add(row, arrows)
        self.go(LaggedStart(FadeIn(a), GrowArrow(arrows[0]), FadeIn(t), GrowArrow(arrows[1]), FadeIn(bb), lag_ratio=0.3), run_time=1.8)
        self.sfx("pop")
        self.at(b, 1)
        back = CurvedArrow(bb.get_bottom() + DOWN * 0.1, a.get_bottom() + DOWN * 0.1, angle=-1.2, color=PURPLE, stroke_width=5)
        ans = chip("B's yes / no  =  A's yes / no", PURPLE, 26).move_to(STAGE + DOWN * 2.2)
        self.show(back, ans, run_time=0.7)
        self.sfx("chime")

    def b_i_rules(self, b):
        self.clear(run_time=0.4)
        r1 = titled_card("RULE 1", GOLD, ["the translation is fast:", "polynomial time"], 5.6, 2.2, 30, 26)
        r2 = titled_card("RULE 2", GOLD, ["the answer is preserved:", "A says yes  ⇔  B says yes"], 5.6, 2.2, 30, 26)
        VGroup(r1, r2).arrange(RIGHT, buff=0.6).move_to(STAGE + UP * 0.4)
        self.show(r1, run_time=0.6)
        self.sfx("pop")
        self.at(b, 1)
        self.show(r2, run_time=0.6)
        self.sfx("pop")

    def b_i_notation(self, b):
        self.clear(run_time=0.4)
        n = VGroup(label("A  ∝  B", 90, GOLD, "BOLD"), label("A reduces to B      (also written  A ≤ₚ B)", 26, MUTED)).arrange(DOWN, buff=0.2)
        n.move_to(STAGE + UP * 1.0)
        self.show(n, anim=GrowFromCenter, run_time=0.6)
        self.sfx("whoosh")
        self.at(b, 1)
        m = VGroup(chip("A is no harder than B", ACCENT, 28), chip("if you can do B, you can do A", SAFE, 28)).arrange(DOWN, buff=0.3)
        m.move_to(STAGE + DOWN * 1.4)
        self.stage.add(m)
        self.go(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in m], lag_ratio=0.5), run_time=1.0)

    def b_i_everyday(self, b):
        self.clear(run_time=0.4)
        head = label("YOU DO THIS EVERY DAY", 32, GOLD, "BOLD").move_to(STAGE + UP * 2.2)
        self.show(head, anim=GrowFromCenter, run_time=0.4)
        r1 = flow([chip("two houses within 5 km ?", PANEL_EDGE, 24), chip("shortest path  (the map app)", SAFE, 24)])
        r2 = flow([chip("seat the guests without a fight ?", PANEL_EDGE, 24), chip("graph colouring", SAFE, 24)])
        rows = VGroup(r1, r2).arrange(DOWN, buff=0.5).move_to(STAGE + UP * 0.5)
        self.show(r1, run_time=0.6)
        self.sfx("pop")
        self.at(b, 1)
        self.show(r2, run_time=0.6)
        self.sfx("pop")
        self.until(b["phrases"][1]["start"] + self.phrase_len(b, 1) * 0.6)
        m = chip("translate  →  then use the tool you already have", GOLD, 28, DARK).move_to(STAGE + DOWN * 1.6)
        self.show(m, anim=GrowFromCenter, run_time=0.5)
        self.sfx("chime")

    # ------------------------------------------------------------ the direction rule
    def b_d_hard(self, b):
        self.clear(run_time=0.4)
        head = chip("THE DIRECTION RULE", KILL, 30).move_to(STAGE + UP * 2.4)
        self.show(head, anim=GrowFromCenter, run_time=0.5)
        self.sfx("pop")
        st = VGroup(label("A  ∝  B", 56, GOLD, "BOLD"), label("⇒", 44, MUTED), label("B is at least as hard as A", 36, KILL, "BOLD")
                    ).arrange(RIGHT, buff=0.5).move_to(STAGE + UP * 0.9)
        self.show(st, run_time=0.6)
        wa = node(STAGE + LEFT * 2.0 + DOWN * 1.0, "A", 0.45, ACCENT, PANEL, 28)
        wb = node(STAGE + RIGHT * 2.0 + DOWN * 1.0, "B", 0.8, KILL, PANEL, 36)
        self.show(wa, wb, anim=GrowFromCenter, run_time=0.5)
        self.at(b, 1)
        why = VGroup(label("if B were easy, A would be easy too", 26, TEXT), label("(solve A by translating it into B)", 22, MUTED)
                     ).arrange(DOWN, buff=0.1).move_to(STAGE + DOWN * 2.5)
        self.show(why, run_time=0.5)

    def b_d_prove(self, b):
        self.clear(run_time=0.4)
        head = label("TO PROVE A NEW PROBLEM X IS HARD", 32, GOLD, "BOLD").move_to(STAGE + UP * 2.3)
        self.show(head, anim=GrowFromCenter, run_time=0.4)
        good = VGroup(chip("KNOWN HARD", KILL, 32), label("∝", 44, GOLD, "BOLD"), chip("X", PURPLE, 32)).arrange(RIGHT, buff=0.5)
        good.move_to(STAGE + UP * 0.9)
        tick = label("✓", 48, SAFE, "BOLD").next_to(good, RIGHT, buff=0.5)
        self.show(good, run_time=0.6)
        self.show(tick, anim=GrowFromCenter, run_time=0.3)
        self.sfx("chime")
        self.at(b, 1)
        bad = VGroup(chip("X", PURPLE, 32), label("∝", 44, GOLD, "BOLD"), chip("KNOWN HARD", KILL, 32)).arrange(RIGHT, buff=0.5)
        bad.move_to(STAGE + DOWN * 0.6)
        cross = label("✗", 48, KILL, "BOLD").next_to(bad, RIGHT, buff=0.5)
        self.show(bad, run_time=0.5)
        self.show(cross, anim=GrowFromCenter, run_time=0.3)
        self.sfx("kill")
        strike = Line(bad.get_left() + LEFT * 0.1, bad.get_right() + RIGHT * 0.1, color=KILL, stroke_width=6)
        self.show(strike, anim=Create, run_time=0.3)
        note = label("known hard problem on the left, your new problem on the right", 24, MUTED).move_to(STAGE + DOWN * 2.2)
        self.show(note, run_time=0.4)

    def b_d_trick(self, b):
        self.clear(run_time=0.4)
        head = label("MEMORY TRICK: HARDNESS FLOWS ALONG THE ARROW", 30, GOLD, "BOLD").move_to(STAGE + UP * 2.3)
        self.show(head, anim=GrowFromCenter, run_time=0.4)
        sat = node(STAGE + LEFT * 3.5 + UP * 0.3, "SAT", 0.75, KILL, KILL, 30, DARK)
        x = node(STAGE + RIGHT * 3.5 + UP * 0.3, "X", 0.75, PANEL_EDGE, PANEL, 34)
        arr = big_arrow(sat.get_right(), x.get_left(), GOLD, 8)
        self.show(sat, x, run_time=0.5)
        self.show(arr, anim=GrowArrow, run_time=0.5)
        self.at(b, 1)
        dot = Dot(color=KILL, radius=0.16).move_to(arr.get_start())
        self.add(dot)
        self.play(MoveAlongPath(dot, Line(arr.get_start(), arr.get_end())), run_time=1.0)
        self.remove(dot)
        self.go(x[0].animate.set_fill(KILL).set_stroke(KILL), x[1].animate.set_color(DARK), run_time=0.5)
        self.sfx("kill")
        c = chip("X inherits the hardness of SAT", KILL, 28).move_to(STAGE + DOWN * 1.4)
        self.show(c, anim=GrowFromCenter, run_time=0.5)
        n = label("the arrow always starts at the problem you already know is hard", 22, MUTED).move_to(STAGE + DOWN * 2.3)
        self.show(n, run_time=0.4)

    # ------------------------------------------------------------ reduction 1: HC -> TSP
    def van_graph(self, center, r=1.3, costs=False):
        pts = ring(center, r, 4, start=3 * np.pi / 4)
        E = {frozenset(e) for e in VAN_EDGES}
        g = VGroup()
        labels = VGroup()
        for i in range(4):
            for j in range(i + 1, 4):
                have = frozenset((i, j)) in E
                if have:
                    g.add(edge(pts[i], pts[j], SAFE if costs else MUTED, 4))
                elif costs:
                    g.add(edge(pts[i], pts[j], KILL, 3, dashed=True))
                if costs:
                    mid = (pts[i] + pts[j]) / 2
                    off = UP * 0.25 if have and abs(pts[i][1] - pts[j][1]) < 0.1 else (RIGHT * 0.28 if have else RIGHT * 0.0)
                    labels.add(label("1" if have else "2", 22, SAFE if have else KILL, "BOLD").move_to(mid + off))
        nodes = VGroup(*[node(p, f"H{k + 1}", 0.32, TEXT, PANEL, 18) for k, p in enumerate(pts)])
        out = VGroup(g, labels, nodes)
        out.pts, out.edges, out.nodes = pts, g, nodes
        return out

    def b_r1_problems(self, b):
        self.clear(run_time=0.4)
        hc = titled_card("HAMILTONIAN CYCLE", ACCENT, ["a delivery van: every house once,", "back home, only on existing roads"], 6.3, 1.7)
        hc.move_to(STAGE + LEFT * 3.3 + UP * 2.0)
        self.show(hc, run_time=0.6)
        g = self.van_graph(STAGE + LEFT * 3.3 + DOWN * 1.0)
        self.show(g, run_time=0.6)
        van = label("🚚", 36).move_to(g.pts[0] + LEFT * 0.7 + UP * 0.1) if False else VGroup()
        self.at(b, 1)
        tsp = titled_card("TSP  (decision)", KILL, ["with road costs,", "is there a tour of cost ≤ k ?"], 6.3, 1.7)
        tsp.move_to(STAGE + RIGHT * 3.3 + UP * 2.0)
        self.show(tsp, run_time=0.6)
        self.sfx("pop")
        arr = big_arrow(hc.get_right(), tsp.get_left(), GOLD, 8)
        self.show(arr, anim=GrowArrow, run_time=0.5)
        self.r1_hc, self.r1_tsp = hc, tsp

    def b_r1_build(self, b):
        self.clear(run_time=0.4)
        head = chip("THE TRANSLATION", GOLD, 28, DARK).move_to(STAGE + UP * 2.5)
        self.show(head, run_time=0.4)
        g = self.van_graph(STAGE + LEFT * 3.2 + DOWN * 0.3, 1.6, costs=True)
        self.show(g.nodes, run_time=0.4)
        self.stage.add(g.edges, g[1])
        self.go(LaggedStart(*[Create(e) for e in g.edges], lag_ratio=0.15), FadeIn(g[1]), run_time=1.4)
        self.sfx("pop")
        rules = VGroup(chip("road exists  →  cost 1", SAFE, 26), chip("no road  →  cost 2", KILL, 26)).arrange(DOWN, buff=0.3)
        rules.move_to(STAGE + RIGHT * 3.2 + UP * 0.9)
        self.stage.add(rules)
        self.go(LaggedStart(*[FadeIn(r, shift=LEFT * 0.3) for r in rules], lag_ratio=0.5), run_time=1.0)
        self.at(b, 1)
        k = chip("k  =  n  =  4", GOLD, 34, DARK).move_to(STAGE + RIGHT * 3.2 + DOWN * 1.0)
        self.show(k, anim=GrowFromCenter, run_time=0.5)
        self.sfx("chime")
        self.r1_graph = g

    def b_r1_why(self, b):
        g = self.r1_graph
        tour = VGroup(*[Line(g.pts[i], g.pts[(i + 1) % 4], color=GOLD, stroke_width=10, buff=0.32) for i in range(4)])
        for t in tour:
            t.set_z_index(-0.5)
        self.stage.add(tour)
        self.go(LaggedStart(*[Create(t) for t in tour], lag_ratio=0.3), run_time=1.2)
        self.sfx("place")
        c1 = VGroup(label("cost ≤ n  ⇒  n roads of cost 1", 24, TEXT), label("⇒  a Hamiltonian cycle", 24, SAFE, "BOLD")).arrange(DOWN, buff=0.08)
        c1.move_to(STAGE + RIGHT * 3.2 + DOWN * 1.9)
        self.show(c1, run_time=0.5)
        self.at(b, 1)
        c2 = VGroup(label("Hamiltonian cycle  ⇒  tour of cost exactly n", 24, TEXT), label("yes  ⇔  yes", 28, GOLD, "BOLD")).arrange(DOWN, buff=0.08)
        c2.move_to(STAGE + RIGHT * 3.2 + DOWN * 2.9)
        self.show(c2, run_time=0.5)
        self.sfx("chime")
        self.r1_cost = chip("tour cost 1+1+1+1 = 4 = n", GOLD, 22, DARK).next_to(g, DOWN, buff=0.3)
        self.show(self.r1_cost, run_time=0.4)

    def b_r1_time(self, b):
        self.clear(run_time=0.4)
        c = chip("the translation lists n² pairs: polynomial", SAFE, 28).move_to(STAGE + UP * 1.5)
        self.show(c, run_time=0.5)
        self.at(b, 1)
        st = VGroup(chip("Hamiltonian cycle", ACCENT, 30), label("∝", 44, GOLD, "BOLD"), chip("TSP", KILL, 30)).arrange(RIGHT, buff=0.5)
        st.move_to(STAGE + UP * 0.2)
        self.show(st, anim=GrowFromCenter, run_time=0.5)
        self.sfx("whoosh")
        res = VGroup(label("Hamiltonian cycle is NP-hard", 26, TEXT), label("⇒  TSP is NP-hard", 32, KILL, "BOLD")).arrange(DOWN, buff=0.1)
        res.move_to(STAGE + DOWN * 1.5)
        self.show(res, run_time=0.5)
        self.sfx("chime")

    # ------------------------------------------------------------ reduction 2: IS <-> VC
    def penta(self, center, r=1.5, names=None):
        pts = ring(center, r, 5)
        es = VGroup(*[edge(pts[i], pts[j], MUTED, 4, buff=0.34) for i, j in PENTA_EDGES])
        nodes = VGroup(*[node(p, names[k] if names else str(k + 1), 0.34, TEXT, PANEL, 17 if names else 20) for k, p in enumerate(pts)])
        out = VGroup(es, nodes)
        out.pts, out.edges, out.nodes = pts, es, nodes
        return out

    def b_r2_problems(self, b):
        self.clear(run_time=0.4)
        g = self.penta(STAGE + DOWN * 0.5, 1.6, GUESTS)
        self.show(g, run_time=0.7)
        is_ = titled_card("INDEPENDENT SET", SAFE, ["invite k guests,", "no two of them dislike each other"], 5.4, 1.7)
        is_.move_to(STAGE + LEFT * 4.1 + UP * 1.9)
        self.show(is_, run_time=0.6)
        self.sfx("pop")
        k1 = label("edge = dislike", 20, MUTED).next_to(g, DOWN, buff=0.3)
        self.show(k1, run_time=0.3)
        self.at(b, 1)
        vc = titled_card("VERTEX COVER", KILL, ["place k guards at junctions,", "every street has one at an end"], 5.4, 1.7)
        vc.move_to(STAGE + RIGHT * 4.1 + UP * 1.9)
        self.show(vc, run_time=0.6)
        self.sfx("pop")
        k2 = label("or: edge = street, node = junction", 20, MUTED).next_to(k1, DOWN, buff=0.1)
        self.show(k2, run_time=0.3)
        self.r2_graph = g

    def b_r2_build(self, b):
        self.clear(self.r2_graph, run_time=0.4)
        g = self.r2_graph
        self.go(g.animate.move_to(STAGE + LEFT * 3.4 + DOWN * 0.2), run_time=0.5)
        same = chip("same graph for both", GOLD, 26, DARK).move_to(STAGE + RIGHT * 3.0 + UP * 2.0)
        self.show(same, run_time=0.4)
        self.at(b, 1)
        q1 = chip("can you invite k guests ?", SAFE, 26).move_to(STAGE + RIGHT * 3.0 + UP * 0.8)
        q2 = chip("can n − k guards cover every street ?", KILL, 26).move_to(STAGE + RIGHT * 3.0 + DOWN * 0.6)
        arr = big_arrow(q1.get_bottom(), q2.get_top(), GOLD, 6)
        self.show(q1, run_time=0.4)
        self.show(arr, anim=GrowArrow, run_time=0.3)
        self.show(q2, run_time=0.4)
        self.sfx("pop")
        ex = chip("here: k = 2 guests  ⇔  5 − 2 = 3 guards", PANEL_EDGE, 22).move_to(STAGE + RIGHT * 3.0 + DOWN * 1.8)
        self.show(ex, run_time=0.4)

    def b_r2_why(self, b):
        g = self.r2_graph
        party, guards = [0, 2], [1, 3, 4]
        self.go(*[g.nodes[i][0].animate.set_fill(SAFE).set_stroke(SAFE) for i in party],
                *[g.nodes[i][1].animate.set_color(DARK) for i in party], run_time=0.6)
        self.sfx("place")
        self.go(*[g.nodes[i][0].animate.set_fill(KILL).set_stroke(KILL) for i in guards],
                *[g.nodes[i][1].animate.set_color(DARK) for i in guards], run_time=0.6)
        self.sfx("place")
        leg = VGroup(chip("party", SAFE, 20), chip("guards", KILL, 20)).arrange(RIGHT, buff=0.3).next_to(g, DOWN, buff=0.3)
        self.show(leg, run_time=0.3)
        self.at(b, 1)
        self.go(*[e.animate.set_color(KILL) for e in g.edges], run_time=0.6)
        c = VGroup(label("no dislike inside the party", 24, SAFE, "BOLD"), label("⇔  every dislike touches someone outside", 24, KILL, "BOLD"),
                   label("complement the set, flip the number", 24, GOLD)).arrange(DOWN, buff=0.12).move_to(STAGE + RIGHT * 3.0 + DOWN * 2.95)
        self.show(c, run_time=0.6)
        self.sfx("chime")

    def b_r2_lesson(self, b):
        self.clear(run_time=0.4)
        c = chip("a reduction can be almost trivial", GOLD, 30, DARK).move_to(STAGE + UP * 1.6)
        self.show(c, anim=GrowFromCenter, run_time=0.5)
        self.at(b, 1)
        r1 = VGroup(chip("Independent set", SAFE, 28), label("∝", 40, GOLD, "BOLD"), chip("Vertex cover", KILL, 28)).arrange(RIGHT, buff=0.4)
        r2 = VGroup(chip("Vertex cover", KILL, 28), label("∝", 40, GOLD, "BOLD"), chip("Independent set", SAFE, 28)).arrange(RIGHT, buff=0.4)
        rows = VGroup(r1, r2).arrange(DOWN, buff=0.4).move_to(STAGE + UP * 0.0)
        self.stage.add(rows)
        self.go(LaggedStart(FadeIn(r1), FadeIn(r2), lag_ratio=0.5), run_time=1.0)
        self.sfx("pop")
        eq = label("equally hard", 32, TEXT, "BOLD").move_to(STAGE + DOWN * 1.7)
        self.show(eq, run_time=0.4)

    # ------------------------------------------------------------ reduction 3: subset sum -> knapsack
    def b_r3_problems(self, b):
        self.clear(run_time=0.4)
        ss = titled_card("SUBSET SUM", ACCENT, ["can you pay exactly ₹500", "with these notes, no change?"], 6.0, 1.7)
        ss.move_to(STAGE + LEFT * 3.3 + UP * 2.0)
        self.show(ss, run_time=0.6)
        notes = VGroup(*[chip(f"₹{v}", GOLD, 22, DARK) for v in NOTES]).arrange(RIGHT, buff=0.15).next_to(ss, DOWN, buff=0.5)
        notes.set_x(STAGE[0] - 2.2)
        self.stage.add(notes)
        self.go(LaggedStart(*[GrowFromCenter(n) for n in notes], lag_ratio=0.2), run_time=1.2)
        self.sfx("pop")
        self.at(b, 1)
        kp = titled_card("DECISION KNAPSACK", KILL, ["is there a packing with", "weight ≤ m  and  profit ≥ r ?"], 6.0, 1.7)
        kp.move_to(STAGE + RIGHT * 3.3 + UP * 2.0)
        self.show(kp, run_time=0.6)
        arr = big_arrow(ss.get_right(), kp.get_left(), GOLD, 8)
        self.show(arr, anim=GrowArrow, run_time=0.5)
        self.r3_notes = notes

    def b_r3_build(self, b):
        self.clear(run_time=0.4)
        head = chip("THE TRANSLATION", GOLD, 28, DARK).move_to(STAGE + UP * 2.5)
        self.show(head, run_time=0.4)
        rows = [["note", "weight w", "profit p"]] + [[f"₹{v}", str(v), str(v)] for v in NOTES]
        grid = VGroup()
        for r, row in enumerate(rows):
            line = VGroup(*[label(t, 22, MUTED if r == 0 else TEXT, "BOLD" if r == 0 else "NORMAL") for t in row])
            for j, t in enumerate(line):
                t.move_to(np.array([j * 1.7, -r * 0.48, 0]))
            grid.add(line)
        box = card(grid.width + 0.8, grid.height + 0.5)
        self.r3_table = VGroup(box, grid.move_to(box)).move_to(STAGE + LEFT * 3.0 + DOWN * 0.4)
        self.show(self.r3_table, run_time=0.6)
        self.r3_grid = grid
        rule = chip("weight = profit = value of the note", ACCENT, 24).move_to(STAGE + RIGHT * 3.3 + UP * 0.9)
        self.show(rule, run_time=0.5)
        self.sfx("pop")
        self.at(b, 1)
        mr = chip("m = 500,   r = 500", GOLD, 34, DARK).move_to(STAGE + RIGHT * 3.3 + DOWN * 0.6)
        self.show(mr, anim=GrowFromCenter, run_time=0.5)
        self.sfx("chime")

    def b_r3_why(self, b):
        pick = [1, 2, 3]                                        # rows 200, 200, 100 (1-based rows after the header)
        hl = VGroup(*[SurroundingRectangle(self.r3_grid[i], color=SAFE, buff=0.08, stroke_width=3) for i in (2, 3, 1)])
        self.show(hl, anim=Create, run_time=0.6)
        self.sfx("place")
        s = chip("200 + 200 + 100 = 500", SAFE, 22).next_to(self.r3_table, DOWN, buff=0.25)
        self.show(s, run_time=0.4)
        why = VGroup(label("weight ≤ 500  and  profit ≥ 500", 24, TEXT), label("⇒  total exactly 500", 26, GOLD, "BOLD"),
                     label("yes  ⇔  yes", 26, SAFE, "BOLD")).arrange(DOWN, buff=0.1).move_to(STAGE + RIGHT * 3.3 + DOWN * 2.0)
        self.show(why, run_time=0.5)
        self.at(b, 1)
        self.clear(run_time=0.4)
        c = chip("copies n numbers: linear time", SAFE, 28).move_to(STAGE + UP * 1.5)
        self.show(c, run_time=0.5)
        st = VGroup(chip("Subset sum", ACCENT, 30), label("∝", 44, GOLD, "BOLD"), chip("Knapsack", KILL, 30)).arrange(RIGHT, buff=0.5)
        st.move_to(STAGE + UP * 0.2)
        self.show(st, anim=GrowFromCenter, run_time=0.5)
        self.sfx("whoosh")
        res = label("knapsack is at least as hard as subset sum", 28, KILL, "BOLD").move_to(STAGE + DOWN * 1.3)
        self.show(res, run_time=0.5)

    # ------------------------------------------------------------ proving NP-hardness
    def b_c_chain(self, b):
        self.clear(run_time=0.4)
        head = label("REDUCTIONS CHAIN", 34, GOLD, "BOLD").move_to(STAGE + UP * 2.3)
        self.show(head, anim=GrowFromCenter, run_time=0.4)
        ch = flow([chip("A", ACCENT, 36), chip("B", PURPLE, 36), chip("C", KILL, 36)], buff=1.2, color=GOLD).move_to(STAGE + UP * 0.8)
        self.show(ch, run_time=0.8)
        self.sfx("pop")
        long = CurvedArrow(ch[0][0].get_bottom() + DOWN * 0.1, ch[0][2].get_bottom() + DOWN * 0.1, angle=1.0, color=SAFE, stroke_width=5)
        lab = chip("A ∝ C : translate twice, still polynomial", SAFE, 24).move_to(STAGE + DOWN * 1.2)
        self.show(long, lab, run_time=0.6)
        self.at(b, 1)
        root = chip("so one root is enough:  SAT", KILL, 28).move_to(STAGE + DOWN * 2.3)
        self.show(root, anim=GrowFromCenter, run_time=0.5)
        self.sfx("chime")

    def b_c_tree(self, b):
        self.clear(run_time=0.4)
        P = {"SAT": (-5.6, 1.4), "3-SAT": (-3.2, 1.4), "Clique": (-0.4, 2.4), "Vertex cover": (2.4, 2.4), "Independent set": (5.3, 2.4),
             "Hamiltonian cycle": (0.3, 0.6), "TSP": (3.6, 0.6), "Subset sum": (0.0, -1.2), "Knapsack": (3.2, -1.2)}
        C = {"SAT": KILL, "3-SAT": KILL}
        nodes = {k: chip(k, C.get(k, PURPLE), 22) .move_to(STAGE + np.array([x, y, 0])) for k, (x, y) in P.items()}
        E = [("SAT", "3-SAT"), ("3-SAT", "Clique"), ("Clique", "Vertex cover"), ("Vertex cover", "Independent set"),
             ("3-SAT", "Hamiltonian cycle"), ("Hamiltonian cycle", "TSP"), ("3-SAT", "Subset sum"), ("Subset sum", "Knapsack")]
        arrows = {e: Arrow(nodes[e[0]].get_right() if abs(P[e[0]][1] - P[e[1]][1]) < 0.1 else nodes[e[0]].get_center(),
                           nodes[e[1]].get_left(), buff=0.12, color=GOLD, stroke_width=4, max_tip_length_to_length_ratio=0.2) for e in E}
        for a in arrows.values():
            a.set_z_index(-1)
        order1 = [("SAT", None), ("3-SAT", ("SAT", "3-SAT")), ("Clique", ("3-SAT", "Clique")), ("Vertex cover", ("Clique", "Vertex cover")),
                  ("Independent set", ("Vertex cover", "Independent set"))]
        order2 = [("Hamiltonian cycle", ("3-SAT", "Hamiltonian cycle")), ("TSP", ("Hamiltonian cycle", "TSP")),
                  ("Subset sum", ("3-SAT", "Subset sum")), ("Knapsack", ("Subset sum", "Knapsack"))]
        for k, e in order1:
            anims = [FadeIn(nodes[k])] + ([GrowArrow(arrows[e])] if e else [])
            self.stage.add(nodes[k], *([arrows[e]] if e else []))
            self.go(*anims, run_time=0.4)
        self.sfx("pop")
        self.at(b, 1)
        for k, e in order2:
            self.stage.add(nodes[k], arrows[e])
            self.go(FadeIn(nodes[k]), GrowArrow(arrows[e]), run_time=0.4)
        self.sfx("pop")
        note = label("a family tree of hardness: every branch is one reduction", 24, MUTED).move_to(STAGE + DOWN * 2.6)
        self.show(note, run_time=0.5)

    def b_c_recipe(self, b):
        self.clear(run_time=0.4)
        head = label("RECIPE: PROVE X IS NP-HARD", 32, GOLD, "BOLD").move_to(STAGE + UP * 2.4)
        self.show(head, anim=GrowFromCenter, run_time=0.4)
        steps = ["pick a known NP-hard problem  H", "give the translation  H-instance → X-instance",
                 "show  yes → yes  and  no → no", "show the translation is polynomial time"]
        rows = VGroup(*[VGroup(chip(str(i + 1), GOLD, 24, DARK), label(t, 26, TEXT)).arrange(RIGHT, buff=0.35) for i, t in enumerate(steps)])
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(STAGE + UP * 0.5)
        self.stage.add(rows)
        span = self.phrase_len(b, 0)
        for i, r in enumerate(rows):
            self.until(b["phrases"][0]["start"] + span * (0.25 + 0.18 * i))
            self.go(FadeIn(r, shift=RIGHT * 0.3), run_time=0.4)
            self.sfx("pop", -0.2)
        self.at(b, 1)
        plus = chip("+  X ∈ NP   ⇒   X is NP-complete", PURPLE, 28).move_to(STAGE + DOWN * 2.0)
        self.show(plus, anim=GrowFromCenter, run_time=0.5)
        self.sfx("chime")

    def b_c_use(self, b):
        self.clear(run_time=0.4)
        head = label("REDUCTIONS ALSO WORK FOR YOU", 32, GOLD, "BOLD").move_to(STAGE + UP * 2.2)
        self.show(head, anim=GrowFromCenter, run_time=0.4)
        q = chip("a new rostering problem at a company", ACCENT, 26).move_to(STAGE + UP * 0.9)
        self.show(q, run_time=0.5)
        self.at(b, 1)
        fl = flow([chip("translate", GOLD, 26, DARK), chip("SAT / integer-programming solver", SAFE, 26), chip("answer", PURPLE, 26)])
        fl.move_to(STAGE + DOWN * 0.4)
        self.stage.add(fl)
        self.go(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in fl[0]], lag_ratio=0.4), FadeIn(fl[1]), run_time=1.3)
        self.sfx("pop")
        m = label("translate, then reuse", 30, TEXT, "BOLD").move_to(STAGE + DOWN * 1.8)
        self.show(m, run_time=0.4)

    # ------------------------------------------------------------ practice, tips, recap
    def b_p_intro(self, b):
        self.question_card(b, ["k charging stations at junctions, so that", "every street has one at an end.", "Which problem is this?  How hard?"])

    def b_p_pause(self, b):
        self.pause_screen(b, "Pause and think")

    def b_p_answer(self, b):
        self.pause_over()
        self.clear(run_time=0.4)
        g = self.penta(STAGE + LEFT * 4.2 + DOWN * 0.2, 1.4)
        self.show(g, run_time=0.5)
        self.go(*[g.nodes[i][0].animate.set_fill(KILL).set_stroke(KILL) for i in (1, 3, 4)],
                *[g.nodes[i][1].animate.set_color(DARK) for i in (1, 3, 4)], run_time=0.5)
        maps = VGroup(flow([chip("junctions", PANEL_EDGE, 22), chip("vertices", ACCENT, 22)]),
                      flow([chip("streets", PANEL_EDGE, 22), chip("edges", ACCENT, 22)]),
                      flow([chip("stations", PANEL_EDGE, 22), chip("the cover", KILL, 22)])).arrange(DOWN, buff=0.25, aligned_edge=LEFT)
        maps.move_to(STAGE + RIGHT * 2.6 + UP * 1.5)
        self.stage.add(maps)
        self.go(LaggedStart(*[FadeIn(m, shift=RIGHT * 0.2) for m in maps], lag_ratio=0.3), run_time=1.0)
        name = chip("VERTEX COVER", KILL, 34).move_to(STAGE + RIGHT * 2.6 + DOWN * 0.5)
        self.show(name, anim=GrowFromCenter, run_time=0.5)
        self.sfx("chime")
        self.at(b, 1)
        res = VGroup(label("NP-complete: no polynomial algorithm is known", 24, TEXT),
                     label("for a real city: an approximation, or a solver", 24, SAFE, "BOLD")).arrange(DOWN, buff=0.1)
        res.move_to(STAGE + RIGHT * 2.6 + DOWN * 1.8)
        self.show(res, run_time=0.5)

    def b_tip1(self, b):
        self.tip(b, 1, "Direction first: KNOWN HARD ∝ NEW", "then the 4 steps: translation · yes→yes · no→no · polynomial")

    def b_tip2(self, b):
        self.tip(b, 2, "Learn two reductions by heart", "HC ∝ TSP (costs 1 / 2, k = n)  ·  IS ∝ VC (n − k)")

    def b_tip3(self, b):
        self.tip(b, 3, "Never write  'X ∝ SAT, so X is NP-hard'", "that direction proves nothing; you need  SAT ∝ X")

    def b_recap(self, b):
        self.recap(b, ["A reduction translates A into B, polynomial, answer preserved",
                       "A ∝ B  ⇒  B is at least as hard",
                       "To prove X hard: reduce a known hard problem to X",
                       "Reductions chain from SAT to everything"])
