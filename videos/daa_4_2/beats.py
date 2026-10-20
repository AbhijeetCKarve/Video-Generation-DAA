"""Video 4.2 - P, NP, NP-Hard & NP-Complete (DAA Unit IV).

Each beat = one narration line. The key ties it to its animation in scene.py,
the mood steers delivery and background music, "|" marks caption breaks.

Definitions after Horowitz-Sahni ch. 11: P / NP via deterministic / non-deterministic polynomial algorithms,
L1 reduces to L2 (L1 proportional-to L2), NP-hard = SAT reduces to L, NP-complete = NP-hard and in NP,
Cook's theorem (1971): SAT is in P iff P = NP. Example formula (x1 or x2) and (not x1 or x3).
"""

TITLE = "P, NP, NP-Hard & NP-Complete Explained"
CODE = "4.2"
UNIT = "IV"

BEATS = [
    # ---- hook
    ("hook_q", "curious", "Two questions about the same graph. Does it have a Hamiltonian cycle? And: what is the shortest tour? | One is a yes or no question, the other asks for the best answer."),
    ("hook_names", "explain", "Complexity theory sorts such problems into classes: P, NP, NP hard and NP complete. | Four names that every DAA exam asks about."),
    ("hook_big", "excited", "And behind them sits the most famous open question in computer science: is P equal to NP? | There is a one million dollar prize for the answer."),
    ("hook_mascot", "warm", "Welcome to the DAA series. | I'm Abhijeet Karve, and I'll guide you through every algorithm, step by step."),
    ("syllabus", "explain", "This is Unit Four, video two. | Today: decision versus optimisation problems, the formal definitions of P and NP, NP hard and NP complete, and the P versus NP question."),
    ("exam", "explain", "Defining these four classes, with the diagram, is a guaranteed exam question, | so stay till the end for the exam tips."),
    # ---- decision vs optimisation
    ("d_opt", "explain", "An optimisation problem asks for the best answer: | the shortest tour, the maximum profit, the fewest colours."),
    ("d_dec", "explain", "A decision problem asks only yes or no: | is there a tour of length at most k? Is there a packing with profit at least r? Can the graph be coloured with k colours?"),
    ("d_link", "explain", "The two are linked. If you can solve the decision version in polynomial time, you can solve the optimisation version too, | by asking the yes or no question for different values of k, a polynomial number of times."),
    ("d_why", "emphatic", "That is why complexity theory talks about decision problems only. | Every class we define today is a class of decision problems."),
    # ---- P and NP
    ("p_def", "explain", "The class P: all decision problems that a deterministic algorithm can solve in polynomial time. | Shortest path, minimum spanning tree, is this number prime: all in P."),
    ("np_def", "explain", "The class NP: all decision problems that a non deterministic algorithm can solve in polynomial time. | Guess a candidate answer, verify it in polynomial time."),
    ("np_ex", "explain", "Hamiltonian cycle, the decision knapsack, graph colouring, satisfiability: all in NP. | The certificate, a cycle, a packing, a colouring, an assignment, can be checked fast."),
    ("p_in_np", "emphatic", "Every problem in P is also in NP: a deterministic algorithm is just a non deterministic one that never uses Choice. | So P is a subset of NP."),
    ("pvsnp", "curious", "The open question is the other direction. Is every problem in NP also in P? Nobody knows. | Most computer scientists believe P is not equal to NP, but there is no proof."),
    # ---- satisfiability and reductions
    ("sat", "explain", "To define the hard classes we need one special problem: satisfiability. | Given a Boolean formula, is there an assignment of true and false to its variables that makes it true?"),
    ("sat_ex", "explain", "For example: x one or x two, and, not x one or x three. Setting x one true and x three true satisfies it. | With n variables there are two to the n assignments, but checking one is easy. So SAT is in NP."),
    ("reduce", "explain", "Next, reducibility. Problem L one reduces to L two | if a deterministic polynomial time algorithm can turn any instance of L one into an instance of L two with the same yes or no answer."),
    ("reduce_mean", "explain", "So if L two can be solved in polynomial time, so can L one. L two is at least as hard as L one. | Reductions are the whole of the next video; today we only need the definition."),
    # ---- NP-hard and NP-complete
    ("nph_def", "emphatic", "A problem L is NP hard if satisfiability reduces to L. | Equivalently: every problem in NP reduces to L. L is at least as hard as everything in NP."),
    ("npc_def", "emphatic", "A problem L is NP complete if it is NP hard and it is also in NP. | The hardest problems inside NP."),
    ("cook", "explain", "Why satisfiability? Cook's theorem, nineteen seventy one: satisfiability is in P if and only if P equals NP. | SAT was the first NP complete problem, and every other one is proved by a reduction from it."),
    ("examples", "explain", "NP complete problems: satisfiability, three SAT, Hamiltonian cycle, vertex cover, clique, graph colouring, the decision knapsack. | We will prove some of these in video four point four."),
    ("nph_only", "explain", "Some problems are NP hard but not NP complete, because they are not in NP. | The halting problem is one: no algorithm decides it at all, yet SAT reduces to it. And optimisation versions, like the shortest tour, are NP hard."),
    # ---- the picture
    ("venn", "explain", "Here is the picture to draw in the exam. P inside NP. NP hard overlapping NP. | The overlap is NP complete. Outside NP sit the NP hard problems that are not NP complete."),
    ("collapse", "excited", "If anyone ever finds a polynomial algorithm for one NP complete problem, then by the reductions every problem in NP has one, | and P equals NP. The whole picture collapses into one circle."),
    ("prize", "warm", "That is why it is a millennium prize problem: | one million dollars from the Clay Mathematics Institute, unclaimed since the year two thousand."),
    # ---- practice, tips, recap
    ("p_intro", "curious", "Your turn. Which of these are in NP, and which are also in P? | Is there a path between two vertices of length at most k? Does the graph have a Hamiltonian cycle? Is this array sorted?"),
    ("p_pause", "warm", "Pause the video and decide. | I'll wait!"),
    ("p_answer", "excited", "All three are in NP. The path question and the sorted check are also in P: Dijkstra, and one linear scan. | Hamiltonian cycle is in NP, in fact NP complete, and nobody knows whether it is in P."),
    ("tip1", "emphatic", "Exam tip one. | Give all four definitions in one breath: P, deterministic polynomial; NP, non deterministic polynomial; NP hard, SAT reduces to it; NP complete, NP hard and in NP."),
    ("tip2", "emphatic", "Exam tip two. | Draw the diagram with P inside NP, and name one example in each region: shortest path, Hamiltonian cycle, the halting problem."),
    ("tip3", "emphatic", "Exam tip three. | State Cook's theorem, and what P equals NP would mean: one polynomial algorithm for any NP complete problem gives one for all of NP."),
    ("recap", "warm", "To recap: | decision problems only; | P is deterministic polynomial, NP is guess and verify; | NP hard is as hard as SAT, NP complete is NP hard and in NP; | and P versus NP is still open."),
    ("next", "warm", "In the next video, polynomial time reductions: how to prove a problem is NP hard by reducing a known hard problem to it. | See you there!"),
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
