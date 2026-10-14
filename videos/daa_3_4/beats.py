"""Video 3.4 - Branch & Bound: FIFO, LIFO and LC Search (DAA Unit III).

Each beat = one narration line. The key ties it to its animation in scene.py,
the mood steers delivery and background music, "|" marks caption breaks.

Example: one state space tree (nodes 1-10, leaves are answer nodes) searched three ways.
FIFO stops at node 5 (cost 18), LIFO at node 9 (cost 25), LC at node 7 (cost 12, the cheapest).
"""

TITLE = "Branch & Bound: FIFO, LIFO & LC Search"
CODE = "3.4"
UNIT = "III"

BEATS = [
    # ---- hook
    ("hook_doors", "curious", "You are in a building with three doors, and behind each one are more doors. | Somewhere inside is the exit you want, the cheapest way out."),
    ("hook_ways", "explain", "You could open doors left to right, | or always open the newest door first, | or peek at a price tag on every door and open the cheapest one."),
    ("hook_name", "excited", "Those three strategies are FIFO, LIFO and least cost search. | Together, they are called branch and bound."),
    ("hook_mascot", "warm", "Welcome to the DAA series. | I'm Abhijeet Karve, and I'll guide you through every algorithm, step by step."),
    ("syllabus", "explain", "This is Unit Three, video four. | Today: how branch and bound differs from backtracking, the three search strategies, and how bounds kill nodes."),
    ("exam", "explain", "Comparing FIFO, LIFO and LC search is a classic exam question, | so stay till the end for the exam tips."),
    # ---- branch and bound vs backtracking
    ("b_recap", "explain", "Quick recap of the words from video three point one. | A live node has been generated, but not all its children have. The E node is the one being expanded."),
    ("b_bt", "explain", "In backtracking, as soon as a child is generated, | that child becomes the new E node, so the search dives deep."),
    ("b_bb", "emphatic", "In branch and bound, the E node stays the E node until all its children are generated. | Only then do we pick the next E node from the list of live nodes."),
    ("b_list", "explain", "So everything depends on one question: | which live node do we expand next?"),
    # ---- the three strategies
    ("s_fifo", "explain", "FIFO search keeps the live nodes in a queue. | First in, first out: nodes are expanded level by level, like breadth first search."),
    ("s_lifo", "explain", "LIFO search keeps them in a stack. | Last in, first out: the newest live node is expanded next, so the search goes deep."),
    ("s_lc", "explain", "LC search, least cost search, gives every live node a cost estimate, c hat, | and always expands the live node with the smallest c hat."),
    # ---- the example tree
    ("t_intro", "curious", "Let's run all three on the same tree. | The leaves are answer nodes, and the number on each node is its c hat. We want the cheapest answer."),
    ("t_fifo1", "explain", "FIFO first. Node one is expanded, and its children two, three and four join the queue. | The front of the queue is node two."),
    ("t_fifo2", "explain", "Node two is expanded. Its first child, node five, is an answer node, with cost eighteen. | FIFO stops there."),
    ("t_lifo1", "explain", "Now LIFO. Node one is expanded and two, three, four are pushed on the stack. | The top of the stack is four, the last one pushed."),
    ("t_lifo2", "explain", "Node four is expanded, and its first child, node nine, is an answer, | with cost twenty five. Worse than FIFO!"),
    ("t_lc1", "explain", "Finally LC. After node one, the live nodes have c hat sixteen, ten and twenty one. | The smallest is ten, so node three is expanded."),
    ("t_lc2", "excited", "Its first child, node seven, is an answer with cost twelve, | and that is the cheapest answer in the whole tree."),
    ("t_compare", "warm", "Same tree, three strategies: | FIFO found cost eighteen, LIFO found twenty five, and LC went straight to twelve."),
    # ---- the cost function
    ("c_formula", "explain", "Where does c hat come from? | c hat of x equals f of h of x, plus g hat of x."),
    ("c_parts", "explain", "h of x is the cost of reaching x from the root. | g hat of x is an estimate of the cost from x to the nearest answer node."),
    ("c_lower", "emphatic", "For minimisation problems, c hat must never overestimate. | It is a lower bound on the cost of any answer below that node."),
    # ---- bounding
    ("u_intro", "explain", "Now the bound in branch and bound. | We keep U, the cost of the best answer found so far. At the start, U is infinity."),
    ("u_rule", "emphatic", "The rule is simple: | if a node's c hat is greater than U, nothing below it can beat the best answer, so the node is killed."),
    ("u_trace1", "explain", "Let's make FIFO find the cheapest answer using this rule. | Expanding node two finds answers eighteen and twenty, so U becomes eighteen."),
    ("u_trace2", "explain", "Expanding node three finds answer seven with cost twelve. | U drops to twelve."),
    ("u_kill", "excited", "Next in the queue is node four, but its c hat is twenty one, greater than twelve. | Killed, without generating its children. The best answer is twelve."),
    ("u_upper", "explain", "So c hat gives a lower bound for every node, U gives an upper bound on the best answer, | and whenever a lower bound passes the upper bound, that branch is cut away."),
    # ---- control abstraction
    ("a_code", "explain", "Here is the control abstraction for LC search. | It starts with the root as the E node and an empty list of live nodes."),
    ("a_loop", "explain", "Each child of the E node is checked: if it is an answer node, we output the path and stop. | Otherwise it is added to the live list."),
    ("a_least", "explain", "Then Least removes the live node with the smallest c hat, | and that becomes the next E node."),
    ("a_swap", "warm", "Here is the neat part. | Replace Least with a queue and you get FIFO, replace it with a stack and you get LIFO."),
    # ---- practice, tips, recap
    ("p_intro", "curious", "Your turn. | In this tree, in which order do the nodes become E nodes under LC search?"),
    ("p_pause", "warm", "Pause the video and work it out. | I'll wait!"),
    ("p_answer", "excited", "Node one, then node three with c hat four, then node four with c hat six. | Its child, node seven, is the answer."),
    ("tip1", "emphatic", "Exam tip one. | Explain the difference: in branch and bound, the E node remains the E node until it is dead."),
    ("tip2", "emphatic", "Exam tip two. | For FIFO, LIFO and LC, draw the live node list, queue, stack or priority list, at every step."),
    ("tip3", "emphatic", "Exam tip three. | Write c hat of x equals f of h of x plus g hat of x, and explain the kill rule with U."),
    ("recap", "warm", "To recap: | branch and bound expands an E node completely before choosing the next, | FIFO uses a queue, LIFO a stack, and LC the smallest c hat, | and bounds kill nodes that cannot beat the best answer."),
    ("next", "warm", "In the next video, we apply LC branch and bound to the zero one knapsack problem and the travelling salesperson problem. | See you there!"),
]


def script_text():
    """Narration script in the format the voice tools read: '01  {mood} text'."""
    return "".join(f"{i + 1:02d}  {{{mood}}} {text}\n" for i, (_, mood, text) in enumerate(BEATS))


if __name__ == "__main__":
    import sys
    from pathlib import Path
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("script.txt")
    out.write_text(script_text())
    words = sum(len(t.replace("|", " ").split()) for _, _, t in BEATS)
    print(f"Wrote {out}: {len(BEATS)} beats, {words} words (~{words / 140:.1f} min at 140 wpm)")
