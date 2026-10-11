"""Video 3.3 - Sum of Subsets & Hamiltonian Cycle. Rendered by build.py (needs SCHEDULE / ENVELOPE env vars)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from lesson import *  # noqa: E402,F401,F403

W, M = [7, 11, 13, 24], 31
PW, PM = [3, 5, 6, 7], 15
CITIES = {1: (0, 1.55), 2: (1.5, 0.5), 3: (0.95, -1.3), 4: (-0.95, -1.3), 5: (-1.5, 0.5)}
ROADS = [(1, 2), (1, 3), (1, 5), (2, 3), (2, 4), (3, 5), (4, 5)]


def sumsub_trace(w, m):
    """SumOfSub events for the Tree: (kind, level, x_k) + a tag per event: (s, k, r) after the choice,
    or the failing arithmetic for a killed node."""
    n, ev, tags = len(w), [], []

    def rec(s, k, r):
        s1, r1 = s + w[k], r - w[k]
        if s1 == m:
            ev.append(("place", k, 1)); tags.append(("answer", s1, k + 2, r1))
            ev.append(("back", k, 1)); tags.append(None)
        elif k + 1 < n and s1 + w[k + 1] <= m:
            ev.append(("place", k, 1)); tags.append(("live", s1, k + 2, r1))
            rec(s1, k + 1, r1)
            ev.append(("back", k, 1)); tags.append(None)
        else:
            ev.append(("kill", k, 1))
            tags.append(("dead", f"{s1}+{w[k + 1]}>{m}" if k + 1 < n else f"{s1}≠{m}"))
        if s + r1 >= m and k + 1 < n and s + w[k + 1] <= m:
            ev.append(("place", k, 0)); tags.append(("live", s, k + 2, r1))
            rec(s, k + 1, r1)
            ev.append(("back", k, 0)); tags.append(None)
        else:
            ev.append(("kill", k, 0))
            tags.append(("dead", f"{s}+{r1}<{m}" if s + r1 < m else f"{s}+{w[k + 1]}>{m}"))
    rec(0, 0, sum(w))
    return ev, tags


def ham_trace(n, roads):
    adj = {v: set() for v in range(1, n + 1)}
    for a, b in roads:
        adj[a].add(b)
        adj[b].add(a)
    x, ev = [1], []

    def rec(k):
        for v in range(1, n + 1):
            if v in adj[x[-1]] and v not in x:
                if k == n - 1 and 1 not in adj[v]:
                    ev.append(("kill", k - 1, v))
                    continue
                x.append(v)
                ev.append(("place", k - 1, v))
                done = k == n - 1 or rec(k + 1)
                x.pop()
                ev.append(("back", k - 1, v))
                if done:
                    return True
        return False
    rec(1)
    return ev


SUM_EV, SUM_TAGS = sumsub_trace(W, M)
PR_EV, PR_TAGS = sumsub_trace(PW, PM)
HAM_EV = ham_trace(5, ROADS)


def weight_block(w, size=1.1):
    box = RoundedRectangle(width=size, height=size * 0.85, corner_radius=0.18, fill_color=PANEL, fill_opacity=1,
                           stroke_color=PANEL_EDGE, stroke_width=3)
    return VGroup(box, label(f"{w} kg", 28, TEXT, "BOLD").move_to(box))


class Video(Lesson):
    NEXT = ("3.4  Branch & Bound:", "FIFO, LIFO & LC Search")

    # ------------------------------------------------------------ hook
    def b_hook_weights(self, b):
        self.blocks = VGroup(*[weight_block(w) for w in W]).arrange(RIGHT, buff=0.45).move_to(STAGE + UP * 0.5)
        self.show(self.blocks, anim=FadeIn, run_time=0.8, lag_ratio=0.2, shift=UP * 0.3)
        self.sfx("pop")
        self.at(b, 1)
        q = VGroup(label("pick some  =", 34, MUTED), label("31 kg", 54, GOLD, "BOLD"), label("?", 54, GOLD, "BOLD")
                   ).arrange(RIGHT, buff=0.25).move_to(STAGE + DOWN * 1.3)
        self.show(q, anim=GrowFromCenter, run_time=0.5)
        self.q = q

    def b_hook_answer(self, b):
        glow = lambda idx: [self.blocks[i][0].animate.set_fill(SAFE, 0.85) for i in idx]
        plain = lambda idx: [self.blocks[i][0].animate.set_fill(PANEL, 1) for i in idx]
        a1 = chip("7 + 24 = 31", SAFE, 26).move_to(STAGE + DOWN * 2.1 + LEFT * 2.2)
        a2 = chip("7 + 11 + 13 = 31", SAFE, 26).move_to(STAGE + DOWN * 2.1 + RIGHT * 2.2)
        self.stage.add(a1, a2)
        self.go(*glow([0, 3]), GrowFromCenter(a1), run_time=0.6)
        self.sfx("chime", -0.2)
        self.go(*plain([3]), *glow([1, 2]), GrowFromCenter(a2), run_time=0.6)
        self.sfx("chime", -0.2)
        self.at(b, 1)
        self.clear(run_time=0.4)
        big = MathTex(r"2^{40} = 1{,}099{,}511{,}627{,}776", color=TEXT).scale(1.4).move_to(STAGE + UP * 0.6)
        sub = chip("over a trillion subsets", KILL, 28).move_to(STAGE + DOWN * 0.7)
        self.show(big, anim=Write, run_time=1.2)
        self.show(sub, anim=GrowFromCenter, run_time=0.5)
        self.sfx("pop")

    def b_syllabus(self, b):
        self.syllabus(b, ["Sum of subsets", "Hamiltonian cycle"])

    def b_exam(self, b):
        self.exam_star(b)

    # ------------------------------------------------------------ sum of subsets: the model
    def weights_strip(self, pos):
        chips_ = VGroup(*[chip(str(w), PANEL_EDGE, 24) for w in W]).arrange(RIGHT, buff=0.25)
        target = chip(f"m = {M}", GOLD, 24, "#0F172A")
        return VGroup(chips_, target).arrange(RIGHT, buff=0.6).move_to(pos)

    def b_s_def(self, b):
        self.unsay()
        self.clear(run_time=0.4)
        title = label("Sum of subsets", 44, TEXT, "BOLD").move_to(STAGE + UP * 2.0)
        self.show(title, run_time=0.5)
        self.at(b, 1)
        given = VGroup(MathTex(r"w_1, w_2, \dots, w_n > 0", color=TEXT).scale(1.0),
                       MathTex(r"\text{target } m", color=GOLD).scale(1.0)).arrange(RIGHT, buff=0.8)
        want = label("find every subset with sum exactly m", 30, ACCENT).next_to(given, DOWN, buff=0.4)
        g = VGroup(given, want).move_to(STAGE + UP * 0.5)
        self.show(g, run_time=0.7)
        self.strip = self.weights_strip(STAGE + DOWN * 1.4)
        self.show(self.strip, run_time=0.5, shift=UP * 0.2)
        self.def_group = VGroup(title, g)

    def b_s_tuple(self, b):
        self.drop(self.def_group)
        self.go(self.strip.animate.move_to(STAGE + UP * 2.1), run_time=0.4)
        f = MathTex(r"x = (x_1, x_2, \dots, x_n),\quad x_k \in \{0, 1\}", color=TEXT).scale(1.1).move_to(STAGE + UP * 0.8)
        self.show(f, anim=Write, run_time=1.0)
        self.at(b, 1)
        ex = VGroup(MathTex(r"(1,\ 1,\ 1,\ 0)", color=SAFE).scale(1.1), label("=  7 + 11 + 13", 30, SAFE, "BOLD")
                    ).arrange(RIGHT, buff=0.5).move_to(STAGE + DOWN * 0.6)
        self.show(ex, run_time=0.6)
        self.go(*[self.strip[0][i][0].animate.set_fill(SAFE, 1) for i in (0, 1, 2)], run_time=0.4)
        self.sfx("pop")
        self.tuple_group = VGroup(f, ex)

    def b_s_sort(self, b):
        self.drop(self.tuple_group)
        self.go(*[self.strip[0][i][0].animate.set_fill(PANEL_EDGE, 1) for i in (0, 1, 2)],
                self.strip.animate.move_to(STAGE + UP * 0.8).scale(1.3), run_time=0.5)
        arrow = Arrow(self.strip[0].get_left() + DOWN * 0.7, self.strip[0].get_right() + DOWN * 0.7, buff=0,
                      color=ACCENT, stroke_width=5)
        inc = label("increasing", 26, ACCENT).next_to(arrow, DOWN, buff=0.1)
        self.show(arrow, inc, run_time=0.6)
        self.at(b, 1)
        note = chip("sort first - the bounding function needs it", GOLD, 24, "#0F172A").move_to(STAGE + DOWN * 1.6)
        self.show(note, anim=GrowFromCenter, run_time=0.5)

    def b_s_state(self, b):
        self.clear(run_time=0.4)
        node = Circle(0.55, color=SAFE, fill_color=BG, fill_opacity=1, stroke_width=4).move_to(STAGE + LEFT * 3.3)
        self.show(node, run_time=0.4)
        self.at(b, 1)
        rows = [("s", "sum chosen so far", SAFE), ("k", "next weight to decide", ACCENT), ("r", "sum still undecided", GOLD)]
        g = VGroup(*[VGroup(MathTex(v, color=c).scale(1.3), label(t, 28, TEXT)).arrange(RIGHT, buff=0.4)
                     for v, t, c in rows]).arrange(DOWN, aligned_edge=LEFT, buff=0.45).next_to(node, RIGHT, buff=1.0)
        self.stage.add(g)
        for r in g:
            self.go(FadeIn(r, shift=RIGHT * 0.3), run_time=0.5)
            self.sfx("pop", -0.3)
        tag = MathTex(r"(s,\ k,\ r)", color=TEXT).scale(0.8).next_to(node, DOWN, buff=0.2)
        self.show(tag, run_time=0.4)

    def b_s_bound1(self, b):
        self.clear(run_time=0.4)
        title = label("Bounding function", 34, MUTED, "BOLD").move_to(STAGE + UP * 2.0)
        self.show(title, run_time=0.4)
        self.at(b, 1)
        f = MathTex(r"s + r \;\geq\; m", color=TEXT).scale(1.4)
        t = label("the rest can still reach m", 26, MUTED)
        c = chip("1", ACCENT, 28)
        row = VGroup(c, VGroup(f, t).arrange(DOWN, buff=0.15)).arrange(RIGHT, buff=0.5).move_to(STAGE + UP * 0.7)
        self.show(row, run_time=0.6)
        self.sfx("pop")

    def b_s_bound2(self, b):
        f = MathTex(r"s + w_{k+1} \;\leq\; m", color=TEXT).scale(1.4)
        t = label("the next weight does not overshoot", 26, MUTED)
        c = chip("2", ACCENT, 28)
        row = VGroup(c, VGroup(f, t).arrange(DOWN, buff=0.15)).arrange(RIGHT, buff=0.5).move_to(STAGE + DOWN * 1.1)
        self.show(row, run_time=0.6)
        self.sfx("pop")
        self.at(b, 1)
        self.go(Indicate(row, color=KILL, scale_factor=1.05), run_time=0.7)

    # ------------------------------------------------------------ sum of subsets: the trace
    def tag_for(self, tree, tags, i, size=15):
        """The (s, k, r) label of a live node, or the failing sum under a dead one."""
        node = tree.mobs[tree.event_node[i]]
        t = tags[i]
        if t[0] == "dead":
            return label(t[1], size - 2, KILL).next_to(node, DOWN, buff=0.04)
        _, s, k, r = t
        return label(f"{s},{k},{r}", size - 2, GOLD).next_to(node, UR, buff=0.0)

    def tagged_grow(self, tree, tags, b, phrase, n, per=0.5):
        def extra(i, kind):
            if kind == "back":
                return []
            tag = self.tag_for(tree, tags, i)
            self.stage.add(tag)
            tree.tagmobs.append(tag)
            return [FadeIn(tag)]
        self.grow_tree(tree, SUM_EV if tree is self.tree else PR_EV, b, phrase, n, per, on_event=extra)

    def b_t_root(self, b):
        self.clear(run_time=0.4)
        self.strip = self.weights_strip(np.array([STAGE[0], 3.0, 0])).scale(0.85)
        self.show(self.strip, run_time=0.4)
        self.tree = Tree(SUM_EV, width=8.8, height=3.4, r=0.19, level_names=[f"w{i + 1}={w}" for i, w in enumerate(W)],
                         value_fmt=str, kill_label=True)
        self.tree.center_on(STAGE + DOWN * 0.15 + RIGHT * 1.0)
        self.tree.ev_i, self.tree.tagmobs = 0, []
        self.show(self.tree, run_time=0.5)
        self.at(b, 1)
        root_tag = label(f"0,1,{sum(W)}", 13, GOLD).next_to(self.tree.root, UR, buff=0.0)
        self.show(root_tag, run_time=0.4)
        self.go(Indicate(self.tree.root, color=GOLD, scale_factor=1.8), run_time=0.7)

    def mark_answer(self, tree, ev, text):
        path = tree.path_to(ev)
        node = tree.mobs[tree.event_node[ev]]
        tag = chip(text, SAFE, 18).next_to(node, DOWN, buff=0.12)
        self.stage.add(tag)
        self.go(*[tree.mobs[i][0].animate.set_fill(SAFE, 0.6) for i in path], GrowFromCenter(tag), run_time=0.7)
        self.sfx("chime")

    def b_t_x1(self, b):
        self.tagged_grow(self.tree, SUM_TAGS, b, 0, 1)
        self.at(b, 1)
        self.go(Indicate(self.tree.mobs[self.tree.event_node[0]], color=GOLD, scale_factor=1.5), run_time=0.7)

    def b_t_sol1(self, b):
        self.tagged_grow(self.tree, SUM_TAGS, b, 0, 1)
        self.tagged_grow(self.tree, SUM_TAGS, b, 1, 1)
        self.mark_answer(self.tree, 2, "7+11+13 ✓")

    def b_t_back1(self, b):
        self.tagged_grow(self.tree, SUM_TAGS, b, 0, 1)          # back from the answer
        self.tagged_grow(self.tree, SUM_TAGS, b, 1, 1)          # skip 13 at s = 18: dies

    def b_t_back2(self, b):
        self.tagged_grow(self.tree, SUM_TAGS, b, 0, 2)          # back, then skip 11 (s stays 7)
        self.tagged_grow(self.tree, SUM_TAGS, b, 1, 1)          # take 13: 20 + 24 too big

    def b_t_sol2(self, b):
        self.tagged_grow(self.tree, SUM_TAGS, b, 0, 1)          # skip 13 (s stays 7)
        self.tagged_grow(self.tree, SUM_TAGS, b, 1, 1)          # take 24 = 31
        self.mark_answer(self.tree, 9, "7+24 ✓")

    def b_t_right(self, b):
        self.tagged_grow(self.tree, SUM_TAGS, b, 0, 6, per=0.4)  # kill, backs, then leave 7 out
        self.tagged_grow(self.tree, SUM_TAGS, b, 1, 9, per=0.4)  # the whole right side dies

    def b_t_count(self, b):
        self.at(b, 1)
        res = VGroup(chip("16 nodes generated", SAFE, 24), label("vs", 24, MUTED),
                     chip("31 in the full tree", PANEL_EDGE, 24)).arrange(RIGHT, buff=0.3)
        res.move_to(STAGE + DOWN * 3.0)
        self.show(res, run_time=0.5, shift=UP * 0.2)
        self.sfx("pop")

    # ------------------------------------------------------------ sum of subsets: the algorithm
    def b_s_algo(self, b):
        self.clear(run_time=0.4)
        self.code = CodePanel(["Algorithm SumOfSub(s, k, r)",
                               "{",
                               "  x[k] := 1;",
                               "  if (s + w[k] = m) then write (x[1:k]);",
                               "  else if (s + w[k] + w[k+1] <= m)",
                               "    then SumOfSub(s + w[k], k+1, r - w[k]);",
                               "  if ((s + r - w[k] >= m) and (s + w[k+1] <= m))",
                               "  then",
                               "  {",
                               "    x[k] := 0;",
                               "    SumOfSub(s, k+1, r - w[k]);",
                               "  }",
                               "}"], font_size=21).move_to(STAGE + UP * 0.1)
        self.show(self.code, run_time=0.6)
        self.go(self.code.highlight(0))
        self.at(b, 1)
        self.go(self.code.highlight(2))

    def b_s_algo2(self, b):
        self.go(self.code.highlight(3))
        self.at(b, 1)
        self.go(self.code.highlight(4))
        self.go(self.code.highlight(5))

    def b_s_algo3(self, b):
        self.go(self.code.highlight(6))
        self.at(b, 1)
        self.go(self.code.highlight(9))
        self.go(self.code.highlight(10))

    def b_s_complex(self, b):
        self.clear(run_time=0.4)
        f = MathTex(r"O(2^n)", color=TEXT).scale(2.0).move_to(STAGE + UP * 0.8)
        sub = label("2^n subsets in the worst case", 28, MUTED).next_to(f, DOWN, buff=0.3)
        self.show(f, anim=Write, run_time=1.0)
        self.show(sub, run_time=0.4)
        self.at(b, 1)
        good = chip("Bounding function  →  fast in practice", SAFE, 26).move_to(STAGE + DOWN * 1.4)
        self.show(good, anim=GrowFromCenter, run_time=0.5)
        self.sfx("chime", -0.2)

    # ------------------------------------------------------------ hamiltonian cycle
    def city_graph(self, center, scale=1.0):
        pos = {k: (center[0] + x * scale, center[1] + y * scale) for k, (x, y) in CITIES.items()}
        return Graph(pos, ROADS, r=0.36 * scale)

    def b_h_intro(self, b):
        self.clear(run_time=0.4)
        self.graph = self.city_graph(STAGE + DOWN * 0.1, 1.25)
        self.graph.vert[1][0].set_fill(KILL, 1)
        home = chip("home", KILL, 20).next_to(self.graph.vert[1], UP, buff=0.12)
        self.show(self.graph, home, run_time=0.8)
        self.home = home
        self.at(b, 1)
        rule = label("visit every city once, come back home, roads only", 28, ACCENT).move_to(STAGE + DOWN * 2.6)
        self.show(rule, run_time=0.5)
        self.rule = rule

    def b_h_def(self, b):
        self.drop(self.rule)
        self.go(VGroup(self.graph, self.home).animate.scale(0.8).move_to(STAGE + LEFT * 3.2), run_time=0.5)
        self.at(b, 1)
        t = VGroup(label("Hamiltonian cycle", 34, TEXT, "BOLD"),
                   label("a cycle through every vertex", 26, MUTED),
                   label("exactly once, back to the start", 26, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        box = card(t.width + 0.7, t.height + 0.6, edge=ACCENT)
        self.defcard = VGroup(box, t.move_to(box)).move_to(STAGE + RIGHT * 2.6 + UP * 0.6)
        self.show(self.defcard, run_time=0.6, shift=UP * 0.2)

    def b_h_history(self, b):
        self.at(b, 1)
        t = VGroup(label("Sir William Rowan Hamilton", 24, TEXT, "BOLD"), label("the Icosian game, 1857", 22, MUTED)
                   ).arrange(DOWN, buff=0.1)
        box = card(t.width + 0.6, t.height + 0.5)
        self.hist = VGroup(box, t.move_to(box)).next_to(self.defcard, DOWN, buff=0.4)
        self.show(self.hist, run_time=0.5, shift=UP * 0.2)

    def b_h_tuple(self, b):
        self.drop(self.defcard, self.hist)
        f = MathTex(r"x = (x_1, x_2, x_3, x_4, x_5)", color=TEXT).scale(1.1).move_to(STAGE + RIGHT * 2.6 + UP * 0.9)
        sub = label("the order of the visit", 24, MUTED).next_to(f, DOWN, buff=0.2)
        self.show(f, sub, run_time=0.7)
        self.at(b, 1)
        fix = VGroup(MathTex(r"x_1 = 1", color=KILL).scale(1.1), label("fixed: start at home", 24, MUTED)
                     ).arrange(RIGHT, buff=0.4).move_to(STAGE + RIGHT * 2.6 + DOWN * 0.8)
        self.show(fix, run_time=0.5)
        self.tuple_group = VGroup(f, sub, fix)

    def b_h_bound(self, b):
        self.drop(self.tuple_group)
        checks = [("1", "adjacent to the previous vertex", ACCENT), ("2", "not visited before", GOLD),
                  ("3", "last one: adjacent to vertex 1", KILL)]
        rows = VGroup(*[VGroup(chip(n, c, 26, "#0F172A" if c == GOLD else TEXT), label(t, 26, TEXT)).arrange(RIGHT, buff=0.3)
                        for n, t, c in checks]).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        rows.move_to(STAGE + RIGHT * 2.7 + UP * 0.2)
        self.stage.add(rows)
        self.go(FadeIn(rows[0], shift=RIGHT * 0.3), run_time=0.5)
        self.at(b, 1)
        self.go(FadeIn(rows[1], shift=RIGHT * 0.3), run_time=0.5)
        self.at(b, 2)
        self.go(FadeIn(rows[2], shift=RIGHT * 0.3), run_time=0.5)
        self.sfx("pop")
        self.checks = rows

    # the graph follows the tree: edges light up along the current path
    def path_anims(self, i, kind):
        _, level, v = HAM_EV[i]
        g = self.graph
        if kind == "place":
            prev = self.path[-1]
            self.path.append(v)
            return [g.edge_mobs[(prev, v)].animate.set_stroke(GOLD, width=9), g.vert[v][0].animate.set_fill(GOLD, 0.9)]
        if kind == "back":
            self.path.pop()
            prev = self.path[-1]
            return [g.edge_mobs[(prev, v)].animate.set_stroke(MUTED, width=4), g.vert[v][0].animate.set_fill(PANEL, 1)]
        return [Indicate(g.vert[v], color=KILL, scale_factor=1.2)]

    def b_h_trace1(self, b):
        self.drop(self.checks)
        self.path = [1]
        self.htree = Tree([(k, l, v) for k, l, v in HAM_EV], width=3.6, height=3.4, r=0.2,
                          level_names=["x2", "x3", "x4", "x5"], value_fmt=str, kill_label=True)
        self.htree.center_on(STAGE + RIGHT * 3.0 + UP * 0.1)
        self.htree.ev_i = 0
        self.show(self.htree, run_time=0.5)
        self.grow_tree(self.htree, HAM_EV, b, 0, 1, on_event=self.path_anims)
        self.grow_tree(self.htree, HAM_EV, b, 1, 2, on_event=self.path_anims)

    def b_h_dead(self, b):
        self.grow_tree(self.htree, HAM_EV, b, 0, 1, on_event=self.path_anims)     # 4: no road back to 1
        g = self.graph
        missing = DashedLine(g.pos[4], g.pos[1], color=KILL, stroke_width=6)
        no = chip("no road 4 → 1", KILL, 20).next_to(g, DOWN, buff=0.25)
        self.show(missing, no, run_time=0.5)
        self.sfx("kill")
        self.at(b, 1)
        dead = chip("Dead end!", KILL, 24).next_to(self.htree, DOWN, buff=0.15)
        self.show(dead, anim=GrowFromCenter, run_time=0.4)
        self.dead_bits = VGroup(missing, no, dead)

    def b_h_back(self, b):
        self.drop(self.dead_bits)
        self.grow_tree(self.htree, HAM_EV, b, 0, 3, per=0.45, on_event=self.path_anims)   # back, back, then 4
        self.grow_tree(self.htree, HAM_EV, b, 1, 2, per=0.5, on_event=self.path_anims)    # 5, then 3

    def b_h_found(self, b):
        g = self.graph
        self.go(g.edge_mobs[(3, 1)].animate.set_stroke(SAFE, width=9), run_time=0.5)
        self.sfx("chime")
        self.at(b, 1)
        path = self.htree.path_to(8)
        tag = chip("1 → 2 → 4 → 5 → 3 → 1  ✓", SAFE, 24).next_to(self.htree, DOWN, buff=0.15)
        self.stage.add(tag)
        self.go(*[self.htree.mobs[i][0].animate.set_fill(SAFE, 0.6) for i in path],
                *[g.edge_mobs[e].animate.set_stroke(SAFE, width=9) for e in [(1, 2), (2, 4), (4, 5), (5, 3)]],
                GrowFromCenter(tag), run_time=0.8)

    def b_h_algo(self, b):
        self.clear(run_time=0.4)
        self.nv = CodePanel(["Algorithm NextValue(k)",
                             "repeat",
                             "  x[k] := (x[k] + 1) mod (n + 1);     // next vertex",
                             "  if (x[k] = 0) then return;          // none left",
                             "  if (G[x[k-1], x[k]] <> 0) then      // 1. adjacent",
                             "  {",
                             "    for j := 1 to k-1 do              // 2. not visited",
                             "      if (x[j] = x[k]) then break;",
                             "    if (j = k) then",
                             "      if ((k < n) or (G[x[n], x[1]] <> 0))   // 3. closes",
                             "        then return;",
                             "  }",
                             "until (false);"], font_size=19).move_to(STAGE + UP * 0.1)
        self.show(self.nv, run_time=0.6)
        self.go(self.nv.highlight(0))
        self.go(self.nv.highlight(2))
        self.at(b, 1)
        for ln in (4, 6, 9):
            self.go(self.nv.highlight(ln))

    def b_h_algo2(self, b):
        self.go(self.nv.animate.scale(0.78).move_to(STAGE + LEFT * 2.9 + UP * 0.1), run_time=0.5)
        self.hm = CodePanel(["Algorithm Hamiltonian(k)",
                             "repeat",
                             "  NextValue(k);",
                             "  if (x[k] = 0) then return;",
                             "  if (k = n) then write (x[1:n]);",
                             "  else Hamiltonian(k+1);",
                             "until (false);"], font_size=20).move_to(STAGE + RIGHT * 3.3 + UP * 0.1)
        self.show(self.hm, run_time=0.6)
        self.go(self.hm.highlight(2))
        self.at(b, 1)
        self.go(self.hm.highlight(4))
        self.go(self.hm.highlight(5))

    def b_h_complex(self, b):
        self.clear(run_time=0.4)
        f = MathTex(r"O(n!)", color=TEXT).scale(2.0).move_to(STAGE + UP * 0.8)
        sub = label("every ordering of the remaining vertices, in the worst case", 26, MUTED).next_to(f, DOWN, buff=0.3)
        self.show(f, anim=Write, run_time=1.0)
        self.show(sub, run_time=0.4)
        self.at(b, 1)
        good = chip("Backtracking  ≫  listing all orderings first", SAFE, 26).move_to(STAGE + DOWN * 1.4)
        self.show(good, anim=GrowFromCenter, run_time=0.5)
        self.sfx("chime", -0.2)

    # ------------------------------------------------------------ pattern, practice, tips, recap
    def b_cmp(self, b):
        self.clear(run_time=0.4)
        left = VGroup(label("Sum of subsets", 28, TEXT, "BOLD"), MathTex(r"x_k \in \{0, 1\}", color=MUTED).scale(0.75),
                      label("bound: s, r against m", 22, MUTED)).arrange(DOWN, buff=0.15)
        right = VGroup(label("Hamiltonian cycle", 28, TEXT, "BOLD"), MathTex(r"x_k = \text{next vertex}", color=MUTED).scale(0.75),
                       label("bound: NextValue(k)", 22, MUTED)).arrange(DOWN, buff=0.15)
        cards = VGroup(*[VGroup(card(4.2, 1.9), g) for g in (left, right)])
        for c_ in cards:
            c_[1].move_to(c_[0])
        cards.arrange(RIGHT, buff=0.5).move_to(STAGE + UP * 1.2)
        self.show(cards, run_time=0.6, lag_ratio=0.3)
        self.at(b, 1)
        steps = ["choose x[k]", "check bound", "go deeper", "backtrack"]
        chips_ = VGroup(*[chip(s, c, 24) for s, c in zip(steps, [ACCENT, GOLD, SAFE, BACK])]).arrange(RIGHT, buff=0.55)
        chips_.move_to(STAGE + DOWN * 1.2)
        arrows = VGroup(*[Arrow(chips_[i].get_right(), chips_[i + 1].get_left(), buff=0.08, color=MUTED,
                                stroke_width=4, max_tip_length_to_length_ratio=0.35) for i in range(3)])
        self.stage.add(chips_, arrows)
        self.go(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in chips_], lag_ratio=0.5), FadeIn(arrows), run_time=2.0)

    def b_p_intro(self, b):
        self.question_card(b, ["Weights 3, 5, 6, 7  -  target 15", "Find every subset that works"])

    def b_p_pause(self, b):
        self.pause_screen(b, "Pause and draw the tree")

    def b_p_answer(self, b):
        self.pause_over()
        self.clear(run_time=0.4)
        self.ptree = Tree(PR_EV, width=8.4, height=3.3, r=0.19, level_names=[f"w{i + 1}={w}" for i, w in enumerate(PW)],
                          value_fmt=str, kill_label=True)
        self.ptree.center_on(STAGE + DOWN * 0.1 + RIGHT * 1.0)
        self.ptree.ev_i, self.ptree.tagmobs = 0, []
        self.show(self.ptree, run_time=0.4)
        made = [i for i, ev in enumerate(PR_EV) if ev[0] != "back"]
        step = max(0.22, min(0.4, self.phrase_len(b, 0) / len(made)))
        answer_ev = next(i for i, t in enumerate(PR_TAGS) if t and t[0] == "answer")
        for i in made:
            grow = self.ptree.grow(i)                        # creates the node the tag sits next to
            tag = self.tag_for(self.ptree, PR_TAGS, i, 14)
            self.stage.add(tag)
            self.go(grow, FadeIn(tag), run_time=step)
            self.sfx("kill" if PR_EV[i][0] == "kill" else "place", -step)
            if i == answer_ev:
                self.mark_answer(self.ptree, i, "3+5+7 ✓")
        self.at(b, 1)
        dead = [m for i, m in enumerate(self.ptree.mobs) if m is not None and self.ptree.nodes[i]["kind"] == "kill"]
        self.go(LaggedStart(*[Indicate(m, color=KILL, scale_factor=1.4) for m in dead], lag_ratio=0.08), run_time=1.6)

    def b_tip1(self, b):
        self.tip(b, 1, "Label every node with (s, k, r)", "and write the two bounding conditions beside the tree")

    def b_tip2(self, b):
        self.tip(b, 2, "Sort the weights first, and say so", "the second check needs increasing order")

    def b_tip3(self, b):
        self.tip(b, 3, "Hamiltonian: list the 3 checks of NextValue", "and show the dead end before the cycle")

    def b_recap(self, b):
        self.recap(b, ["Sum of subsets: s, k, r and two bounding checks",
                       "Hamiltonian cycle: next adjacent, unvisited vertex",
                       "Both use the same backtracking control abstraction"])
