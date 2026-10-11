"""Video 3.3 - Sum of Subsets & Hamiltonian Cycle (DAA Unit III).

Each beat = one narration line. The key ties it to its animation in scene.py,
the mood steers delivery and background music, "|" marks caption breaks.

Examples: weights {7, 11, 13, 24} with target 31 (answers 7+11+13 and 7+24);
a 5-city road map whose Hamiltonian cycle is 1-2-4-5-3-1 after one dead end.
"""

TITLE = "Sum of Subsets & Hamiltonian Cycle"
CODE = "3.3"
UNIT = "III"

BEATS = [
    # ---- hook
    ("hook_weights", "curious", "Here are four weights: seven, eleven, thirteen and twenty four kilos. | Can you pick some of them that weigh exactly thirty one?"),
    ("hook_answer", "excited", "Two ways: seven plus twenty four, and seven plus eleven plus thirteen. | With forty weights there are over a trillion subsets, and backtracking finds the answers without trying them all."),
    ("hook_mascot", "warm", "Welcome to the DAA series. | I'm Abhijeet Karve, and I'll guide you through every algorithm, step by step."),
    ("syllabus", "explain", "This is Unit Three, video three. | Two more classic backtracking problems: sum of subsets, and the Hamiltonian cycle."),
    ("exam", "explain", "Both appear in exams as draw-the-state-space-tree questions, | so stay till the end for the exam tips."),
    # ---- sum of subsets: the model
    ("s_def", "explain", "Sum of subsets. | Given n positive weights and a target m, find every subset whose weights add up to exactly m."),
    ("s_tuple", "explain", "A solution is a tuple of zeros and ones: | x k is one if weight k is chosen, and zero if it is left out."),
    ("s_sort", "emphatic", "We keep the weights sorted in increasing order: seven, eleven, thirteen, twenty four. | The bounding function depends on that."),
    ("s_state", "explain", "Every node remembers three numbers: | s, the sum chosen so far; k, the next weight to decide; and r, the sum of the weights still undecided."),
    ("s_bound1", "explain", "Two bounding checks. | First: s plus everything remaining must reach m, otherwise even taking all of it is not enough."),
    ("s_bound2", "explain", "Second: s plus the next weight must not exceed m, | otherwise we have already overshot."),
    # ---- sum of subsets: the trace
    ("t_root", "warm", "Let's trace it. | At the root, s is zero, k is one, and r is fifty five, the sum of all four weights."),
    ("t_x1", "explain", "Weight one is seven. Taking it makes s seven. | That is the left child, x one equals one."),
    ("t_sol1", "excited", "Take eleven as well: s is eighteen. Then take thirteen: s is thirty one. | That equals m, so we have our first answer: seven, eleven, thirteen."),
    ("t_back1", "explain", "Back up one step. At s eighteen, skipping thirteen leaves only twenty four, | and eighteen plus twenty four is forty two, over m. That node dies."),
    ("t_back2", "explain", "Back to s seven, and skip eleven. | Taking thirteen gives twenty, and twenty plus twenty four is forty four, too big, so that node dies."),
    ("t_sol2", "excited", "Skip thirteen as well, so s is still seven, and take twenty four: thirty one. | Second answer: seven and twenty four!"),
    ("t_right", "explain", "Finally, leave seven out. | Every path on this side overshoots thirty one or cannot reach it, so they all die early."),
    ("t_count", "warm", "Done. Sixteen nodes instead of thirty one in the full tree, | and not a single hopeless subset was built."),
    # ---- sum of subsets: the algorithm
    ("s_algo", "explain", "Here is the algorithm, Sum Of Sub of s, k, r. | It first tries x k equals one, then x k equals zero."),
    ("s_algo2", "explain", "Taking weight k: if the new sum equals m, print the answer; | if the sum plus the next weight is still within m, go deeper."),
    ("s_algo3", "explain", "Leaving weight k: go deeper only if the remaining weights can still reach m, | and the next weight does not overshoot."),
    ("s_complex", "explain", "There are two to the power n subsets, so the worst case is order two to the n. | The bounding function is what makes it fast in practice."),
    # ---- hamiltonian cycle
    ("h_intro", "curious", "Now the second problem. | A delivery van must visit five cities and come back home, visiting each city exactly once, using only the roads that exist."),
    ("h_def", "explain", "In graph terms, this is a Hamiltonian cycle: | a cycle that passes through every vertex exactly once and returns to the start."),
    ("h_history", "warm", "It is named after William Hamilton, | who sold it as a board game puzzle in eighteen fifty seven."),
    ("h_tuple", "explain", "Our tuple is the order of the visit, x one to x n. | We fix x one as vertex one, so the same cycle is not counted n times."),
    ("h_bound", "emphatic", "The bounding rule for x k has three checks: | it must be adjacent to the previous vertex, it must not be visited already, | and the last vertex must also be adjacent to vertex one, to close the cycle."),
    ("h_trace1", "explain", "Start at one. Vertex two is adjacent, so x two is two. | From two, the smallest unvisited neighbour is three. From three, it is five."),
    ("h_dead", "emphatic", "The last vertex must be four, the only one left. | Four is adjacent to five, but there is no road from four back to one. Dead end!"),
    ("h_back", "explain", "Backtrack to x three. After vertex two, the next option is four. | From four we go to five, and from five to three."),
    ("h_found", "excited", "Three is adjacent to one, so the cycle closes: | one, two, four, five, three, and back to one. Found!"),
    ("h_algo", "explain", "The algorithm. Next Value of k keeps trying the next vertex for x k | until one passes all three checks."),
    ("h_algo2", "explain", "Hamiltonian of k calls Next Value; | if k equals n it prints the cycle, otherwise it moves on to k plus one."),
    ("h_complex", "explain", "In the worst case it tries every ordering of the remaining vertices, | order of n factorial. Still far better than listing all orderings first."),
    # ---- pattern, practice, tips, recap
    ("cmp", "explain", "Both problems follow the same pattern as the queens: | choose x k, check the bound, go deeper, and come back when stuck."),
    ("p_intro", "curious", "Your turn. | Weights three, five, six and seven, target fifteen. Find every subset that works."),
    ("p_pause", "warm", "Pause the video and draw the tree, with s, k and r at every node. | I'll wait!"),
    ("p_answer", "excited", "There is exactly one answer: three plus five plus seven. | Every path that takes six either overshoots fifteen or falls short."),
    ("tip1", "emphatic", "Exam tip one. | For sum of subsets, label every node with s, k and r, and write the two bounding conditions beside the tree."),
    ("tip2", "emphatic", "Exam tip two. | Sort the weights first, and say that you did. Without sorting, the second check is not valid."),
    ("tip3", "emphatic", "Exam tip three. | For the Hamiltonian cycle, list the three checks of Next Value, and show the dead end before the cycle."),
    ("recap", "warm", "To recap: | sum of subsets tracks s, k and r with two bounding checks, | the Hamiltonian cycle picks the next adjacent unvisited vertex, | and both use the same backtracking control abstraction."),
    ("next", "warm", "In the next video, we move on to Branch and Bound: FIFO, LIFO and least cost search. | See you there!"),
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
