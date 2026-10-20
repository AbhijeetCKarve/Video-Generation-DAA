#!/usr/bin/env python3
"""Build Video 4.1 (Polynomial vs Non-Polynomial & Non-Deterministic Algorithms).

    python3 videos/daa_4_1/build.py schedule --estimate                      # timeline before the voice exists
    python3 videos/daa_4_1/build.py render --quality l                        # quick preview render
    python3 videos/daa_4_1/build.py all --variant cameo --camera <rec> --no-captions   # the real thing
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
    "hook_fast": (None, "bright"),
    "syllabus": ("Today's plan", "calm"),
    "g_poly": ("Growth rates", "calm"),
    "t_def": ("Tractable vs intractable", "calm"),
    "d_det": ("Deterministic vs non-deterministic", "pulse"),
    "n_search": ("Non-deterministic algorithms", "pulse"),
    "n_class": ("The class NP", "calm"),
    "p_intro": ("Practice", "pulse"),
    "tip1": ("Exam tips", "pulse"),
    "recap": ("Recap", "bright"),
}
# lines whose animation needs more time than the narration takes
MIN_WINDOW = {"hook_fast": 6.0, "hook_mascot": 6.0, "g_table": 9.0, "g_point": 7.0, "t_examples": 8.0, "n_idea": 8.0,
              "n_funcs": 7.0, "n_search": 8.0, "n_sort": 12.0, "n_knap": 9.0, "p_pause": 10.0, "p_answer": 9.0}

if __name__ == "__main__":
    main(beats, HERE / "scene.py", HERE.parents[1] / "projects" / "daa-4.1", SECTIONS, MIN_WINDOW,
         {"title": beats.TITLE, "code": beats.CODE, "unit": beats.UNIT, "end_secs": 15.0,
          "title_suffix": "Growth Rates, Tractability & NP",
          # you on camera in three short shots; the welcome line is the on-camera take from the 3.2 recording
          "cameo": {"size": 312, "voice": "voice-real", "real": "projects/daa-3.2/voice-real", "lines": {"04": "03"},
                    "shots": [{"beat": "hook_mascot", "kind": "line", "pos": [-5.8, -1.0]},
                              {"beat": "p_pause", "kind": "after", "pos": [-5.8, -1.0]},
                              {"kind": "end", "pos": [-5.8, 1.3]}]},
          "summary": "The first video of Unit IV, complexity theory. Polynomial versus exponential growth with the "
                     "classic time table (n cubed against 2 to the n at a billion steps a second), tractable versus "
                     "intractable problems, and why the hard problems of Unit III have no known polynomial algorithm. "
                     "Then deterministic versus non-deterministic algorithms: Choice, Failure and Success, "
                     "non-deterministic search in O(1), sorting in O(n), the decision knapsack in O(n), and the "
                     "guess-and-verify idea behind the class NP. Practice question (Hamiltonian cycle) and exam tips.",
          "hashtags": "#DAA #ComplexityTheory #PvsNP #NonDeterministic #Algorithms #DESPU",
          "tags": "daa, design and analysis of algorithms, polynomial time, exponential time, tractable intractable, "
                  "deterministic vs non deterministic algorithms, nondeterministic algorithm, class np, p vs np, "
                  "complexity theory, daa unit 4, etcs329"})
