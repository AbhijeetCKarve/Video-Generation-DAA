#!/usr/bin/env python3
"""Build Video 4.3 (Polynomial-Time Reductions).

    python3 videos/daa_4_3/build.py schedule --estimate
    python3 videos/daa_4_3/build.py all --variant cameo --camera <rec> --no-captions
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
sys.path.insert(0, str(HERE))
import beats  # noqa: E402
from production import main  # noqa: E402

SECTIONS = {
    "hook_real": (None, "bright"),
    "syllabus": ("Today's plan", "calm"),
    "i_translate": ("What is a reduction", "calm"),
    "d_hard": ("The direction rule", "pulse"),
    "r1_problems": ("Reduction 1 · Hamiltonian cycle → TSP", "pulse"),
    "r2_problems": ("Reduction 2 · Independent set ↔ Vertex cover", "pulse"),
    "r3_problems": ("Reduction 3 · Subset sum → Knapsack", "pulse"),
    "c_chain": ("Proving NP-hardness", "calm"),
    "p_intro": ("Practice", "pulse"),
    "tip1": ("Exam tips", "pulse"),
    "recap": ("Recap", "bright"),
}
MIN_WINDOW = {"hook_real": 8.0, "hook_turn": 8.0, "hook_mascot": 6.0, "i_translate": 8.0, "d_trick": 7.0, "r1_problems": 8.0,
              "r1_build": 8.0, "r1_why": 8.0, "r2_problems": 8.0, "r2_why": 7.0, "r3_problems": 7.0, "r3_why": 9.0,
              "c_tree": 9.0, "c_recipe": 10.0, "p_pause": 10.0, "p_answer": 9.0}

if __name__ == "__main__":
    main(beats, HERE / "scene.py", HERE.parents[1] / "projects" / "daa-4.3", SECTIONS, MIN_WINDOW,
         {"title": beats.TITLE, "code": beats.CODE, "unit": beats.UNIT, "end_secs": 15.0,
          "title_suffix": "Everyday Examples",
          "cameo": {"size": 312, "voice": "voice-real", "real": "projects/daa-3.2/voice-real", "lines": {"04": "03"},
                    "shots": [{"beat": "hook_mascot", "kind": "line", "pos": [-5.8, -1.0]},
                              {"beat": "p_pause", "kind": "after", "pos": [-5.8, -1.0]},
                              {"kind": "end", "pos": [-5.8, 1.3]}]},
          "summary": "Reductions explained with everyday problems. What a polynomial-time reduction is (a translator "
                     "that keeps the yes/no answer), the direction rule everyone gets backwards (A reduces to B means B "
                     "is at least as hard), and three worked reductions: Hamiltonian cycle to TSP (a delivery van), "
                     "independent set to vertex cover (party guests versus street guards), and subset sum to the "
                     "decision knapsack (paying an exact bill). Then how reductions chain from SAT into a family tree "
                     "of NP-hard problems, the four-step recipe for proving a problem NP-hard, a practice question "
                     "(charging stations) and exam tips.",
          "hashtags": "#DAA #Reductions #NPHard #PvsNP #ComplexityTheory #Algorithms #DESPU",
          "tags": "daa, design and analysis of algorithms, polynomial time reduction, reductions, np hard proof, "
                  "hamiltonian cycle to tsp, vertex cover independent set, subset sum knapsack, np complete, "
                  "complexity theory, daa unit 4, etcs329"})
