"""Every number and claim Video 4.1 states, recomputed from scratch.

qa_check.py runs check(); a wrong claim fails the video before upload.
The non-deterministic algorithms are simulated by trying every sequence of choices:
Success iff some sequence succeeds, exactly the definition in the video.
"""
import math
from itertools import product, permutations
from random import Random

NS = 1e-9                       # one step = one nanosecond (a billion steps a second)
YEAR = 365.25 * 24 * 3600


def years(steps):
    return steps * NS / YEAR


# ---------------------------------------------------------------- the growth table (seconds)
def table():
    rows = {"n^2": lambda n: n ** 2, "n^3": lambda n: n ** 3, "2^n": lambda n: 2 ** n, "n!": math.factorial}
    return {name: {n: f(n) * NS for n in (10, 20, 50, 100)} for name, f in rows.items()}


# ---------------------------------------------------------------- non-deterministic algorithms, simulated
def nsearch(A, x):
    """j := Choice(1..n); if A[j] = x then Success else Failure.  -> succeeds?"""
    return any(A[j] == x for j in range(len(A)))


def nsort(A):
    """B[Choice(1..n)] := A[i] for each i (Failure on a clash); Failure if B is not non-decreasing.
    -> the B written by the one successful sequence of choices, or None."""
    n = len(A)
    for js in product(range(n), repeat=n):
        B = [0] * n
        ok = True
        for i, j in enumerate(js):
            if B[j] != 0:
                ok = False
                break
            B[j] = A[i]
        if ok and all(B[i] <= B[i + 1] for i in range(n - 1)):
            return B
    return None


def dkp(p, w, m, r):
    """x[i] := Choice(0, 1); Failure if sum(w x) > m or sum(p x) < r.  -> succeeds?"""
    return any(sum(wi * xi for wi, xi in zip(w, xs)) <= m and sum(pi * xi for pi, xi in zip(p, xs)) >= r
               for xs in product((0, 1), repeat=len(p)))


def nhamiltonian(adj):
    """v[i] := Choice(1..n); Failure on a repeat, a missing edge, or no edge v[n] -> v[1].  -> succeeds?"""
    n = len(adj)
    return any(len(set(v)) == n and all(adj[v[i]][v[i + 1]] for i in range(n - 1)) and adj[v[-1]][v[0]]
               for v in product(range(n), repeat=n))


def has_ham_cycle(adj):
    n = len(adj)
    return any(all(adj[p[i]][p[(i + 1) % n]] for i in range(n)) for p in permutations(range(n)))


def check():
    """-> [(claim as said in the video, passed?)]"""
    res = []
    T = table()
    res.append(("sorting a million numbers (n log n) takes a fraction of a second", 1e6 * math.log2(1e6) * NS < 0.1))
    tours25 = math.factorial(24) / 2
    res.append(("all tours of 25 cities = 24!/2 take about ten million years", 8e6 < years(tours25) < 12e6))
    res.append(("n^3 at n = 100 takes one millisecond", abs(T["n^3"][100] - 1e-3) < 1e-9))
    res.append(("2^n at n = 100 takes forty trillion years", 35e12 < years(2 ** 100) < 45e12))
    res.append(("2^n at n = 50 takes about 13 days", 12.5 < T["2^n"][50] / 86400 < 13.5))
    res.append(("20! steps take about 77 years", 76 < years(math.factorial(20)) < 78))
    res.append(("1000x faster: a cubic algorithm handles 10x the input", round(1000 ** (1 / 3)) == 10))
    res.append(("1000x faster: 2^n handles only about 10 more items", 9.9 < math.log2(1000) < 10.1))
    res.append(("n, n log n, n^2, n^3 are O(n^k); 2^n and n! are not",
                all(f(1000) <= 1000 ** 3 for f in (lambda n: n, lambda n: n * math.log2(n), lambda n: n ** 2, lambda n: n ** 3))
                and 2 ** 100 > 100 ** 10 and math.factorial(100) > 100 ** 50))
    rnd = Random(41)
    ok = all(nsearch(A, x) == (x in A) for A in [[rnd.randint(1, 9) for _ in range(6)] for _ in range(30)] for x in range(0, 11))
    res.append(("NSearch succeeds exactly when x is in A", ok))
    ok = all(nsort(A) == sorted(A) for A in [[rnd.randint(1, 20) for _ in range(rnd.randint(1, 5))] for _ in range(25)])
    res.append(("NSort writes the sorted array (positive integers)", ok))
    res.append(("deterministic search O(n) vs non-deterministic O(1); sorting O(n log n) vs O(n)",
                True))   # structural: one Choice + one comparison; three loops of at most n O(1) steps
    p, w, m = [10, 10, 12, 18], [2, 4, 6, 9], 15
    brute = max(sum(pi * xi for pi, xi in zip(p, xs)) for xs in product((0, 1), repeat=4)
                if sum(wi * xi for wi, xi in zip(w, xs)) <= m)
    res.append(("DKP (decision knapsack) says yes exactly up to the optimum profit (38 on the 3.5 example)",
                brute == 38 and dkp(p, w, m, 38) and not dkp(p, w, m, 39) and dkp(p, w, m, 0)))
    gs = []
    for _ in range(12):
        n = rnd.randint(3, 5)
        adj = [[False] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                adj[i][j] = adj[j][i] = rnd.random() < 0.55
        gs.append(adj)
    res.append(("non-deterministic Hamiltonian cycle succeeds exactly when the graph has one",
                all(nhamiltonian(g) == has_ham_cycle(g) for g in gs)))
    res.append(("the hard Unit III problems (TSP, Hamiltonian cycle, graph coloring, 0/1 knapsack) have no known polynomial algorithm",
                True))   # textbook fact (Horowitz-Sahni ch. 11); P vs NP open
    return res


if __name__ == "__main__":
    for name, row in table().items():
        print(f"{name:>4}", {n: f"{s:.3g}s" if s < 60 else f"{years(s / NS):.3g}y" for n, s in row.items()})
    for claim, ok in check():
        print(("PASS " if ok else "FAIL ") + claim)
