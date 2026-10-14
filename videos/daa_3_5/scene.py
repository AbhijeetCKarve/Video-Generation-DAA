"""Video 3.5 - 0/1 Knapsack & TSP with Branch & Bound. Rendered by build.py (needs SCHEDULE / ENVELOPE env vars)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from lesson import *  # noqa: E402,F401,F403

P, W, M = [10, 10, 12, 18], [2, 4, 6, 9], 15
INF = float("inf")
COST = [[INF, 20, 30, 10, 11], [15, INF, 16, 4, 2], [3, 5, INF, 2, 4], [19, 6, 18, INF, 3], [16, 4, 7, 16, INF]]
ROW_RED = [[INF, 10, 20, 0, 1], [13, INF, 14, 2, 0], [1, 3, INF, 0, 2], [16, 3, 15, INF, 0], [12, 0, 3, 12, INF]]
ROOT_RED = [[INF, 10, 17, 0, 1], [12, INF, 11, 2, 0], [0, 3, INF, 0, 2], [15, 3, 12, INF, 0], [11, 0, 0, 12, INF]]
# child 1 -> 4: row 1 and column 4 out, 4 -> 1 blocked, then reduced (no further reduction needed)
CHILD_14 = [[INF, INF, INF, INF, INF], [12, INF, 11, INF, 0], [0, 3, INF, INF, 2], [INF, 3, 12, INF, 0],
            [11, 0, 0, INF, INF]]
E_C, LIVE_C = GOLD, ACCENT


def cell_text(v):
    return "∞" if v == INF else str(v)


class Matrix(VGroup):
    """A cost matrix as a grid of cells with row/column labels; values can be swapped with animations."""

    def __init__(self, data, center, size=0.62, font=26, **kw):
        super().__init__(**kw)
        self.n, self.size = len(data), size
        self.vals = [row[:] for row in data]
        self.cell = {}
        self.box = {}
        for r in range(self.n):
            for c in range(self.n):
                q = np.array([center[0] + (c - 2) * size, center[1] - (r - 2) * size, 0])
                b = Square(size, stroke_color=PANEL_EDGE, stroke_width=2, fill_color=PANEL, fill_opacity=1).move_to(q)
                t = label(cell_text(data[r][c]), font, TEXT if data[r][c] != INF else MUTED).move_to(q)
                self.box[(r, c)], self.cell[(r, c)] = b, t
                self.add(b, t)
        self.rlab = VGroup(*[label(str(r + 1), 20, MUTED, "BOLD").move_to(self.box[(r, 0)].get_center() + LEFT * size)
                             for r in range(self.n)])
        self.clab = VGroup(*[label(str(c + 1), 20, MUTED, "BOLD").move_to(self.box[(0, c)].get_center() + UP * size)
                             for c in range(self.n)])
        self.add(self.rlab, self.clab)

    def set_values(self, data, color=TEXT):
        """Animations that replace every changed cell's number."""
        anims = []
        for r in range(self.n):
            for c in range(self.n):
                if data[r][c] != self.vals[r][c]:
                    new = label(cell_text(data[r][c]), 26, color if data[r][c] != INF else MUTED).move_to(self.cell[(r, c)])
                    anims.append(Transform(self.cell[(r, c)], new))   # the cell stays in this group (no ghosts)
        self.vals = [row[:] for row in data]
        return anims

    def row_rect(self, r, color):
        g = VGroup(*[self.box[(r, c)] for c in range(self.n)])
        return SurroundingRectangle(g, color=color, buff=0.0, stroke_width=4)

    def col_rect(self, c, color):
        g = VGroup(*[self.box[(r, c)] for r in range(self.n)])
        return SurroundingRectangle(g, color=color, buff=0.0, stroke_width=4)

    def min_cells(self, line, kind):
        vals = [self.vals[line][c] for c in range(self.n)] if kind == "row" else [self.vals[r][line] for r in range(self.n)]
        lo = min(vals)
        i = vals.index(lo)
        return (self.cell[(line, i)] if kind == "row" else self.cell[(i, line)]), lo


class KTree(VGroup):
    """The knapsack LC tree: fixed positions, nodes appear with an (optimistic / guaranteed) tag."""

    def __init__(self, center, **kw):
        super().__init__(**kw)
        self.pos = {"r": (0, 1.9), "1": (-1.5, 0.75), "0": (1.5, 0.75), "11": (-2.4, -0.4), "10": (-0.6, -0.4),
                    "111": (-3.1, -1.55), "110": (-1.7, -1.55)}
        self.p = {k: np.array([center[0] + x, center[1] + y, 0]) for k, (x, y) in self.pos.items()}
        self.node, self.tag, self.edge = {}, {}, {}
        self.ring = None

    def make(self, key, text, opt, guar, color=TEXT):
        q = self.p[key]
        shape = Circle(0.34, color=color, fill_color=BG, fill_opacity=1, stroke_width=4).move_to(q)
        t = label(text, 15, color, "BOLD").move_to(q)
        tag = VGroup(label(str(opt), 20, GOLD, "BOLD"), label("/", 18, MUTED), label(str(guar), 20, SAFE, "BOLD")
                     ).arrange(RIGHT, buff=0.06).next_to(shape, DOWN, buff=0.08)
        self.node[key], self.tag[key] = VGroup(shape, t), tag
        anims = [GrowFromCenter(self.node[key]), FadeIn(tag)]
        if len(key) > 1 or key != "r":
            parent = "r" if len(key) == 1 else key[:-1]
            if key != "r":
                d = (q - self.p[parent]) / np.linalg.norm(q - self.p[parent])
                ln = Line(self.p[parent] + d * 0.3, q - d * 0.3, color=MUTED, stroke_width=3)
                self.edge[key] = ln
                self.add(ln)
                anims.insert(0, Create(ln))
        self.add(self.node[key], tag)
        return anims

    def enode(self, scene, key):
        if self.ring is None:
            self.ring = Circle(0.4, color=E_C, stroke_width=6).move_to(self.p[key])
            scene.add(self.ring)
            scene.stage.add(self.ring)
            return [Create(self.ring)]
        return [self.ring.animate.move_to(self.p[key])]


class Video(Lesson):
    NEXT = ("4.1  P vs NP:", "Deterministic & non-deterministic")

    # ------------------------------------------------------------ hook
    def item_card(self, i, small=False):
        s = 0.8 if small else 1.0
        g = VGroup(label(f"item {i + 1}", 20 * s, MUTED), label(f"₹{P[i]}", 30 * s, GOLD, "BOLD"),
                   label(f"{W[i]} kg", 22 * s, TEXT)).arrange(DOWN, buff=0.08 * s)
        box = card(1.5 * s, 1.75 * s)
        return VGroup(box, g.move_to(box))

    def b_hook_bag(self, b):
        bag = VGroup(RoundedRectangle(width=2.2, height=2.6, corner_radius=0.3, fill_color=PANEL, fill_opacity=1,
                                      stroke_color=GOLD, stroke_width=4),
                     Arc(radius=0.6, start_angle=0, angle=np.pi, color=GOLD, stroke_width=6).shift(UP * 1.3))
        bag.add(label("15 kg", 34, GOLD, "BOLD").move_to(bag[0]))
        bag.move_to(STAGE + LEFT * 3.6 + UP * 0.2)
        self.show(bag, run_time=0.6)
        self.at(b, 1)
        items = VGroup(*[self.item_card(i) for i in range(4)]).arrange(RIGHT, buff=0.3).move_to(STAGE + RIGHT * 1.6 + UP * 0.2)
        self.show(items, run_time=0.8, lag_ratio=0.2)
        self.sfx("pop")
        self.hook_items = items

    def b_hook_tsp(self, b):
        self.clear(run_time=0.4)
        pts = {k + 1: STAGE + np.array([1.9 * np.sin(2 * np.pi * k / 5), 0.3 + 1.9 * np.cos(2 * np.pi * k / 5), 0])
               for k in range(5)}
        g = VGroup(*[Line(pts[a], pts[b_], color=PANEL_EDGE, stroke_width=2) for a in pts for b_ in pts if a < b_])
        dots = VGroup(*[VGroup(Circle(0.3, color=TEXT, fill_color=PANEL, fill_opacity=1, stroke_width=3).move_to(q),
                               label(str(k), 22, TEXT, "BOLD").move_to(q)) for k, q in pts.items()])
        self.show(g, dots, run_time=0.7)
        self.at(b, 1)
        c = chip("24 possible tours - which is cheapest?", KILL, 26).move_to(STAGE + DOWN * 2.5)
        self.show(c, anim=GrowFromCenter, run_time=0.5)
        self.sfx("pop")

    def b_hook_name(self, b):
        self.clear(run_time=0.4)
        title = label("LC BRANCH & BOUND", 72, GOLD, "BOLD").move_to(STAGE + UP * 0.7)
        self.show(title, anim=GrowFromCenter, run_time=0.7)
        self.sfx("whoosh")
        self.at(b, 1)
        sub = chip("+ a clever lower bound for each problem", ACCENT, 28).move_to(STAGE + DOWN * 0.8)
        self.show(sub, run_time=0.5)

    def b_syllabus(self, b):
        self.syllabus(b, ["0/1 Knapsack with LC search", "TSP with the reduced cost matrix"],
                      unit_text="UNIT III  ·  BRANCH & BOUND")

    def b_exam(self, b):
        self.exam_star(b)

    # ------------------------------------------------------------ knapsack: the model
    def item_table(self, pos, ratio=False):
        rows = [["item", "p", "w"] + (["p/w"] if ratio else [])]
        for i in range(4):
            rows.append([str(i + 1), str(P[i]), str(W[i])] + ([f"{P[i] / W[i]:g}"] if ratio else []))
        grid = VGroup()
        for r, row in enumerate(rows):
            line = VGroup(*[label(t, 22, MUTED if r == 0 else TEXT, "BOLD" if r == 0 else "NORMAL") for t in row])
            for j, t in enumerate(line):
                t.move_to(np.array([j * 0.9, -r * 0.5, 0]))
            grid.add(line)
        box = card(grid.width + 0.6, grid.height + 0.5)
        return VGroup(box, grid.move_to(box)).move_to(pos)

    def b_k_problem(self, b):
        self.unsay()
        self.clear(run_time=0.4)
        title = label("0/1 Knapsack", 44, TEXT, "BOLD").move_to(STAGE + UP * 2.2)
        self.show(title, run_time=0.5)
        self.at(b, 1)
        self.table = self.item_table(STAGE + LEFT * 3.0 + DOWN * 0.3)
        cap = chip("capacity m = 15", GOLD, 26, "#0F172A").move_to(STAGE + RIGHT * 2.6 + DOWN * 0.3)
        self.show(self.table, cap, run_time=0.6)
        self.k_title, self.cap = title, cap

    def b_k_ratio(self, b):
        new = self.item_table(STAGE + LEFT * 3.0 + DOWN * 0.3, ratio=True)
        self.go(Transform(self.table, new), run_time=0.6)        # the table stays the stage's object
        self.at(b, 1)
        ok = chip("already in p/w order ✓", SAFE, 24).move_to(STAGE + RIGHT * 2.6 + DOWN * 1.3)
        self.show(ok, anim=GrowFromCenter, run_time=0.4)

    def b_k_bounds(self, b):
        self.clear(run_time=0.4)
        node = Circle(0.5, color=TEXT, stroke_width=4).move_to(STAGE + LEFT * 3.5 + UP * 0.3)
        tag = VGroup(label("38", 36, GOLD, "BOLD"), label("/", 30, MUTED), label("32", 36, SAFE, "BOLD")
                     ).arrange(RIGHT, buff=0.1).next_to(node, DOWN, buff=0.2)
        self.show(node, tag, run_time=0.5)
        self.at(b, 1)
        r1 = VGroup(chip("optimistic", GOLD, 26, "#0F172A"), label("fill the rest fractionally", 26, TEXT)).arrange(RIGHT, buff=0.4)
        r2 = VGroup(chip("guaranteed", SAFE, 26), label("whole items only", 26, TEXT)).arrange(RIGHT, buff=0.4)
        rows = VGroup(r1, r2).arrange(DOWN, aligned_edge=LEFT, buff=0.5).move_to(STAGE + RIGHT * 1.6 + UP * 0.3)
        self.stage.add(rows)
        self.go(FadeIn(r1, shift=RIGHT * 0.3), run_time=0.5)
        self.at(b, 2)
        self.go(FadeIn(r2, shift=RIGHT * 0.3), run_time=0.5)
        self.sfx("pop")

    def b_k_root(self, b):
        self.clear(run_time=0.4)
        self.table = self.item_table(STAGE + LEFT * 4.6 + UP * 1.1, ratio=True).scale(0.85)
        self.show(self.table, run_time=0.4)
        fill = VGroup()
        for i, col in ((0, SAFE), (1, SAFE), (2, SAFE)):
            fill.add(chip(f"item {i + 1}: {W[i]} kg, ₹{P[i]}", col, 22))
        fill.add(chip("1/3 of item 4: 3 kg, ₹6", GOLD, 22, "#0F172A"))
        fill.arrange(DOWN, buff=0.15).move_to(STAGE + RIGHT * 1.2 + UP * 0.9)
        self.stage.add(fill)
        self.go(LaggedStart(*[FadeIn(f, shift=RIGHT * 0.3) for f in fill[:3]], lag_ratio=0.4), run_time=1.2)
        self.at(b, 1)
        self.go(FadeIn(fill[3], shift=RIGHT * 0.3), run_time=0.5)
        self.at(b, 2)
        res = VGroup(label("optimistic  38", 30, GOLD, "BOLD"), label("guaranteed  32", 30, SAFE, "BOLD")
                     ).arrange(DOWN, buff=0.2).move_to(STAGE + RIGHT * 1.2 + DOWN * 1.9)
        self.show(res, run_time=0.5)
        self.sfx("chime")

    def b_k_rule(self, b):
        self.clear(run_time=0.4)
        r1 = VGroup(chip("expand", E_C, 26, "#0F172A"), label("the live node with the best optimistic bound", 26, TEXT)
                    ).arrange(RIGHT, buff=0.4)
        r2 = VGroup(chip("kill", KILL, 26), label("when optimistic  <  best guaranteed so far", 26, TEXT)
                    ).arrange(RIGHT, buff=0.4)
        rows = VGroup(r1, r2).arrange(DOWN, aligned_edge=LEFT, buff=0.6).move_to(STAGE + UP * 0.3)
        self.stage.add(rows)
        self.go(FadeIn(r1, shift=RIGHT * 0.3), run_time=0.5)
        self.at(b, 1)
        self.go(FadeIn(r2, shift=RIGHT * 0.3), run_time=0.5)
        self.sfx("pop")

    # ------------------------------------------------------------ knapsack: the trace
    def b_k_x1(self, b):
        self.clear(run_time=0.4)
        self.table = self.item_table(STAGE + LEFT * 4.8 + UP * 1.0, ratio=True).scale(0.8)
        self.show(self.table, run_time=0.4)
        self.kt = KTree(STAGE + RIGHT * 1.4 + UP * 0.2)
        self.stage.add(self.kt)
        self.go(*self.kt.make("r", "", 38, 32), run_time=0.5)
        self.go(*self.kt.enode(self, "r"), run_time=0.3)
        self.go(*self.kt.make("1", "x₁=1", 38, 32), run_time=0.5)
        self.sfx("place", -0.3)
        self.at(b, 1)
        self.go(*self.kt.make("0", "x₁=0", 32, 22), run_time=0.5)
        self.sfx("place", -0.3)
        self.at(b, 2)
        self.go(*self.kt.enode(self, "1"), run_time=0.5)

    def b_k_x2(self, b):
        self.go(*self.kt.make("11", "x₂=1", 38, 32), run_time=0.5)
        self.sfx("place", -0.3)
        self.at(b, 1)
        self.go(*self.kt.make("10", "x₂=0", 36, 22), run_time=0.5)
        self.sfx("place", -0.3)
        self.go(*self.kt.enode(self, "11"), run_time=0.5)

    def b_k_x3(self, b):
        self.go(*self.kt.make("111", "x₃=1", 38, 32), run_time=0.5)
        self.sfx("place", -0.3)
        self.at(b, 1)
        self.go(*self.kt.make("110", "x₃=0", 38, 38, color=SAFE), run_time=0.5)
        self.sfx("chime", -0.2)
        note = chip("items 1, 2, 4 fit whole: 10 + 10 + 18", SAFE, 22).next_to(self.kt.tag["110"], DOWN, buff=0.15)
        self.show(note, anim=GrowFromCenter, run_time=0.4)
        self.k_note = note

    def b_k_answer(self, b):
        self.drop(self.k_note)
        kt = self.kt
        self.go(*[kt.edge[k].animate.set_stroke(SAFE, width=7) for k in ("1", "11", "110")],
                *[kt.node[k][0].animate.set_fill(SAFE, 0.6) for k in ("1", "11", "110")], run_time=0.7)
        self.at(b, 1)
        ans = VGroup(MathTex(r"x = (1,\,1,\,0,\,1)", color=SAFE).scale(1.0),
                     label("profit 38  ·  weight 15", 26, TEXT, "BOLD")).arrange(DOWN, buff=0.15)
        box = card(ans.width + 0.6, ans.height + 0.5, edge=SAFE)
        self.ans = VGroup(box, ans.move_to(box)).move_to(STAGE + RIGHT * 4.3 + DOWN * 1.9)
        self.show(self.ans, run_time=0.5, shift=UP * 0.2)
        self.sfx("chime")

    def b_k_kill(self, b):
        kt = self.kt
        xs = VGroup()
        for k in ("10", "0", "111"):
            x = label("×", 50, KILL, "BOLD").move_to(kt.p[k])
            xs.add(x)
            self.stage.add(x)
            self.go(kt.node[k][0].animate.set_stroke(KILL, 4), FadeIn(x, scale=1.6), run_time=0.35)
            self.sfx("kill", -0.3)
        self.at(b, 1)
        c = chip("4 of 16 choices examined", GOLD, 24, "#0F172A").next_to(self.ans, UP, buff=0.3)
        self.show(c, anim=GrowFromCenter, run_time=0.4)

    def b_k_sign(self, b):
        self.at(b, 1)
        t = VGroup(label("Textbook form (minimisation):", 24, MUTED, "BOLD"),
                   MathTex(r"\hat{c} = -38,\quad u = -32", color=TEXT).scale(0.9)).arrange(DOWN, buff=0.12)
        box = card(t.width + 0.6, t.height + 0.5)
        self.show(VGroup(box, t.move_to(box)).move_to(STAGE + LEFT * 3.6 + DOWN * 2.0), run_time=0.5, shift=UP * 0.2)

    # ------------------------------------------------------------ TSP: the reduced cost matrix
    def b_t_problem(self, b):
        self.clear(run_time=0.4)
        title = label("Travelling salesperson", 44, TEXT, "BOLD").move_to(STAGE + UP * 2.6)
        self.show(title, run_time=0.5)
        self.at(b, 1)
        self.mx = Matrix(COST, STAGE + LEFT * 2.6 + DOWN * 0.3)
        self.show(self.mx, run_time=0.8)
        self.t_title = title
        self.side = VGroup()

    def side_note(self, text, color, i):
        c = chip(text, color, 24, "#0F172A" if color in (GOLD, BACK) else TEXT)
        c.move_to(STAGE + RIGHT * 3.7 + UP * (1.6 - 0.75 * i))
        self.side.add(c)
        self.show(c, anim=GrowFromCenter, run_time=0.4)
        return c

    def b_t_rows(self, b):
        self.drop(self.t_title)
        self.at(b, 1)
        mx = self.mx
        for r in range(5):
            cell, lo = mx.min_cells(r, "row")
            rect = mx.row_rect(r, GOLD)
            self.go(Create(rect), Indicate(cell, color=GOLD), run_time=0.3)
            self.go(FadeOut(rect), run_time=0.15)
        self.go(*mx.set_values(ROW_RED), run_time=0.8)
        self.sfx("pop")
        self.side_note("rows: 10 + 2 + 2 + 3 + 4 = 21", GOLD, 0)

    def b_t_cols(self, b):
        mx = self.mx
        for c in (0, 2):
            rect = mx.col_rect(c, ACCENT)
            self.go(Create(rect), run_time=0.3)
            self.go(FadeOut(rect), run_time=0.15)
        self.go(*mx.set_values(ROOT_RED), run_time=0.8)
        self.sfx("pop")
        self.side_note("columns: 1 + 0 + 3 + 0 + 0 = 4", ACCENT, 1)
        self.at(b, 1)
        self.side_note("ĉ(root) = 21 + 4 = 25", SAFE, 2)
        self.sfx("chime")

    def b_t_child(self, b):
        self.drop(*self.side)
        self.side = VGroup()
        mx = self.mx
        self.at(b, 1)
        rr, cr = mx.row_rect(0, KILL), mx.col_rect(3, KILL)
        self.stage.add(rr, cr)
        self.go(Create(rr), Create(cr), run_time=0.5)
        self.go(*mx.set_values(CHILD_14), run_time=0.8)
        self.sfx("pop")
        blk = chip("4 → 1 blocked: ∞", KILL, 22).move_to(STAGE + RIGHT * 3.7 + UP * 1.6)
        self.side.add(blk)
        self.show(blk, run_time=0.4)
        self.rr, self.cr = rr, cr

    def b_t_child2(self, b):
        f = MathTex(r"\hat{c}(1\!\to\!4) = 25 + 0 + 0 = 25", color=SAFE).scale(0.95).move_to(STAGE + RIGHT * 3.7 + UP * 0.4)
        self.show(f, anim=Write, run_time=1.0)
        self.at(b, 1)
        parts = VGroup(label("parent", 20, MUTED), label("reduced cost of the road", 20, MUTED),
                       label("new reduction", 20, MUTED)).arrange(DOWN, aligned_edge=LEFT, buff=0.08)
        parts.next_to(f, DOWN, buff=0.3).align_to(f, LEFT)
        self.show(parts, run_time=0.5)
        self.sfx("chime")

    def tsp_tree(self, center):
        self.tp = {"1": (0, 2.2), "12": (-2.7, 1.0), "13": (-0.9, 1.0), "14": (0.9, 1.0), "15": (2.7, 1.0),
                   "142": (-0.9, -0.2), "143": (0.9, -0.2), "145": (2.7, -0.2),
                   "1423": (-1.8, -1.4), "1425": (0.0, -1.4), "14253": (0.0, -2.5)}
        self.tq = {k: np.array([center[0] + x, center[1] + y, 0]) for k, (x, y) in self.tp.items()}
        self.tn, self.te = {}, {}

    def tnode(self, key, chat, color=TEXT):
        q = self.tq[key]
        shape = Circle(0.32, color=color, fill_color=BG, fill_opacity=1, stroke_width=4).move_to(q)
        t = label(key[-1], 22, color, "BOLD").move_to(q)
        tag = label(str(chat), 22, GOLD, "BOLD").next_to(shape, RIGHT if key != "1" else UR, buff=0.05)
        node = VGroup(shape, t)
        self.tn[key] = node
        anims = [GrowFromCenter(node), FadeIn(tag)]
        if len(key) > 1:
            parent = key[:-1]
            d = (q - self.tq[parent]) / np.linalg.norm(q - self.tq[parent])
            ln = Line(self.tq[parent] + d * 0.32, q - d * 0.32, color=MUTED, stroke_width=3)
            self.te[key] = ln
            self.stage.add(ln)
            anims.insert(0, Create(ln))
        self.stage.add(node, tag)
        return anims

    def b_t_level1(self, b):
        self.clear(run_time=0.4)
        self.tsp_tree(STAGE + DOWN * 0.1)
        self.go(*self.tnode("1", 25), run_time=0.5)
        self.go(*self.tnode("14", 25, SAFE), run_time=0.5)
        self.sfx("place", -0.3)
        self.at(b, 1)
        for k, c in (("12", 35), ("13", 53), ("15", 31)):
            self.go(*self.tnode(k, c), run_time=0.4)
            self.sfx("place", -0.3)

    def b_t_lc(self, b):
        self.tring = Circle(0.42, color=E_C, stroke_width=6).move_to(self.tq["14"])
        self.stage.add(self.tring)
        self.go(Create(self.tring), run_time=0.4)
        self.at(b, 1)
        for k, c in (("142", 28), ("143", 50), ("145", 36)):
            self.go(*self.tnode(k, c, SAFE if k == "142" else TEXT), run_time=0.4)
            self.sfx("place", -0.3)

    def b_t_path(self, b):
        self.go(self.tring.animate.move_to(self.tq["142"]), run_time=0.4)
        for k, c in (("1423", 52), ("1425", 28)):
            self.go(*self.tnode(k, c, SAFE if k == "1425" else TEXT), run_time=0.4)
            self.sfx("place", -0.3)
        self.at(b, 1)
        self.go(self.tring.animate.move_to(self.tq["1425"]), run_time=0.4)
        self.go(*self.tnode("14253", 28, SAFE), run_time=0.5)
        self.sfx("chime", -0.2)

    def b_t_done(self, b):
        path = ["14", "142", "1425", "14253"]
        self.go(*[self.te[k].animate.set_stroke(SAFE, width=7) for k in path],
                *[self.tn[k][0].animate.set_fill(SAFE, 0.6) for k in ["1"] + path], run_time=0.7)
        tour = chip("1 → 4 → 2 → 5 → 3 → 1   cost 28", SAFE, 26).move_to(STAGE + RIGHT * 4.0 + DOWN * 2.3)
        self.show(tour, anim=GrowFromCenter, run_time=0.5)
        self.sfx("chime")
        self.at(b, 1)
        others = chip("every other live node ≥ 31  →  optimal", GOLD, 22, "#0F172A").next_to(tour, UP, buff=0.3)
        self.show(others, anim=GrowFromCenter, run_time=0.4)

    # ------------------------------------------------------------ pattern, practice, tips, recap
    def b_cmp(self, b):
        self.clear(run_time=0.4)
        left = VGroup(label("Knapsack", 30, TEXT, "BOLD"), label("bound: fractional fill", 24, MUTED),
                      label("maximise profit", 22, MUTED)).arrange(DOWN, buff=0.15)
        right = VGroup(label("TSP", 30, TEXT, "BOLD"), label("bound: reduced cost matrix", 24, MUTED),
                       label("minimise cost", 22, MUTED)).arrange(DOWN, buff=0.15)
        cards = VGroup(*[VGroup(card(4.4, 2.0), g) for g in (left, right)])
        for c_ in cards:
            c_[1].move_to(c_[0])
        cards.arrange(RIGHT, buff=0.5).move_to(STAGE + UP * 1.2)
        self.show(cards, run_time=0.6, lag_ratio=0.3)
        self.at(b, 1)
        steps = ["trusted lower bound", "LC: expand the smallest", "kill the rest"]
        chips_ = VGroup(*[chip(s, c, 24, "#0F172A" if c == GOLD else TEXT) for s, c in zip(steps, [ACCENT, GOLD, KILL])]
                        ).arrange(RIGHT, buff=0.55).move_to(STAGE + DOWN * 1.2)
        arrows = VGroup(*[Arrow(chips_[i].get_right(), chips_[i + 1].get_left(), buff=0.08, color=MUTED,
                                stroke_width=4, max_tip_length_to_length_ratio=0.35) for i in range(2)])
        self.stage.add(chips_, arrows)
        self.go(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in chips_], lag_ratio=0.5), FadeIn(arrows), run_time=1.6)

    def b_p_intro(self, b):
        self.question_card(b, ["Same items, but the bag holds 12 kg.", "The two bounds at the root?"])

    def b_p_pause(self, b):
        self.pause_screen(b, "Pause and work it out")

    def b_p_answer(self, b):
        self.pause_over()
        self.clear(run_time=0.4)
        table = self.item_table(STAGE + LEFT * 3.2 + UP * 0.3, ratio=True)
        self.show(table, run_time=0.4)
        fill = VGroup(*[chip(f"item {i + 1}: {W[i]} kg, ₹{P[i]}", SAFE, 22) for i in range(3)]).arrange(DOWN, buff=0.15)
        fill.move_to(STAGE + RIGHT * 2.2 + UP * 0.6)
        self.stage.add(fill)
        self.go(LaggedStart(*[FadeIn(f, shift=RIGHT * 0.3) for f in fill], lag_ratio=0.4), run_time=1.2)
        w = chip("2 + 4 + 6 = 12 kg exactly", GOLD, 22, "#0F172A").next_to(fill, DOWN, buff=0.3)
        self.show(w, run_time=0.4)
        self.at(b, 1)
        res = VGroup(label("optimistic 32", 30, GOLD, "BOLD"), label("=", 30, MUTED), label("guaranteed 32", 30, SAFE, "BOLD")
                     ).arrange(RIGHT, buff=0.3).move_to(STAGE + DOWN * 2.0)
        self.show(res, anim=GrowFromCenter, run_time=0.5)
        self.sfx("chime")

    def b_tip1(self, b):
        self.tip(b, 1, "Knapsack: order by p/w, write ĉ and u at every node", "the fractional bound and the whole-item bound")

    def b_tip2(self, b):
        self.tip(b, 2, "TSP: show both reductions", "and the reduced matrix of at least one child")

    def b_tip3(self, b):
        self.tip(b, 3, "Say why the answer is optimal", "no live node has a bound that can beat it")

    def b_recap(self, b):
        self.recap(b, ["Knapsack bound: the fractional fill",
                       "TSP bound: the reduced cost matrix",
                       "LC branch & bound: best answer, not every node"])
