"""Video 4.5 - Approximation Algorithms & Applications. Rendered by build.py (needs SCHEDULE / ENVELOPE env vars)."""
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from lesson import *  # noqa: E402,F401,F403

PURPLE = UNIT_COLORS["IV"]
DARK = "#0F172A"
VC_EDGES = [(1, 2), (2, 3), (3, 4), (3, 5), (4, 5), (4, 6), (4, 7), (5, 6)]
VC_POS = {1: (-3.0, 1.2), 2: (-1.5, 1.2), 3: (0.0, 1.2), 4: (1.5, 1.2), 5: (0.75, -0.3), 6: (2.25, -0.3), 7: (3.0, 1.2)}
CITY = {"A": (0, 0), "B": (4, 0), "C": (4, 3), "D": (0, 3), "E": (2, 5)}
MST_EDGES = [("A", "D"), ("D", "E"), ("E", "C"), ("C", "B")]
TOUR = ["A", "D", "E", "C", "B"]


def node(pos, text, r=0.3, color=TEXT, fill=PANEL, size=20, text_color=TEXT):
    return VGroup(Circle(r, color=color, fill_color=fill, fill_opacity=1, stroke_width=3).move_to(pos),
                  label(text, size, text_color, "BOLD").move_to(pos))


def edge(a, b, color=MUTED, width=4, buff=0.32):
    ln = Line(a, b, color=color, stroke_width=width, buff=buff)
    ln.set_z_index(-1)
    return ln


def titled_card(title, color, lines, w, h, title_size=26, line_size=21, line_color=TEXT):
    body = VGroup(label(title, title_size, color, "BOLD"), *[label(t, line_size, line_color) for t in lines]).arrange(DOWN, buff=0.12)
    if body.width > w - 0.3:
        body.scale_to_fit_width(w - 0.3)
    box = card(w, h, edge=color)
    return VGroup(box, body.move_to(box))


def chips(items, color, size=22, buff=0.25):
    return VGroup(*[chip(t, color, size, DARK if color in (GOLD, SAFE) else TEXT) for t in items]).arrange(RIGHT, buff=buff)


def paint(nodes, idx, color):
    return [a for i in idx for a in (nodes[i][0].animate.set_fill(color).set_stroke(color), nodes[i][1].animate.set_color(DARK))]


class Video(Lesson):
    NEXT = ("5.1  Network flow", "& the max-flow min-cut theorem")

    def screen(self, head_text, color, sub=None):
        self.clear(run_time=0.4)
        head = chip(head_text, color, 26, DARK if color in (GOLD, SAFE) else TEXT).move_to(STAGE + UP * 2.55)
        self.show(head, anim=GrowFromCenter, run_time=0.5)
        self.sfx("pop")
        if sub:
            t = label(sub, 28, TEXT, "BOLD").move_to(STAGE + UP * 1.8)
            if t.width > 13.0:
                t.scale_to_fit_width(13.0)
            self.show(t, run_time=0.4)
        return head

    def punch(self, text, color=GOLD, size=28, y=-2.4):
        c = chip(text, color, size, DARK if color in (GOLD, SAFE) else TEXT).move_to(STAGE + UP * y)
        if c.width > 13.2:
            c.scale_to_fit_width(13.2)
        self.show(c, anim=GrowFromCenter, run_time=0.5)
        self.sfx("chime")
        return c

    # ------------------------------------------------------------ graphs
    def vc_graph(self, center, scale=1.0, size=20):
        pts = {k: center + np.array([x * scale, y * scale, 0]) for k, (x, y) in VC_POS.items()}
        es = VGroup(*[edge(pts[a], pts[b], MUTED, 4, 0.32 * scale) for a, b in VC_EDGES])
        nodes = VGroup(*[node(pts[k], str(k), 0.3 * scale, TEXT, PANEL, size) for k in sorted(pts)])
        g = VGroup(es, nodes)
        g.pts, g.edges, g.nodes = pts, es, nodes
        return g

    def city_map(self, center, scale=0.6):
        pts = {k: center + np.array([(x - 2) * scale, (y - 2.5) * scale, 0]) for k, (x, y) in CITY.items()}
        nodes = VGroup(*[node(pts[k], k, 0.3, TEXT, PANEL, 20) for k in CITY])
        g = VGroup(nodes)
        g.pts, g.nodes = pts, nodes
        return g

    # ------------------------------------------------------------ hook
    def b_hook_vans(self, b):
        rng = np.random.RandomState(7)
        pts = [STAGE + LEFT * 3.0 + np.array([rng.uniform(-3.0, 3.0), rng.uniform(-2.0, 2.0), 0]) for _ in range(40)]
        dots = VGroup(*[Dot(p, radius=0.07, color=ACCENT) for p in pts])
        self.show(dots, run_time=0.8)
        van = chip("200 cities, tomorrow", GOLD, 28, DARK).move_to(STAGE + RIGHT * 3.6 + UP * 1.4)
        self.show(van, run_time=0.5)
        hard = VGroup(label("exact best route: NP-hard", 26, KILL, "BOLD"), label("no computer finds it in time", 22, MUTED)).arrange(DOWN, buff=0.1)
        hard.move_to(STAGE + RIGHT * 3.6 + UP * 0.2)
        self.show(hard, run_time=0.5)
        self.at(b, 1)
        q = VGroup(label("yet the vans leave at 8 a.m.", 26, TEXT), label("with a route.  How?", 32, GOLD, "BOLD")).arrange(DOWN, buff=0.1)
        q.move_to(STAGE + RIGHT * 3.6 + DOWN * 1.4)
        self.show(q, run_time=0.5)
        self.sfx("pop")
        self.hook_dots = dots

    def b_hook_idea(self, b):
        self.clear(self.hook_dots, run_time=0.4)
        pts = [d.get_center() for d in self.hook_dots]
        order = sorted(range(len(pts)), key=lambda i: math.atan2(pts[i][1] - (STAGE + LEFT * 3.0)[1], pts[i][0] - (STAGE + LEFT * 3.0)[0]))
        path = VGroup(*[Line(pts[order[i]], pts[order[(i + 1) % len(order)]], color=SAFE, stroke_width=3) for i in range(len(order))])
        self.stage.add(path)
        self.go(Create(path), run_time=1.6)
        self.sfx("place")
        g = VGroup(label("not the best route", 26, MUTED), label("at most 2 × the best", 40, SAFE, "BOLD"), label("in seconds", 26, TEXT)).arrange(DOWN, buff=0.15)
        g.move_to(STAGE + RIGHT * 3.6 + UP * 0.8)
        self.show(g, run_time=0.6)
        self.at(b, 1)
        t = chip("APPROXIMATION ALGORITHM", GOLD, 30, DARK).move_to(STAGE + RIGHT * 3.6 + DOWN * 1.2)
        self.show(t, anim=GrowFromCenter, run_time=0.5)
        self.sfx("chime")
        n = label("how the real world handles NP-hard problems", 22, MUTED).move_to(STAGE + RIGHT * 3.6 + DOWN * 2.1)
        self.show(n, run_time=0.4)

    def b_hook_promise(self, b):
        self.clear(run_time=0.4)
        rows = VGroup(*[VGroup(chip(str(i + 1), ACCENT, 26), label(t, 32, TEXT, "BOLD")).arrange(RIGHT, buff=0.3) for i, t in enumerate(
            ["The approximation ratio", "Vertex cover: a 2-approximation with proof", "TSP: a 2-approximation with proof", "NP-hardness in AI, big data and cryptography"])])
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(STAGE + UP * 0.2)
        self.stage.add(rows)
        self.go(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.3) for r in rows[:3]], lag_ratio=0.4), run_time=1.4)
        self.at(b, 1)
        self.go(FadeIn(rows[3], shift=RIGHT * 0.3), run_time=0.5)
        self.sfx("pop")

    def b_syllabus(self, b):
        self.syllabus(b, ["Approximation ratios", "Vertex cover: 2 for 1", "TSP: 2 for 1 from a spanning tree", "AI, big data, cryptography"],
                      unit_text="UNIT IV  ·  COMPLEXITY")

    def b_exam(self, b):
        self.exam_star(b)

    # ------------------------------------------------------------ ratio
    def b_r_def(self, b):
        self.unsay()
        self.screen("APPROXIMATION ALGORITHM", GOLD)
        c = titled_card("polynomial time  +  a guarantee", SAFE, ["returns a solution close to optimal", "and promises how close"], 8.0, 1.9, 28, 24).move_to(STAGE + UP * 1.0)
        self.show(c, run_time=0.6)
        self.at(b, 1)
        f = VGroup(label("ratio  ρ  =", 36, TEXT, "BOLD"), VGroup(label("cost of our answer", 26, GOLD, "BOLD"), Line(LEFT * 1.8, RIGHT * 1.8, color=TEXT, stroke_width=3),
                   label("optimal cost", 26, SAFE, "BOLD")).arrange(DOWN, buff=0.12)).arrange(RIGHT, buff=0.4).move_to(STAGE + DOWN * 0.9)
        self.show(f, run_time=0.6)
        self.sfx("pop")
        two = chip("a 2-approximation never costs more than twice the optimum", ACCENT, 24).move_to(STAGE + DOWN * 2.5)
        self.show(two, run_time=0.5)

    def b_r_why(self, b):
        self.screen("WHY ACCEPT THIS?", GOLD)
        l = titled_card("exact", KILL, ["exponential time", "optimal … never"], 5.2, 2.2, 32, 26)
        r = titled_card("approximate", SAFE, ["polynomial time", "twice optimal … in one second"], 5.2, 2.2, 32, 26)
        VGroup(l, r).arrange(RIGHT, buff=0.8).move_to(STAGE + UP * 0.6)
        self.show(l, run_time=0.5)
        self.at(b, 1)
        self.show(r, run_time=0.5)
        self.sfx("chime")
        n = label("in practice the answers are usually far closer than the guarantee", 24, MUTED).move_to(STAGE + DOWN * 1.5)
        self.show(n, run_time=0.5)

    def b_r_terms(self, b):
        self.screen("THREE TERMS", GOLD)
        rows = VGroup(VGroup(chip("ρ", GOLD, 30, DARK), label("the approximation ratio, always ≥ 1", 28, TEXT)).arrange(RIGHT, buff=0.4),
                      VGroup(chip("ρ-approximation algorithm", GOLD, 24, DARK), label("polynomial, within ρ of optimal, always", 28, TEXT)).arrange(RIGHT, buff=0.4),
                      VGroup(chip("PTAS", GOLD, 24, DARK), label("within 1 + ε for any ε you choose; slower as ε shrinks", 28, TEXT)).arrange(RIGHT, buff=0.4)
                      ).arrange(DOWN, aligned_edge=LEFT, buff=0.5).move_to(STAGE + UP * 0.2)
        if rows.width > 13.0:
            rows.scale_to_fit_width(13.0)
        self.stage.add(rows)
        self.go(LaggedStart(FadeIn(rows[0], shift=RIGHT * 0.3), FadeIn(rows[1], shift=RIGHT * 0.3), lag_ratio=0.5), run_time=1.2)
        self.at(b, 1)
        self.go(FadeIn(rows[2], shift=RIGHT * 0.3), run_time=0.5)
        self.sfx("pop")

    # ------------------------------------------------------------ vertex cover
    def b_v_problem(self, b):
        self.screen("VERTEX COVER", ACCENT)
        g = self.vc_graph(STAGE + LEFT * 2.6 + DOWN * 0.3, 1.0)
        self.show(g, run_time=0.7)
        d = VGroup(label("smallest set of vertices", 26, TEXT), label("that touches every edge", 26, TEXT, "BOLD")).arrange(DOWN, buff=0.1).move_to(STAGE + RIGHT * 3.8 + UP * 0.8)
        self.show(d, run_time=0.5)
        self.at(b, 1)
        h = chip("NP-hard exactly  (video 4.4)", KILL, 24).move_to(STAGE + RIGHT * 3.8 + DOWN * 0.8)
        self.show(h, run_time=0.5)
        self.vc = g

    def b_v_algo(self, b):
        self.clear(self.vc, run_time=0.4)
        self.screen("APPROX-VERTEX-COVER", ACCENT)
        self.go(self.vc.animate.move_to(STAGE + LEFT * 3.0 + DOWN * 0.5), run_time=0.4)
        code = CodePanel(["C := {}",
                          "while edges remain:",
                          "  pick any edge (u, v)",
                          "  C := C + {u, v}",
                          "  delete every edge touching u or v",
                          "return C"], font_size=22).move_to(STAGE + RIGHT * 3.4 + DOWN * 0.2)
        self.show(code, run_time=0.6)
        self.go(code.highlight(2))
        self.at(b, 1)
        self.go(code.highlight(4))
        self.code = code

    def b_v_trace(self, b):
        g = self.vc
        steps = [((2, 3), [(1, 2), (2, 3), (3, 4), (3, 5)]), ((5, 6), [(4, 5), (4, 6), (5, 6)]), ((4, 7), [(4, 7)])]
        idx = {e: i for i, e in enumerate(VC_EDGES)}
        picks = VGroup()
        for n, ((u, v), gone) in enumerate(steps):
            if n == 2:
                self.at(b, 1)
            else:
                self.until(b["phrases"][0]["start"] + self.phrase_len(b, 0) * (0.05 + 0.5 * n))
            pe = g.edges[idx[(u, v)]]
            self.go(pe.animate.set_color(GOLD).set_stroke(width=9), run_time=0.4)
            self.go(*paint(g.nodes, [u - 1, v - 1], GOLD), run_time=0.4)
            self.sfx("place")
            self.go(*[g.edges[idx[e]].animate.set_opacity(0.12) for e in gone if e != (u, v)], pe.animate.set_opacity(0.35), run_time=0.5)
            picks.add(chip(f"({u},{v})", GOLD, 22, DARK))
        picks.arrange(RIGHT, buff=0.2).move_to(STAGE + RIGHT * 3.4 + DOWN * 1.9)
        self.show(picks, run_time=0.4)
        res = chip("cover = {2, 3, 4, 5, 6, 7}:  size 6", ACCENT, 24).move_to(STAGE + RIGHT * 3.4 + DOWN * 2.7)
        self.show(res, anim=GrowFromCenter, run_time=0.5)
        self.sfx("chime")
        self.picks = picks

    def b_v_proof(self, b):
        self.clear(run_time=0.4)
        self.screen("THE PROOF, IN TWO LINES", ACCENT)
        l1 = titled_card("picked edges share no vertex  ⇒  a matching of size k", SAFE,
                         ["every cover needs an endpoint of each picked edge", "so  OPT  ≥  k"], 10.5, 1.9, 26, 24).move_to(STAGE + UP * 0.9)
        self.show(l1, run_time=0.6)
        self.sfx("pop")
        self.at(b, 1)
        l2 = titled_card("we used exactly  2k  vertices", GOLD, ["|C|  =  2k  ≤  2 · OPT"], 10.5, 1.6, 26, 28).move_to(STAGE + DOWN * 1.2)
        self.show(l2, run_time=0.6)
        self.sfx("chime")
        self.punch("a 2-approximation", GOLD, 30, -2.75)

    def b_v_tight(self, b):
        self.screen("THE BOUND IS TIGHT", ACCENT)
        g = self.vc_graph(STAGE + LEFT * 2.8 + DOWN * 0.5, 1.0)
        self.show(g, run_time=0.5)
        self.go(*paint(g.nodes, [1, 2, 3, 4, 5, 6], GOLD), run_time=0.6)
        ours = chip("ours: 3 edges  →  6 vertices", GOLD, 24, DARK).move_to(STAGE + RIGHT * 3.6 + UP * 0.9)
        self.show(ours, run_time=0.4)
        self.at(b, 1)
        self.go(*[g.nodes[i][0].animate.set_fill(PANEL).set_stroke(TEXT) for i in range(7)], *[g.nodes[i][1].animate.set_color(TEXT) for i in range(7)], run_time=0.4)
        self.go(*paint(g.nodes, [1, 3, 4], SAFE), run_time=0.6)
        self.sfx("chime")
        opt = chip("optimum: {2, 4, 5}  →  3 vertices", SAFE, 24, DARK).move_to(STAGE + RIGHT * 3.6 + DOWN * 0.1)
        self.show(opt, run_time=0.4)
        r = VGroup(label("6 / 3  =  2", 36, TEXT, "BOLD"), chip("O(V + E)", ACCENT, 22)).arrange(RIGHT, buff=0.5).move_to(STAGE + RIGHT * 3.6 + DOWN * 1.3)
        self.show(r, run_time=0.5)

    # ------------------------------------------------------------ TSP
    def b_t_metric(self, b):
        self.screen("METRIC TSP", PURPLE, "the triangle inequality:  d(a, c)  ≤  d(a, b) + d(b, c)")
        pa, pb, pc = STAGE + LEFT * 2.5 + DOWN * 1.2, STAGE + UP * 0.8, STAGE + RIGHT * 2.5 + DOWN * 1.2
        tri = VGroup(Line(pa, pc, color=SAFE, stroke_width=6), Line(pa, pb, color=KILL, stroke_width=4), Line(pb, pc, color=KILL, stroke_width=4),
                     node(pa, "a"), node(pb, "b"), node(pc, "c"))
        self.show(tri, run_time=0.7)
        d = VGroup(label("direct", 22, SAFE, "BOLD").next_to(tri[0], DOWN, buff=0.15), label("via b", 22, KILL, "BOLD").next_to(pb, UP, buff=0.4))
        self.show(d, run_time=0.4)
        self.at(b, 1)
        self.punch("true for road distances, flight distances, any real map", ACCENT, 24, -2.6)

    def b_t_algo(self, b):
        self.screen("MST  →  WALK  →  TOUR", PURPLE)
        code = CodePanel(["T := minimum spanning tree (Prim / Kruskal)",
                          "walk around T, visiting every vertex",
                          "skip vertices already visited",
                          "return the walk as the tour"], font_size=22).move_to(STAGE + LEFT * 2.8 + UP * 0.4)
        self.show(code, run_time=0.6)
        self.go(code.highlight(0))
        self.at(b, 1)
        self.go(code.highlight(1))
        self.go(code.highlight(2))
        m = self.city_map(STAGE + RIGHT * 4.2 + DOWN * 0.3)
        self.show(m, run_time=0.5)
        self.cmap = m

    def b_t_trace(self, b):
        self.clear(self.cmap, run_time=0.4)
        self.screen("FIVE CITIES", PURPLE)
        m = self.cmap
        self.go(m.animate.move_to(STAGE + LEFT * 3.2 + DOWN * 0.5), run_time=0.4)
        tree = VGroup(*[edge(m.pts[a], m.pts[b], SAFE, 6, 0.3) for a, b in MST_EDGES])
        self.show(tree, anim=Create, run_time=0.8)
        self.sfx("place")
        c1 = chip("MST cost ≈ 11.7", SAFE, 24, DARK).move_to(STAGE + RIGHT * 3.4 + UP * 1.3)
        self.show(c1, run_time=0.4)
        c2 = chip("walk around it:  2 × 11.7", PANEL_EDGE, 24).move_to(STAGE + RIGHT * 3.4 + UP * 0.4)
        self.show(c2, run_time=0.4)
        self.at(b, 1)
        tour = VGroup(*[edge(m.pts[TOUR[i]], m.pts[TOUR[(i + 1) % 5]], GOLD, 5, 0.3) for i in range(5)])
        self.go(FadeOut(tree), run_time=0.3)
        self.stage.remove(tree)
        self.show(tour, anim=Create, run_time=1.0)
        self.sfx("chime")
        c3 = chip("tour A D E C B A  ≈ 15.7", GOLD, 24, DARK).move_to(STAGE + RIGHT * 3.4 + DOWN * 0.6)
        self.show(c3, run_time=0.4)
        n = label("here the shortcuts reach the optimum", 22, MUTED).move_to(STAGE + RIGHT * 3.4 + DOWN * 1.5)
        self.show(n, run_time=0.4)

    def b_t_proof(self, b):
        self.screen("WHY AT MOST TWICE", PURPLE)
        rows = VGroup(VGroup(chip("1", GOLD, 24, DARK), label("optimal tour minus one edge is a spanning tree  ⇒  MST  ≤  OPT", 26, TEXT)).arrange(RIGHT, buff=0.3),
                      VGroup(chip("2", GOLD, 24, DARK), label("the full walk costs  2 · MST  ≤  2 · OPT", 26, TEXT)).arrange(RIGHT, buff=0.3),
                      VGroup(chip("3", GOLD, 24, DARK), label("shortcuts never increase the cost  (triangle inequality)", 26, TEXT)).arrange(RIGHT, buff=0.3)
                      ).arrange(DOWN, aligned_edge=LEFT, buff=0.45).move_to(STAGE + UP * 0.4)
        if rows.width > 13.0:
            rows.scale_to_fit_width(13.0)
        self.stage.add(rows)
        self.go(FadeIn(rows[0], shift=RIGHT * 0.3), run_time=0.5)
        self.at(b, 1)
        self.go(FadeIn(rows[1], shift=RIGHT * 0.3), run_time=0.5)
        self.go(FadeIn(rows[2], shift=RIGHT * 0.3), run_time=0.5)
        self.punch("tour  ≤  2 · OPT:  a 2-approximation", GOLD, 30, -2.2)

    def b_t_better(self, b):
        self.screen("CAN WE DO BETTER?", PURPLE)
        c1 = titled_card("Christofides", SAFE, ["metric TSP", "1.5-approximation"], 5.0, 2.0, 30, 26)
        c2 = titled_card("no triangle inequality", KILL, ["no constant ratio at all", "unless  P = NP"], 5.6, 2.0, 30, 26)
        VGroup(c1, c2).arrange(RIGHT, buff=0.8).move_to(STAGE + UP * 0.6)
        self.show(c1, run_time=0.5)
        self.at(b, 1)
        self.show(c2, run_time=0.5)
        self.sfx("kill")
        self.punch("hardness limits even how well you can approximate", GOLD, 26, -1.6)

    # ------------------------------------------------------------ applications
    def app_screen(self, title, color, left, right=None):
        self.screen(title, color)
        cards = VGroup(*[titled_card(t, color, lines, 6.3, 2.6, 26, 22) for t, lines in ([left] + ([right] if right else []))])
        cards.arrange(RIGHT, buff=0.5).move_to(STAGE + UP * 0.5)
        return cards

    def b_a_ai(self, b):
        cards = self.app_screen("APPLICATIONS  ·  AI", ACCENT, ("NP-hard, all of them", ["training a network to the global optimum", "k-means clustering", "the smallest decision tree"]),
                                ("so we use heuristics", ["gradient descent", "Lloyd's algorithm", "good solutions, not optimal ones"]))
        self.show(cards[0], run_time=0.6)
        self.at(b, 1)
        self.show(cards[1], run_time=0.6)
        self.sfx("pop")
        self.punch("and that is enough", GOLD, 26, -1.6)

    def b_a_ai2(self, b):
        cards = self.app_screen("APPLICATIONS  ·  AI PLANNING", ACCENT, ("planning and scheduling", ["reduce to SAT", "modern solvers: millions of clauses"]),
                                ("hard in theory", ["routinely solved in practice", "the theory says where to expect trouble"]))
        self.show(cards[0], run_time=0.6)
        self.at(b, 1)
        self.show(cards[1], run_time=0.6)
        self.sfx("pop")

    def b_a_big(self, b):
        self.screen("APPLICATIONS  ·  BIG DATA", SAFE, "exact answers on a billion rows are too slow: approximate on purpose")
        self.at(b, 1)
        cards = VGroup(titled_card("HyperLogLog", SAFE, ["count distinct users", "in a few kilobytes"], 4.1, 2.0, 26, 22),
                       titled_card("Count-Min Sketch", SAFE, ["find the frequent items", "in a stream"], 4.1, 2.0, 26, 22),
                       titled_card("k-means++", SAFE, ["seed the clusters", "an O(log k) approximation"], 4.1, 2.0, 26, 22)).arrange(RIGHT, buff=0.35).move_to(STAGE + DOWN * 0.3)
        self.stage.add(cards)
        self.go(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cards], lag_ratio=0.4), run_time=1.5)
        self.sfx("pop")

    def b_a_big2(self, b):
        cards = self.app_screen("APPLICATIONS  ·  BIG DATA CLUSTERS", SAFE, ("scheduling and placement", ["jobs onto machines, data across machines", "bin packing and partitioning: NP-hard"]),
                                ("greedy approximations", ["first fit decreasing", "within a constant factor of optimal, at scale"]))
        self.show(cards[0], run_time=0.6)
        self.at(b, 1)
        self.show(cards[1], run_time=0.6)
        self.sfx("pop")

    def b_a_crypto(self, b):
        self.screen("APPLICATIONS  ·  CRYPTOGRAPHY", KILL, "hardness, upside down: here we WANT the problem to be hard")
        self.at(b, 1)
        cards = VGroup(titled_card("RSA", KILL, ["factoring large numbers", "is hard"], 5.0, 2.0, 30, 24), titled_card("Elliptic curves", KILL, ["the discrete logarithm", "is hard"], 5.0, 2.0, 30, 24)
                       ).arrange(RIGHT, buff=0.6).move_to(STAGE + DOWN * 0.3)
        self.stage.add(cards)
        self.go(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cards], lag_ratio=0.5), run_time=1.2)
        self.sfx("pop")

    def b_a_crypto2(self, b):
        self.screen("POST-QUANTUM CRYPTOGRAPHY", KILL)
        c = titled_card("lattice problems", KILL, ["shortest vector problem: NP-hard in its exact form", "not known to be broken even by quantum computers"], 10.0, 2.0, 30, 24).move_to(STAGE + UP * 0.8)
        self.show(c, run_time=0.6)
        self.at(b, 1)
        self.punch("the hardness you studied this unit is the lock on your bank account", GOLD, 26, -1.2)

    def b_a_sum(self, b):
        self.screen("ONE LIST OF HARD PROBLEMS, THREE MEANINGS", GOLD)
        self.at(b, 1)
        cards = VGroup(titled_card("AI", ACCENT, ["approximate them"], 4.0, 1.8, 34, 26), titled_card("Big data", SAFE, ["approximate on purpose,", "for speed"], 4.0, 1.8, 34, 26),
                       titled_card("Cryptography", KILL, ["rely on them", "staying hard"], 4.0, 1.8, 34, 26)).arrange(RIGHT, buff=0.5).move_to(STAGE + UP * 0.2)
        self.stage.add(cards)
        self.go(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cards], lag_ratio=0.4), run_time=1.5)
        self.sfx("chime")

    # ------------------------------------------------------------ practice, tips, recap
    def b_p_intro(self, b):
        self.question_card(b, ["APPROX-VERTEX-COVER on the path 1-2-3-4-5,", "picking edge (1,2) first.", "Your cover?  The optimum?"])

    def b_p_pause(self, b):
        self.pause_screen(b, "Pause and work it out")

    def b_p_answer(self, b):
        self.pause_over()
        self.clear(run_time=0.4)
        pts = [STAGE + LEFT * 4.0 + RIGHT * 2.0 * i + UP * 1.4 for i in range(5)]
        es = VGroup(*[edge(pts[i], pts[i + 1], MUTED, 5, 0.32) for i in range(4)])
        nodes = VGroup(*[node(p, str(i + 1)) for i, p in enumerate(pts)])
        self.show(es, nodes, run_time=0.5)
        self.go(es[0].animate.set_color(GOLD).set_stroke(width=9), *paint(nodes, [0, 1], GOLD), run_time=0.5)
        self.go(es[1].animate.set_opacity(0.12), es[0].animate.set_opacity(0.35), run_time=0.3)
        self.go(es[2].animate.set_color(GOLD).set_stroke(width=9), *paint(nodes, [2, 3], GOLD), run_time=0.5)
        self.go(es[3].animate.set_opacity(0.12), es[2].animate.set_opacity(0.35), run_time=0.3)
        self.sfx("place")
        ours = chip("ours: {1, 2, 3, 4}  →  size 4", GOLD, 26, DARK).move_to(STAGE + DOWN * 0.2)
        self.show(ours, run_time=0.4)
        self.at(b, 1)
        opt = chip("optimum: {2, 4}  →  size 2", SAFE, 26, DARK).move_to(STAGE + DOWN * 1.1)
        self.show(opt, run_time=0.4)
        self.sfx("chime")
        self.punch("ratio exactly 2: within the guarantee", ACCENT, 26, -2.2)

    def b_tip1(self, b):
        self.tip(b, 1, "Define the ratio with the formula", "minimisation: ours / OPT ≥ 1;  maximisation: OPT / ours")

    def b_tip2(self, b):
        self.tip(b, 2, "Vertex cover: algorithm + the two-line proof", "picked edges = a matching;  OPT ≥ k;  ours = 2k")

    def b_tip3(self, b):
        self.tip(b, 3, "TSP: triangle inequality, MST ≤ OPT, walk = 2·MST, shortcuts", "mention Christofides for 1.5")

    def b_recap(self, b):
        self.recap(b, ["Approximation: a guarantee in polynomial time", "Vertex cover and metric TSP: simple 2-approximations with short proofs",
                       "AI approximates, big data embraces, cryptography relies on hardness"])
