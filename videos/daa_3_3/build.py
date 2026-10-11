#!/usr/bin/env python3
"""Build Video 3.3 (Sum of Subsets & Hamiltonian Cycle).

    python3 videos/daa_3_3/build.py schedule --estimate                      # timeline before the voice exists
    python3 videos/daa_3_3/build.py render --quality l                        # quick preview render
    python3 videos/daa_3_3/build.py all --variant cameo --camera <rec> --no-captions   # the real thing
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
sys.path.insert(0, str(HERE))
import beats  # noqa: E402
from production import main  # noqa: E402

# section title shown in the header + background music mood, set at the section's first line
SECTIONS = {
    "hook_weights": (None, "bright"),
    "syllabus": ("Today's plan", "calm"),
    "s_def": ("Sum of subsets", "calm"),
    "t_root": ("Sum of subsets · State space tree", "pulse"),
    "s_algo": ("Sum of subsets · Algorithm", "quiet"),
    "h_intro": ("Hamiltonian cycle", "calm"),
    "h_trace1": ("Hamiltonian cycle · Step by step", "pulse"),
    "h_algo": ("Hamiltonian cycle · Algorithm", "quiet"),
    "cmp": ("The common pattern", "calm"),
    "p_intro": ("Practice", "pulse"),
    "tip1": ("Exam tips", "pulse"),
    "recap": ("Recap", "bright"),
}
# lines whose animation needs more time than the narration takes
MIN_WINDOW = {"hook_weights": 6.0, "hook_answer": 9.0, "hook_mascot": 6.0, "t_root": 5.0, "t_right": 9.0,
              "t_count": 5.0, "h_trace1": 6.0, "h_back": 6.0, "h_found": 5.0, "p_pause": 10.0, "p_answer": 11.0}

if __name__ == "__main__":
    main(beats, HERE / "scene.py", HERE.parents[1] / "projects" / "daa-3.3", SECTIONS, MIN_WINDOW,
         {"title": beats.TITLE, "code": beats.CODE, "unit": beats.UNIT, "end_secs": 15.0,
          # you on camera in three short shots; the welcome line is the on-camera take from the 3.2 recording
          "cameo": {"size": 312, "voice": "voice-real", "real": "projects/daa-3.2/voice-real", "lines": {"03": "03"},
                    "shots": [{"beat": "hook_mascot", "kind": "line", "pos": [-5.8, -1.0]},
                              {"beat": "p_pause", "kind": "after", "pos": [-5.8, -1.0]},
                              {"kind": "end", "pos": [-5.8, 1.3]}]},
          "summary": "Two more classic backtracking problems. Sum of subsets: which weights add up to exactly "
                     "the target? We build the state space tree with s, k and r at every node and the two bounding "
                     "checks (weights 7, 11, 13, 24, target 31). Hamiltonian cycle: visit every city once and come "
                     "back, with the three checks of NextValue, a dead end and the cycle found. Algorithms "
                     "(SumOfSub, NextValue, Hamiltonian), time complexity, a practice question and exam tips.",
          "hashtags": "#DAA #Backtracking #SumOfSubsets #HamiltonianCycle #Algorithms #DESPU",
          "tags": "daa, design and analysis of algorithms, backtracking, sum of subsets, subset sum, hamiltonian cycle, "
                  "state space tree, bounding function, nextvalue, daa unit 3, etcs329"})
