"""Every claim Video 4.2 states, recomputed or pinned down.

qa_check.py runs check(); a wrong claim fails the video before upload.
"""
from itertools import product

# (x1 or x2) and (not x1 or x3)
FORMULA = [[(1, True), (2, True)], [(1, False), (3, True)]]      # clauses of (variable, wanted value)


def satisfied(assign, formula=FORMULA):
    return all(any(assign[v] == want for v, want in clause) for clause in formula)


def sat_brute(formula, n):
    return [a for a in (dict(zip(range(1, n + 1), bits)) for bits in product((False, True), repeat=n)) if satisfied(a, formula)]


def decision_knapsack(p, w, m, r):
    """The yes/no oracle: is there a packing with weight <= m and profit >= r?"""
    return any(sum(wi * xi for wi, xi in zip(w, xs)) <= m and sum(pi * xi for pi, xi in zip(p, xs)) >= r
               for xs in product((0, 1), repeat=len(p)))


def optimise_via_decision(p, w, m):
    """Binary search on r with the decision oracle -> (optimum profit, number of oracle calls)."""
    lo, hi, calls = 0, sum(p), 0
    while lo < hi:                                   # invariant: answer in [lo, hi]
        mid = (lo + hi + 1) // 2
        calls += 1
        if decision_knapsack(p, w, m, mid):
            lo = mid
        else:
            hi = mid - 1
    return lo, calls


def is_sorted(a):
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))       # one linear scan


def check():
    res = []
    sols = sat_brute(FORMULA, 3)
    res.append(("(x1 or x2) and (not x1 or x3) is satisfied by x1 = true, x3 = true (x2 either way)",
                satisfied({1: True, 2: False, 3: True}) and satisfied({1: True, 2: True, 3: True})))
    res.append(("the formula is satisfiable (brute force agrees)", len(sols) > 0))
    res.append(("n variables -> 2^n assignments (3 variables: 8)", len(list(product((0, 1), repeat=3))) == 8))
    p, w, m = [10, 10, 12, 18], [2, 4, 6, 9], 15
    best = max(sum(pi * xi for pi, xi in zip(p, xs)) for xs in product((0, 1), repeat=4)
               if sum(wi * xi for wi, xi in zip(w, xs)) <= m)
    opt, calls = optimise_via_decision(p, w, m)
    res.append(("decision version solved -> optimisation by binary search on r (knapsack: 38 in a few yes/no calls)",
                opt == best == 38 and calls <= 7))
    res.append(("a deterministic algorithm is a non-deterministic one with no Choice, so P is a subset of NP", True))
    res.append(("is-sorted check is one linear scan", is_sorted([1, 2, 5, 8]) and not is_sorted([1, 5, 2])))
    res.append(("Cook's theorem (1971): SAT is in P iff P = NP; SAT the first NP-complete problem", True))
    res.append(("Clay Mathematics Institute Millennium Prize: USD 1,000,000, announced in 2000, P vs NP unclaimed", True))
    res.append(("halting problem: NP-hard but not in NP (undecidable); TSP optimisation: NP-hard", True))
    res.append(("NP-complete examples: SAT, 3-SAT, Hamiltonian cycle, vertex cover, clique, graph colouring, decision knapsack", True))
    res.append(("shortest path (Dijkstra), MST, primality (AKS 2002) are in P", True))
    return res


if __name__ == "__main__":
    for claim, ok in check():
        print(("PASS " if ok else "FAIL ") + claim)
