"""Video 3.5 - 0/1 Knapsack & TSP with Branch & Bound (DAA Unit III).

Each beat = one narration line. The key ties it to its animation in scene.py,
the mood steers delivery and background music, "|" marks caption breaks.

Examples (Horowitz-Sahni): knapsack p = 10,10,12,18, w = 2,4,6,9, m = 15 -> x = (1,1,0,1), profit 38.
TSP 5 cities, reduced cost matrix: root c-hat 25, tour 1-4-2-5-3-1 costs 28.
"""

TITLE = "0/1 Knapsack & TSP with Branch & Bound"
CODE = "3.5"
UNIT = "III"

BEATS = [
    # ---- hook
    ("hook_bag", "curious", "A bag that holds fifteen kilos, and four items worth ten, ten, twelve and eighteen rupees. | Which ones do you take to earn the most?"),
    ("hook_tsp", "curious", "A salesperson must visit five cities and come home. | There are twenty four possible tours. Which one is cheapest?"),
    ("hook_name", "excited", "Both are solved by least cost branch and bound, | the LC search from the last video, with a clever lower bound for each problem."),
    ("hook_mascot", "warm", "Welcome to the DAA series. | I'm Abhijeet Karve, and I'll guide you through every algorithm, step by step."),
    ("syllabus", "explain", "This is Unit Three, video five, the last one on branch and bound. | Today: the zero one knapsack with LC search, and the travelling salesperson problem with the reduced cost matrix."),
    ("exam", "explain", "Both traces are long answer questions in the exam, | so stay till the end for the exam tips."),
    # ---- knapsack: the model
    ("k_problem", "explain", "The zero one knapsack. | Four items with profits ten, ten, twelve, eighteen, and weights two, four, six, nine. The bag holds fifteen."),
    ("k_ratio", "explain", "First we order the items by profit per kilo: five, two and a half, two, two. | These are already in that order."),
    ("k_bounds", "emphatic", "Every node gets two numbers. | An optimistic bound: fill the remaining space fractionally, like the fractional knapsack. And a guaranteed profit: whole items only."),
    ("k_root", "explain", "At the root, items one, two and three fit: weight twelve, profit thirty two. | Three kilos are left, and a third of item four adds six. So the bounds are thirty eight and thirty two."),
    ("k_rule", "explain", "LC search always expands the live node with the best optimistic bound, | and a node is killed when its optimistic bound cannot beat the best guaranteed profit found so far."),
    # ---- knapsack: the trace
    ("k_x1", "explain", "Level one. Taking item one keeps the bounds at thirty eight and thirty two. | Leaving it out drops them to thirty two and twenty two. We expand the thirty eight."),
    ("k_x2", "explain", "Level two. Taking item two: still thirty eight and thirty two. | Leaving it out: thirty six and twenty two."),
    ("k_x3", "excited", "Level three. Taking item three: thirty eight and thirty two again. | But leaving item three out, item four fits whole: ten plus ten plus eighteen. Guaranteed thirty eight!"),
    ("k_answer", "excited", "A guaranteed thirty eight equals the best optimistic bound anywhere, so nothing can beat it. | The answer is x equals one, one, zero, one: profit thirty eight, weight exactly fifteen."),
    ("k_kill", "explain", "Every other live node is killed: thirty six and thirty two are both below thirty eight. | Only four of the sixteen possible choices were ever examined."),
    ("k_sign", "explain", "One textbook detail. | Branch and bound minimises, so the book writes these bounds as negatives: c hat equals minus thirty eight, and u equals minus thirty two."),
    # ---- tsp: the reduced cost matrix
    ("t_problem", "curious", "Now the travelling salesperson. | Here is the cost matrix for five cities. Infinity on the diagonal, because a city has no road to itself."),
    ("t_rows", "explain", "The lower bound comes from reducing the matrix. | Subtract the smallest entry from every row: ten, two, two, three and four. That is twenty one."),
    ("t_cols", "explain", "Then do the same for every column: one, zero, three, zero, zero, another four. | Every tour must pay at least these amounts, so c hat of the root is twenty five."),
    ("t_child", "explain", "For each child, take a road, say one to four. | Cross out row one and column four, block the road back, four to one, and reduce again."),
    ("t_child2", "explain", "The child's c hat is the parent's twenty five, plus the reduced cost of that road, plus the new reduction. | For one to four: twenty five plus zero plus zero, twenty five."),
    ("t_level1", "explain", "The other roads from city one cost more: | one to two gives thirty five, one to three fifty three, and one to five thirty one."),
    ("t_lc", "explain", "LC search expands the smallest: one to four. | From four: to two is twenty eight, to three fifty, to five thirty six."),
    ("t_path", "explain", "Expand one, four, two. From two: to three is fifty two, to five is twenty eight. | Expand one, four, two, five, and the only city left, three, keeps c hat at twenty eight."),
    ("t_done", "excited", "The tour one, four, two, five, three, back to one costs twenty eight. | Every other live node is thirty one or more, so this tour is optimal."),
    # ---- pattern, practice, tips, recap
    ("cmp", "explain", "Same recipe both times. | A lower bound you can trust, LC search expanding the smallest one, and bounds that kill the rest."),
    ("p_intro", "curious", "Your turn. | Same four items, but the bag holds only twelve kilos. What are the two bounds at the root?"),
    ("p_pause", "warm", "Pause the video and work it out. | I'll wait!"),
    ("p_answer", "excited", "Items one, two and three weigh exactly twelve, so both bounds are thirty two, | and the answer is found at the root."),
    ("tip1", "emphatic", "Exam tip one. | For the knapsack, order by profit per weight first, and write both bounds, c hat and u, at every node."),
    ("tip2", "emphatic", "Exam tip two. | For TSP, show the row reduction, the column reduction, and the reduced matrix of at least one child."),
    ("tip3", "emphatic", "Exam tip three. | Say why the answer is optimal: no live node has a bound that can beat it."),
    ("recap", "warm", "To recap: | the knapsack bound is the fractional fill, | the TSP bound is the reduced cost matrix, | and LC branch and bound finds the best answer without visiting every node."),
    ("next", "warm", "That completes Unit Three. In the next video we start Unit Four, with P versus NP and deterministic versus non deterministic algorithms. | See you there!"),
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
