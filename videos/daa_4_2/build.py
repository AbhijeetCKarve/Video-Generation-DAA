#!/usr/bin/env python3
"""Build Video 4.2 (P, NP, NP-Hard & NP-Complete).

    python3 videos/daa_4_2/build.py schedule --estimate                      # timeline before the voice exists
    python3 videos/daa_4_2/build.py all --variant cameo --camera <rec> --no-captions   # the real thing
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
sys.path.insert(0, str(HERE))
import beats  # noqa: E402
from production import main  # noqa: E402

SECTIONS = {
    "hook_q": (None, "bright"),
    "syllabus": ("Today's plan", "calm"),
    "d_opt": ("Decision vs optimisation", "calm"),
    "p_def": ("P and NP", "calm"),
    "sat": ("SAT and reductions", "pulse"),
    "nph_def": ("NP-hard and NP-complete", "pulse"),
    "venn": ("The picture", "calm"),
    "p_intro": ("Practice", "pulse"),
    "tip1": ("Exam tips", "pulse"),
    "recap": ("Recap", "bright"),
}
MIN_WINDOW = {"hook_q": 7.0, "hook_mascot": 6.0, "d_dec": 7.0, "np_ex": 7.0, "sat_ex": 9.0, "reduce": 8.0, "examples": 7.0,
              "venn": 9.0, "collapse": 7.0, "p_pause": 10.0, "p_answer": 9.0}

if __name__ == "__main__":
    main(beats, HERE / "scene.py", HERE.parents[1] / "projects" / "daa-4.2", SECTIONS, MIN_WINDOW,
         {"title": beats.TITLE, "code": beats.CODE, "unit": beats.UNIT, "end_secs": 15.0,
          "title_suffix": "The P vs NP Question",
          "cameo": {"size": 312, "voice": "voice-real", "real": "projects/daa-3.2/voice-real", "lines": {"04": "03"},
                    "shots": [{"beat": "hook_mascot", "kind": "line", "pos": [-5.8, -1.0]},
                              {"beat": "p_pause", "kind": "after", "pos": [-5.8, -1.0]},
                              {"kind": "end", "pos": [-5.8, 1.3]}]},
          "summary": "The four classes every DAA exam asks about. Decision versus optimisation problems and why "
                     "complexity theory uses decision problems only. P (deterministic polynomial time) and NP "
                     "(non-deterministic polynomial time: guess and verify), why P is inside NP, and the open P vs NP "
                     "question. Satisfiability and the idea of a polynomial-time reduction, then NP-hard (SAT reduces "
                     "to it) and NP-complete (NP-hard and in NP), Cook's theorem, the standard examples, and the "
                     "diagram to draw in the exam, including what happens if P = NP. Practice question and exam tips.",
          "hashtags": "#DAA #PvsNP #NPComplete #NPHard #ComplexityTheory #Algorithms #DESPU",
          "tags": "daa, design and analysis of algorithms, p vs np, class p, class np, np hard, np complete, "
                  "cook's theorem, satisfiability, polynomial time reduction, decision problem, complexity theory, "
                  "daa unit 4, etcs329"})
