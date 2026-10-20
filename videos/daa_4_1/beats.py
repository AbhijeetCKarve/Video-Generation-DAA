"""Video 4.1 - Polynomial vs Non-Polynomial & Deterministic vs Non-Deterministic Algorithms (DAA Unit IV).

Each beat = one narration line. The key ties it to its animation in scene.py,
the mood steers delivery and background music, "|" marks caption breaks.

Numbers (facts.py recomputes them): 1 step = 1 ns. n^3 at n = 100 -> 1 ms; 2^n at n = 100 -> 40 trillion years;
all tours of 25 cities (24!/2) -> about 10 million years. Non-deterministic algorithms after Horowitz-Sahni ch. 11:
NSearch O(1), NSort O(n), DKP (decision knapsack) O(n).
"""

TITLE = "Polynomial vs Exponential & Non-Deterministic Algorithms"
CODE = "4.1"
UNIT = "IV"

BEATS = [
    # ---- hook
    ("hook_fast", "curious", "Imagine a computer that does one billion steps every second. | Sorting a million numbers takes it a fraction of a second."),
    ("hook_slow", "curious", "Now ask it to try every tour of twenty five cities. | It will still be running ten million years from now."),
    ("hook_name", "excited", "The difference is not the computer. It is the growth rate of the algorithm, | and that one idea is the start of complexity theory."),
    ("hook_mascot", "warm", "Welcome to the DAA series. | I'm Abhijeet Karve, and I'll guide you through every algorithm, step by step."),
    ("syllabus", "explain", "This is Unit Four, video one. | Today: polynomial versus exponential growth, tractable and intractable problems, and deterministic versus non deterministic algorithms."),
    ("exam", "explain", "Non deterministic algorithms are a favourite short note in the exam, | so stay till the end for the exam tips."),
    # ---- growth rates
    ("g_poly", "explain", "An algorithm runs in polynomial time when its running time is bounded by a polynomial in the input size: | n, n log n, n squared, n cubed, any n to the power k."),
    ("g_exp", "explain", "It runs in exponential time when n sits in the exponent, | like two to the n, or n factorial. These grow much, much faster."),
    ("g_table", "emphatic", "Watch the table, at a billion steps a second. | n cubed for n equals one hundred takes one millisecond. Two to the n for n equals one hundred takes forty trillion years."),
    ("g_point", "explain", "The point is the gap. Make the computer a thousand times faster, | and a cubic algorithm handles ten times the input, but an exponential one handles only about ten more items."),
    # ---- tractable vs intractable
    ("t_def", "explain", "Problems that have a polynomial time algorithm are called tractable. | Problems for which no polynomial time algorithm is known are called intractable."),
    ("t_examples", "explain", "Sorting, searching, shortest paths, the minimum spanning tree: all tractable. | The travelling salesperson, Hamiltonian cycle, graph coloring, the zero one knapsack: no polynomial algorithm is known for any of them."),
    ("t_unit3", "explain", "Those are exactly the problems from Unit Three. | Backtracking and branch and bound help on average, but in the worst case they still take exponential time."),
    ("t_open", "curious", "Nobody has proved that these problems have no polynomial algorithm. Nobody has found one either. | That open question is P versus NP, the subject of the next video."),
    # ---- deterministic vs non-deterministic
    ("d_det", "explain", "Every algorithm so far has been deterministic: | each step has exactly one outcome, and the same input always follows the same path."),
    ("n_idea", "excited", "A non deterministic algorithm is allowed one magical step: Choice. | Choice picks an element from a set, and if any pick can lead to success, it picks that one."),
    ("n_funcs", "explain", "Three functions. Choice of S picks an element of the set S. Failure signals an unsuccessful completion. Success signals a successful one. | Each takes order one time."),
    ("n_rule", "emphatic", "The rule: if there is any sequence of choices that leads to Success, the algorithm is assumed to make exactly those choices. | It fails only when no sequence of choices can succeed."),
    ("n_search", "explain", "Example one: searching. j is Choice of one to n. | If A of j equals x, write j and Success. Otherwise, Failure."),
    ("n_search2", "explain", "Deterministically, search takes n steps in the worst case. | Non deterministically, it takes order one: the position is guessed, and one comparison checks it."),
    ("n_sort", "explain", "Example two: sorting positive integers. For each i, guess a position j with Choice of one to n. If B of j is already filled, Failure. Else B of j gets A of i. | Then check: if any B of i is bigger than B of i plus one, Failure. Otherwise write B, and Success."),
    ("n_sort2", "explain", "Every loop runs at most n times, so non deterministic sorting is order n, | where the best deterministic sort needs n log n."),
    ("n_interp", "explain", "Two ways to picture it. A machine with unlimited parallelism that tries every choice at the same time, | or a lucky guesser whose guess is then verified. Either way: guess, then verify."),
    ("n_knap", "explain", "Example three: the zero one knapsack as a yes or no question. Is there a choice of items with weight at most m and profit at least r? | Guess each x of i as zero or one with Choice, add up the weight and profit, and check. Order n."),
    ("n_point", "emphatic", "That is the pattern behind every hard problem from Unit Three. | Finding the answer looks exponential, but checking a given answer is polynomial."),
    ("n_class", "explain", "That gives the class NP: non deterministic polynomial time. | A yes or no problem is in NP when a non deterministic algorithm solves it in polynomial time: guess the answer, verify it fast."),
    # ---- practice, tips, recap
    ("p_intro", "curious", "Your turn. | Write a non deterministic algorithm that decides whether a graph on n vertices has a Hamiltonian cycle, in polynomial time."),
    ("p_pause", "warm", "Pause the video and write it down. | I'll wait!"),
    ("p_answer", "excited", "Guess: for each position i, v of i is Choice of one to n. | Verify: no vertex repeats, every consecutive pair is an edge, and the last vertex connects back to the first. That check is polynomial, so Hamiltonian cycle is in NP."),
    ("tip1", "emphatic", "Exam tip one. | Define a polynomial time algorithm by the bound order n to the k, and give the growth table: n cubed against two to the n."),
    ("tip2", "emphatic", "Exam tip two. | For non deterministic algorithms, name the three functions, Choice, Failure and Success, and state the rule: the algorithm fails only when no sequence of choices succeeds."),
    ("tip3", "emphatic", "Exam tip three. | Write non deterministic search or sorting as your example, with its time: order one for search, order n for sorting."),
    ("recap", "warm", "To recap: | polynomial time is tractable, exponential time is not, | the hard problems of Unit Three have no known polynomial algorithm, | and a non deterministic algorithm guesses with Choice and verifies in polynomial time."),
    ("next", "warm", "In the next video, we define the classes P, NP, NP hard and NP complete properly, and meet the P versus NP question. | See you there!"),
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
