"""Every number and result Video 3.5 states, recomputed from scratch.

qa_check.py runs check(); a wrong claim fails the video before upload.
"""
from itertools import product

INF = float("inf")
P, W, M = [10, 10, 12, 18], [2, 4, 6, 9], 15                       # knapsack (Horowitz-Sahni example)
COST = [[INF, 20, 30, 10, 11],                                      # TSP cost matrix (Horowitz-Sahni example)
        [15, INF, 16, 4, 2],
        [3, 5, INF, 2, 4],
        [19, 6, 18, INF, 3],
        [16, 4, 7, 16, INF]]


# ---------------------------------------------------------------- knapsack bounds
def bounds(fixed):
    """fixed: decisions for the first k items (1 take / 0 skip). -> (optimistic, guaranteed) profit,
    or None when the fixed items already overflow. Optimistic = fill the rest fractionally."""
    w = sum(W[i] for i, x in enumerate(fixed) if x)
    p = sum(P[i] for i, x in enumerate(fixed) if x)
    if w > M:
        return None
    guaranteed, ww = p, w
    for i in range(len(fixed), len(P)):                            # whole items, greedily by ratio order
        if ww + W[i] <= M:
            ww += W[i]
            guaranteed += P[i]
    optimistic, ww, pp = p, w, p
    for i in range(len(fixed), len(P)):
        if ww + W[i] <= M:
            ww += W[i]
            pp += P[i]
        else:
            pp += P[i] * (M - ww) / W[i]
            break
    return pp, guaranteed


def best_knapsack():
    best = max((sum(p * x for p, x in zip(P, xs)), xs) for xs in product((0, 1), repeat=4)
               if sum(w * x for w, x in zip(W, xs)) <= M)
    return best


# ---------------------------------------------------------------- TSP reduced cost matrix
def reduce(m):
    """Row then column reduction. -> (reduced matrix, total reduction)."""
    m = [row[:] for row in m]
    total = 0
    for r in range(len(m)):
        lo = min(m[r])
        if lo != INF and lo > 0:
            m[r] = [v - lo if v != INF else INF for v in m[r]]
            total += lo
    for c in range(len(m)):
        lo = min(m[r][c] for r in range(len(m)))
        if lo != INF and lo > 0:
            for r in range(len(m)):
                if m[r][c] != INF:
                    m[r][c] -= lo
            total += lo
    return m, total


def child(m, chat, path, j):
    """Reduced matrix and c-hat for extending `path` (ending at i) with the edge i -> j."""
    i = path[-1]
    n = [row[:] for row in m]
    for c in range(len(n)):
        n[i][c] = INF
    for r in range(len(n)):
        n[r][j] = INF
    n[j][path[0]] = INF
    red, extra = reduce(n)
    return red, chat + m[i][j] + extra


def tsp_lc():
    """LC branch and bound from city 1: the trace as (path, c-hat) in the order nodes are expanded."""
    root, r = reduce(COST)
    live = [([0], root, r)]
    trace, best = [], None
    while live:
        live.sort(key=lambda t: t[2])
        path, m, c = live.pop(0)
        trace.append(([p + 1 for p in path], c))
        if len(path) == 5:
            best = ([p + 1 for p in path] + [1], c)
            break
        for j in range(5):
            if j not in path:
                red, cj = child(m, c, path, j)
                live.append((path + [j], red, cj))
    return trace, best, live


def check():
    """-> [(claim as said in the video, passed?)]"""
    res = []
    res.append(("items are in profit/weight order: 5, 2.5, 2, 2", [p / w for p, w in zip(P, W)] == [5, 2.5, 2, 2]))
    res.append(("root: optimistic 38, guaranteed 32", bounds([]) == (38, 32)))
    res.append(("x1 = 1: 38 / 32;  x1 = 0: 32 / 22", bounds([1]) == (38, 32) and bounds([0]) == (32, 22)))
    res.append(("x2 = 1: 38 / 32;  x2 = 0: 36 / 22", bounds([1, 1]) == (38, 32) and bounds([1, 0]) == (36, 22)))
    res.append(("x3 = 1: 38 / 32;  x3 = 0: 38 / 38 (items 1, 2, 4 fit whole)",
                bounds([1, 1, 1]) == (38, 32) and bounds([1, 1, 0]) == (38, 38)))
    res.append(("the best knapsack is x = (1,1,0,1), profit 38, weight 15",
                best_knapsack() == (38, (1, 1, 0, 1)) and sum(W[i] for i in (0, 1, 3)) == 15))
    res.append(("with x = (1,1,1), item 4 does not fit (weight 21 > 15)", 2 + 4 + 6 + 9 == 21))
    root, r = reduce(COST)
    res.append(("row reduction 10, 2, 2, 3, 4 = 21", [min(row) for row in COST] == [10, 2, 2, 3, 4]))
    res.append(("column reduction 1, 0, 3, 0, 0 = 4, root c-hat 25", r == 25))
    kids = {j + 1: child(root, 25, [0], j)[1] for j in range(1, 5)}
    res.append(("children of the root: 1-2 = 35, 1-3 = 53, 1-4 = 25, 1-5 = 31", kids == {2: 35, 3: 53, 4: 25, 5: 31}))
    trace, best, _ = tsp_lc()
    order = [t[0] for t in trace]
    res.append(("LC expands 1, 1-4, 1-4-2, 1-4-2-5, then the leaf 1-4-2-5-3",
                order == [[1], [1, 4], [1, 4, 2], [1, 4, 2, 5], [1, 4, 2, 5, 3]]))
    res.append(("children of 1-4: to 2 = 28, to 3 = 50, to 5 = 36",
                {j + 1: child(reduce(COST)[0] and child(root, 25, [0], 3)[0], 25, [0, 3], j)[1] for j in (1, 2, 4)}
                == {2: 28, 3: 50, 5: 36}))
    res.append(("children of 1-4-2: to 3 = 52, to 5 = 28", trace[2][1] == 28 and
                {j + 1: child(child(child(root, 25, [0], 3)[0], 25, [0, 3], 1)[0], 28, [0, 3, 1], j)[1] for j in (2, 4)}
                == {3: 52, 5: 28}))
    res.append(("the tour 1-4-2-5-3-1 costs 28", best == ([1, 4, 2, 5, 3, 1], 28) and
                COST[0][3] + COST[3][1] + COST[1][4] + COST[4][2] + COST[2][0] == 28))
    res.append(("practice: capacity 12 -> items 1, 2, 3 fit exactly, optimistic = guaranteed = 32",
                sum(W[:3]) == 12 and sum(P[:3]) == 32))
    return res


if __name__ == "__main__":
    for claim, ok in check():
        print(("PASS " if ok else "FAIL ") + claim)
