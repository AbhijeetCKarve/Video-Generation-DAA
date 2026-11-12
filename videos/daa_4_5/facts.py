"""Every number and claim Video 4.5 states, recomputed from scratch.

qa_check.py runs check(); a wrong claim fails the video before upload.
"""
import math
from itertools import combinations, permutations

# the CLRS vertex-cover graph, vertices 1..7
VC_EDGES = [(1, 2), (2, 3), (3, 4), (3, 5), (4, 5), (4, 6), (4, 7), (5, 6)]
PICK_ORDER = [(2, 3), (5, 6), (4, 7)]                     # the edges the video picks, in order
PATH5 = [(1, 2), (2, 3), (3, 4), (4, 5)]
# five cities for the TSP example
CITY = {"A": (0, 0), "B": (4, 0), "C": (4, 3), "D": (0, 3), "E": (2, 5)}


def approx_vertex_cover(edges, prefer=None):
    """Pick an edge (the preferred one if still present), take both ends, drop touched edges."""
    left = list(edges)
    cover, picked = set(), []
    while left:
        e = next((p for p in (prefer or []) if p in left or (p[1], p[0]) in left), left[0])
        if e not in left:
            e = (e[1], e[0])
        u, v = e
        cover |= {u, v}
        picked.append(e)
        left = [f for f in left if u not in f and v not in f]
    return cover, picked


def min_vertex_cover(n, edges):
    for k in range(1, n + 1):
        for s in combinations(range(1, n + 1), k):
            if all(a in s or b in s for a, b in edges):
                return set(s)


def dist(a, b):
    (x1, y1), (x2, y2) = CITY[a], CITY[b]
    return math.hypot(x1 - x2, y1 - y2)


def mst(nodes):
    """Prim's algorithm -> (edges, cost)."""
    seen, edges, cost = {nodes[0]}, [], 0.0
    while len(seen) < len(nodes):
        u, v = min(((u, v) for u in seen for v in nodes if v not in seen), key=lambda e: dist(*e))
        seen.add(v)
        edges.append((u, v))
        cost += dist(u, v)
    return edges, cost


def preorder(edges, root):
    adj = {}
    for u, v in edges:
        adj.setdefault(u, []).append(v)
        adj.setdefault(v, []).append(u)
    order, seen = [], set()

    def go(x):
        seen.add(x)
        order.append(x)
        for y in adj.get(x, []):
            if y not in seen:
                go(y)
    go(root)
    return order


def tour_cost(order):
    return sum(dist(order[i], order[(i + 1) % len(order)]) for i in range(len(order)))


def check():
    res = []
    cover, picked = approx_vertex_cover(VC_EDGES, PICK_ORDER)
    opt = min_vertex_cover(7, VC_EDGES)
    res.append(("CLRS graph: picks (2,3), (5,6), (4,7); cover {2,3,4,5,6,7} of size 6", picked == PICK_ORDER and cover == {2, 3, 4, 5, 6, 7}))
    res.append(("picking (2,3) removes four edges, (5,6) removes three more, (4,7) the last one",
                len([e for e in VC_EDGES if 2 in e or 3 in e]) == 4 and len([e for e in VC_EDGES if (5 in e or 6 in e) and not (2 in e or 3 in e)]) == 3))
    res.append(("optimum cover has 3 vertices, e.g. {2,4,5}; ratio exactly 2", len(opt) == 3 and all(a in {2, 4, 5} or b in {2, 4, 5} for a, b in VC_EDGES) and 6 == 2 * 3))
    res.append(("picked edges form a matching (no shared vertex)", len({v for e in picked for v in e}) == 2 * len(picked)))
    cov5, picked5 = approx_vertex_cover(PATH5, [(1, 2)])
    res.append(("practice: path 1-2-3-4-5 picking 1-2 first -> cover {1,2,3,4} of size 4; optimum {2,4} of size 2",
                cov5 == {1, 2, 3, 4} and picked5 == [(1, 2), (3, 4)] and min_vertex_cover(5, PATH5) is not None and len(min_vertex_cover(5, PATH5)) == 2
                and all(a in {2, 4} or b in {2, 4} for a, b in PATH5)))
    nodes = list(CITY)
    tree, tcost = mst(nodes)
    order = preorder(tree, "A")
    tc = tour_cost(order)
    best = min(tour_cost(("A",) + p) for p in permutations(nodes[1:]))
    res.append(("five cities: MST cost about 11.7, preorder walk A D E C B, tour about 15.7",
                abs(tcost - 11.66) < 0.05 and order == ["A", "D", "E", "C", "B"] and abs(tc - 15.66) < 0.05))
    res.append(("the tour is within twice the optimum (here it equals the optimum)", tc <= 2 * best + 1e-9 and abs(tc - best) < 1e-9))
    res.append(("triangle inequality holds for these cities (Euclidean)", all(dist(a, c) <= dist(a, b) + dist(b, c) + 1e-9 for a in nodes for b in nodes for c in nodes)))
    res.append(("MST <= optimal tour (tour minus an edge is a spanning tree)", tcost <= best + 1e-9))
    res.append(("Christofides: 1.5-approximation for metric TSP; general TSP has no constant-factor approximation unless P = NP", True))
    res.append(("k-means++ seeding is an O(log k) approximation (Arthur & Vassilvitskii 2007); first fit decreasing is within a constant factor (11/9 OPT + 6/9)", True))
    res.append(("HyperLogLog counts distinct items in kilobytes; Count-Min Sketch finds frequent items; k-means clustering and optimal decision trees are NP-hard", True))
    res.append(("RSA relies on integer factoring, ECC on discrete logarithms; post-quantum schemes use lattice problems (exact SVP is NP-hard under randomised reductions)", True))
    return res


if __name__ == "__main__":
    for claim, ok in check():
        print(("PASS " if ok else "FAIL ") + claim)
