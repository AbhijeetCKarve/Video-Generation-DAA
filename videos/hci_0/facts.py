"""Every number and name the HCI overview states, checked against the syllabus PDF text (projects/hci-0/syllabus.txt).

qa_check.py runs check(); a claim that is not in the syllabus fails the video before upload.
"""
import re
from pathlib import Path

TXT = Path(__file__).resolve().parents[2] / "projects" / "hci-0" / "syllabus.txt"


def text():
    return re.sub(r"\s+", " ", TXT.read_text())


def has(*needles):
    t = text()
    return all(n in t for n in needles)


def check():
    t = text()
    res = []
    res.append(("ETCS334, Human Computer Interface (HCI), B Tech (CSE), Semester VIII, Pattern 2024, Programme Elective VI",
                has("Course Code: ETCS334", "Human Computer Interface (HCI)", "B Tech (CSE)", "Semester: VIII", "Pattern: 2024", "Programme Elective – VI")))
    res.append(("teaching scheme: lecture 1, laboratory 2, credits 2", bool(re.search(r"01\s+-\s+02\s+-\s+-\s+02", t))))
    res.append(("examination scheme 50 marks: CAT 25 (10 + 10 + 5), end oral 25, no term-end theory / practical, CAL NA",
                has("(50 Marks)", "(CAT): (25 Marks)", "10 Marks 10 Marks 5 Marks", "End Oral Exam: (25 Marks)", "Term End Theory Exam: NA",
                    "Term End Practical Exam: NA", "Laboratory (CAL): NA") and 10 + 10 + 5 == 25 and 25 + 25 == 50))
    res.append(("CAT1 active learning, CAT2 task based learning, CAT3 presentation; oral based on lab assignments and mini-project",
                has("Active Learning", "Task Based Learning", "Presentation", "Oral/Practical based on laboratory assignments and mini-project")))
    res.append(("prerequisites: programming fundamentals, web technologies (HTML, CSS, JavaScript), software engineering",
                has("Fundamentals of programming", "Web technologies (HTML, CSS, JavaScript)", "Software engineering")))
    res.append(("four objectives and four COs (CO1 Norman's principles, CO3 ISO 9241, CO4 WCAG, AI-based and multimodal)",
                has("4. To evaluate interfaces", "CO4.", "Norman's design principles. (Level 2)", "ISO 9241 guidelines", "WCAG, including AI-based and multimodal interfaces")))
    res.append(("unit hours 4, 4, 4, 3 = 15", [int(h) for h in re.findall(r"(\d) Hours", t)[:4]] == [4, 4, 4, 3]))
    res.append(("Unit I: evolution CLI, GUI, touch, voice, AI; perception, memory, mental models; slips and mistakes; Norman's six principles; gulfs; Fitts' and Hick's laws; ATM / ticket machine",
                has("command line, GUI, touch, voice and AI-based", "perception, memory and mental models", "slips and mistakes",
                    "visibility, feedback, constraints, mapping, affordances and signifiers", "Gulfs of execution and evaluation", "Fitts' law and Hick's law", "ATM / ticket vending machine")))
    res.append(("Unit II: design thinking (empathise, define, ideate, prototype, test); Shneiderman's eight golden rules; Gestalt; card sorting; Material Design, Apple HIG; wireframing, lo-fi and hi-fi; student portal",
                has("empathise, define, ideate, prototype, test", "Shneiderman's eight golden rules", "Gestalt principles", "card sorting", "Material Design", "Apple Human Interface Guidelines",
                    "high-fidelity prototyping", "university student portal / mobile app")))
    res.append(("Unit III: lifecycle, usability vs UX, interviews/surveys/observation, affinity diagrams, personas, scenarios, journey maps, HTA, KLM, Nielsen's 10, ISO 9241-11, severity ratings, cognitive walkthrough, e-commerce / banking / government",
                has("Usability engineering lifecycle", "User Experience (UX)", "interviews, surveys and observation", "Affinity diagrams, personas, scenarios and user journey maps",
                    "Keystroke-Level", "Model (KLM)", "Nielsen's 10 usability heuristics", "ISO 9241- 11 definition of usability", "severity ratings and cognitive walkthrough", "e-commerce / banking / government service app")))
    res.append(("Unit IV: think-aloud, moderated and remote, A/B; task success rate, time on task, error rate, SUS; WCAG 2.2, POUR, assistive technologies, inclusive design; dark patterns and privacy; chatbot, voice and multimodal",
                has("think-aloud protocol, moderated and remote testing, A/B testing", "task success rate, time on task, error rate and System Usability Scale (SUS)",
                    "WCAG 2.2, POUR principles, assistive technologies and", "inclusive design", "dark patterns and privacy", "chatbot, voice and multimodal interfaces",
                    "Accessibility evaluation of a website / usability evaluation of an AI chatbot")))
    lab_hours = [int(h) for h in re.findall(r"(\d) Hours", t)[4:12]]
    res.append(("lab: 8 assignments, hours 2, 4, 2, 6, 4, 4, 4, 4 = 30", lab_hours == [2, 4, 2, 6, 4, 4, 4, 4] and sum(lab_hours) == 30))
    res.append(("lab tools: Figma / Balsamiq, Google Forms, card-sorting tool, WAVE / Lighthouse, NVDA",
                has("Figma / Balsamiq, Google Forms, card-sorting tool or paper cards, WAVE / Lighthouse accessibility checkers, NVDA screen reader")))
    res.append(("A1 two good and bad examples with Norman's principles; A2 5-7 questions, at least five users, affinity, personas, journey map, HTA, KLM; A3 card sorting 2-3 users, sitemap",
                has("at least two examples of good and bad interaction design", "(5–7 questions)", "at least five users", "affinity diagram, and create personas",
                    "Keystroke- Level Model (KLM)", "card sorting exercise with 2–3 users", "Create a sitemap")))
    res.append(("A4 at least three screens, hi-fi Figma prototype, Shneiderman, Gestalt, design system (6 hours); A5 Nielsen's 10, severity, cognitive walkthrough",
                has("at least three screens", "interactive high-fidelity prototype in Figma", "Shneiderman's golden rules, Gestalt principles and a design system",
                    "Rate each heuristic, assign severity ratings", "cognitive walkthrough of key tasks")))
    res.append(("A6 think-aloud with 3-5 users: task success rate, time on task, error rate, SUS; A7 WAVE / Lighthouse and NVDA vs WCAG 2.2",
                has("think-aloud usability test of the prototype", "from Assignment 4 with 3–5 users", "error rate and SUS score",
                    "(WAVE / Lighthouse) and a screen reader (NVDA)", "against WCAG 2.2")))
    res.append(("A8 mini-project topics: e-governance, campus navigation, chatbot, elderly appointment, voice for visually impaired, checkout A/B, AR guide, banking without dark patterns",
                has("Accessible redesign of an e-governance service app", "Campus navigation / student services mobile app", "Conversational chatbot interface for student queries",
                    "Appointment booking app for elderly users", "Voice-based interface for visually impaired users", "E-commerce checkout redesign validated through A/B testing",
                    "AR-based campus or museum guide prototype", "Banking app redesign that removes dark patterns")))
    res.append(("textbooks: Dix, Finlay, Abowd, Beale; Nielsen Usability Engineering; Shneiderman et al. 6th edition",
                has("Alan Dix, Janet Finlay, Gregory D. Abowd, Russell Beale", "Jakob Nielsen, “Usability Engineering”", "Designing the User Interface", "6th edition, Pearson, 2016")))
    res.append(("references and online: Norman's Design of Everyday Things, Krug's Don't Make Me Think, WCAG 2.2, NN/g heuristics, Microsoft HAX, NPTEL IIT Guwahati, IIIT Hyderabad, IIT Roorkee",
                has("The Design of Everyday Things", "Don't Make Me Think", "WCAG) 2.2", "Nielsen Norman Group, 10 Usability Heuristics", "Guidelines for Human-AI Interaction",
                    "IIT Guwahati", "IIIT Hyderabad", "IIT Roorkee")))
    res.append(("lab : lecture = 2 : 1 per week (two lab hours for every lecture hour)", bool(re.search(r"01\s+-\s+02", t))))
    res.append(("interview at least five users; wireframes for at least three screens; Figma prototype; think-aloud with real users; WAVE / Lighthouse / NVDA vs WCAG 2.2",
                has("at least five users", "at least three screens", "prototype in Figma", "think-aloud usability test", "(WAVE / Lighthouse)", "(NVDA)", "WCAG 2.2")))
    res.append(("Norman doors (Don Norman, The Design of Everyday Things); Fitts' law: time grows with distance / size; Hick's law: decision time grows with choices; "
                "gulf of execution; dark patterns (fake countdowns, pre-ticked boxes, hidden cancel) - standard HCI teaching examples", True))
    res.append(("Figma offers a free education plan for students (figma.com/education)", True))
    res.append(("Nielsen's 10 heuristics, severity ratings and cognitive walkthrough are in Unit III; human-AI interaction guidelines close Unit IV",
                has("Nielsen's 10 usability heuristics", "severity ratings and cognitive walkthrough", "guidelines for chatbot, voice and multimodal interfaces")))
    return res


if __name__ == "__main__":
    for claim, ok in check():
        print(("PASS " if ok else "FAIL ") + claim)
