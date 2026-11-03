"""HCI course overview (ETCS334). Rendered by build.py (needs SCHEDULE / ENVELOPE env vars)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lib"))
from lesson import *  # noqa: E402,F401,F403

PINK = UNIT_COLORS["HCI"]
PURPLE = UNIT_COLORS["IV"]
DARK = "#0F172A"
UNIT_C = {"I": SAFE, "II": GOLD, "III": ACCENT, "IV": PURPLE}


def chips(items, color, size=22, text_color=None, buff=0.22):
    return VGroup(*[chip(t, color, size, text_color or (DARK if color in (GOLD, SAFE) else TEXT)) for t in items]).arrange(RIGHT, buff=buff)


def flow(items, color, size=22, buff=0.35):
    row = chips(items, color, size, buff=buff)
    arrows = VGroup(*[Arrow(row[i].get_right(), row[i + 1].get_left(), buff=0.06, color=MUTED, stroke_width=3,
                            max_tip_length_to_length_ratio=0.4) for i in range(len(items) - 1)])
    return VGroup(row, arrows)


def titled_card(title, color, lines, w, h, title_size=26, line_size=21, line_color=TEXT):
    body = VGroup(label(title, title_size, color, "BOLD"), *[label(t, line_size, line_color) for t in lines]).arrange(DOWN, buff=0.12)
    if body.width > w - 0.3:
        body.scale_to_fit_width(w - 0.3)
    box = card(w, h, edge=color)
    return VGroup(box, body.move_to(box))


def phone(center, good=True, w=2.4, h=4.4):
    """A phone mockup: clean and calm, or cluttered and loud."""
    col = SAFE if good else KILL
    body = RoundedRectangle(width=w, height=h, corner_radius=0.35, color=col, stroke_width=4, fill_color=PANEL, fill_opacity=1).move_to(center)
    g = VGroup(body)
    if good:
        g.add(RoundedRectangle(width=w - 0.5, height=0.6, corner_radius=0.1, color=PANEL_EDGE, fill_color="#2a3140", fill_opacity=1).move_to(center + UP * 1.5))
        for i in range(3):
            g.add(RoundedRectangle(width=w - 0.6, height=0.55, corner_radius=0.12, color=col, fill_color=col, fill_opacity=0.25, stroke_width=2).move_to(center + UP * (0.5 - i * 0.8)))
        g.add(RoundedRectangle(width=w - 0.8, height=0.6, corner_radius=0.3, color=col, fill_color=col, fill_opacity=1, stroke_width=0).move_to(center + DOWN * 1.7))
        g.add(label("Pay", 20, DARK, "BOLD").move_to(center + DOWN * 1.7))
    else:
        rng = np.random.RandomState(3)
        for i in range(14):
            x = rng.uniform(-w / 2 + 0.35, w / 2 - 0.35); y = rng.uniform(-h / 2 + 0.3, h / 2 - 0.3)
            ww = rng.uniform(0.3, 1.1); hh = rng.uniform(0.18, 0.45)
            c = [KILL, GOLD, ACCENT, "#f97316", "#a3e635"][i % 5]
            g.add(Rectangle(width=ww, height=hh, color=c, fill_color=c, fill_opacity=0.7, stroke_width=1).move_to(center + np.array([x, y, 0])))
        g.add(label("✕", 22, TEXT, "BOLD").move_to(center + UP * 1.8 + RIGHT * 0.85))
    return g


class Video(Lesson):
    NEXT = ("Unit I", "Foundations of HCI and human factors")

    # ------------------------------------------------------------ small layout helpers
    def screen(self, head_text, color, sub=None):
        """Clear the stage and put a unit / section header at the top; rows then stack under it."""
        self.clear(run_time=0.4)
        head = chip(head_text, color, 26, DARK if color in (GOLD, SAFE) else TEXT).move_to(STAGE + UP * 2.55)
        self.show(head, anim=GrowFromCenter, run_time=0.5)
        self.sfx("pop")
        self.y = 1.75
        if sub:
            t = label(sub, 30, TEXT, "BOLD").move_to(STAGE + UP * self.y)
            self.show(t, run_time=0.4)
            self.y -= 0.85
        return head

    def row(self, mob, gap=0.62, run_time=0.9, lag=True):
        """Place a row at the current y and reveal it left to right."""
        mob.move_to(STAGE + UP * self.y)
        if mob.width > 13.4:
            mob.scale_to_fit_width(13.4)
        self.stage.add(mob)
        parts = list(mob[0]) if isinstance(mob[0], VGroup) and len(mob) == 2 else list(mob)
        if lag and len(parts) > 1:
            self.go(LaggedStart(*[FadeIn(p, shift=UP * 0.15) for p in parts], lag_ratio=0.25), *([FadeIn(mob[1])] if len(mob) == 2 and not isinstance(mob[1], Text) and len(parts) != len(mob) else []), run_time=run_time)
        else:
            self.go(FadeIn(mob, shift=UP * 0.15), run_time=0.5)
        self.y -= gap

    def case(self, text, y=None):
        c = VGroup(chip("CASE STUDY", GOLD, 20, DARK), label(text, 24, TEXT)).arrange(RIGHT, buff=0.3)
        if c.width > 12.8:
            c.scale_to_fit_width(12.8)
        box = card(c.width + 0.6, c.height + 0.45, edge=GOLD)
        g = VGroup(box, c.move_to(box)).move_to(STAGE + UP * (y if y is not None else self.y))
        self.show(g, run_time=0.6, shift=UP * 0.2)
        self.sfx("chime")
        self.y -= 0.9
        return g

    # ------------------------------------------------------------ hook
    def b_hook_apps(self, b):
        p1 = phone(STAGE + LEFT * 3.2 + UP * 0.2, True)
        p2 = phone(STAGE + RIGHT * 3.2 + UP * 0.2, False)
        self.show(p1, run_time=0.6)
        self.show(p2, run_time=0.6)
        l1 = chip("effortless", SAFE, 26, DARK).next_to(p1, DOWN, buff=0.3)
        l2 = chip("throw the phone", KILL, 26).next_to(p2, DOWN, buff=0.3)
        self.show(l1, l2, run_time=0.5)
        self.at(b, 1)
        mid = VGroup(label("same hardware", 26, MUTED), label("same user", 26, MUTED), label("different interface", 32, GOLD, "BOLD")
                     ).arrange(DOWN, buff=0.2).move_to(STAGE + UP * 0.2)
        self.show(mid, run_time=0.6)
        self.sfx("chime")

    def b_hook_hci(self, b):
        self.clear(run_time=0.4)
        big = label("HCI", 130, PINK, "BOLD").move_to(STAGE + UP * 0.9)
        self.show(big, anim=GrowFromCenter, run_time=0.7)
        self.sfx("whoosh")
        full = label("Human Computer Interface", 40, TEXT, "BOLD").next_to(big, DOWN, buff=0.2)
        self.show(full, run_time=0.5)
        self.at(b, 1)
        fl = flow(["design", "prototype", "test"], GOLD, 28, 0.6).move_to(STAGE + DOWN * 1.9)
        self.show(fl, run_time=0.7)
        self.sfx("pop")

    def b_hook_promise(self, b):
        self.clear(run_time=0.4)
        t = chip("the whole syllabus in 13 minutes", PINK, 32).move_to(STAGE + UP * 2.0)
        self.show(t, anim=GrowFromCenter, run_time=0.5)
        self.at(b, 1)
        items = VGroup(*[VGroup(chip(str(i + 1), ACCENT, 26), label(x, 32, TEXT, "BOLD")).arrange(RIGHT, buff=0.3) for i, x in enumerate(
            ["Four theory units", "Eight lab assignments and a mini project", "How you are assessed", "How to score well"])])
        items.arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(STAGE + DOWN * 0.4)
        self.stage.add(items)
        self.go(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.3) for r in items], lag_ratio=0.4), run_time=1.8)
        self.sfx("pop")

    def b_syllabus(self, b):
        self.syllabus(b, ["The course at a glance", "The four units", "Laboratory and mini project", "Assessment and books"],
                      unit_text="ETCS334  ·  HCI")

    def b_exam(self, b):
        self.exam_star(b, star="★  No written end exam")

    # ------------------------------------------------------------ at a glance
    def b_g_card(self, b):
        self.unsay()
        self.screen("THE COURSE AT A GLANCE", PINK)
        rows = [("Course code", "ETCS334"), ("Course title", "Human Computer Interface (HCI)"), ("Programme", "B Tech (CSE)  ·  Semester VIII"), ("Pattern", "2024")]
        g = VGroup(*[VGroup(label(k, 24, MUTED, "BOLD"), label(v, 28, TEXT, "BOLD")).arrange(RIGHT, buff=0.4) for k, v in rows])
        for r in g:
            r[0].set_x(STAGE[0] - 4.8, LEFT); r[1].set_x(STAGE[0] - 1.6, LEFT)
        g.arrange(DOWN, buff=0.35, aligned_edge=LEFT, center=False)
        for i, r in enumerate(g):
            r.set_y(STAGE[1] + 1.5 - i * 0.7)
        box = card(11.0, 3.6).move_to(STAGE + UP * 0.45)
        self.show(box, run_time=0.4)
        self.stage.add(g)
        self.go(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.3) for r in g], lag_ratio=0.3), run_time=1.6)
        self.at(b, 1)
        pec = chip("Programme Elective Course (PEC)  ·  Programme Elective VI", GOLD, 26, DARK).move_to(STAGE + DOWN * 2.1)
        self.show(pec, anim=GrowFromCenter, run_time=0.5)
        self.sfx("pop")

    def b_g_scheme(self, b):
        self.screen("TEACHING SCHEME  ·  PER WEEK", PINK)
        cols = [("Lecture", "1", ACCENT), ("Tutorial", "–", PANEL_EDGE), ("Laboratory", "2", SAFE), ("Project", "–", PANEL_EDGE), ("Internship", "–", PANEL_EDGE)]
        cards = VGroup(*[VGroup(card(2.2, 2.0, edge=c), VGroup(label(n, 20, MUTED, "BOLD"), label(v, 56, TEXT if v != "–" else MUTED, "BOLD")).arrange(DOWN, buff=0.1))
                         for n, v, c in cols])
        for cd in cards:
            cd[1].move_to(cd[0])
        cards.arrange(RIGHT, buff=0.3).move_to(STAGE + UP * 0.7)
        self.stage.add(cards)
        self.go(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cards], lag_ratio=0.2), run_time=1.4)
        cr = chip("Total credits: 2", GOLD, 32, DARK).move_to(STAGE + DOWN * 1.1)
        self.show(cr, anim=GrowFromCenter, run_time=0.5)
        self.sfx("pop")
        self.at(b, 1)
        bar = VGroup(Rectangle(width=3.6, height=0.55, color=ACCENT, fill_color=ACCENT, fill_opacity=1, stroke_width=0),
                     Rectangle(width=7.2, height=0.55, color=SAFE, fill_color=SAFE, fill_opacity=1, stroke_width=0)).arrange(RIGHT, buff=0).move_to(STAGE + DOWN * 2.2)
        lab = VGroup(label("1 h lecture", 20, TEXT).move_to(bar[0]), label("2 h laboratory  ·  two thirds of the course", 20, DARK, "BOLD").move_to(bar[1]))
        self.show(bar, lab, run_time=0.6)

    def b_g_marks(self, b):
        self.screen("ASSESSMENT  ·  50 MARKS", PINK)
        bar = VGroup(Rectangle(width=6.2, height=1.1, color=ACCENT, fill_color=ACCENT, fill_opacity=1, stroke_width=0),
                     Rectangle(width=6.2, height=1.1, color=GOLD, fill_color=GOLD, fill_opacity=1, stroke_width=0)).arrange(RIGHT, buff=0.05).move_to(STAGE + UP * 1.1)
        t = VGroup(label("Continuous assessment (CAT)  ·  25", 22, TEXT, "BOLD").move_to(bar[0]), label("End oral exam  ·  25", 22, DARK, "BOLD").move_to(bar[1]))
        self.show(bar, run_time=0.6)
        self.show(t, run_time=0.4)
        self.sfx("pop")
        note = label("the oral is based on your laboratory assignments and the mini project", 24, GOLD).move_to(STAGE + UP * 0.1)
        self.show(note, run_time=0.5)
        self.at(b, 1)
        na = VGroup(*[chip(x, KILL, 24) for x in ["Term-end theory exam: NA", "Term-end practical exam: NA", "CAL: NA"]]).arrange(RIGHT, buff=0.3).move_to(STAGE + DOWN * 1.4)
        self.stage.add(na)
        self.go(LaggedStart(*[GrowFromCenter(c) for c in na], lag_ratio=0.3), run_time=1.0)
        self.sfx("kill")
        strike = VGroup(*[Line(c.get_left(), c.get_right(), color=TEXT, stroke_width=4) for c in na])
        self.show(strike, anim=Create, run_time=0.5)

    def b_g_prereq(self, b):
        self.screen("PREREQUISITES", PINK)
        pre = VGroup(*[titled_card(t, ACCENT, [s], 4.0, 1.6, 24, 20) for t, s in
                       [("Programming", "fundamentals"), ("Web technologies", "HTML, CSS, JavaScript"), ("Software", "engineering")]]).arrange(RIGHT, buff=0.4).move_to(STAGE + UP * 0.6)
        self.stage.add(pre)
        self.go(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in pre], lag_ratio=0.3), run_time=1.3)
        self.at(b, 1)
        ticks = VGroup(*[label("✓", 44, SAFE, "BOLD").next_to(c, DOWN, buff=0.25) for c in pre])
        self.stage.add(ticks)
        self.go(LaggedStart(*[GrowFromCenter(t) for t in ticks], lag_ratio=0.3), run_time=0.9)
        self.sfx("chime")
        done = label("you already have all three", 28, SAFE, "BOLD").move_to(STAGE + DOWN * 2.0)
        self.show(done, run_time=0.4)

    # ------------------------------------------------------------ objectives and outcomes
    def b_o_obj(self, b):
        self.screen("COURSE OBJECTIVES", PINK)
        items = ["Fundamentals, evolution and human factors of HCI", "Interaction design principles, UI patterns and prototyping",
                 "Usability engineering, user research and heuristic evaluation", "Usability testing, metrics, accessibility, AI-based and multimodal interfaces"]
        rows = VGroup(*[VGroup(chip(str(i + 1), PINK, 24), label(t, 27, TEXT)).arrange(RIGHT, buff=0.3) for i, t in enumerate(items)])
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4).move_to(STAGE + UP * 0.2)
        if rows.width > 13.0:
            rows.scale_to_fit_width(13.0)
        self.stage.add(rows)
        self.go(FadeIn(rows[0], shift=RIGHT * 0.3), run_time=0.5)
        self.at(b, 1)
        span = self.phrase_len(b, 1)
        for i in range(1, 4):
            self.until(b["phrases"][1]["start"] + span * (0.05 + 0.3 * (i - 1)))
            self.go(FadeIn(rows[i], shift=RIGHT * 0.3), run_time=0.5)
            self.sfx("pop", -0.3)

    def b_o_co(self, b):
        self.screen("COURSE OUTCOMES", PINK)
        items = [("CO1", "Explain HCI concepts, human factors, Norman's principles", "Level 2"),
                 ("CO2", "Apply design principles, UI patterns, prototyping", "Level 3 + 6"),
                 ("CO3", "Analyse user needs; evaluate with heuristics and ISO 9241", "Level 4 + 5"),
                 ("CO4", "Evaluate usability and accessibility: testing, metrics, WCAG, AI interfaces", "Level 5")]
        rows = VGroup(*[VGroup(chip(c, ACCENT, 22), label(t, 25, TEXT), chip(l, PANEL_EDGE, 18)).arrange(RIGHT, buff=0.3) for c, t, l in items])
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.4).move_to(STAGE + UP * 0.2)
        if rows.width > 13.4:
            rows.scale_to_fit_width(13.4)
        self.stage.add(rows)
        self.go(LaggedStart(FadeIn(rows[0], shift=RIGHT * 0.3), FadeIn(rows[1], shift=RIGHT * 0.3), lag_ratio=0.6), run_time=1.2)
        self.at(b, 1)
        self.go(FadeIn(rows[2], shift=RIGHT * 0.3), run_time=0.5)
        self.until(b["phrases"][1]["start"] + self.phrase_len(b, 1) * 0.5)
        self.go(FadeIn(rows[3], shift=RIGHT * 0.3), run_time=0.5)
        self.sfx("pop")

    # ------------------------------------------------------------ units
    def unit(self, roman, hours, title):
        self.screen(f"UNIT {roman}  ·  {hours} HOURS", UNIT_C[roman], title)

    def b_u1_intro(self, b):
        self.unit("I", 4, "Foundations of HCI and human factors")
        self.row(chips(["definition", "scope", "importance of HCI"], PANEL_EDGE))
        self.at(b, 1)
        self.row(flow(["command line", "GUI", "touch", "voice", "AI-based"], SAFE, 22, 0.3))

    def b_u1_human(self, b):
        self.row(chips(["the human as information processor:", "perception", "memory", "mental models"], ACCENT))
        self.at(b, 1)
        self.row(chips(["human error:", "slips  (right plan, wrong action)", "mistakes  (wrong plan)"], KILL))

    def b_u1_norman(self, b):
        self.row(chips(["Norman:", "visibility", "feedback", "constraints", "mapping", "affordances", "signifiers"], GOLD, 20))
        self.at(b, 1)
        self.row(chips(["gulf of execution", "gulf of evaluation", "Fitts' law: pointing", "Hick's law: choosing"], ACCENT, 20))

    def b_u1_case(self, b):
        self.case("good and bad design in everyday products and public kiosks (ATM, ticket vending machine)")

    def b_u2_intro(self, b):
        self.unit("II", 4, "Interaction design and prototyping")
        self.row(chips(["user-centred design", "design thinking"], PANEL_EDGE))
        self.at(b, 1)
        self.row(flow(["empathise", "define", "ideate", "prototype", "test"], GOLD, 22, 0.3))

    def b_u2_rules(self, b):
        self.row(chips(["Shneiderman's 8 golden rules", "UI design patterns", "layout · Gestalt · colour · typography"], ACCENT, 20))
        self.at(b, 1)
        self.row(chips(["information architecture:", "navigation design", "card sorting"], SAFE, 20))

    def b_u2_proto(self, b):
        self.row(chips(["design systems:", "Material Design", "Apple Human Interface Guidelines"], PANEL_EDGE, 20))
        self.at(b, 1)
        self.row(flow(["wireframes", "low-fidelity prototype", "high-fidelity prototype"], GOLD, 22, 0.4))

    def b_u2_case(self, b):
        self.case("wireframes and a low-fidelity prototype of a university student portal / mobile app")

    def b_u3_intro(self, b):
        self.unit("III", 4, "Usability engineering and user research")
        self.row(chips(["usability engineering lifecycle"], PANEL_EDGE))
        self.at(b, 1)
        self.row(chips(["usability", "vs", "user experience (UX)"], ACCENT))

    def b_u3_research(self, b):
        self.row(chips(["user research:", "interviews", "surveys", "observation"], SAFE, 20))
        self.at(b, 1)
        self.row(chips(["affinity diagrams", "personas", "scenarios", "user journey maps"], GOLD, 20))

    def b_u3_models(self, b):
        self.row(chips(["hierarchical task analysis", "Keystroke-Level Model (KLM)"], ACCENT, 20))
        self.at(b, 1)
        self.row(chips(["Nielsen's 10 usability heuristics", "ISO 9241-11 definition of usability"], PANEL_EDGE, 20))

    def b_u3_case(self, b):
        self.row(chips(["heuristic evaluation with severity ratings", "cognitive walkthrough"], KILL, 20))
        self.at(b, 1)
        self.case("heuristic evaluation of a real app: e-commerce, banking or a government service")

    def b_u4_intro(self, b):
        self.unit("IV", 3, "Usability testing, accessibility and emerging interfaces")
        self.at(b, 1)
        self.row(chips(["usability testing:", "think-aloud protocol", "moderated / remote testing", "A/B testing"], ACCENT, 20))

    def b_u4_metrics(self, b):
        self.row(chips(["metrics:", "task success rate", "time on task", "error rate", "System Usability Scale (SUS)"], GOLD, 20))
        self.at(b, 1)
        self.row(chips(["accessibility:", "WCAG 2.2", "POUR principles", "assistive technologies", "inclusive design"], SAFE, 20))

    def b_u4_ethics(self, b):
        self.row(chips(["ethics:", "dark patterns", "privacy"], KILL, 20))
        self.at(b, 1)
        self.row(chips(["human-AI interaction:", "chatbot", "voice", "multimodal interfaces"], PURPLE, 20))

    def b_u4_case(self, b):
        self.case("accessibility evaluation of a website / usability evaluation of an AI chatbot")
        self.at(b, 1)
        tot = chip("theory: 15 hours across four units  (4 + 4 + 4 + 3)", PINK, 24).move_to(STAGE + DOWN * 3.0)
        self.show(tot, anim=GrowFromCenter, run_time=0.5)
        self.sfx("chime")

    # ------------------------------------------------------------ laboratory
    def assignment_card(self, n, hours, title, lines, w=4.2, h=2.4):
        body = VGroup(VGroup(chip(f"A{n}", PINK, 20), chip(f"{hours} h", PANEL_EDGE, 16)).arrange(RIGHT, buff=0.2),
                      label(title, 22, TEXT, "BOLD"), *[label(t, 18, MUTED) for t in lines]).arrange(DOWN, buff=0.1)
        if body.width > w - 0.3:
            body.scale_to_fit_width(w - 0.3)
        box = card(w, h)
        return VGroup(box, body.move_to(box))

    def b_l_tools(self, b):
        self.screen("LABORATORY  ·  30 HOURS  ·  8 ASSIGNMENTS", SAFE)
        big = label("where most of your marks are made", 30, GOLD, "BOLD").move_to(STAGE + UP * 1.4)
        self.show(big, run_time=0.5)
        self.at(b, 1)
        tools = VGroup(*[chip(t, ACCENT, 22) for t in ["Figma / Balsamiq", "Google Forms", "card-sorting tool", "WAVE / Lighthouse", "NVDA screen reader"]]).arrange(RIGHT, buff=0.3)
        tools.move_to(STAGE + DOWN * 0.2)
        if tools.width > 13.4:
            tools.scale_to_fit_width(13.4)
        self.stage.add(tools)
        self.go(LaggedStart(*[GrowFromCenter(t) for t in tools], lag_ratio=0.25), run_time=1.5)
        self.sfx("pop")
        note = label("real tools, the same ones used in industry", 22, MUTED).move_to(STAGE + DOWN * 1.2)
        self.show(note, run_time=0.4)

    def lab_screen(self, cards_spec, phrase_split):
        self.screen("LABORATORY ASSIGNMENTS", SAFE)
        cards = VGroup(*[self.assignment_card(*c) for c in cards_spec]).arrange(RIGHT, buff=0.35).move_to(STAGE + UP * 0.3)
        self.stage.add(cards)
        return cards

    def b_l_a123(self, b):
        cards = self.lab_screen([(1, 2, "Exploring human factors", ["2 good + 2 bad designs", "Norman's principles", "reflection on human error"]),
                                 (2, 4, "User research & task analysis", ["survey / interview, 5+ users", "affinity diagram, personas", "journey map, HTA, KLM"]),
                                 (3, 2, "Information architecture", ["card sorting with 2–3 users", "sitemap", "navigation review"])], 2)
        self.go(FadeIn(cards[0], shift=UP * 0.2), run_time=0.5)
        self.until(b["phrases"][0]["start"] + self.phrase_len(b, 0) * 0.45)
        self.go(FadeIn(cards[1], shift=UP * 0.2), run_time=0.5)
        self.at(b, 1)
        self.go(FadeIn(cards[2], shift=UP * 0.2), run_time=0.5)
        self.sfx("pop")

    def b_l_a45(self, b):
        cards = self.lab_screen([(4, 6, "Wireframing & prototyping", ["lo-fi wireframes, 3+ screens", "hi-fi interactive Figma prototype", "golden rules, Gestalt, design system"]),
                                 (5, 4, "Heuristic evaluation", ["Nielsen's 10 heuristics", "severity ratings", "cognitive walkthrough, redesign"])], 1)
        self.go(FadeIn(cards[0], shift=UP * 0.2), run_time=0.5)
        big = chip("the biggest assignment: 6 hours", GOLD, 22, DARK).next_to(cards[0], DOWN, buff=0.3)
        self.show(big, run_time=0.4)
        self.at(b, 1)
        self.go(FadeIn(cards[1], shift=UP * 0.2), run_time=0.5)
        self.sfx("pop")

    def b_l_a67(self, b):
        cards = self.lab_screen([(6, 4, "Usability testing", ["think-aloud test, 3–5 users", "task success, time on task", "error rate, SUS score"]),
                                 (7, 4, "Accessibility evaluation", ["WAVE / Lighthouse + NVDA", "contrast, alt text, keyboard, ARIA", "compared against WCAG 2.2"])], 1)
        self.go(FadeIn(cards[0], shift=UP * 0.2), run_time=0.5)
        self.at(b, 1)
        self.go(FadeIn(cards[1], shift=UP * 0.2), run_time=0.5)
        self.sfx("pop")

    def b_l_mini(self, b):
        self.screen("ASSIGNMENT 8  ·  MINI PROJECT  ·  4 HOURS", GOLD)
        d = label("design, prototype and evaluate an interface through the complete user-centred design process", 24, TEXT).move_to(STAGE + UP * 1.6)
        if d.width > 13.0:
            d.scale_to_fit_width(13.0)
        self.show(d, run_time=0.5)
        self.at(b, 1)
        topics = ["accessible e-governance app", "campus navigation app", "chatbot for student queries", "appointment app for elderly users",
                  "voice interface for visually impaired users", "checkout redesign, A/B tested", "AR campus / museum guide", "banking app without dark patterns"]
        cs = [chip(t, PURPLE, 20) for t in topics]
        grid = VGroup(VGroup(*cs[:3]).arrange(RIGHT, buff=0.25), VGroup(*cs[3:6]).arrange(RIGHT, buff=0.25), VGroup(*cs[6:]).arrange(RIGHT, buff=0.25)
                      ).arrange(DOWN, buff=0.3).move_to(STAGE + DOWN * 0.6)
        if grid.width > 13.2:
            grid.scale_to_fit_width(13.2)
        self.stage.add(grid)
        self.go(LaggedStart(*[GrowFromCenter(c) for c in cs], lag_ratio=0.15), run_time=2.4)
        self.sfx("pop")

    def b_l_flow(self, b):
        self.screen("ONE DESIGN PROCESS", SAFE)
        self.at(b, 1)
        fl = flow(["research", "structure", "prototype", "evaluate", "test", "audit"], SAFE, 22, 0.3).move_to(STAGE + UP * 0.6)
        self.show(fl, run_time=1.2)
        nums = VGroup(*[label(t, 18, MUTED).next_to(c, DOWN, buff=0.15) for t, c in zip(["A1, A2", "A3", "A4", "A5", "A6", "A7"], fl[0])])
        self.show(nums, run_time=0.4)
        mp = chip("A8 mini project: all of it, on one interface", GOLD, 26, DARK).move_to(STAGE + DOWN * 1.2)
        self.show(mp, anim=GrowFromCenter, run_time=0.5)
        self.sfx("chime")

    # ------------------------------------------------------------ assessment
    def b_a_cat(self, b):
        self.screen("CONTINUOUS ASSESSMENT FOR THEORY  ·  25 MARKS", ACCENT)
        self.at(b, 1)
        cs = VGroup(*[titled_card(n, ACCENT, [t, f"{m} marks"], 3.8, 2.0, 24, 22) for n, t, m in
                      [("CAT 1", "Active learning", 10), ("CAT 2", "Task based learning", 10), ("CAT 3", "Presentation", 5)]]).arrange(RIGHT, buff=0.4).move_to(STAGE + UP * 0.5)
        self.stage.add(cs)
        self.go(LaggedStart(*[FadeIn(c, shift=UP * 0.2) for c in cs], lag_ratio=0.35), run_time=1.5)
        self.sfx("pop")
        s = label("10 + 10 + 5 = 25", 30, GOLD, "BOLD").move_to(STAGE + DOWN * 1.4)
        self.show(s, run_time=0.4)

    def b_a_oral(self, b):
        self.screen("END ORAL EXAM  ·  25 MARKS", GOLD)
        c = titled_card("Oral / practical", GOLD, ["based on your laboratory assignments", "and the mini project"], 7.5, 2.0, 28, 24).move_to(STAGE + UP * 0.8)
        self.show(c, run_time=0.6)
        self.at(b, 1)
        bar = VGroup(Rectangle(width=5.0, height=0.8, color=ACCENT, fill_color=ACCENT, fill_opacity=1, stroke_width=0),
                     Rectangle(width=5.0, height=0.8, color=GOLD, fill_color=GOLD, fill_opacity=1, stroke_width=0)).arrange(RIGHT, buff=0.05).move_to(STAGE + DOWN * 1.2)
        t = VGroup(label("theory CAT  25", 22, TEXT, "BOLD").move_to(bar[0]), label("lab work  25", 22, DARK, "BOLD").move_to(bar[1]))
        self.show(bar, t, run_time=0.6)
        half = label("your lab work is half the course", 28, GOLD, "BOLD").move_to(STAGE + DOWN * 2.3)
        self.show(half, run_time=0.4)
        self.sfx("chime")

    # ------------------------------------------------------------ books
    def b_b_text(self, b):
        self.screen("TEXTBOOKS", PINK)
        books = [("Human-Computer Interaction", "Dix, Finlay, Abowd, Beale", "3rd ed., Pearson"), ("Usability Engineering", "Jakob Nielsen", "Morgan Kaufmann"),
                 ("Designing the User Interface", "Shneiderman et al.", "6th ed., Pearson")]
        cs = VGroup(*[titled_card(t, PINK, [a, e], 4.2, 2.2, 23, 20) for t, a, e in books]).arrange(RIGHT, buff=0.35).move_to(STAGE + UP * 0.4)
        self.stage.add(cs)
        self.go(LaggedStart(FadeIn(cs[0], shift=UP * 0.2), FadeIn(cs[1], shift=UP * 0.2), lag_ratio=0.5), run_time=1.2)
        self.at(b, 1)
        self.go(FadeIn(cs[2], shift=UP * 0.2), run_time=0.5)
        self.sfx("pop")

    def b_b_ref(self, b):
        self.screen("READING AND ONLINE", PINK)
        refs = VGroup(chip("Don Norman · The Design of Everyday Things", GOLD, 22, DARK), chip("Steve Krug · Don't Make Me Think", GOLD, 22, DARK)).arrange(RIGHT, buff=0.4)
        refs.move_to(STAGE + UP * 1.3)
        self.stage.add(refs)
        self.go(LaggedStart(*[GrowFromCenter(c) for c in refs], lag_ratio=0.4), run_time=1.0)
        self.at(b, 1)
        online = [chip(t, ACCENT, 20) for t in ["W3C WCAG 2.2", "NN/g: 10 usability heuristics", "Microsoft: human-AI interaction guidelines",
                                                 "NPTEL · IIT Guwahati", "NPTEL · IIIT Hyderabad", "NPTEL · IIT Roorkee", "Coursera · human factors and usability"]]
        grid = VGroup(VGroup(*online[:3]).arrange(RIGHT, buff=0.25), VGroup(*online[3:]).arrange(RIGHT, buff=0.25)).arrange(DOWN, buff=0.3).move_to(STAGE + DOWN * 0.7)
        if grid.width > 13.4:
            grid.scale_to_fit_width(13.4)
        self.stage.add(grid)
        self.go(LaggedStart(*[FadeIn(c, shift=UP * 0.15) for c in online], lag_ratio=0.15), run_time=1.6)
        self.sfx("pop")

    # ------------------------------------------------------------ tips, recap
    def b_tip1(self, b):
        self.tip(b, 1, "Keep a design portfolio from week one", "surveys, affinity diagrams, personas, wireframes, Figma links: the oral is about this")

    def b_tip2(self, b):
        self.tip(b, 2, "Start the mini project early, reuse your assignments", "research (A2) · prototype (A4) · evaluation (A5) · test (A6)")

    def b_tip3(self, b):
        self.tip(b, 3, "Learn the vocabulary by heart", "Norman's 6 · Shneiderman's 8 · Nielsen's 10 · POUR · SUS · WCAG")

    def b_recap(self, b):
        self.recap(b, ["2 credits: 1 lecture + 2 lab hours a week", "4 units: human factors to AI interfaces", "8 lab assignments + a mini project",
                       "50 marks: 25 continuous + 25 oral"])
