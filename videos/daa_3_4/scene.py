"""Video 3.4 - Branch & Bound: FIFO, LIFO & LC Search. Rendered by build.py (needs SCHEDULE / ENVELOPE env vars)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from lesson import *  # noqa: E402,F401,F403

CHILDREN = {1: [2, 3, 4], 2: [5, 6], 3: [7, 8], 4: [9, 10]}
CHAT = {1: 10, 2: 16, 3: 10, 4: 21, 5: 18, 6: 20, 7: 12, 8: 15, 9: 25, 10: 22}
ANSWER = {5, 6, 7, 8, 9, 10}
POS = {1: (0, 1.9), 2: (-2.6, 0.45), 3: (0, 0.45), 4: (2.6, 0.45),
       5: (-3.3, -1.0), 6: (-1.9, -1.0), 7: (-0.7, -1.0), 8: (0.7, -1.0), 9: (1.9, -1.0), 10: (3.3, -1.0)}

P_CHILDREN = {1: [2, 3, 4], 2: [8, 9], 3: [5, 6], 4: [7]}
P_CHAT = {1: 4, 2: 7, 3: 4, 4: 6, 5: 9, 6: 8, 7: 6, 8: 10, 9: 11}
P_ANSWER = {7}
P_POS = {1: (0, 1.7), 2: (-2.2, 0.35), 3: (0, 0.35), 4: (2.2, 0.35),
         8: (-2.8, -1.0), 9: (-1.6, -1.0), 5: (-0.6, -1.0), 6: (0.6, -1.0), 7: (2.2, -1.0)}

LIVE_C, E_C = ACCENT, GOLD


class BBTree(VGroup):
    """A whole state space tree drawn faint up front; nodes light up as they are generated,
    expanded (E-node ring), found to be answers, or killed. Answer nodes are squares."""

    def __init__(self, children, chat, answer, pos, center, scale=1.0, r=0.32, **kw):
        super().__init__(**kw)
        self.children, self.chat, self.answer = children, chat, answer
        self.p = {v: np.array([center[0] + x * scale, center[1] + y * scale, 0]) for v, (x, y) in pos.items()}
        self.r = r
        self.edges, self.node, self.tag = {}, {}, {}
        for u, kids in children.items():
            for v in kids:
                d = (self.p[v] - self.p[u]) / np.linalg.norm(self.p[v] - self.p[u])
                ln = Line(self.p[u] + d * r, self.p[v] - d * r, color=PANEL_EDGE, stroke_width=3)
                self.edges[v] = ln
                self.add(ln)
        for v, q in self.p.items():
            shape = (RoundedRectangle(width=2 * r, height=2 * r, corner_radius=0.08) if v in answer
                     else Circle(r))
            shape.set_stroke(PANEL_EDGE, 3).set_fill(BG, 1).move_to(q)
            num = label(str(v), 24, MUTED, "BOLD").move_to(q)
            self.node[v] = VGroup(shape, num)
            self.tag[v] = label(str(chat[v]), 20, GOLD, "BOLD").next_to(shape, UR, buff=0.02)
            self.add(self.node[v], self.tag[v])
        self.ring = None

    def reset(self):
        anims = []
        for v, (shape, num) in self.node.items():
            anims += [shape.animate.set_stroke(PANEL_EDGE, 3).set_fill(BG, 1), num.animate.set_color(MUTED)]
        for ln in self.edges.values():
            anims.append(ln.animate.set_stroke(PANEL_EDGE, 3))
        return anims

    def gen(self, v):
        shape, num = self.node[v]
        anims = [shape.animate.set_stroke(TEXT, 4), num.animate.set_color(TEXT)]
        if v in self.edges:
            anims.append(self.edges[v].animate.set_stroke(MUTED, 4))
        return anims

    def enode(self, scene, v):
        """Move the gold E-node ring to v (creating it the first time)."""
        target = Circle(self.r + 0.1, color=E_C, stroke_width=6).move_to(self.p[v])
        if self.ring is None:
            self.ring = target
            scene.add(self.ring)
            scene.stage.add(self.ring)
            return [Create(self.ring)]
        return [self.ring.animate.move_to(self.p[v])]

    def found(self, v, color=SAFE):
        shape, num = self.node[v]
        return [shape.animate.set_fill(color, 0.85).set_stroke(color, 4), num.animate.set_color(BG)]

    def kill(self, v):
        x = label("×", 54, KILL, "BOLD").move_to(self.p[v])
        return x, [self.node[v][0].animate.set_stroke(KILL, 4), FadeIn(x, scale=1.6)]


class LiveList(VGroup):
    """The list of live nodes, drawn as a row of chips: a queue, a stack or a priority list."""

    def __init__(self, kind, pos, width=4.6, **kw):
        super().__init__(**kw)
        self.kind = kind
        title = {"FIFO": "FIFO  ·  queue", "LIFO": "LIFO  ·  stack", "LC": "LC  ·  smallest ĉ first"}[kind]
        col = {"FIFO": ACCENT, "LIFO": BACK, "LC": SAFE}[kind]
        self.head = chip(title, col, 24, "#0F172A" if kind == "LIFO" else TEXT)
        self.box = RoundedRectangle(width=width, height=1.0, corner_radius=0.18, fill_color=PANEL, fill_opacity=1,
                                    stroke_color=PANEL_EDGE, stroke_width=2)
        VGroup(self.head, self.box).arrange(DOWN, buff=0.2).move_to(pos)
        note = {"FIFO": "← front", "LIFO": "top →", "LC": "← next"}[kind]
        self.note = label(note, 18, MUTED).next_to(self.box, DOWN, buff=0.1)
        self.note.align_to(self.box, RIGHT if kind == "LIFO" else LEFT)
        self.add(self.head, self.box, self.note)
        self.items = []                       # [(node, chip)]

    def _chip(self, v, chat):
        txt = f"{v}" if self.kind != "LC" else f"{v} ({chat})"
        return chip(txt, LIVE_C, 24)

    def _layout(self):
        row = VGroup(*[c for _, c in self.items])
        if not self.items:
            return []
        target = row.copy().arrange(RIGHT, buff=0.15).move_to(self.box).align_to(self.box, LEFT).shift(RIGHT * 0.2)
        return [c.animate.move_to(t) for (_, c), t in zip(self.items, target)]

    def add_nodes(self, vs, chat, src):
        new = []
        for v in vs:
            c = self._chip(v, chat[v]).move_to(src[v]).scale(0.8)
            self.items.append((v, c))
            new.append(c)
        if self.kind == "LC":
            self.items.sort(key=lambda it: (chat[it[0]], it[0]))
        return new, self._layout()

    def next_node(self):
        """Which node leaves the list next, and its chip."""
        return self.items[-1] if self.kind == "LIFO" else self.items[0]

    def remove(self, v):
        c = next(c for n, c in self.items if n == v)
        self.items = [(n, k) for n, k in self.items if n != v]
        return c, self._layout()


def door(price=None, w=1.3, h=2.0):
    d = RoundedRectangle(width=w, height=h, corner_radius=0.12, fill_color=PANEL, fill_opacity=1,
                         stroke_color=MUTED, stroke_width=3)
    knob = Dot(d.get_right() + LEFT * 0.22, radius=0.06, color=GOLD)
    return VGroup(d, knob)


class Video(Lesson):
    NEXT = ("3.5  Knapsack & TSP", "with Branch & Bound")

    # ------------------------------------------------------------ hook
    def b_hook_doors(self, b):
        self.doors = VGroup(*[door() for _ in range(3)]).arrange(RIGHT, buff=1.0).move_to(STAGE + UP * 0.6)
        self.show(self.doors, run_time=0.8, lag_ratio=0.2)
        self.sfx("pop")
        self.at(b, 1)
        small = VGroup()
        for d in self.doors:
            pair = VGroup(door(w=0.55, h=0.85), door(w=0.55, h=0.85)).arrange(RIGHT, buff=0.18)
            small.add(pair.next_to(d, DOWN, buff=0.35).set_opacity(0.45))
        exit_ = chip("EXIT  ·  cheapest", SAFE, 22).move_to(STAGE + DOWN * 2.3)
        self.show(small, exit_, run_time=0.7)
        self.small_doors = small

    def b_hook_ways(self, b):
        hi = lambda d, c: d[0].animate.set_stroke(c, 6)
        for d in self.doors:                                    # left to right
            self.go(hi(d, ACCENT), run_time=0.3)
        self.go(*[hi(d, MUTED) for d in self.doors], run_time=0.2)
        self.at(b, 1)
        self.go(hi(self.doors[2], BACK), Indicate(self.doors[2], color=BACK), run_time=0.7)   # the newest
        self.go(hi(self.doors[2], MUTED), run_time=0.2)
        self.at(b, 2)
        tags = VGroup(*[chip(str(c), GOLD, 26, "#0F172A").next_to(d, UP, buff=0.15)
                        for d, c in zip(self.doors, (16, 10, 21))])
        self.show(tags, anim=GrowFromCenter, run_time=0.5)
        self.go(hi(self.doors[1], SAFE), self.doors[1][0].animate.set_fill(SAFE, 0.35), run_time=0.5)
        self.sfx("chime", -0.2)
        self.price_tags = tags

    def b_hook_name(self, b):
        labels_ = VGroup(*[chip(t, c, 26, k) for t, c, k in (("FIFO", ACCENT, TEXT), ("LIFO", BACK, "#0F172A"),
                                                              ("LC", SAFE, TEXT))])
        for l_, d in zip(labels_, self.doors):
            l_.move_to(d)
        self.show(labels_, anim=GrowFromCenter, run_time=0.5)
        self.sfx("pop")
        self.at(b, 1)
        self.clear(run_time=0.4)
        title = label("BRANCH & BOUND", 80, GOLD, "BOLD").move_to(STAGE + UP * 0.4)
        self.show(title, anim=GrowFromCenter, run_time=0.7)
        self.sfx("whoosh")

    def b_syllabus(self, b):
        self.syllabus(b, ["Branch & bound vs backtracking", "FIFO, LIFO and LC search", "Bounds that kill nodes"],
                      unit_text="UNIT III  ·  BRANCH & BOUND")

    def b_exam(self, b):
        self.exam_star(b)

    # ------------------------------------------------------------ branch & bound vs backtracking
    def mini(self, center, title):
        """Root + 3 children + 2 grandchildren under the first child."""
        pos = {"r": (0, 1.0), "a": (-1.2, 0), "b": (0, 0), "c": (1.2, 0), "a1": (-1.6, -1.0), "a2": (-0.8, -1.0)}
        p = {k: np.array([center[0] + x, center[1] + y, 0]) for k, (x, y) in pos.items()}
        edges = [("r", "a"), ("r", "b"), ("r", "c"), ("a", "a1"), ("a", "a2")]
        g = VGroup(*[Line(p[u], p[v], color=PANEL_EDGE, stroke_width=3) for u, v in edges])
        dots = {k: Circle(0.2, color=PANEL_EDGE, fill_color=BG, fill_opacity=1, stroke_width=3).move_to(q)
                for k, q in p.items()}
        head = label(title, 28, TEXT, "BOLD").move_to(np.array([center[0], center[1] + 1.75, 0]))
        return VGroup(head, g, *dots.values()), dots, p

    def b_b_recap(self, b):
        self.unsay()
        self.clear(run_time=0.4)
        grp, dots, p = self.mini(STAGE + UP * 0.2, "")
        self.show(grp, run_time=0.5)
        self.at(b, 1)
        live = [dots[k].animate.set_stroke(LIVE_C, 5) for k in ("b", "c")]
        ring = Circle(0.3, color=E_C, stroke_width=6).move_to(p["a"])
        legend = VGroup(chip("live", LIVE_C, 22), chip("E-node", E_C, 22, "#0F172A")).arrange(RIGHT, buff=0.4)
        legend.move_to(STAGE + DOWN * 2.0)
        self.stage.add(ring, legend)
        self.go(*live, Create(ring), FadeIn(legend), run_time=0.8)

    def b_b_bt(self, b):
        self.clear(run_time=0.4)
        self.bt, self.bt_dots, self.bt_p = self.mini(STAGE + LEFT * 3.2 + UP * 0.1, "Backtracking")
        self.bb, self.bb_dots, self.bb_p = self.mini(STAGE + RIGHT * 3.2 + UP * 0.1, "Branch & bound")
        self.show(self.bt, self.bb, run_time=0.5)
        self.at(b, 1)
        ring = Circle(0.3, color=E_C, stroke_width=6).move_to(self.bt_p["r"])
        self.stage.add(ring)
        self.go(Create(ring), run_time=0.3)
        for k in ("a", "a1"):                                    # each new child becomes the E-node at once
            self.go(self.bt_dots[k].animate.set_stroke(TEXT, 4), ring.animate.move_to(self.bt_p[k]), run_time=0.5)
            self.sfx("place", -0.4)
        tag = chip("dives deep", BACK, 22, "#0F172A").next_to(self.bt, DOWN, buff=0.2)
        self.show(tag, run_time=0.3)

    def b_b_bb(self, b):
        ring = Circle(0.3, color=E_C, stroke_width=6).move_to(self.bb_p["r"])
        self.stage.add(ring)
        self.go(Create(ring), run_time=0.3)
        for k in ("a", "b", "c"):                                # all children first, E-node stays put
            self.go(self.bb_dots[k].animate.set_stroke(LIVE_C, 5), run_time=0.4)
            self.sfx("place", -0.3)
        self.at(b, 1)
        self.go(ring.animate.move_to(self.bb_p["b"]), run_time=0.6)
        tag = chip("then picks the next E-node", ACCENT, 22).next_to(self.bb, DOWN, buff=0.2)
        self.show(tag, run_time=0.3)

    def b_b_list(self, b):
        self.clear(run_time=0.4)
        q = label("Which live node next?", 48, TEXT, "BOLD").move_to(STAGE + UP * 0.9)
        nodes = VGroup(*[chip(str(v), LIVE_C, 30) for v in (2, 3, 4)]).arrange(RIGHT, buff=0.5).move_to(STAGE + DOWN * 0.5)
        self.show(q, run_time=0.5)
        self.show(nodes, anim=GrowFromCenter, run_time=0.5)

    # ------------------------------------------------------------ the three strategies
    def strategy_card(self, i, title, col, dark, lines, icon):
        t = chip(title, col, 26, "#0F172A" if dark else TEXT)
        body = VGroup(*[label(s, 22, TEXT) for s in lines]).arrange(DOWN, buff=0.08)
        g = VGroup(t, icon, body).arrange(DOWN, buff=0.3)
        box = card(3.9, 4.3)
        return VGroup(box, g.move_to(box)).move_to(STAGE + np.array([-4.2 + 4.2 * i, 0.15, 0]))

    def b_s_fifo(self, b):
        self.clear(run_time=0.4)
        icon = VGroup(*[chip(str(v), LIVE_C, 22) for v in (2, 3, 4)]).arrange(RIGHT, buff=0.12)
        icon.add(Arrow(icon.get_right() + RIGHT * 0.7, icon.get_right() + RIGHT * 0.1, buff=0, color=MUTED, stroke_width=4),
                 Arrow(icon.get_left() + LEFT * 0.1, icon.get_left() + LEFT * 0.7, buff=0, color=MUTED, stroke_width=4))
        c = self.strategy_card(0, "FIFO", ACCENT, False, ["queue", "first in, first out", "level by level"], icon)
        self.show(c, run_time=0.6, shift=UP * 0.2)

    def b_s_lifo(self, b):
        icon = VGroup(*[chip(str(v), LIVE_C, 22) for v in (4, 3, 2)]).arrange(DOWN, buff=0.08)
        top = label("top", 18, MUTED).next_to(icon, RIGHT, buff=0.15).align_to(icon, UP)
        c = self.strategy_card(1, "LIFO", BACK, True, ["stack", "last in, first out", "goes deep"], VGroup(icon, top))
        self.show(c, run_time=0.6, shift=UP * 0.2)

    def b_s_lc(self, b):
        icon = VGroup(*[chip(t, LIVE_C, 22) for t in ("3 (10)", "2 (16)", "4 (21)")]).arrange(RIGHT, buff=0.1)
        c = self.strategy_card(2, "LC", SAFE, False, ["least cost", "smallest ĉ first", "goes where it is cheap"], icon)
        self.show(c, run_time=0.6, shift=UP * 0.2)

    # ------------------------------------------------------------ one tree, three searches
    def setup_tree(self):
        self.tree = BBTree(CHILDREN, CHAT, ANSWER, POS, STAGE + LEFT * 2.2 + DOWN * 0.15, scale=0.92)
        return self.tree

    def start_strategy(self, b, kind):
        t = self.tree
        if t.ring is not None:
            self.drop(t.ring, *getattr(self, "marks", []))
            t.ring = None
        if getattr(self, "live", None) is not None:
            self.drop(self.live, *[c for _, c in self.live.items])
        self.marks = []
        self.go(*t.reset(), run_time=0.4)
        self.live = LiveList(kind, STAGE + RIGHT * 4.3 + UP * 0.9)
        self.show(self.live, run_time=0.4)
        self.go(*t.gen(1), *t.enode(self, 1), run_time=0.4)
        new, lay = self.live.add_nodes([2, 3, 4], CHAT, t.p)
        self.stage.add(*new)
        self.go(*[a for v in (2, 3, 4) for a in t.gen(v)], *[FadeIn(c) for c in new], run_time=0.6)
        self.go(*lay, run_time=0.5)
        self.sfx("place", -0.4)

    def point_next(self, b):
        self.at(b, 1)
        v, c = self.live.next_node()
        self.go(Indicate(c, color=GOLD, scale_factor=1.3), Indicate(self.tree.node[v], color=GOLD), run_time=0.8)

    def pop_and_find(self, b, answer_v, color, text):
        t = self.tree
        v, _ = self.live.next_node()
        c, lay = self.live.remove(v)
        self.stage.remove(c)
        self.go(FadeOut(c, shift=UP * 0.3), *lay, *t.enode(self, v), run_time=0.6)
        self.go(*t.gen(answer_v), run_time=0.4)
        self.sfx("place", -0.3)
        self.go(*t.found(answer_v, color), run_time=0.5)
        res = chip(text, color, 24, "#0F172A" if color in (GOLD, BACK) else TEXT).next_to(t.node[answer_v], DOWN, buff=0.15)
        self.marks.append(res)
        self.show(res, anim=GrowFromCenter, run_time=0.4)
        self.sfx("chime" if color == SAFE else "pop")

    def b_t_intro(self, b):
        self.clear(run_time=0.4)
        t = self.setup_tree()
        legend = VGroup(VGroup(Circle(0.14, color=MUTED, stroke_width=3), label("node", 20, MUTED)).arrange(RIGHT, buff=0.12),
                        VGroup(RoundedRectangle(width=0.28, height=0.28, corner_radius=0.05, color=MUTED, stroke_width=3),
                               label("answer node", 20, MUTED)).arrange(RIGHT, buff=0.12),
                        VGroup(label("16", 20, GOLD, "BOLD"), label("= ĉ", 20, MUTED)).arrange(RIGHT, buff=0.12)
                        ).arrange(RIGHT, buff=0.5).move_to(STAGE + LEFT * 2.2 + DOWN * 2.4)
        self.show(t, legend, run_time=0.8)
        self.at(b, 1)
        self.go(LaggedStart(*[Indicate(t.tag[v], color=GOLD, scale_factor=1.6) for v in sorted(t.tag)], lag_ratio=0.1),
                run_time=1.6)

    def b_t_fifo1(self, b):
        self.start_strategy(b, "FIFO")
        self.point_next(b)

    def b_t_fifo2(self, b):
        self.pop_and_find(b, 5, BACK, "FIFO: cost 18")

    def b_t_lifo1(self, b):
        self.start_strategy(b, "LIFO")
        self.point_next(b)

    def b_t_lifo2(self, b):
        self.pop_and_find(b, 9, KILL, "LIFO: cost 25")

    def b_t_lc1(self, b):
        self.start_strategy(b, "LC")
        self.point_next(b)

    def b_t_lc2(self, b):
        self.pop_and_find(b, 7, SAFE, "LC: cost 12 ✓")
        self.at(b, 1)
        best = chip("cheapest answer in the tree", SAFE, 24).next_to(self.live, DOWN, buff=0.6)
        self.marks.append(best)
        self.show(best, anim=GrowFromCenter, run_time=0.4)

    def b_t_compare(self, b):
        self.clear(run_time=0.4)
        self.tree = None
        self.live = None
        rows = [("FIFO", ACCENT, TEXT, "node 5", "18"), ("LIFO", BACK, "#0F172A", "node 9", "25"),
                ("LC", SAFE, TEXT, "node 7", "12  ✓")]
        cards = VGroup()
        for name, col, tc, node, cost in rows:
            g = VGroup(chip(name, col, 30, tc), label(node, 26, MUTED), label("cost " + cost, 40, TEXT, "BOLD")
                       ).arrange(DOWN, buff=0.3)
            box = card(3.4, 3.0, edge=SAFE if name == "LC" else PANEL_EDGE)
            cards.add(VGroup(box, g.move_to(box)))
        cards.arrange(RIGHT, buff=0.5).move_to(STAGE + UP * 0.3)
        self.stage.add(cards)
        self.at(b, 1)
        self.go(LaggedStart(*[FadeIn(c, shift=UP * 0.3) for c in cards], lag_ratio=0.5), run_time=2.0)
        self.sfx("chime", -0.3)

    # ------------------------------------------------------------ the cost function
    def b_c_formula(self, b):
        self.clear(run_time=0.4)
        self.at(b, 1)
        f = MathTex(r"\hat{c}(x)", r"=", r"f(h(x))", r"+", r"\hat{g}(x)", color=TEXT).scale(1.8).move_to(STAGE + UP * 1.0)
        self.formula = f
        self.show(f, anim=Write, run_time=1.4)

    def b_c_parts(self, b):
        f = self.formula
        h = VGroup(Brace(f[2], DOWN, color=ACCENT), label("cost from the root to x", 24, ACCENT))
        h[1].next_to(h[0], DOWN, buff=0.1).align_to(h[0], RIGHT)
        self.show(h, run_time=0.6)
        self.at(b, 1)
        g = VGroup(Brace(f[4], DOWN, color=GOLD), label("estimated cost from x", 24, GOLD),
                   label("to the nearest answer node", 24, GOLD))
        g[1].next_to(g[0], DOWN, buff=0.1).align_to(g[0], LEFT)
        g[2].next_to(g[1], DOWN, buff=0.05).align_to(g[1], LEFT)
        self.show(g, run_time=0.6)

    def b_c_lower(self, b):
        t = VGroup(label("Minimisation:", 28, TEXT, "BOLD"),
                   MathTex(r"\hat{c}(x) \;\leq\; \text{cost of every answer below } x", color=SAFE).scale(0.9)
                   ).arrange(RIGHT, buff=0.4)
        box = card(t.width + 0.8, t.height + 0.6, edge=SAFE)
        self.show(VGroup(box, t.move_to(box)).move_to(STAGE + DOWN * 2.2), run_time=0.6, shift=UP * 0.2)
        self.at(b, 1)
        lb = chip("a lower bound", SAFE, 26).move_to(STAGE + RIGHT * 4.6 + UP * 2.6)
        self.show(lb, anim=GrowFromCenter, run_time=0.4)

    # ------------------------------------------------------------ bounding: FIFO finds the cheapest answer
    def b_u_intro(self, b):
        self.clear(run_time=0.4)
        self.setup_tree()
        self.show(self.tree, run_time=0.6)
        self.at(b, 1)
        self.u_val = MathTex(r"U = \infty", color=GOLD).scale(1.4)
        self.u_box = card(3.0, 1.3, edge=GOLD)
        self.u_val.move_to(self.u_box)
        self.u_grp = VGroup(self.u_box, self.u_val).move_to(STAGE + RIGHT * 4.4 + UP * 1.6)
        sub = label("best answer so far", 20, MUTED).next_to(self.u_grp, DOWN, buff=0.1)
        self.show(self.u_grp, sub, run_time=0.5)

    def set_u(self, value):
        new = MathTex(f"U = {value}", color=GOLD).scale(1.4).move_to(self.u_box)
        old = self.u_val
        self.u_val = new
        self.u_grp.remove(old)
        self.u_grp.add(new)
        self.stage.add(new)
        self.go(ReplacementTransform(old, new), Indicate(self.u_box, color=GOLD), run_time=0.6)
        self.sfx("chime", -0.3)

    def b_u_rule(self, b):
        self.at(b, 1)
        rule = VGroup(MathTex(r"\hat{c}(x) > U", color=KILL).scale(1.1), label("⇒  kill x", 28, KILL, "BOLD")
                      ).arrange(RIGHT, buff=0.3)
        box = card(rule.width + 0.6, 1.0, edge=KILL)
        self.rule = VGroup(box, rule.move_to(box)).move_to(STAGE + RIGHT * 4.4 + DOWN * 0.2)
        self.show(self.rule, run_time=0.5, shift=UP * 0.2)

    def b_u_trace1(self, b):
        t = self.tree
        self.marks = []
        self.go(*t.gen(1), *t.enode(self, 1), *[a for v in (2, 3, 4) for a in t.gen(v)], run_time=0.7)
        self.sfx("place", -0.5)
        self.at(b, 1)
        self.go(*t.enode(self, 2), run_time=0.4)
        self.go(*t.gen(5), *t.gen(6), run_time=0.5)
        self.go(*t.found(5, BACK), *t.found(6, BACK), run_time=0.4)
        self.set_u(18)

    def b_u_trace2(self, b):
        t = self.tree
        self.go(*t.enode(self, 3), run_time=0.4)
        self.go(*t.gen(7), *t.gen(8), run_time=0.5)
        self.go(*t.found(7, SAFE), *t.found(8, BACK), run_time=0.4)
        self.at(b, 1)
        self.set_u(12)

    def b_u_kill(self, b):
        t = self.tree
        self.go(*t.enode(self, 4), run_time=0.4)
        cmp_ = MathTex(r"21 > 12", color=KILL).scale(1.0).next_to(t.node[4], RIGHT, buff=0.35)
        self.show(cmp_, run_time=0.4)
        x, anims = t.kill(4)
        self.stage.add(x)
        self.go(*anims, run_time=0.5)
        self.sfx("kill", -0.4)
        for v in (9, 10):                                     # its children are never generated
            self.go(t.node[v].animate.set_opacity(0.15), t.tag[v].animate.set_opacity(0.15),
                    t.edges[v].animate.set_opacity(0.15), run_time=0.25)
        self.at(b, 1)
        best = chip("best answer: node 7, cost 12", SAFE, 24).next_to(self.rule, DOWN, buff=0.4)
        self.show(best, anim=GrowFromCenter, run_time=0.4)
        self.go(Indicate(t.node[7], color=SAFE, scale_factor=1.4), run_time=0.6)

    def b_u_upper(self, b):
        self.clear(run_time=0.4)
        line = NumberLine(x_range=[0, 26, 2], length=10, include_numbers=True, font_size=24, color=MUTED)
        line.move_to(STAGE + DOWN * 0.2)
        self.show(line, run_time=0.5)
        dots = VGroup()
        for v in (2, 3, 4):
            d = Dot(line.n2p(CHAT[v]), radius=0.12, color=LIVE_C)
            dots.add(VGroup(d, label(f"ĉ({v})", 20, LIVE_C).next_to(d, UP, buff=0.15)))
        self.show(dots, run_time=0.5)
        lower = chip("lower bounds ĉ(x)", LIVE_C, 22).move_to(STAGE + DOWN * 1.9 + LEFT * 3.4)
        self.show(lower, run_time=0.3)
        self.at(b, 1)
        u = DashedLine(line.n2p(12) + DOWN * 0.8, line.n2p(12) + UP * 1.1, color=GOLD, stroke_width=5)
        ul = chip("U = 12  (upper bound)", GOLD, 22, "#0F172A").next_to(u, UP, buff=0.1)
        zone = Rectangle(width=line.n2p(26)[0] - line.n2p(12)[0], height=1.6, fill_color=KILL, fill_opacity=0.15,
                         stroke_width=0).move_to(line.n2p(19) + UP * 0.15)
        cut = label("cut away", 24, KILL, "BOLD").move_to(zone).shift(DOWN * 1.1)
        self.show(zone, u, ul, cut, run_time=0.6)
        self.go(*[dots[i][0].animate.set_color(KILL) for i in (0, 2)], run_time=0.4)
        self.sfx("kill", -0.3)

    # ------------------------------------------------------------ control abstraction
    def b_a_code(self, b):
        self.clear(run_time=0.4)
        self.code = CodePanel(["Algorithm LCSearch(t)",
                               "{",
                               "  if (t is an answer node) then output t and return;",
                               "  E := t;  // E-node",
                               "  initialise the list of live nodes to be empty;",
                               "  repeat",
                               "  {",
                               "    for each child x of E do",
                               "    {",
                               "      if (x is an answer node) then",
                               "        output the path from x to t and return;",
                               "      Add(x);  (x -> parent) := E;",
                               "    }",
                               "    if (no live nodes left) then",
                               "      write (\"No answer node\"); return;",
                               "    E := Least();",
                               "  } until (false);",
                               "}"], font_size=19)
        self.code.scale_to_fit_height(min(self.code.height, 5.9)).move_to(STAGE + LEFT * 1.4 + DOWN * 0.3)
        self.show(self.code, run_time=0.6)
        self.go(self.code.highlight(0))
        self.at(b, 1)
        self.go(self.code.highlight(3))
        self.go(self.code.highlight(4))

    def b_a_loop(self, b):
        self.go(self.code.highlight(7))
        self.go(self.code.highlight(9))
        self.go(self.code.highlight(10))
        self.at(b, 1)
        self.go(self.code.highlight(11))

    def b_a_least(self, b):
        self.go(self.code.highlight(15))
        self.at(b, 1)
        note = VGroup(label("Least()", 26, SAFE, "BOLD"), label("live node with", 22, TEXT),
                      label("the smallest ĉ", 22, TEXT)).arrange(DOWN, buff=0.08)
        box = card(3.0, note.height + 0.5, edge=SAFE)
        self.least_note = VGroup(box, note.move_to(box)).move_to(STAGE + RIGHT * 5.0 + UP * 1.0)
        self.show(self.least_note, run_time=0.5)

    def b_a_swap(self, b):
        self.at(b, 1)
        swaps = VGroup(chip("queue  →  FIFO", ACCENT, 22), chip("stack  →  LIFO", BACK, 22, "#0F172A"))
        swaps.arrange(DOWN, buff=0.25).next_to(self.least_note, DOWN, buff=0.4)
        self.stage.add(swaps)
        self.go(LaggedStart(*[FadeIn(s, shift=LEFT * 0.3) for s in swaps], lag_ratio=0.5), run_time=1.0)
        self.sfx("pop")

    # ------------------------------------------------------------ practice
    def b_p_intro(self, b):
        self.clear(run_time=0.4)
        head = label("YOUR TURN", 34, GOLD, "BOLD").move_to(STAGE + UP * 2.9)
        self.show(head, anim=GrowFromCenter, run_time=0.4)
        self.sfx("pop")
        self.ptree = BBTree(P_CHILDREN, P_CHAT, P_ANSWER, P_POS, STAGE + RIGHT * 0.6 + DOWN * 0.1, scale=0.95)
        self.show(self.ptree, run_time=0.6)
        self.at(b, 1)
        q = label("Order of E-nodes under LC search?", 32, TEXT, "BOLD").move_to(STAGE + DOWN * 2.3)
        self.show(q, run_time=0.5)
        self.p_question = q

    def b_p_pause(self, b):
        self.drop(self.p_question)
        pause = chip("⏸  Pause and work it out", GOLD, 28, "#0F172A").move_to(STAGE + DOWN * 2.3)
        self.show(pause, anim=GrowFromCenter, run_time=0.4)
        self.p_pause_chip = pause
        self.at(b, 1)
        if CAMEO and "p_pause" in CAMEOS:     # you wait on camera while they work it out
            self.cameo_in(CAMEOS["p_pause"])

    def b_p_answer(self, b):
        self.pause_over()
        self.drop(self.p_pause_chip)
        t = self.ptree
        live = LiveList("LC", STAGE + RIGHT * 5.0 + UP * 0.9, width=3.6)
        self.show(live, run_time=0.3)
        order = VGroup()
        steps = [(1, [2, 3, 4]), (3, [5, 6]), (4, [7])]
        for i, (e, kids) in enumerate(steps):
            if i == 1:
                self.at(b, 0)
            if e != 1:
                c, lay = live.remove(e)
                self.stage.remove(c)
                self.go(FadeOut(c, shift=UP * 0.3), *lay, run_time=0.4)
            self.go(*t.gen(e), *t.enode(self, e), run_time=0.45)
            o = chip(str(e), E_C, 26, "#0F172A")
            order.add(o)
            order.arrange(RIGHT, buff=0.25).move_to(STAGE + DOWN * 2.3)
            self.stage.add(o)
            self.go(FadeIn(o), run_time=0.3)
            if e == 4:
                self.go(*t.gen(7), run_time=0.4)
                self.go(*t.found(7, SAFE), run_time=0.4)
                self.sfx("chime")
                break
            new, lay = live.add_nodes(kids, P_CHAT, t.p)
            self.stage.add(*new)
            self.go(*[a for v in kids for a in t.gen(v)], *[FadeIn(c) for c in new], run_time=0.5)
            self.go(*lay, run_time=0.4)
            self.sfx("place", -0.3)
        self.at(b, 1)
        ans = chip("E-nodes: 1, 3, 4  ·  answer: node 7", SAFE, 24).next_to(order, DOWN, buff=0.25)
        self.show(ans, anim=GrowFromCenter, run_time=0.4)

    # ------------------------------------------------------------ tips, recap
    def b_tip1(self, b):
        self.tip(b, 1, "B&B: the E-node stays until it is dead", "backtracking switches to each new child at once")

    def b_tip2(self, b):
        self.tip(b, 2, "Draw the live-node list at every step", "queue (FIFO), stack (LIFO), sorted by ĉ (LC)")

    def b_tip3(self, b):
        self.tip(b, 3, "ĉ(x) = f(h(x)) + ĝ(x)", "and the kill rule: ĉ(x) > U")

    def b_recap(self, b):
        self.recap(b, ["Expand an E-node completely, then choose the next",
                       "FIFO: queue  ·  LIFO: stack  ·  LC: smallest ĉ",
                       "Kill a node when ĉ(x) > U"])
