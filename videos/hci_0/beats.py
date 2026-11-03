"""HCI course overview - ETCS334 Human Computer Interface syllabus for B.Tech CSE (Semester VIII), about 13 minutes.

Each beat = one narration line. The key ties it to its animation in scene.py,
the mood steers delivery and background music, "|" marks caption breaks.
Every number comes from the syllabus PDF (projects/hci-0/syllabus.txt); facts.py checks them against that text.
"""

TITLE = "Human Computer Interface (ETCS334): The Complete Syllabus Explained"
CODE = "ETCS334"
UNIT = "HCI"

BEATS = [
    # ---- hook
    ("hook_apps", "curious", "Why does one app feel effortless, and another makes you want to throw your phone across the room? | Same hardware, same user. The difference is the interface."),
    ("hook_hci", "excited", "Human Computer Interface, HCI, is the subject of designing that difference. | This semester you will design, prototype and test real interfaces, and find out why users do what they do."),
    ("hook_promise", "explain", "This video walks through the whole syllabus in thirteen minutes: | the four theory units, the eight lab assignments and the mini project, how you are assessed, and how to score well."),
    ("hook_mascot", "warm", "Welcome to the HCI series. | I'm Abhijeet Karve, and I'll guide you through this course, step by step."),
    ("syllabus", "explain", "This is the course overview for ETCS334, Human Computer Interface. | Today: the course at a glance, the four units, the laboratory and mini project, the assessment, and the books."),
    ("exam", "explain", "This course has no written end exam, and that changes how you should study it. | So stay till the end for the tips on scoring."),
    # ---- the course at a glance
    ("g_card", "explain", "The course at a glance. ETCS334, Human Computer Interface, in semester eight of B Tech Computer Science, pattern twenty twenty four. | It is a programme elective, elective number six."),
    ("g_scheme", "explain", "The teaching scheme: one lecture hour and two laboratory hours every week, for two credits. | So two thirds of your time in this course is in the lab, doing."),
    ("g_marks", "emphatic", "Assessment is out of fifty marks. Twenty five come from continuous assessment for theory, | and twenty five from an end oral exam based on your laboratory assignments and mini project. No term end written paper, no term end practical."),
    ("g_prereq", "explain", "Prerequisites: fundamentals of programming, web technologies, HTML, CSS and JavaScript, | and software engineering. You already have all three."),
    # ---- objectives and outcomes
    ("o_obj", "explain", "Four course objectives: understand the fundamentals and human factors of HCI, | learn interaction design, UI patterns and prototyping, apply usability engineering and user research, and evaluate interfaces with usability testing, metrics and accessibility standards, including AI based interfaces."),
    ("o_co", "explain", "They map to four course outcomes. CO one: explain HCI concepts, human factors and Norman's principles. CO two: apply design principles and prototyping. | CO three: analyse user needs and evaluate with heuristics and ISO nine two four one. CO four: evaluate usability and accessibility with testing, metrics and WCAG, including AI and multimodal interfaces."),
    # ---- unit I
    ("u1_intro", "explain", "Unit one, four hours: foundations of HCI and human factors. | What HCI is, and how interaction evolved: command line, graphical interfaces, touch, voice, and now AI based interfaces."),
    ("u1_human", "explain", "Then the human as an information processor: perception, memory and mental models, | and human error: slips, where you know what to do but your hand does something else, and mistakes, where the plan itself is wrong."),
    ("u1_norman", "emphatic", "Norman's six design principles: visibility, feedback, constraints, mapping, affordances and signifiers. | The gulfs of execution and evaluation, Fitts' law for pointing, and Hick's law for choosing."),
    ("u1_case", "warm", "The case study: good and bad interaction design in everyday products and public kiosks, | like an ATM or a ticket vending machine. You will never look at one the same way again."),
    # ---- unit II
    ("u2_intro", "explain", "Unit two, four hours: interaction design and prototyping. | User centred design and design thinking in five steps: empathise, define, ideate, prototype, test."),
    ("u2_rules", "explain", "Shneiderman's eight golden rules and UI design patterns. Visual design: layout, Gestalt principles, colour and typography. | Information architecture: navigation design and card sorting."),
    ("u2_proto", "explain", "Design systems and platform guidelines, Material Design and Apple's Human Interface Guidelines, | then wireframing, and low fidelity and high fidelity prototyping."),
    ("u2_case", "warm", "The case study: wireframing and a low fidelity prototype of a university student portal or mobile app. | This is where Figma enters your life."),
    # ---- unit III
    ("u3_intro", "explain", "Unit three, four hours: usability engineering and user research. | The usability engineering lifecycle, and the difference between usability and user experience."),
    ("u3_research", "explain", "User research methods: interviews, surveys and observation. Then making sense of the data: | affinity diagrams, personas, scenarios and user journey maps."),
    ("u3_models", "explain", "Hierarchical task analysis, and the Keystroke Level Model, which predicts how long an expert takes for a task. | Nielsen's ten usability heuristics, and the ISO nine two four one dash eleven definition of usability."),
    ("u3_case", "warm", "Heuristic evaluation with severity ratings, and the cognitive walkthrough. | The case study: a heuristic evaluation of a real app, e-commerce, banking or a government service."),
    # ---- unit IV
    ("u4_intro", "explain", "Unit four, three hours: usability testing, accessibility and emerging interfaces. | Usability testing: the think aloud protocol, moderated and remote testing, and A B testing."),
    ("u4_metrics", "explain", "Usability metrics: task success rate, time on task, error rate, and the System Usability Scale, SUS. | Accessibility: WCAG two point two, the POUR principles, assistive technologies and inclusive design."),
    ("u4_ethics", "emphatic", "Ethics in HCI: dark patterns and privacy. | And human AI interaction: guidelines for chatbot, voice and multimodal interfaces, the newest part of the subject."),
    ("u4_case", "warm", "The case study: an accessibility evaluation of a website, or a usability evaluation of an AI chatbot. | That is the theory: fifteen hours across four units."),
    # ---- laboratory
    ("l_tools", "explain", "Now the laboratory, where most of your marks are made. Thirty hours, eight assignments, and real tools: | Figma or Balsamiq, Google Forms, a card sorting tool, the WAVE and Lighthouse accessibility checkers, and the NVDA screen reader."),
    ("l_a123", "explain", "Assignment one: analyse two good and two bad designs with Norman's principles. Assignment two: a survey or interview with at least five users, then personas, a journey map, task analysis and a KLM estimate. | Assignment three: card sorting with two or three users, a sitemap, and a navigation review."),
    ("l_a45", "explain", "Assignment four, the biggest at six hours: low fidelity wireframes for at least three screens, turned into an interactive high fidelity Figma prototype. | Assignment five: a heuristic evaluation against Nielsen's ten heuristics, with severity ratings and a cognitive walkthrough."),
    ("l_a67", "explain", "Assignment six: a think aloud usability test of your own prototype with three to five users, recording task success, time on task, error rate and the SUS score. | Assignment seven: an accessibility audit of a public website with WAVE, Lighthouse and NVDA, compared against WCAG two point two."),
    ("l_mini", "excited", "Assignment eight is the mini project: design, prototype and evaluate an interface through the complete user centred design process. | Suggested topics include an accessible e-governance app, a campus navigation app, a chatbot for student queries, an appointment app for elderly users, a voice interface for visually impaired users, a checkout redesign validated by A B testing, an AR campus guide, and a banking app without dark patterns."),
    ("l_flow", "warm", "Notice the flow: the assignments are the stages of one design process, | research, structure, prototype, evaluate, test, audit, and the mini project puts them together."),
    # ---- assessment
    ("a_cat", "explain", "Assessment in detail. Continuous assessment for theory is twenty five marks: | CAT one, active learning, ten marks; CAT two, task based learning, ten marks; CAT three, a presentation, five marks."),
    ("a_oral", "emphatic", "The end oral exam is twenty five marks, and it is based on your laboratory assignments and the mini project. | So your lab work is not a side activity. It is half the course."),
    # ---- books
    ("b_text", "explain", "The textbooks: Dix, Finlay, Abowd and Beale, Human Computer Interaction; Jakob Nielsen, Usability Engineering; | and Shneiderman and colleagues, Designing the User Interface, sixth edition."),
    ("b_ref", "explain", "For reading you will enjoy: Don Norman's The Design of Everyday Things, and Steve Krug's Don't Make Me Think. | Online: the WCAG two point two guidelines, Nielsen Norman Group's ten heuristics, Microsoft's guidelines for human AI interaction, and NPTEL courses from IIT Guwahati, IIIT Hyderabad and IIT Roorkee."),
    # ---- tips, recap, close
    ("tip1", "emphatic", "Tip one. | Keep a design portfolio from week one: every survey, affinity diagram, persona, wireframe and Figma link. The oral exam is a conversation about that portfolio."),
    ("tip2", "emphatic", "Tip two. | Start the mini project early, and reuse your assignments as its stages: the research from assignment two, the prototype from four, the evaluation from five, the test from six."),
    ("tip3", "emphatic", "Tip three. | Learn the vocabulary by heart: Norman's six principles, Shneiderman's eight rules, Nielsen's ten heuristics, the four POUR principles, SUS and WCAG. They come up in every presentation and every oral."),
    ("recap", "warm", "To recap: | two credits, one lecture and two lab hours a week; | four units from human factors to AI interfaces; | eight lab assignments and a mini project; | and fifty marks: twenty five continuous, twenty five oral."),
    ("next", "warm", "That is the whole course on one page. | See you in the first lecture: Unit One, foundations of HCI."),
]


def script_text():
    """Narration script in the format the voice tools read: '01  {mood} text'."""
    return "".join(f"{i + 1:02d}  {{{mood}}} {text}\n" for i, (_, mood, text) in enumerate(BEATS))


if __name__ == "__main__":
    import sys
    from pathlib import Path
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("script.txt")
    out.write_text(script_text())
    words = sum(len(t.replace("|", " ").split()) for _, _, t in BEATS)
    print(f"Wrote {out}: {len(BEATS)} beats, {words} words (~{words / 140:.1f} min at 140 wpm)")
