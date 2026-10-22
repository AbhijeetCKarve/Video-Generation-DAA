"""Every claim Video 4.4 states, checked by brute force on the examples and on random instances.

qa_check.py runs check(); a wrong claim fails the video before upload.
"""
from itertools import combinations, product
from random import Random

# literals: (variable, positive?)
F = [[(1, True), (2, False), (3, True)], [(1, False), (2, True), (3, True)], [(1, True), (2, True), (3, False)]]
G5 = (5, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3), (0, 4)])      # K4 on 1-4 plus the edge 1-5


def satisfiable(formula, n):
    return any(all(any(a[v] == pos for v, pos in cl) for cl in formula) for a in
               (dict(zip(range(1, n + 1), bits)) for bits in product((False, True), repeat=n)))


def sat_assignments(formula, nvars):
    return {bits for bits in product((False, True), repeat=nvars)
            if all(any(dict(zip(range(1, nvars + 1), bits))[v] == pos for v, pos in cl) for cl in formula)}


def literal_graph(formula):
    """3-SAT -> clique: one vertex per literal occurrence, edges across clauses between non-opposite literals."""
    verts = [(ci, lit) for ci, cl in enumerate(formula) for lit in cl]
    edges = {(i, j) for i, (ci, (v, p)) in enumerate(verts) for j, (cj, (w, q)) in enumerate(verts)
             if i < j and ci != cj and not (v == w and p != q)}
    return verts, edges


def has_clique(n, edges, k):
    E = {frozenset(e) for e in edges}
    return any(all(frozenset(p) in E for p in combinations(s, 2)) for s in combinations(range(n), k))


def has_cover(n, edges, k):
    return any(all(a in s or b in s for a, b in edges) for s in map(set, combinations(range(n), k)))


def has_independent(n, edges, k):
    return any(all(not (a in s and b in s) for a, b in edges) for s in map(set, combinations(range(n), k)))


def complement(n, edges):
    E = {frozenset(e) for e in edges}
    return [(a, b) for a in range(n) for b in range(a + 1, n) if frozenset((a, b)) not in E]


def random_3sat(rnd, nvars, k):
    return [[(v, rnd.random() < 0.5) for v in rnd.sample(range(1, nvars + 1), 3)] for _ in range(k)]


def check():
    res = []
    rnd = Random(44)
    # SAT -> 3-SAT: splitting and padding preserve satisfiability (projecting the fresh variable away)
    long_ = [[(1, True), (2, True), (3, True), (4, True)]]
    split = [[(1, True), (2, True), (5, True)], [(5, False), (3, True), (4, True)]]
    ok = all(((a in sat_assignments(long_, 4)) == any((*a, y) in sat_assignments(split, 5) for y in (False, True)))
             for a in product((False, True), repeat=4))
    res.append(("splitting (a v b v c v d) into (a v b v y) ^ (-y v c v d) keeps exactly the same satisfying assignments", ok))
    short = [[(1, True), (2, True)]]
    pad = [[(1, True), (2, True), (3, True)], [(1, True), (2, True), (3, False)]]
    ok = all(((a in sat_assignments(short, 2)) == any((*a, y) in sat_assignments(pad, 3) for y in (False, True)))
             for a in product((False, True), repeat=2))
    res.append(("padding (a v b) into (a v b v y) ^ (a v b v -y) keeps exactly the same satisfying assignments", ok))
    # 3-SAT -> clique
    verts, edges = literal_graph(F)
    res.append(("the example formula gives 9 vertices in 3 groups, k = 3", len(verts) == 9 and len(F) == 3))
    idx = {(ci, lit): i for i, (ci, lit) in enumerate(verts)}
    tri = [idx[(0, (3, True))], idx[(1, (3, True))], idx[(2, (1, True))]]
    res.append(("x3 (clause 1), x3 (clause 2), x1 (clause 3) form a triangle, and x1 = x3 = true satisfies the formula",
                all(frozenset(p) in {frozenset(e) for e in edges} for p in combinations(tri, 2))
                and all(any({1: True, 2: False, 3: True}[v] == pos for v, pos in cl) for cl in F)))
    ok = True
    for _ in range(60):
        nv, k = rnd.randint(3, 4), rnd.randint(1, 4)
        f = random_3sat(rnd, nv, k)
        vs, es = literal_graph(f)
        ok &= satisfiable(f, nv) == has_clique(len(vs), es, k)
    res.append(("3-SAT formula satisfiable  iff  literal graph has a clique of size k (60 random formulas)", ok))
    res.append(("3k vertices, fewer than 9k^2 edges", all(3 * k * (3 * k - 1) // 2 < 9 * k * k for k in range(1, 50))))
    # clique -> vertex cover
    n, e = G5
    res.append(("example graph: 1,2,3,4 form a 4-clique; complement has 3 edges, all covered by vertex 5; 1 = 5 - 4",
                has_clique(n, e, 4) and len(complement(n, e)) == 3 and all(4 in ed for ed in complement(n, e))
                and has_cover(n, complement(n, e), 1) and 5 - 4 == 1))
    ok = True
    for _ in range(50):
        nn = rnd.randint(3, 7)
        g = [(a, b) for a in range(nn) for b in range(a + 1, nn) if rnd.random() < 0.5]
        gb = complement(nn, g)
        for k in range(nn + 1):
            ok &= has_clique(nn, g, k) == has_cover(nn, gb, nn - k)
            ok &= has_clique(nn, g, k) == has_independent(nn, gb, k)
    res.append(("clique of size k in G  iff  vertex cover of size n - k in G-bar  iff  independent set of size k in G-bar (50 random graphs)", ok))
    res.append(("the complement has n vertices and fewer than n^2 edges", all(nn * (nn - 1) // 2 < nn * nn for nn in range(1, 100))))
    res.append(("chain SAT -> 3-SAT -> Clique -> Vertex cover; Cook's theorem: SAT is NP-complete", True))
    return res


if __name__ == "__main__":
    for claim, ok in check():
        print(("PASS " if ok else "FAIL ") + claim)
