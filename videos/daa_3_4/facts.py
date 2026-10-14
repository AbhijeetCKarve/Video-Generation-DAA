"""Every number and result Video 3.4 states, recomputed from scratch.

qa_check.py runs check(); a wrong claim fails the video before upload.

The example tree (a minimisation problem): node -> children, c-hat (lower bound) of every node,
and the leaves are answer nodes whose c-hat is their exact cost.
"""
from collections import deque
import heapq

CHILDREN = {1: [2, 3, 4], 2: [5, 6], 3: [7, 8], 4: [9, 10]}
CHAT = {1: 10, 2: 16, 3: 10, 4: 21, 5: 18, 6: 20, 7: 12, 8: 15, 9: 25, 10: 22}
ANSWER = {5, 6, 7, 8, 9, 10}

# practice question
P_CHILDREN = {1: [2, 3, 4], 2: [8, 9], 3: [5, 6], 4: [7]}
P_CHAT = {1: 4, 2: 7, 3: 4, 4: 6, 5: 9, 6: 8, 7: 6, 8: 10, 9: 11}
P_ANSWER = {7}


def search(kind, children, chat, answer, root=1):
    """Horowitz-style LC/FIFO/LIFO search that stops at the first answer node generated.
    -> (E-nodes in order, nodes generated in order, the answer found)."""
    live, enodes, made, tick = [], [], [root], 0
    e = root
    while True:
        enodes.append(e)
        for x in children.get(e, []):
            made.append(x)
            if x in answer:
                return enodes, made, x
            tick += 1
            live.append((chat[x], tick, x))
        if not live:
            return enodes, made, None
        if kind == "FIFO":
            e = live.pop(0)[2]
        elif kind == "LIFO":
            e = live.pop()[2]
        else:                                        # LC: the live node with the smallest c-hat
            live.sort()
            e = live.pop(0)[2]


def fifo_best(children, chat, answer, root=1):
    """FIFO branch and bound for the cheapest answer: U = best answer so far; a node whose
    lower bound is worse than U is killed. -> (U history, killed nodes, best answer)."""
    q, U, best, history, killed = deque([root]), float("inf"), None, [], []
    while q:
        e = q.popleft()
        if chat[e] > U:
            killed.append(e)
            continue
        for x in children.get(e, []):
            if x in answer:
                if chat[x] < U:
                    U, best = chat[x], x
                    history.append(U)
            else:
                q.append(x)
    return history, killed, best


def check():
    """-> [(claim as said in the video, passed?)]"""
    r = []
    e, made, ans = search("FIFO", CHILDREN, CHAT, ANSWER)
    r.append(("FIFO E-nodes 1, 2 and stops at answer node 5 (cost 18)", e == [1, 2] and ans == 5 and CHAT[5] == 18))
    r.append(("FIFO queue after expanding node 1 is 2, 3, 4", made[1:4] == [2, 3, 4]))
    e, made, ans = search("LIFO", CHILDREN, CHAT, ANSWER)
    r.append(("LIFO expands 4 (the last pushed) and stops at answer node 9 (cost 25)",
              e == [1, 4] and ans == 9 and CHAT[9] == 25))
    e, made, ans = search("LC", CHILDREN, CHAT, ANSWER)
    r.append(("LC expands 3 (smallest c-hat, 10) and stops at answer node 7 (cost 12)",
              e == [1, 3] and ans == 7 and CHAT[7] == 12))
    r.append(("node 7 (cost 12) is the cheapest answer in the tree", min(CHAT[a] for a in ANSWER) == 12 == CHAT[7]))
    r.append(("c-hat is a lower bound: every node's c-hat <= the cheapest answer below it",
              all(CHAT[v] <= min(CHAT[a] for a in leaves(v)) for v in CHILDREN)))
    hist, killed, best = fifo_best(CHILDREN, CHAT, ANSWER)
    r.append(("FIFO with bounding: U becomes 18, then 12; node 4 (c-hat 21) is killed; best answer 7",
              hist == [18, 12] and killed == [4] and best == 7))
    e, made, ans = search("LC", P_CHILDREN, P_CHAT, P_ANSWER)
    r.append(("practice: LC E-nodes are 1, 3, 4, and node 7 is the answer", e == [1, 3, 4] and ans == 7))
    return r


def leaves(v):
    out, stack = [], [v]
    while stack:
        n = stack.pop()
        if n in CHILDREN:
            stack += CHILDREN[n]
        else:
            out.append(n)
    return out


if __name__ == "__main__":
    for claim, ok in check():
        print(("PASS " if ok else "FAIL ") + claim)
