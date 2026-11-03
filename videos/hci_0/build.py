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
    "hook_angry": (None, "bright"),
    "syllabus": ("Today's plan", "calm"),
    "w_meet": ("What HCI is", "calm"),
    "i_door": ("Five ideas you can use tomorrow", "pulse"),
    "p_intro": ("Your turn", "pulse"),
    "b_lab": ("What you will build", "calm"),
    "t_units12": ("The theory", "calm"),
    "m_scheme": ("Marks", "calm"),
    "r_career": ("Why pick this elective", "pulse"),
    "tip1": ("Three tips", "pulse"),
    "recap": ("Recap", "bright"),
}
MIN_WINDOW = {"hook_angry": 8.0, "hook_mascot": 6.0, "hook_promise": 7.0, "w_meet": 7.0, "w_three": 7.0, "i_door": 8.0, "i_chat": 8.0,
              "i_fitts": 8.0, "i_hick": 8.0, "i_gulf": 8.0, "i_dark": 8.0, "p_pause": 10.0, "p_answer": 7.0, "b_lab": 7.0, "b_mini": 8.0,
              "t_units12": 7.0, "m_scheme": 8.0, "m_fair": 7.0}

if __name__ == "__main__":
    main(beats, HERE / "scene.py", HERE.parents[1] / "projects" / "hci-0", SECTIONS, MIN_WINDOW,
         {"title": beats.TITLE, "code": beats.CODE, "unit": beats.UNIT, "end_secs": 15.0,
          "badge": "HCI  ·  ETCS334  ·  INTRO SESSION", "series": "HCI SERIES",
          "yt_title": "Why Take HCI? Human Computer Interface (ETCS334) Introductory Session | What You Build, Marks, Why Enrol",
          "course_line": "Course: Human Computer Interface (ETCS334), B.Tech CSE Semester VIII, DES Pune University",
          "cameo": {"size": 312, "voice": "voice-real", "real": "projects/daa-3.2/voice-real", "lines": {}, "shots": []},
          "summary": "The introductory session for ETCS334 Human Computer Interface (B.Tech CSE, Semester VIII, Programme "
                     "Elective VI). What HCI is, through things you use every day: Norman doors, the signifiers in a chat app, "
                     "Fitts' law and the thumb zone, Hick's law and the 50-button remote, the gulf of execution on a microwave, "
                     "and dark patterns. Then what you will build in the laboratory (user research, personas, card sorting, "
                     "wireframes and a Figma prototype, a usability test with real metrics, an accessibility audit with WAVE, "
                     "Lighthouse and NVDA, and a mini project), the four units in brief, how the 50 marks work with no written "
                     "end exam, four reasons to enrol, and three tips to start tonight.",
          "hashtags": "#HCI #HumanComputerInteraction #UX #Usability #Syllabus #DESPU",
          "tags": "hci, human computer interface, human computer interaction, hci syllabus, etcs334, ux design course, usability engineering, "
                  "norman design principles, nielsen heuristics, wcag, figma prototyping, des pune university, btech cse"})
