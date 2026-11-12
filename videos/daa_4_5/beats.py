"""Video 4.5 - Approximation Algorithms & Applications in AI, Big Data and Cryptography (DAA Unit IV, last video).

Each beat = one narration line. The key ties it to its animation in scene.py,
the mood steers delivery and background music, "|" marks caption breaks.

Vertex cover: the matching-based 2-approximation on the CLRS graph (vertices 1-7), picks (2,3), (5,6), (4,7) -> 6,
optimum {2,4,5} = 3. Metric TSP: MST + preorder walk on five cities A(0,0) B(4,0) C(4,3) D(0,3) E(2,5).
facts.py recomputes every number.
"""

TITLE = "Approximation Algorithms & Applications in AI, Big Data and Crypto"
CODE = "4.5"
UNIT = "IV"

BEATS = [
    # ---- hook
    ("hook_vans", "curious", "A delivery company must visit two hundred cities tomorrow. The exact best route is NP hard: no computer will find it in time. | Yet the vans leave at eight in the morning, with a route. How?"),
    ("hook_idea", "excited", "They do not find the best route. They find one that is guaranteed to be at most twice the best, in seconds. | That is an approximation algorithm, and it is how the real world handles NP hard problems."),
    ("hook_promise", "explain", "Today: what an approximation ratio is, two classic algorithms with proofs you can write in the exam, vertex cover and TSP, | and where NP hardness shows up in AI, big data and cryptography."),
    ("hook_mascot", "warm", "Welcome to the DAA series. | I'm Abhijeet Karve, and I'll guide you through every algorithm, step by step."),
    ("syllabus", "explain", "This is Unit Four, video five, the last of the unit. | Today: approximation ratios, the two for one vertex cover algorithm, the two for one TSP tour from a minimum spanning tree, and applications in AI, big data and cryptography."),
    ("exam", "explain", "The vertex cover approximation and its proof is a favourite exam question, | so stay till the end for the exam tips."),
    # ---- approximation ratio
    ("r_def", "explain", "An approximation algorithm runs in polynomial time and returns a solution that is close to optimal, with a guarantee. | For a minimisation problem the ratio is the cost of our answer divided by the optimal cost. A two approximation never costs more than twice the optimum."),
    ("r_why", "emphatic", "Why accept this? Because the alternative is exact and exponential. | Twice optimal in one second beats optimal never. And in practice the answers are usually far closer than the guarantee."),
    ("r_terms", "explain", "Three terms. The ratio rho, always at least one. A rho approximation algorithm. | And for some problems a PTAS, a polynomial time approximation scheme: within one plus epsilon of optimal for any epsilon you choose, with a running time that grows as epsilon shrinks."),
    # ---- vertex cover 2-approximation
    ("v_problem", "explain", "Vertex cover again: the guards at junctions, the smallest set of vertices that touches every edge. | NP hard to solve exactly, as we proved last time."),
    ("v_algo", "explain", "The approximation. While edges remain: pick any edge u v, put both u and v into the cover, | and delete every edge that touches u or v. Repeat."),
    ("v_trace", "explain", "On this graph. Pick edge two three: the cover gets two and three, and their four edges go. Pick edge five six: five and six join, three more edges go. | Pick the last edge, four seven: four and seven join. No edges left. Cover of size six."),
    ("v_proof", "emphatic", "The proof is two lines. The edges we picked share no vertex, so they form a matching of size k, and any cover must contain an endpoint of each one: the optimum is at least k. | We used exactly two k vertices. So our cover is at most twice the optimum."),
    ("v_tight", "explain", "Here we picked three edges and used six vertices, while the optimum, two, four, five, has three. | The bound is tight. And the algorithm is polynomial: order V plus E."),
    # ---- metric TSP 2-approximation
    ("t_metric", "explain", "Now TSP with the triangle inequality: going directly is never longer than going through a third city. | True for road distances, flight distances, any real map."),
    ("t_algo", "explain", "The algorithm. Build a minimum spanning tree with Prim or Kruskal. Walk around the tree, visiting every vertex, | and skip any vertex you have already seen. That walk is your tour."),
    ("t_trace", "explain", "Five cities. The spanning tree costs about eleven point seven. Walking around it costs twice that. | Shortcutting the repeats gives the tour A, D, E, C, B, back to A, about fifteen point seven. Here the shortcuts happen to reach the optimum."),
    ("t_proof", "emphatic", "Why at most twice? Remove one edge from the optimal tour and you get a spanning tree, so the minimum spanning tree costs at most the optimal tour. | The full walk costs twice the tree, at most twice optimal, and shortcuts never increase the cost. A two approximation."),
    ("t_better", "explain", "Christofides improves this to one and a half. And without the triangle inequality, no constant ratio is possible unless P equals NP. | Hardness limits even how well you can approximate."),
    # ---- applications
    ("a_ai", "explain", "Applications. AI first. Training a neural network to the global optimum, clustering with k means, finding the smallest decision tree: all NP hard. | Gradient descent and Lloyd's algorithm are heuristics: good solutions, not optimal ones, and that is enough."),
    ("a_ai2", "explain", "Planning and scheduling in AI are reductions to SAT, and modern SAT solvers handle millions of clauses. | Hard in theory, routinely solved in practice. The theory tells you where to expect trouble."),
    ("a_big", "explain", "Big data. Exact answers on a billion rows are too slow, so we approximate on purpose. | Count distinct users with HyperLogLog in a few kilobytes, find frequent items with a Count Min Sketch, and seed clustering with k means plus plus, an order log k approximation."),
    ("a_big2", "explain", "Scheduling jobs on a cluster and placing data across machines are bin packing and partitioning problems, NP hard. | Greedy approximations like first fit decreasing stay within a constant factor of optimal, and they run at scale."),
    ("a_crypto", "emphatic", "Cryptography turns hardness upside down. Everything so far wanted problems to be easy. Cryptography wants them hard. | RSA relies on factoring large numbers being hard, elliptic curve cryptography on the discrete logarithm."),
    ("a_crypto2", "explain", "And the newest schemes, post quantum cryptography, are built on lattice problems like the shortest vector problem, NP hard in their exact form, | which even quantum computers are not known to break. The hardness you studied this unit is the lock on your bank account."),
    ("a_sum", "warm", "So the same list of hard problems means three things. | In AI, approximate them. In big data, approximate them on purpose, for speed. In cryptography, rely on them staying hard."),
    # ---- practice, tips, recap
    ("p_intro", "curious", "Your turn. Run the vertex cover approximation on a path of five vertices, edges one two, two three, three four, four five, picking edge one two first. | What cover do you get, and what is the optimum?"),
    ("p_pause", "warm", "Pause the video and work it out. | I'll wait!"),
    ("p_answer", "excited", "Pick one two: the cover gets one and two, edges one two and two three go. Pick three four: three and four join, the rest go. Cover of size four. | The optimum is two: vertices two and four. Ratio exactly two, within the guarantee."),
    ("tip1", "emphatic", "Exam tip one. | Define the approximation ratio with the formula: for minimisation, our cost over the optimal cost, at least one; for maximisation, the other way round."),
    ("tip2", "emphatic", "Exam tip two. | For vertex cover, write the algorithm and the two line proof: picked edges form a matching, optimum at least k, ours exactly two k."),
    ("tip3", "emphatic", "Exam tip three. | For TSP: state the triangle inequality, then tree at most optimal, walk equals twice the tree, shortcuts never increase. Mention Christofides for one and a half."),
    ("recap", "warm", "To recap: | approximation trades exactness for a guarantee, in polynomial time; | vertex cover and metric TSP both have simple two approximations with short proofs; | and NP hardness is approximated in AI, embraced in big data, and relied upon in cryptography."),
    ("next", "warm", "That completes Unit Four. In the next video we start Unit Five, with network flow and the max flow min cut theorem. | See you there!"),
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
