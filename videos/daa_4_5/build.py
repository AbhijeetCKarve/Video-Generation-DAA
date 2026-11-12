#!/usr/bin/env python3
"""Build Video 4.5 (Approximation Algorithms & Applications).

    python3 videos/daa_4_5/build.py schedule --estimate
    python3 videos/daa_4_5/build.py all --variant cameo --no-captions
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
sys.path.insert(0, str(HERE))
import beats  # noqa: E402
from production import main  # noqa: E402

SECTIONS = {
    "hook_vans": (None, "bright"),
    "syllabus": ("Today's plan", "calm"),
    "r_def": ("Approximation ratio", "calm"),
    "v_problem": ("Vertex cover · 2-approximation", "pulse"),
    "t_metric": ("Metric TSP · 2-approximation", "pulse"),
    "a_ai": ("Applications", "calm"),
    "p_intro": ("Practice", "pulse"),
    "tip1": ("Exam tips", "pulse"),
    "recap": ("Recap", "bright"),
}
MIN_WINDOW = {"hook_vans": 7.0, "hook_idea": 8.0, "hook_mascot": 6.0, "r_def": 8.0, "v_algo": 7.0, "v_trace": 12.0, "v_proof": 8.0,
              "v_tight": 8.0, "t_algo": 7.0, "t_trace": 9.0, "t_proof": 8.0, "a_big": 8.0, "p_pause": 10.0, "p_answer": 9.0}

if __name__ == "__main__":
    main(beats, HERE / "scene.py", HERE.parents[1] / "projects" / "daa-4.5", SECTIONS, MIN_WINDOW,
         {"title": beats.TITLE, "code": beats.CODE, "unit": beats.UNIT, "end_secs": 15.0,
          "title_suffix": "Vertex Cover, TSP & Real Uses",
          "cameo": {"size": 312, "voice": "voice-real", "real": "projects/daa-3.2/voice-real", "lines": {}, "shots": []},
          "summary": "The last video of Unit IV. What an approximation algorithm and its ratio are, and why a guaranteed "
                     "2x answer in polynomial time beats an exact answer that never arrives. Two classic algorithms with "
                     "exam-ready proofs: the matching-based 2-approximation for vertex cover (traced on a 7-vertex graph, "
                     "with the tight example) and the MST-based 2-approximation for metric TSP (five cities, the triangle "
                     "inequality, Christofides). Then where NP-hardness lives in practice: heuristics in AI and SAT solvers, "
                     "sketches and greedy scheduling in big data, and the hard problems that cryptography relies on. "
                     "Practice question and exam tips.",
          "hashtags": "#DAA #ApproximationAlgorithms #VertexCover #TSP #NPHard #Algorithms #DESPU",
          "tags": "daa, design and analysis of algorithms, approximation algorithms, approximation ratio, vertex cover approximation, "
                  "tsp approximation mst, christofides, np hard applications, ptas, big data algorithms, cryptography hardness, "
                  "daa unit 4, etcs329"})
