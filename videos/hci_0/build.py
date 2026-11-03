#!/usr/bin/env python3
"""Build the HCI course overview (ETCS334 syllabus, about 13 minutes).

    python3 videos/hci_0/build.py schedule --estimate
    python3 videos/hci_0/build.py all --variant cameo --no-captions
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
sys.path.insert(0, str(HERE))
import beats  # noqa: E402
from production import main  # noqa: E402

SECTIONS = {
    "hook_apps": (None, "bright"),
    "syllabus": ("Today's plan", "calm"),
    "g_card": ("The course at a glance", "calm"),
    "o_obj": ("Objectives and outcomes", "calm"),
    "u1_intro": ("Unit I · Foundations of HCI", "pulse"),
    "u2_intro": ("Unit II · Interaction design", "pulse"),
    "u3_intro": ("Unit III · Usability engineering", "pulse"),
    "u4_intro": ("Unit IV · Testing, accessibility, AI", "pulse"),
    "l_tools": ("Laboratory", "calm"),
    "a_cat": ("Assessment", "calm"),
    "b_text": ("Books", "calm"),
    "tip1": ("How to score", "pulse"),
    "recap": ("Recap", "bright"),
}
MIN_WINDOW = {"hook_apps": 7.0, "hook_mascot": 6.0, "hook_promise": 7.0, "g_card": 7.0, "g_scheme": 7.0, "g_marks": 7.0, "o_obj": 9.0,
              "o_co": 9.0, "l_tools": 7.0, "l_a123": 9.0, "l_mini": 10.0, "l_flow": 7.0, "a_cat": 7.0, "b_ref": 8.0}

if __name__ == "__main__":
    main(beats, HERE / "scene.py", HERE.parents[1] / "projects" / "hci-0", SECTIONS, MIN_WINDOW,
         {"title": beats.TITLE, "code": beats.CODE, "unit": beats.UNIT, "end_secs": 15.0,
          "badge": "HCI  ·  ETCS334  ·  COURSE OVERVIEW", "series": "HCI SERIES",
          "yt_title": "Human Computer Interface (ETCS334) Syllabus Explained | Theory, Labs and Marks in 13 Minutes",
          "course_line": "Course: Human Computer Interface (ETCS334), B.Tech CSE Semester VIII, DES Pune University",
          "cameo": {"size": 312, "voice": "voice-real", "real": "projects/daa-3.2/voice-real", "lines": {}, "shots": []},
          "summary": "The complete ETCS334 Human Computer Interface syllabus for B.Tech CSE (Semester VIII) in one video: "
                     "the course at a glance (1 lecture + 2 lab hours a week, 2 credits, 50 marks with no written end exam), "
                     "the four theory units from human factors and Norman's principles to usability testing, WCAG 2.2 and "
                     "human-AI interaction, the eight laboratory assignments with Figma, card sorting, heuristic evaluation, "
                     "usability testing and accessibility audits, the mini project, the assessment scheme, the books, and "
                     "three tips on how to score.",
          "hashtags": "#HCI #HumanComputerInteraction #UX #Usability #Syllabus #DESPU",
          "tags": "hci, human computer interface, human computer interaction, hci syllabus, etcs334, ux design course, usability engineering, "
                  "norman design principles, nielsen heuristics, wcag, figma prototyping, des pune university, btech cse"})
