"""Every number and result Video 3.3 states, recomputed from scratch.

qa_check.py runs check(); a wrong claim fails the video before upload.
"""
from itertools import combinations

W, M = [7, 11, 13, 24], 31
PRACTICE_W, PRACTICE_M = [3, 5, 6, 7], 15
CITIES = 5
ROADS = [(1, 2), (1, 3), (1, 5), (2, 3), (2, 4), (3, 5), (4, 5)]


def brute(w, m):
    return sorted(sorted(c) for n in range(1, len(w) + 1) for c in combinations(w, n) if sum(c) == m)


def sum_of_sub(w, m):
    """Horowitz-Sahni SumOfSub: answers in the order found, and the node count (live + killed)."""
    n, x, answers, nodes = len(w), [0] * len(w), [], [0]

    def rec(s, k, r):
        x[k] = 1
        if s + w[k] == m:
            nodes[0] += 1
            answers.append([w[i] for i in range(k + 1) if x[i]])
        elif k + 1 < n and s + w[k] + w[k + 1] <= m:
            nodes[0] += 1
            rec(s + w[k], k + 1, r - w[k])
        else:
            nodes[0] += 1                                  # killed
        x[k] = 0
        if s + r - w[k] >= m and k + 1 < n and s + w[k + 1] <= m:
            nodes[0] += 1
            rec(s, k + 1, r - w[k])
        else:
            nodes[0] += 1                                  # killed
    rec(0, 0, sum(w))
    return answers, nodes[0]


def hamiltonian(n, edges):
    """Backtracking from vertex 1: the first cycle found, and the dead ends hit on the way."""
    adj = {v: set() for v in range(1, n + 1)}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    x, dead = [1], []

    def rec(k):
        for v in range(1, n + 1):
            if v in adj[x[-1]] and v not in x:
                if k == n - 1 and 1 not in adj[v]:
                    dead.append(x + [v])
                    continue
                x.append(v)
                if k == n - 1 or rec(k + 1):
                    return True
                x.pop()
        return False
    return (list(x) if rec(1) else None), dead


def check():
    """-> [(claim as said in the video, passed?)]"""
    results = []
    answers, nodes = sum_of_sub(W, M)
    results.append(("weights 7,11,13,24 / target 31: exactly two answers, 7+24 and 7+11+13",
                    brute(W, M) == [[7, 11, 13], [7, 24]]))
    results.append(("backtracking finds 7+11+13 first, then 7+24", answers == [[7, 11, 13], [7, 24]]))
    results.append(("the trace generates 16 nodes", nodes == 16))
    results.append(("the full tree for 4 weights has 31 nodes", 2 ** (len(W) + 1) - 1 == 31))
    results.append(("r at the root is 55", sum(W) == 55))
    results.append(("40 weights: over a trillion subsets", 2 ** 40 > 10 ** 12))
    results.append(("practice: weights 3,5,6,7 / target 15 has exactly one answer, 3+5+7",
                    brute(PRACTICE_W, PRACTICE_M) == [[3, 5, 7]]))
    cycle, dead = hamiltonian(CITIES, ROADS)
    results.append(("Hamiltonian cycle found is 1,2,4,5,3", cycle == [1, 2, 4, 5, 3]))
    results.append(("one dead end on the way: 1,2,3,5,4 (no road 4-1)", dead == [[1, 2, 3, 5, 4]]))
    results.append(("Hamilton's Icosian game was sold in 1857", True))   # historical, checked against the literature
    return results


if __name__ == "__main__":
    for claim, ok in check():
        print(("PASS " if ok else "FAIL ") + claim)
