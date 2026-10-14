#!/usr/bin/env python3
"""Build Video 3.4 (Branch & Bound: FIFO, LIFO & LC Search).

    python3 videos/daa_3_4/build.py schedule --estimate                      # timeline before the voice exists
    python3 videos/daa_3_4/build.py render --quality l                        # quick preview render
    python3 videos/daa_3_4/build.py all --variant cameo --camera <rec> --no-captions   # the real thing
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
    "hook_doors": (None, "bright"),
    "syllabus": ("Today's plan", "calm"),
    "b_recap": ("Branch & bound vs backtracking", "calm"),
    "s_fifo": ("FIFO, LIFO and LC", "calm"),
    "t_intro": ("One tree, three searches", "pulse"),
    "c_formula": ("The cost function", "quiet"),
    "u_intro": ("Bounding", "pulse"),
    "a_code": ("Control abstraction", "quiet"),
    "p_intro": ("Practice", "pulse"),
    "tip1": ("Exam tips", "pulse"),
    "recap": ("Recap", "bright"),
}
# lines whose animation needs more time than the narration takes
MIN_WINDOW = {"hook_doors": 6.0, "hook_ways": 7.5, "hook_mascot": 6.0, "b_bt": 5.0, "b_bb": 6.0,
              "t_fifo1": 6.5, "t_lifo1": 6.5, "t_lc1": 6.5, "t_fifo2": 5.0, "t_lifo2": 5.0, "t_lc2": 5.0,
              "u_trace1": 6.5, "u_kill": 7.0, "u_upper": 6.0, "p_pause": 10.0, "p_answer": 9.0}

if __name__ == "__main__":
    main(beats, HERE / "scene.py", HERE.parents[1] / "projects" / "daa-3.4", SECTIONS, MIN_WINDOW,
         {"title": beats.TITLE, "code": beats.CODE, "unit": beats.UNIT, "end_secs": 15.0, "title_suffix": "Explained with One Example",
          # you on camera in three short shots; the welcome line is the on-camera take from the 3.2 recording
          "cameo": {"size": 312, "voice": "voice-real", "real": "projects/daa-3.2/voice-real", "lines": {"04": "03"},
                    "shots": [{"beat": "hook_mascot", "kind": "line", "pos": [-5.8, -1.0]},
                              {"beat": "p_pause", "kind": "after", "pos": [-5.8, -1.0]},
                              {"kind": "end", "pos": [-5.8, 1.3]}]},
          "summary": "Branch and bound, step by step: how it differs from backtracking (the E-node stays until it is "
                     "dead), the three ways to pick the next live node (FIFO queue, LIFO stack, least cost search), "
                     "one state space tree searched all three ways, the cost function c-hat(x) = f(h(x)) + g-hat(x), "
                     "upper and lower bounds that kill nodes, the LC search control abstraction, a practice question "
                     "and exam tips.",
          "hashtags": "#DAA #BranchAndBound #LCSearch #Algorithms #DESPU",
          "tags": "daa, design and analysis of algorithms, branch and bound, fifo branch and bound, lifo branch and bound, "
                  "lc search, least cost search, live node, e-node, bounding function, daa unit 3, etcs329"})
