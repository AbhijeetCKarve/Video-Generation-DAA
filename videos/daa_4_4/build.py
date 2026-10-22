#!/usr/bin/env python3
"""Build Video 4.4 (Proving NP-Completeness: 3-SAT, Clique & Vertex Cover).

    python3 videos/daa_4_4/build.py schedule --estimate
    python3 videos/daa_4_4/build.py all --variant cameo --camera <rec> --no-captions
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
sys.path.insert(0, str(HERE))
import beats  # noqa: E402
from production import main  # noqa: E402

SECTIONS = {
    "hook_clique": (None, "bright"),
    "syllabus": ("Today's plan", "calm"),
    "t_steps": ("The two-step template", "calm"),
    "s_def": ("3-SAT", "pulse"),
    "c_def": ("Clique · 3-SAT → Clique", "pulse"),
    "v_def": ("Vertex cover · Clique → Vertex cover", "pulse"),
    "r_triangle": ("How they relate", "calm"),
    "p_intro": ("Practice", "pulse"),
    "tip1": ("Exam tips", "pulse"),
    "recap": ("Recap", "bright"),
}
MIN_WINDOW = {"hook_clique": 8.0, "hook_chain": 7.0, "hook_mascot": 6.0, "t_steps": 8.0, "s_def": 7.0, "s_innp": 6.0, "s_reduce": 8.0,
              "s_short": 9.0, "c_def": 7.0, "c_build": 8.0, "c_edges": 8.0, "c_example": 7.0, "v_build": 8.0, "v_example": 8.0,
              "r_triangle": 7.0, "r_chain": 8.0, "p_pause": 10.0, "p_answer": 9.0}

if __name__ == "__main__":
    main(beats, HERE / "scene.py", HERE.parents[1] / "projects" / "daa-4.4", SECTIONS, MIN_WINDOW,
         {"title": beats.TITLE, "code": beats.CODE, "unit": beats.UNIT, "end_secs": 15.0,
          "title_suffix": "Step by Step",
          "cameo": {"size": 312, "voice": "voice-real", "real": "projects/daa-3.2/voice-real", "lines": {"04": "03"},
                    "shots": [{"beat": "hook_mascot", "kind": "line", "pos": [-5.8, -1.0]},
                              {"beat": "p_pause", "kind": "after", "pos": [-5.8, -1.0]},
                              {"kind": "end", "pos": [-5.8, 1.3]}]},
          "summary": "How to prove a problem NP-complete, with the same two-step template every time: show it is in NP "
                     "(a certificate checked in polynomial time), then reduce a known NP-complete problem to it. Three "
                     "proofs step by step: 3-SAT (SAT reduces to it by splitting and padding clauses), clique (the "
                     "literal graph built from a 3-SAT formula, worked on a 3-clause example), and vertex cover (the "
                     "complement graph, cover of size n - k). Then how clique, independent set and vertex cover are one "
                     "triangle, the chain from Cook's theorem, a practice proof (independent set) and exam tips.",
          "hashtags": "#DAA #NPComplete #3SAT #Clique #VertexCover #ComplexityTheory #Algorithms #DESPU",
          "tags": "daa, design and analysis of algorithms, np complete proof, 3 sat np complete, clique np complete, "
                  "vertex cover np complete, 3sat to clique reduction, clique to vertex cover, cook's theorem, "
                  "complexity theory, daa unit 4, etcs329"})
