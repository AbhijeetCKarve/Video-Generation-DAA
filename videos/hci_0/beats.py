"""HCI introductory session (ETCS334) - a 13-minute first class that makes students want the elective.

Each beat = one narration line. The key ties it to its animation in scene.py,
the mood steers delivery and background music, "|" marks caption breaks.
Course numbers come from the syllabus PDF (projects/hci-0/syllabus.txt); facts.py checks them against that text.
"""

TITLE = "Human Computer Interface (ETCS334): Why You Should Take This Elective"
CODE = "ETCS334"
UNIT = "HCI"

BEATS = [
    # ---- hook: pain they have felt
    ("hook_angry", "curious", "Think of the last time an app made you angry. You tapped the wrong button. A form threw away everything you typed. A ticket machine ate your money. | The hardware was fine. The design failed you."),
    ("hook_subject", "excited", "There is a whole subject about this: why some things are a joy to use and others are torture, and how to design the joyful kind. | It is called Human Computer Interface, and it is the elective I am asking you to pick this semester."),
    ("hook_promise", "explain", "In the next thirteen minutes I will show you what HCI is, through things you use every day, | what you will build in this course, how you will be marked, and why I think it is the most useful elective you can choose."),
    ("hook_mascot", "warm", "Welcome to the HCI series. | I'm Abhijeet Karve, and I'll guide you through this course, step by step."),
    ("syllabus", "explain", "This is the introductory session for ETCS334, Human Computer Interface. | Today: what HCI is, five ideas you can use tomorrow, what you will build, how marks work, and why to enrol."),
    ("exam", "explain", "Stay till the end: | I will give you a one minute test you can run on any app tonight."),
    # ---- what HCI is
    ("w_meet", "explain", "HCI studies the meeting point of a human and a machine: the screen, the buttons, the voice assistant, the touch gestures. | It asks one question: does this design fit the way humans actually think and behave?"),
    ("w_three", "explain", "It sits between three fields: computer science, which builds the system; | psychology, which explains the user; and design, which shapes what the user sees. In this course you touch all three."),
    ("w_blame", "emphatic", "Here is the surprising part. When a user makes a mistake, HCI does not blame the user. | It blames the design. That one shift in thinking is the heart of the subject."),
    # ---- five ideas from everyday life
    ("i_door", "explain", "Idea one: affordances and signifiers. A door with a flat metal plate says push. A door with a handle says pull. | When a door has a handle but needs a push, people walk into it. Don Norman named these Norman doors, and your apps are full of them."),
    ("i_chat", "explain", "Look at a chat app. The paper plane signifies send, the microphone signifies record, and the blue ticks give feedback: delivered, read. | Visibility, feedback, signifiers: three of Norman's six principles, in one screen."),
    ("i_fitts", "explain", "Idea two: Fitts' law. The time to reach a target depends on how far it is and how big it is. | That is why the buttons you use most sit at the bottom of the phone, under your thumb, and why the close button on an ad is tiny on purpose."),
    ("i_hick", "explain", "Idea three: Hick's law. The more choices you show, the longer a person takes to decide. | Compare a television remote with fifty buttons to a streaming remote with six. Same job, very different feeling. Fewer visible choices, faster users."),
    ("i_gulf", "explain", "Idea four: the gulf of execution. You know what you want, and you cannot work out how to make the machine do it. | A microwave with twelve buttons, when all you want is two minutes on high. Good design closes that gulf."),
    ("i_dark", "emphatic", "Idea five: dark patterns. A countdown timer that resets when you reload. A pre-ticked insurance box on a ticket booking. A cancel button hidden in grey. | These are designs built to trick you, and in this course you will learn to spot them, and to refuse to build them."),
    # ---- practice
    ("p_intro", "curious", "Your turn. Think of one app that annoys you, and name the exact moment it goes wrong. | Is it a missing signifier, a button too small, too many choices, or a gulf you cannot cross?"),
    ("p_pause", "warm", "Pause the video and think of one. | I'll wait!"),
    ("p_answer", "excited", "If you could name it, you have just done your first heuristic evaluation. | This course turns that instinct into a method: Nielsen's ten heuristics, severity ratings, and a cognitive walkthrough."),
    # ---- what you will build
    ("b_lab", "explain", "Now, what you will actually do, because this course has two laboratory hours for every lecture hour. | You will not sit and memorise. You will design."),
    ("b_research", "explain", "First you study real users: interview five people about an app, turn what they say into personas and a journey map, | and predict how long an expert takes on a task with the keystroke level model."),
    ("b_proto", "explain", "Then you structure the information with card sorting, draw wireframes for at least three screens, | and turn them into a clickable prototype in Figma, following Shneiderman's golden rules and a real design system."),
    ("b_test", "explain", "Then you test it: a think aloud usability test with real users, recording task success rate, time on task, error rate and the System Usability Scale. | Numbers, not opinions."),
    ("b_access", "explain", "Then you audit a public website for accessibility with WAVE, Lighthouse and the NVDA screen reader, against WCAG two point two, | and discover how many sites a blind user simply cannot use."),
    ("b_mini", "excited", "And finally the mini project: a complete user centred design of something you choose. | An accessible e-governance app, a campus navigation app, a chatbot for student queries, a voice interface for visually impaired users, or a banking app without dark patterns."),
    # ---- theory in brief
    ("t_units12", "explain", "The theory supports every step. Unit one: the human, perception, memory, error, and Norman's principles. | Unit two: interaction design, design thinking, visual design and prototyping."),
    ("t_units34", "explain", "Unit three: usability engineering, user research, task analysis and heuristic evaluation. | Unit four: usability testing, accessibility, ethics, and designing for AI: chatbots, voice and multimodal interfaces."),
    # ---- marks
    ("m_scheme", "emphatic", "Marks: fifty in total, and no written end exam. | Twenty five marks of continuous assessment: active learning, task based learning and a presentation. Twenty five marks in an end oral, based on your laboratory work and the mini project."),
    ("m_fair", "explain", "So the student who does the assignments properly walks into the oral with a portfolio, | and the oral becomes a conversation about their own designs. That is a very fair way to be marked."),
    # ---- why enrol
    ("r_career", "explain", "Why pick this elective? Reason one: every product company has UX roles, and every developer who understands users ships better software. | HCI is the one subject that makes you both."),
    ("r_ai", "explain", "Reason two: AI changed the interface. Chatbots, voice assistants and copilots need design more than ever, | and this course ends exactly there, with guidelines for human AI interaction."),
    ("r_portfolio", "explain", "Reason three: a portfolio. By the end you own a Figma prototype, a usability report and an accessibility audit. | Those are things you can show in an interview, not just a grade on a marksheet."),
    ("r_fun", "warm", "Reason four: it is fun. You will argue about buttons, test your friends, break websites, and see the world differently. | Once you learn to see bad design, you cannot unsee it."),
    # ---- tips, recap, close
    ("tip1", "emphatic", "Tip one, the one minute test I promised. | Open any app and try one task you have never done in it. Count the taps, and note every moment you hesitate. Each hesitation is a design problem. Do it tonight."),
    ("tip2", "emphatic", "Tip two. | Install Figma this week; it has a free education plan for students, and we start wireframing early."),
    ("tip3", "emphatic", "Tip three. | Keep a design diary from day one: every bad interface you meet, one line each. By the end of the course it is a goldmine for your mini project."),
    ("recap", "warm", "To recap: | HCI designs the meeting point of humans and machines; | it blames the design, not the user; | you will research, prototype, test and audit real interfaces; | and you are marked on what you build, not on a written paper."),
    ("next", "warm", "Enrol, bring a problem you want to fix, and we start with the human. | See you in the first lecture."),
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
