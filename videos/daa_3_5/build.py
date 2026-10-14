#!/usr/bin/env python3
"""Build Video 3.5 (0/1 Knapsack & TSP with Branch & Bound).

    python3 videos/daa_3_5/build.py schedule --estimate                      # timeline before the voice exists
    python3 videos/daa_3_5/build.py render --quality l                        # quick preview render
    python3 videos/daa_3_5/build.py all --variant cameo --camera <rec> --no-captions   # the real thing
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
    "hook_bag": (None, "bright"),
    "syllabus": ("Today's plan", "calm"),
    "k_problem": ("0/1 Knapsack", "calm"),
    "k_x1": ("0/1 Knapsack \u00b7 LC search", "pulse"),
    "t_problem": ("TSP \u00b7 Reduced cost matrix", "calm"),
    "t_level1": ("TSP \u00b7 LC search", "pulse"),
    "cmp": ("The common recipe", "calm"),
    "p_intro": ("Practice", "pulse"),
    "tip1": ("Exam tips", "pulse"),
    "recap": ("Recap", "bright"),
}
# lines whose animation needs more time than the narration takes
MIN_WINDOW = {"hook_bag": 6.0, "hook_mascot": 6.0, "k_root": 8.0, "k_x1": 7.0, "k_kill": 5.5, "t_rows": 8.0,
              "t_cols": 6.0, "t_child": 6.0, "t_level1": 6.0, "t_lc": 6.0, "t_path": 7.0, "p_pause": 10.0,
              "p_answer": 7.0}

if __name__ == "__main__":
    main(beats, HERE / "scene.py", HERE.parents[1] / "projects" / "daa-3.5", SECTIONS, MIN_WINDOW,
         {"title": beats.TITLE, "code": beats.CODE, "unit": beats.UNIT, "end_secs": 15.0, "title_suffix": "LC Search Step by Step",
          # you on camera in three short shots; the welcome line is the on-camera take from the 3.2 recording
          "cameo": {"size": 312, "voice": "voice-real", "real": "projects/daa-3.2/voice-real", "lines": {"04": "03"},
                    "shots": [{"beat": "hook_mascot", "kind": "line", "pos": [-5.8, -1.0]},
                              {"beat": "p_pause", "kind": "after", "pos": [-5.8, -1.0]},
                              {"kind": "end", "pos": [-5.8, 1.3]}]},
          "summary": "The last video on branch and bound. The 0/1 knapsack with LC search: order by profit per "
                     "weight, the fractional (optimistic) bound and the whole-item (guaranteed) bound at every node, "
                     "and the full trace to x = (1,1,0,1), profit 38. The travelling salesperson problem with the "
                     "reduced cost matrix: row and column reduction, the c-hat of every child, and the LC search to "
                     "the optimal tour 1-4-2-5-3-1 of cost 28. Practice question and exam tips.",
          "hashtags": "#DAA #BranchAndBound #Knapsack #TSP #Algorithms #DESPU",
          "tags": "daa, design and analysis of algorithms, branch and bound, 0/1 knapsack, lc branch and bound, "
                  "travelling salesman problem, tsp branch and bound, reduced cost matrix, daa unit 3, etcs329"})
