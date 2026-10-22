"""Video 4.4 - Proving NP-Completeness: 3-SAT, Clique & Vertex Cover (DAA Unit IV).

Each beat = one narration line. The key ties it to its animation in scene.py,
the mood steers delivery and background music, "|" marks caption breaks.

Proofs after Karp / Horowitz-Sahni: SAT -> 3-SAT (split long clauses, pad short ones),
3-SAT -> Clique (the literal graph, clique of size k = number of clauses),
Clique -> Vertex cover (the complement graph, cover of size n - k). facts.py checks each one by brute force.
Example formula: (x1 v -x2 v x3) ^ (-x1 v x2 v x3) ^ (x1 v x2 v -x3). Example graph: K4 on 1-4 plus the edge 1-5.
"""

TITLE = "Proving NP-Completeness: 3-SAT, Clique & Vertex Cover"
CODE = "4.4"
UNIT = "IV"

BEATS = [
    # ---- hook
    ("hook_clique", "curious", "On a social network, can you find five people who all follow each other? | That is the clique problem, and it is NP complete. Today we prove it."),
    ("hook_chain", "explain", "We will prove three problems NP complete, one after the other: three SAT, clique, and vertex cover. | Each proof is a reduction from the previous one."),
    ("hook_name", "excited", "Proving NP completeness sounds frightening, | but it is the same two step template every time, and by the end you will write these proofs yourself."),
    ("hook_mascot", "warm", "Welcome to the DAA series. | I'm Abhijeet Karve, and I'll guide you through every algorithm, step by step."),
    ("syllabus", "explain", "This is Unit Four, video four. | Today: the two step template, three SAT, the reduction from three SAT to clique, from clique to vertex cover, and how the three are related."),
    ("exam", "explain", "Prove that a problem is NP complete is a classic eight mark question. | So stay till the end for the exam tips."),
    # ---- the template
    ("t_steps", "emphatic", "The template. Step one: show X is in NP. Give a certificate, and check it in polynomial time. | Step two: show X is NP hard. Take a known NP complete problem and reduce it to X."),
    ("t_why", "explain", "Why does this prove NP complete? NP hard plus in NP is the definition from video four point two. | And the direction, known hard problem reduces to X, is the rule from video four point three."),
    ("t_start", "explain", "The chain needs a start, and Cook's theorem gives it: SAT is NP complete. | Every other proof borrows from SAT, directly or through a chain."),
    # ---- 3-SAT
    ("s_def", "explain", "Three SAT. A formula in conjunctive normal form: an AND of clauses, where every clause is an OR of exactly three literals. | Is it satisfiable?"),
    ("s_innp", "explain", "Step one. Three SAT is in NP: | the certificate is an assignment, and checking every clause takes linear time."),
    ("s_reduce", "explain", "Step two. SAT reduces to three SAT. Translate every clause into clauses of exactly three literals. | A long clause is split with a fresh variable: a or b or c or d becomes, a or b or y, and, not y or c or d."),
    ("s_short", "explain", "A short clause is padded: a or b becomes, a or b or y, and, a or b or not y. | The new formula is satisfiable exactly when the old one is, and the translation is linear in the size of the formula. Three SAT is NP complete."),
    # ---- clique
    ("c_def", "explain", "Clique. Given a graph and a number k, is there a set of k vertices that are all pairwise connected? | Five people who all follow each other: a clique of size five."),
    ("c_innp", "explain", "Step one. Clique is in NP: | the certificate is the k vertices; check the k choose two edges between them, polynomial."),
    ("c_build", "explain", "Step two. Three SAT reduces to clique. Take a three SAT formula with k clauses. | Make one vertex for every literal of every clause: three k vertices, in k groups."),
    ("c_edges", "explain", "Draw an edge between two vertices when they are in different clauses and they are not opposites: never x with not x. | Then ask for a clique of size k."),
    ("c_example", "explain", "Our example has three clauses, so nine vertices and k equals three. | Picking x three from clause one, x three from clause two and x one from clause three gives a triangle: a clique of size three."),
    ("c_why", "explain", "Why it works. A clique of size k picks one literal from every clause with no contradictions, so setting those literals true satisfies the formula. | And a satisfying assignment picks one true literal per clause, and those k vertices form a clique. Yes matches yes."),
    ("c_done", "excited", "The graph has three k vertices and fewer than nine k squared edges: polynomial. | Clique is NP complete."),
    # ---- vertex cover
    ("v_def", "explain", "Vertex cover. Given a graph and k, is there a set of k vertices that touches every edge? | The guards at junctions from the last video."),
    ("v_innp", "explain", "Step one. Vertex cover is in NP: | the certificate is the k vertices; check that every edge touches one of them, polynomial."),
    ("v_build", "explain", "Step two. Clique reduces to vertex cover. Take the graph G and build its complement, G bar: same vertices, with an edge exactly where G has none. | Ask for a cover of size n minus k."),
    ("v_example", "explain", "Our example: five vertices, and one, two, three, four form a clique of size four. | In the complement, the only edges are the three missing from G, and vertex five alone covers them. Clique of four, cover of one: one is five minus four."),
    ("v_why", "explain", "Why it works. The k clique vertices have no complement edges among them, so every complement edge touches the other n minus k vertices: they are a cover. | And the vertices outside a cover have no edges in G bar, so they are a clique in G."),
    ("v_done", "excited", "The complement has the same n vertices and fewer than n squared edges: polynomial. | Vertex cover is NP complete."),
    # ---- how they relate
    ("r_triangle", "explain", "Three problems, one triangle. | A clique in G, an independent set in G bar, and the complement of a vertex cover in G bar are the same set of vertices. Any one of them solves the others."),
    ("r_chain", "explain", "And the chain: SAT to three SAT to clique to vertex cover. | Each arrow is one reduction, and hardness flows down the arrows from Cook's theorem to everything."),
    ("r_use", "warm", "In the exam you may use any of these as your known NP complete problem. | Pick the one that looks most like your new problem: that makes the translation short."),
    # ---- practice, tips, recap
    ("p_intro", "curious", "Your turn. Independent set: is there a set of k vertices with no edges among them? | Prove it is NP complete, using clique as the known problem."),
    ("p_pause", "warm", "Pause the video and write the two steps. | I'll wait!"),
    ("p_answer", "excited", "In NP: the certificate is the set; check that no pair is an edge. | NP hard: a clique of size k in G is an independent set of size k in G bar. So clique reduces to independent set: the complement graph, the same k. Done."),
    ("tip1", "emphatic", "Exam tip one. | Always write both steps with headings: in NP, and NP hard. Students lose marks by proving only the reduction."),
    ("tip2", "emphatic", "Exam tip two. | For the reduction, write four things: the known problem, the translation, yes if and only if yes, and the polynomial size."),
    ("tip3", "emphatic", "Exam tip three. | Memorise the two pictures: the literal graph for three SAT to clique, and the complement graph for clique to vertex cover."),
    ("recap", "warm", "To recap: | NP complete means in NP plus a reduction from a known NP complete problem; | three SAT by splitting clauses, clique by the literal graph; | vertex cover by the complement graph; | and all three are linked."),
    ("next", "warm", "In the next video, the last of Unit Four: approximation algorithms, and how NP hard problems are handled in AI, big data and cryptography. | See you there!"),
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
