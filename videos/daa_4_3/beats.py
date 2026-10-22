"""Video 4.3 - Polynomial-Time Reductions (DAA Unit IV).

Each beat = one narration line. The key ties it to its animation in scene.py,
the mood steers delivery and background music, "|" marks caption breaks.

Everyday framing: exam timetabling (graph colouring), a delivery van (Hamiltonian cycle -> TSP),
party guests vs street guards (independent set <-> vertex cover), paying an exact bill (subset sum -> knapsack),
charging stations (vertex cover). Reductions after Horowitz-Sahni ch. 11 / Karp's tree. facts.py checks each one
by brute force on small instances.
"""

TITLE = "Polynomial-Time Reductions Made Simple"
CODE = "4.3"
UNIT = "IV"

BEATS = [
    # ---- hook
    ("hook_real", "curious", "Your college must schedule the final exams. Two exams cannot share a slot if some student takes both. | How few slots do you need? That is exam timetabling."),
    ("hook_turn", "excited", "Draw one node per exam, and an edge when a student takes both. | Now the question is: can this graph be coloured with k colours? You just performed a reduction."),
    ("hook_name", "explain", "Reductions are how we solve a new problem with an old algorithm, | and how we prove that a problem is hard. Today we make them simple."),
    ("hook_mascot", "warm", "Welcome to the DAA series. | I'm Abhijeet Karve, and I'll guide you through every algorithm, step by step."),
    ("syllabus", "explain", "This is Unit Four, video three. | Today: what a reduction is, the direction rule that confuses everyone, three worked reductions with everyday problems, and how reductions prove NP hardness."),
    ("exam", "explain", "Reductions are the toughest topic in this unit, and a guaranteed question. | So stay till the end for the exam tips."),
    # ---- the idea
    ("i_translate", "explain", "Think of a reduction as a translator. You have a problem A you cannot solve, and a problem B with a known solver. | The reduction translates every A question into a B question, so that B's yes or no is also A's yes or no."),
    ("i_rules", "emphatic", "Two rules. One: the translation itself must be fast, polynomial time. | Two: the answer must be preserved. A says yes exactly when B says yes."),
    ("i_notation", "explain", "We write A reduces to B, A proportional to B, or A less than or equal, with a small p, B. | Read it as: A is no harder than B. If you can do B, you can do A."),
    ("i_everyday", "warm", "You do this every day. Are two houses within five kilometres? You ask the map app for the shortest path. | Can these guests be seated without a fight? That is graph colouring. Translate, then use the tool you already have."),
    # ---- the direction rule
    ("d_hard", "emphatic", "Now the part everyone gets backwards. A reduces to B means B is at least as hard as A. | If B were easy, A would be easy too, through the translation."),
    ("d_prove", "emphatic", "So to prove that a new problem X is hard, you reduce a known hard problem to X. | Not the other way around. Known hard problem on the left, your new problem on the right."),
    ("d_trick", "warm", "A memory trick: hardness flows along the arrow. | SAT reduces to X, so X inherits the hardness of SAT. The arrow always starts at the problem you already know is hard."),
    # ---- reduction 1: Hamiltonian cycle -> TSP
    ("r1_problems", "explain", "Reduction one. Hamiltonian cycle: a delivery van must visit every house exactly once and return home, using only the roads that exist. | TSP, decision version: with road costs, is there a tour of cost at most k?"),
    ("r1_build", "explain", "The translation. Take the road map with n houses. Make every pair of houses a road: cost one if the road exists, cost two if it does not. | And set k equal to n."),
    ("r1_why", "explain", "Why it works. A tour of cost at most n must use n roads of cost one, so it is a Hamiltonian cycle. | And a Hamiltonian cycle gives a tour of cost exactly n. Yes matches yes."),
    ("r1_time", "excited", "The translation lists n squared pairs: polynomial. | So Hamiltonian cycle reduces to TSP, and since Hamiltonian cycle is NP hard, TSP is NP hard too."),
    # ---- reduction 2: independent set <-> vertex cover
    ("r2_problems", "explain", "Reduction two. Independent set: invite k guests to a party where no two invited people dislike each other. | Vertex cover: place k guards at junctions so that every street has a guard at one of its ends."),
    ("r2_build", "explain", "Same graph for both: people and dislikes, or junctions and streets. | The translation changes only the number: can you invite k guests? becomes: can n minus k guards cover every street?"),
    ("r2_why", "explain", "Why it works. A set is independent exactly when everyone outside it forms a cover. | No dislike inside the party means every dislike touches someone outside. Complement the set, flip the number."),
    ("r2_lesson", "warm", "Lesson: a reduction can be almost trivial. | Independent set reduces to vertex cover, and vertex cover reduces to independent set. They are equally hard."),
    # ---- reduction 3: subset sum -> knapsack
    ("r3_problems", "explain", "Reduction three. Subset sum: you have notes of various values. Can you pay exactly five hundred rupees, no change? | The decision knapsack: is there a packing with weight at most m and profit at least r?"),
    ("r3_build", "explain", "The translation: each note becomes an item whose weight and profit are both its value. | Set m and r both to five hundred."),
    ("r3_why", "explain", "Weight at most five hundred and profit at least five hundred force the total to be exactly five hundred. Yes matches yes. | The translation copies n numbers: linear time. Subset sum reduces to knapsack, so knapsack is at least as hard as subset sum."),
    # ---- how reductions prove NP-hardness
    ("c_chain", "explain", "Reductions chain. If A reduces to B and B reduces to C, then A reduces to C: translate twice, still polynomial. | That is why one hard problem, SAT, is enough as the root."),
    ("c_tree", "explain", "From SAT, by Cook's theorem, we go to three SAT, then to clique, vertex cover and independent set, | to Hamiltonian cycle and TSP, to subset sum and knapsack. A family tree of hardness, every branch one reduction."),
    ("c_recipe", "emphatic", "The recipe for proving X is NP hard, in four steps. Pick a known NP hard problem. Give the translation. Show yes maps to yes and no maps to no. Show the translation is polynomial. | Add that X is in NP, and X is NP complete."),
    ("c_use", "warm", "Reductions also work for you. A new rostering problem at a company? | Translate it to SAT or integer programming and hand it to a solver that is already excellent. Translate, then reuse."),
    # ---- practice, tips, recap
    ("p_intro", "curious", "Your turn. Your city wants k charging stations at junctions, so that every street has a station at one of its ends. | Which problem is this, and what does that tell you about its difficulty?"),
    ("p_pause", "warm", "Pause the video and think. | I'll wait!"),
    ("p_answer", "excited", "It is vertex cover, exactly: junctions are vertices, streets are edges, stations are the cover. | Vertex cover is NP complete, so no polynomial algorithm is known. For a real city, use an approximation or a solver."),
    ("tip1", "emphatic", "Exam tip one. | Write the direction rule first: the known hard problem reduces to the new problem. Then the four steps: translation, yes to yes, no to no, polynomial time."),
    ("tip2", "emphatic", "Exam tip two. | Learn the two worked reductions by heart: Hamiltonian cycle to TSP with costs one and two and k equal to n, and independent set to vertex cover with n minus k."),
    ("tip3", "emphatic", "Exam tip three. | Never write: X reduces to SAT, so X is NP hard. That direction proves nothing. SAT reduces to X is what you need."),
    ("recap", "warm", "To recap: | a reduction translates A into B in polynomial time, preserving the answer; | A reduces to B means B is at least as hard; | to prove X is hard, reduce a known hard problem to X; | and reductions chain from SAT to everything."),
    ("next", "warm", "In the next video, we prove NP completeness properly: three SAT, vertex cover and clique, step by step. | See you there!"),
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
