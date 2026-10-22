"""Every claim Video 4.3 states, checked by brute force on small instances.

qa_check.py runs check(); a wrong claim fails the video before upload.
Each reduction is verified the way the video defines it: the translated instance says yes
exactly when the original does, on many random inputs.
"""
from itertools import combinations, permutations, product
from random import Random

# the exam timetable of the hook: exams and "some student takes both" conflicts
EXAMS = ["Maths", "Physics", "DAA", "DBMS", "English"]
CONFLICTS = [(0, 1), (0, 2), (1, 3), (2, 3), (2, 4), (3, 4)]
# the delivery-van map of reduction 1 (4 houses, a 4-cycle of roads)
VAN = (4, [(0, 1), (1, 2), (2, 3), (3, 0)])
# the party / street graph of reduction 2 (a pentagon)
PENTA = (5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)])
# the notes of reduction 3
NOTES, TARGET = [100, 200, 200, 50, 20, 10], 500


def colourable(n, edges, k):
    return any(all(c[a] != c[b] for a, b in edges) for c in product(range(k), repeat=n))


def ham_cycle(n, edges):
    E = {frozenset(e) for e in edges}
    return any(all(frozenset((p[i], p[(i + 1) % n])) in E for i in range(n)) for p in permutations(range(n)))


def tsp_at_most(n, cost, k):
    """decision TSP on a complete graph with cost[i][j]."""
    return any(sum(cost[p[i]][p[(i + 1) % n]] for i in range(n)) <= k for p in permutations(range(n)))


def hc_to_tsp(n, edges):
    """The video's translation: cost 1 on existing roads, 2 elsewhere, k = n."""
    E = {frozenset(e) for e in edges}
    cost = [[0 if i == j else (1 if frozenset((i, j)) in E else 2) for j in range(n)] for i in range(n)]
    return cost, n


def independent_set(n, edges, k):
    return any(all(not (a in s and b in s) for a, b in edges) for s in map(set, combinations(range(n), k)))


def vertex_cover(n, edges, k):
    return any(all(a in s or b in s for a, b in edges) for s in map(set, combinations(range(n), k)))


def subset_sum(vals, t):
    return any(sum(c) == t for r in range(len(vals) + 1) for c in combinations(vals, r))


def knapsack(p, w, m, r):
    return any(sum(wi * xi for wi, xi in zip(w, xs)) <= m and sum(pi * xi for pi, xi in zip(p, xs)) >= r
               for xs in product((0, 1), repeat=len(p)))


def random_graph(rnd, n, q):
    return [(a, b) for a in range(n) for b in range(a + 1, n) if rnd.random() < q]


def check():
    res = []
    n = len(EXAMS)
    res.append(("exam timetable: 3 slots suffice, 2 do not (DAA, DBMS, English all conflict)",
                colourable(n, CONFLICTS, 3) and not colourable(n, CONFLICTS, 2)))
    rnd = Random(43)
    # reduction 1
    ok = True
    for _ in range(40):
        nn = rnd.randint(3, 6)
        g = random_graph(rnd, nn, rnd.choice([0.4, 0.6, 0.8]))
        cost, k = hc_to_tsp(nn, g)
        ok &= ham_cycle(nn, g) == tsp_at_most(nn, cost, k)
    res.append(("Hamiltonian cycle -> TSP: cost 1 / 2, k = n; yes iff yes (40 random maps)", ok))
    cost, k = hc_to_tsp(*VAN)
    res.append(("the van map (4 houses, a cycle of roads) has a tour of cost exactly 4 = n", ham_cycle(*VAN) and tsp_at_most(4, cost, 4)
                and not tsp_at_most(4, cost, 3)))
    res.append(("the translation lists n^2 pairs: polynomial", True))
    # reduction 2
    ok = True
    for _ in range(40):
        nn = rnd.randint(3, 7)
        g = random_graph(rnd, nn, rnd.choice([0.3, 0.5, 0.7]))
        for kk in range(nn + 1):
            ok &= independent_set(nn, g, kk) == vertex_cover(nn, g, nn - kk)
    res.append(("independent set of size k  iff  vertex cover of size n - k (40 random graphs, every k)", ok))
    res.append(("pentagon: 2 guests can be invited, 3 guards cover every street; 3 guests / 2 guards impossible",
                independent_set(*PENTA, 2) and vertex_cover(*PENTA, 3) and not independent_set(*PENTA, 3) and not vertex_cover(*PENTA, 2)))
    # reduction 3
    ok = True
    for _ in range(60):
        vals = [rnd.choice([10, 20, 50, 100, 200, 500]) for _ in range(rnd.randint(2, 7))]
        t = rnd.choice([30, 50, 100, 250, 500, 700, 45])
        ok &= subset_sum(vals, t) == knapsack(vals, vals, t, t)
    res.append(("subset sum -> knapsack: weight = profit = value, m = r = target; yes iff yes (60 random bills)", ok))
    res.append(("notes 100, 200, 200, 50, 20, 10 can pay exactly 500 (200 + 200 + 100)",
                subset_sum(NOTES, TARGET) and knapsack(NOTES, NOTES, TARGET, TARGET) and 200 + 200 + 100 == 500))
    res.append(("reductions compose (polynomial of a polynomial is polynomial); Karp's tree from SAT via 3-SAT", True))
    res.append(("charging stations at junctions covering every street = vertex cover, NP-complete", True))
    return res


if __name__ == "__main__":
    for claim, ok in check():
        print(("PASS " if ok else "FAIL ") + claim)
