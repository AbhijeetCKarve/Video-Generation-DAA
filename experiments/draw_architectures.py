"""Architecture diagrams for the two papers, drawn as SVG and rendered to
PNG with the bundled Chromium.

  figures/fig_damad_architecture.{svg,png}        DAMAD (paper 1)
  figures/obj2/fig_study_architecture.{svg,png}   the measurement study (paper 2)

The drawings are meant to be read without the text: every box says in
plain words what goes in, what happens and what comes out, and the
numbers (window lengths, K, 300-window calibration, 600-window shadow
period, ...) are the ones the code uses.
"""
from __future__ import annotations

import html
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONT = "DejaVu Sans, Arial, Helvetica, sans-serif"

# ------------------------------------------------------------------ palette
C = {
    "data": ("#E8F1E4", "#5B8C5A"),      # green: data / sensors
    "model": ("#DCE9F7", "#3C6EA5"),     # blue: models
    "score": ("#FBE6D4", "#C96A2B"),     # orange: scoring / thresholds
    "gate": ("#FFF1C9", "#B8860B"),      # yellow: drift gate / decisions
    "memory": ("#F6DCE3", "#B5405E"),    # pink: memory / control
    "meta": ("#E7DDF3", "#6E4BA3"),      # purple: meta-learning
    "neutral": ("#F2F2F2", "#777777"),
    "good": ("#DFF2E1", "#2E8B57"),
    "bad": ("#F9DADA", "#C0392B"),
}


class SVG:
    def __init__(self, w: int, h: int):
        self.w, self.h = w, h
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'font-family="{FONT}">',
            '<defs>',
            '<marker id="arr" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto" markerUnits="userSpaceOnUse">'
            '<path d="M0,0 L10,5 L0,10 z" fill="#333"/></marker>',
            '<marker id="arr-red" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto" markerUnits="userSpaceOnUse">'
            '<path d="M0,0 L10,5 L0,10 z" fill="#C0392B"/></marker>',
            '<marker id="arr-green" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto" markerUnits="userSpaceOnUse">'
            '<path d="M0,0 L10,5 L0,10 z" fill="#2E8B57"/></marker>',
            '<marker id="arr-purple" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto" markerUnits="userSpaceOnUse">'
            '<path d="M0,0 L10,5 L0,10 z" fill="#6E4BA3"/></marker>',
            '</defs>',
            f'<rect x="0" y="0" width="{w}" height="{h}" fill="white"/>',
        ]

    def add(self, s: str):
        self.parts.append(s)

    def text(self, x, y, s, size=15, weight="normal", anchor="start", fill="#222", style="normal", family=None):
        fam = f' font-family="{family}"' if family else ""
        self.add(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" '
                 f'fill="{fill}" font-style="{style}"{fam}>{html.escape(s)}</text>')

    def lines(self, x, y, lines, size=14, lh=None, anchor="start", fill="#333", weight="normal"):
        lh = lh or size * 1.32
        for i, l in enumerate(lines):
            self.text(x, y + i * lh, l, size=size, anchor=anchor, fill=fill, weight=weight)

    def box(self, x, y, w, h, kind="neutral", title=None, body=(), title_size=16, body_size=13.5, r=10,
            badge=None, dashed=False):
        fill, stroke = C[kind]
        dash = ' stroke-dasharray="7,5"' if dashed else ""
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" '
                 f'stroke-width="2"{dash}/>')
        ty = y + 24
        if badge:
            self.add(f'<circle cx="{x + 20}" cy="{y + 20}" r="13" fill="{stroke}"/>')
            self.text(x + 20, y + 25, badge, size=14, weight="bold", anchor="middle", fill="white")
        if title:
            self.text(x + (42 if badge else 14), ty, title, size=title_size, weight="bold", fill="#1a1a1a")
            ty += title_size * 1.5
        self.lines(x + 14, ty, body, size=body_size)
        return (x, y, w, h)

    def band(self, x, y, w, h, label, color="#555", fill="#FAFAFA"):
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="{color}" '
                 f'stroke-width="1.5" stroke-dasharray="2,4"/>')
        self.add(f'<rect x="{x + 16}" y="{y - 13}" width="{10 + 9.2 * len(label)}" height="26" rx="6" fill="{color}"/>')
        self.text(x + 21, y + 5, label, size=15, weight="bold", fill="white")

    def arrow(self, pts, color="#333", width=2.2, dashed=False, label=None, label_dy=-8, marker="arr", label_size=13,
              label_fill=None, label_anchor="middle", label_at=0.5):
        d = "M" + " L".join(f"{px},{py}" for px, py in pts)
        dash = ' stroke-dasharray="8,6"' if dashed else ""
        self.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{dash} marker-end="url(#{marker})"/>')
        if label:
            # label near the middle of the polyline (by segment count)
            i = max(0, min(len(pts) - 2, int(label_at * (len(pts) - 1))))
            (x1, y1), (x2, y2) = pts[i], pts[i + 1]
            lx, ly = (x1 + x2) / 2, (y1 + y2) / 2 + label_dy
            self.text(lx, ly, label, size=label_size, anchor=label_anchor, fill=label_fill or color, style="italic")

    def sparkline(self, x, y, w, h, ys, color="#3C6EA5", width=1.8):
        n = len(ys)
        lo, hi = min(ys), max(ys)
        pts = [(x + i * w / (n - 1), y + h - (v - lo) / (hi - lo + 1e-9) * h) for i, v in enumerate(ys)]
        self.add('<polyline points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts) +
                 f'" fill="none" stroke="{color}" stroke-width="{width}"/>')

    def grid(self, x, y, cols, rows, cw, ch, fill="#C9DAF0", stroke="#3C6EA5", highlight=None):
        for r in range(rows):
            for c in range(cols):
                f = fill
                if highlight and highlight(c, r):
                    f = "#F3B0A3"
                self.add(f'<rect x="{x + c * cw}" y="{y + r * ch}" width="{cw}" height="{ch}" fill="{f}" '
                         f'stroke="{stroke}" stroke-width="0.6"/>')

    def bar(self, x, y, w, h, frac, color, line_frac=None, line_color="#B8860B"):
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#eee" stroke="#999" stroke-width="0.8"/>')
        self.add(f'<rect x="{x}" y="{y + h * (1 - frac)}" width="{w}" height="{h * frac}" fill="{color}"/>')
        if line_frac is not None:
            ly = y + h * (1 - line_frac)
            self.add(f'<line x1="{x - 6}" y1="{ly}" x2="{x + w + 6}" y2="{ly}" stroke="{line_color}" stroke-width="2.5" '
                     f'stroke-dasharray="4,3"/>')

    def save(self, path: Path):
        self.add("</svg>")
        path.write_text("\n".join(self.parts), encoding="utf-8")


def render_png(svg: Path, png: Path, w: int, h: int, scale: float = 2.0):
    chrome = sorted(Path("/opt/pw-browsers").glob("chromium-*/chrome-linux*/chrome"))
    if not chrome:
        print("chromium not found; SVG only")
        return
    html_path = svg.with_suffix(".html")
    html_path.write_text(f'<html><body style="margin:0;background:white"><img src="{svg.name}" '
                         f'style="width:{w}px;height:{h}px;display:block"></body></html>')
    subprocess.run([str(chrome[-1]), "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                    f"--force-device-scale-factor={scale}", f"--window-size={w},{h}",
                    f"--screenshot={png}", f"file://{html_path}"], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    html_path.unlink()


# ===================================================================== DAMAD
def draw_damad():
    W, H = 1760, 1500
    s = SVG(W, H)
    s.text(W / 2, 40, "DAMAD: a detector that watches a plant every step and re-learns only when the plant changes",
           size=24, weight="bold", anchor="middle")
    s.text(W / 2, 66, "Read top to bottom. Green = data, blue = models, orange = scores and thresholds, "
           "yellow = decisions, pink = memory and safety, purple = meta-learning.", size=14, anchor="middle", fill="#555")

    # ---------------------------------------------------------------- band A: before deployment
    s.band(30, 100, W - 60, 230, "A  Before deployment (done once, offline)", color="#6E4BA3")
    bx, by, bw, bh, gap = 50, 130, 300, 180, 32
    s.box(bx, by, bw, bh, "data", "Past normal recordings",
          ["Weeks of sensor readings from the",
           "plant while it was running normally.",
           "No faults are needed for training."])
    s.sparkline(bx + 20, by + 120, 110, 40, [3, 4, 3.5, 5, 4.2, 4.8, 3.9, 4.4, 5.1, 4.0, 4.3], "#5B8C5A")
    s.sparkline(bx + 150, by + 120, 110, 40, [1, 1.4, 1.2, 1.1, 1.6, 2.4, 2.2, 2.6, 2.3, 2.5, 2.4], "#5B8C5A")
    s.arrow([(bx + bw, by + bh / 2), (bx + bw + gap, by + bh / 2)])
    x2 = bx + bw + gap
    s.box(x2, by, bw, bh, "gate", "Cut into operating regimes",
          ["One change detector (ADWIN) per sensor.",
           "When 20 % of sensors report a change",
           "within 200 steps, a new regime starts",
           "(regimes are at least 400 steps long)."])
    # timeline icon with coloured segments
    segs = [("#5B8C5A", 60), ("#3C6EA5", 40), ("#C96A2B", 70), ("#6E4BA3", 50), ("#B5405E", 40)]
    tx = x2 + 20
    for col, ln in segs:
        s.add(f'<rect x="{tx}" y="{by + 140}" width="{ln}" height="14" fill="{col}" opacity="0.8"/>')
        tx += ln + 3
    s.text(x2 + 20, by + 170, "regime 1   regime 2   regime 3   regime 4   ...", size=11, fill="#555")
    s.arrow([(x2 + bw, by + bh / 2), (x2 + bw + gap, by + bh / 2)])
    x3 = x2 + bw + gap
    s.box(x3, by, bw, bh, "meta", "Practice tasks (episodes)",
          ["Each regime becomes one practice task:",
           "K windows from its first half to learn",
           "from (support), 32 windows from its",
           "second half to be tested on (query)."])
    s.arrow([(x3 + bw, by + bh / 2), (x3 + bw + gap, by + bh / 2)])
    x4 = x3 + bw + gap
    s.box(x4, by, bw, bh, "meta", "Meta-training (MAML++)",
          ["400 rounds, 4 tasks per round. In each",
           "task the model takes 3 small learning",
           "steps on the support windows and is",
           "judged on the query windows. The result",
           "is a starting point that adapts quickly."])
    s.arrow([(x4 + bw, by + bh / 2), (x4 + bw + gap, by + bh / 2)])
    x5 = x4 + bw + gap
    s.box(x5, by, W - 50 - x5, bh, "model", "θ*: the adaptable start",
          ["A VAE (an autoencoder that",
           "reconstructs an 8-step window",
           "of all sensors) whose weights",
           "are a good starting point for",
           "any regime of this plant."])
    s.text(x5 + (W - 50 - x5) / 2, by + 150, "★", size=34, anchor="middle", fill="#3C6EA5")

    # ---------------------------------------------------------------- band B: steady state
    s.band(30, 380, W - 60, 300, "B  Every step while the plant runs (the steady-state path)", color="#3C6EA5")
    by = 420
    bw2, bh2, gap2 = 255, 200, 28
    x = 50
    s.box(x, by, bw2, bh2, "data", "1  Readings arrive",
          ["Every sensor of the plant",
           "sends one value per step.",
           "The last 8 steps form the",
           "current window."])
    s.grid(x + 30, by + 125, 8, 4, 22, 13)
    s.text(x + 30, by + 192, "8 steps × all sensors", size=11, fill="#555")
    s.arrow([(x + bw2, by + bh2 / 2), (x + bw2 + gap2, by + bh2 / 2)])
    x += bw2 + gap2
    s.box(x, by, bw2 + 30, bh2, "model", "2  Model guesses 'normal'",
          ["The VAE θ (adapted from θ*)",
           "compresses the window to 16",
           "numbers and rebuilds it. It can",
           "only rebuild what it has seen",
           "as normal, so a faulty window",
           "comes back wrong."])
    s.sparkline(x + 170, by + 130, 90, 40, [2, 3, 2.5, 4, 3.2, 3.8, 3.1], "#5B8C5A")
    s.sparkline(x + 170, by + 130, 90, 40, [2.1, 2.9, 2.6, 3.9, 3.1, 3.9, 3.0], "#3C6EA5", 1.4)
    s.text(x + 170, by + 185, "input vs rebuilt", size=11, fill="#555")
    s.arrow([(x + bw2 + 30, by + bh2 / 2), (x + bw2 + 30 + gap2, by + bh2 / 2)])
    x += bw2 + 30 + gap2
    bw2 = 275
    s.box(x, by, bw2, bh2, "score", "3  Residual r_t",
          ["How far the rebuilt window",
           "is from the real one (mean",
           "squared difference). Large",
           "residual = the plant is not",
           "doing what 'normal' looks",
           "like."])
    s.bar(x + 228, by + 100, 28, 75, 0.45, "#C96A2B")
    s.arrow([(x + bw2, by + bh2 / 2), (x + bw2 + gap2, by + bh2 / 2)])
    x += bw2 + gap2
    s.box(x, by, bw2, bh2, "score", "4  Compare with line τ",
          ["τ is the alarm line. It is set",
           "from the data (no labels) and",
           "does NOT move between",
           "regime changes, so ordinary",
           "ups and downs do not cause",
           "alarms."])
    s.bar(x + 228, by + 100, 28, 75, 0.45, "#C96A2B", line_frac=0.7)
    s.text(x + 260, by + 126, "τ", size=13, fill="#B8860B", weight="bold")
    s.arrow([(x + bw2, by + 70), (x + bw2 + gap2, by + 70)])
    s.arrow([(x + bw2, by + 150), (x + bw2 + gap2, by + 150)])
    x += bw2 + gap2
    s.box(x, by, 200, 80, "bad", "ALARM", ["r_t above the line τ"], title_size=17)
    s.box(x, by + 112, 200, 80, "good", "Normal", ["r_t at or below τ"], title_size=17)
    # tap to the gate
    tapx = 646 + 275 / 2
    s.arrow([(tapx, by + bh2), (tapx, by + bh2 + 60)], color="#B8860B", marker="arr")
    s.text(tapx + 10, by + bh2 + 30, "every residual is also handed to the drift gate (band C)", size=13, fill="#B8860B", style="italic")

    # ---------------------------------------------------------------- band C: drift gate
    s.band(30, 730, W - 60, 225, "C  Module 1, the drift gate: has the plant moved to a different way of running?", color="#B8860B")
    by = 770
    bw3, bh3, gap3 = 300, 160, 30
    x = 50
    s.box(x, by, bw3, bh3, "gate", "Average over blocks",
          ["The log of the residual is averaged",
           "over blocks of 10 windows, so one",
           "odd window cannot trigger anything."])
    s.arrow([(x + bw3, by + bh3 / 2), (x + bw3 + gap3, by + bh3 / 2)])
    x += bw3 + gap3
    s.box(x, by, bw3, bh3, "gate", "ADWIN: old blocks vs recent",
          ["A sliding-window test asks whether the",
           "recent blocks have a different average",
           "from the older ones, with a guarantee",
           "on how often it is wrong by chance."])
    s.arrow([(x + bw3, by + bh3 / 2), (x + bw3 + gap3, by + bh3 / 2)])
    x += bw3 + gap3
    s.box(x, by, bw3 + 40, bh3, "gate", "Two conditions before it counts",
          ["(a) the residual went UP, not down: a",
           "model that now fits better needs no help;",
           "(b) it rose by at least 65 % over the level",
           "seen after the last adaptation, and at",
           "least 400 windows have passed since then."])
    s.arrow([(x + bw3 + 40, by + bh3 / 2), (x + bw3 + 40 + gap3, by + bh3 / 2)])
    x += bw3 + 40 + gap3
    s.box(x, by, 260, bh3, "bad", "Regime change confirmed",
          ["The plant is now running in a",
           "way the model does not fit.",
           "Go to band D."], title_size=16)
    s.text(x + 130, by + 140, "⚡", size=28, anchor="middle")
    s.arrow([(x + 260, by + bh3 / 2), (x + 260 + 30, by + bh3 / 2)])
    s.box(x + 290, by, W - 50 - (x + 290), bh3, "neutral", "Otherwise",
          ["nothing changes: the same",
           "model and the same τ keep",
           "scoring (band B)."])

    # ---------------------------------------------------------------- band D: after a change
    s.band(30, 1005, W - 60, 470, "D  After a confirmed change (rare): re-learn, re-set the line, remember, check", color="#B5405E")
    by = 1045
    bw4, bh4, gap4 = 320, 190, 26
    x = 50
    s.box(x, by, bw4, bh4, "data", "Collect K example windows",
          ["The next K windows (K = 1, 5 or 10)",
           "are taken as examples of the new",
           "normal. Nothing else is needed: no",
           "labels, no engineer, no retraining",
           "on weeks of data."], badge="1")
    s.arrow([(x + bw4, by + bh4 / 2), (x + bw4 + gap4, by + bh4 / 2)])
    x += bw4 + gap4
    s.box(x, by, bw4, bh4, "model", "Module 2: adapt the model",
          ["Start again from θ* (the adaptable",
           "start, band A) and take 3 learning",
           "steps on the K windows. This takes",
           "well under a second and gives the",
           "new model θ used in band B, step 2."], badge="2")
    s.arrow([(x + bw4, by + bh4 / 2), (x + bw4 + gap4, by + bh4 / 2)])
    x += bw4 + gap4
    s.box(x, by, bw4, bh4, "score", "Module 4: new alarm line",
          ["Score the next 300 windows with the",
           "new model, fit the tail of those",
           "residuals (peaks-over-threshold) and",
           "set τ where only 1 in 100 normal",
           "windows would cross it. τ then stays",
           "fixed until the next confirmed change."], badge="3")
    s.arrow([(x + bw4, by + bh4 / 2), (x + bw4 + gap4, by + bh4 / 2)])
    x += bw4 + gap4
    s.box(x, by, bw4, bh4, "memory", "Module 3: remember it",
          ["Its last 300 steps, its sensor",
           "averages and its τ go into a memory",
           "of at most 8 regimes (oldest out).",
           "If the plant returns to a known",
           "regime later, nothing is forgotten."], badge="4")
    s.arrow([(x + bw4, by + bh4 / 2), (x + bw4 + gap4, by + bh4 / 2)])
    x += bw4 + gap4
    s.box(x, by, W - 50 - x, bh4, "meta", "Refresh θ*",
          ["10 short meta-training rounds",
           "on the new regime plus up to 3",
           "remembered ones (chosen by",
           "similarity and recency) update",
           "θ*, so the next adaptation",
           "starts from a better place."], badge="5")
    # safety check box spanning
    by2 = by + bh4 + 30
    s.box(50, by2, W - 100, 160, "memory", "Safety check for the next 600 windows: was it really a change of regime, or a long fault?",
          ["A long fault also raises the residual, so the gate can confirm a 'change' that is really an anomaly. To catch this, the old model and its old τ keep scoring in the",
           "background (the champion) while the new ones are live (the challenger). Every 50 windows the two residuals are compared; if the old model fits the",
           "stream better by a clear margin (0.1 log units), the adaptation, the new τ and the memory entry are all undone and the detector is back where it was.",
           "Dashed arrows: the new θ goes to band B step 2, the new τ to band B step 4, and the refreshed θ* to step 2 of this band."], badge="6",
          title_size=16, body_size=13.5)
    # feedback arrows (dashed) from step 2 and 3 up to band B
    x2c = 50 + bw4 + gap4 + bw4 / 2
    s.arrow([(x2c, by), (x2c, 985), (365, 985), (365, 705), (475, 705), (475, 630)],
            color="#3C6EA5", dashed=True, marker="arr", label="new model θ → band B step 2", label_dy=-6, label_at=0.2, label_size=12)
    x3 = 50 + 2 * (bw4 + gap4) + bw4 / 2
    s.arrow([(x3, by), (x3, 975), (1065, 975), (1065, 630)],
            color="#C96A2B", dashed=True, label="new alarm line τ → band B step 4", label_dy=-6, label_at=0.5, label_size=12)
    s.text(40, H - 12, "Steady state costs one forward pass per window; the dashed re-learning path runs only after a confirmed change "
           "and is reversible through the safety check.", size=12.5, fill="#555")
    out = ROOT / "figures" / "fig_damad_architecture.svg"
    s.save(out)
    render_png(out, out.with_suffix(".png"), W, H)
    print("wrote", out)


# ================================================================ measurement study
def draw_study():
    W, H = 1760, 1730
    s = SVG(W, H)
    s.text(W / 2, 40, "The measurement study: what is trained, what is adapted, what is measured",
           size=24, weight="bold", anchor="middle")
    s.text(W / 2, 66, "Read top to bottom. Green = data, blue = the detector, purple = meta-learning, orange = scores and "
           "thresholds, yellow = instruments that most reports leave out.", size=14, anchor="middle", fill="#555")

    # ---------------------------------------------------------------- band 1: tasks
    s.band(30, 100, W - 60, 220, "1  Turn one plant's normal data into practice tasks", color="#5B8C5A")
    by = 130
    bw, bh, gap = 300, 170, 30
    x = 50
    s.box(x, by, bw, bh, "data", "Normal recording",
          ["Sensor readings while the plant (or",
           "the spacecraft channel) ran normally.",
           "Cut into windows of 30 steps, one",
           "window every 5 steps."])
    s.grid(x + 20, by + 108, 10, 3, 18, 12)
    s.text(x + 20, by + 160, "30 steps × d sensors", size=11, fill="#555")
    s.arrow([(x + bw, by + bh / 2), (x + bw + gap, by + bh / 2)])
    x += bw + gap
    s.box(x, by, bw, bh, "data", "Describe each window",
          ["For every sensor: its average and",
           "its spread inside the window.",
           "A window becomes a list of 2·d",
           "numbers that says 'how the plant",
           "was running' during those 30 steps."])
    s.arrow([(x + bw, by + bh / 2), (x + bw + gap, by + bh / 2)])
    x += bw + gap
    s.box(x, by, bw, bh, "gate", "Group similar windows",
          ["k-means puts windows that",
           "describe the same way of running",
           "together. k = 2 to 12 is tried; the",
           "grouping with the best silhouette",
           "score wins. That score says how",
           "distinct the regimes are (the",
           "task-diversity score)."])
    # cluster icon
    import math
    for cx, cy, col in [(x + 245, by + 20, "#5B8C5A"), (x + 280, by + 32, "#3C6EA5"), (x + 262, by + 46, "#C96A2B")]:
        for k in range(7):
            a = k * 2 * math.pi / 7
            s.add(f'<circle cx="{cx + 9 * math.cos(a):.1f}" cy="{cy + 6 * math.sin(a):.1f}" r="2.6" fill="{col}"/>')
    s.arrow([(x + bw, by + bh / 2), (x + bw + gap, by + bh / 2)])
    x += bw + gap
    s.box(x, by, bw, bh, "meta", "One group = one task",
          ["Groups with at least 80 windows are",
           "tasks. One in five is kept back to",
           "check meta-training. A practice",
           "episode draws 20 windows to learn",
           "from (support) and 20 to be judged",
           "on (query) from the same task."])
    s.arrow([(x + bw, by + bh / 2), (x + bw + gap, by + bh / 2)])
    x += bw + gap
    s.box(x, by, W - 50 - x, bh, "data", "Telemetry sets",
          ["SMAP and MSL have one",
           "recording per channel, so",
           "each channel is a task and",
           "the grouping is run inside",
           "every channel to score its",
           "diversity."])

    # ---------------------------------------------------------------- band 2: detector
    s.band(30, 370, W - 60, 215, "2  The detector: an LSTM autoencoder that learns to rebuild normal windows", color="#3C6EA5")
    by = 405
    layers = [("input window", "30 steps × d sensors", "data", 150),
              ("LSTM, 64 units", "reads the window step by step", "model", 150),
              ("LSTM, 32 units", "keeps a running summary", "model", 150),
              ("code", "16 numbers: the whole window squeezed", "meta", 160),
              ("repeat ×30", "the code is handed to every output step", "neutral", 160),
              ("LSTM, 32 → LSTM, 64", "unfolds the code back in time", "model", 190),
              ("linear layer", "one value per sensor per step", "model", 150),
              ("rebuilt window", "30 steps × d sensors", "data", 150)]
    x = 50
    for i, (t, sub, kind, w) in enumerate(layers):
        h = 120
        yy = by + 20
        s.box(x, yy, w, h, kind, None, [], r=8)
        s.text(x + w / 2, yy + 48, t, size=14, weight="bold", anchor="middle")
        # wrap sub into two lines of ~22 chars
        words, l1, l2 = sub.split(), "", ""
        for wd in words:
            if len(l1 + " " + wd) <= 22 and not l2:
                l1 = (l1 + " " + wd).strip()
            else:
                l2 = (l2 + " " + wd).strip()
        s.text(x + w / 2, yy + 72, l1, size=11.5, anchor="middle", fill="#444")
        s.text(x + w / 2, yy + 88, l2, size=11.5, anchor="middle", fill="#444")
        if i < len(layers) - 1:
            s.arrow([(x + w, yy + h / 2), (x + w + 22, yy + h / 2)])
        x += w + 22
    s.box(x + 6, by + 20, W - 50 - x - 6, 120, "score", "Anomaly score",
          ["average squared difference",
           "between the real window and",
           "the rebuilt one. Trained on",
           "normal windows only, so an",
           "unusual window scores high."], title_size=15, body_size=12.5)
    s.text(50, by + 172, "Between 69k and 101k weights depending on the number of sensors. A flat 4-layer autoencoder (MLP-AE) on the same windows "
           "and Isolation Forest are the comparison detectors; 'Scratch' is this network with random weights and no training at all.",
           size=12.5, fill="#444")

    # ---------------------------------------------------------------- band 3: meta-training with the control
    s.band(30, 635, W - 60, 400, "3  Meta-training with first-order MAML, and the fault that leaves no trace in the loss curve", color="#6E4BA3")
    by = 675
    x = 50
    s.box(x, by, 220, 150, "meta", "Meta-model θ",
          ["The weights being",
           "meta-trained. 600 rounds",
           "(3,000 in the long run),",
           "4 tasks per round."])
    s.arrow([(x + 220, by + 75), (x + 250, by + 75)])
    x += 250
    s.box(x, by, 230, 150, "model", "Make a copy",
          ["The copy, not θ, is",
           "trained on the task so",
           "that θ stays the shared",
           "starting point."])
    s.arrow([(x + 230, by + 75), (x + 260, by + 75)])
    x += 260
    s.box(x, by, 260, 150, "model", "5 steps on support",
          ["The copy takes 5 small SGD",
           "steps (rate 0.1, gradient",
           "clipped) on the task's 20",
           "support windows."])
    s.arrow([(x + 260, by + 75), (x + 290, by + 75)])
    x += 290
    s.box(x, by, 250, 150, "score", "Judge on query",
          ["The adapted copy rebuilds the",
           "task's 20 query windows; the",
           "error is the query loss. Its",
           "gradient says how θ should",
           "move so that 5 steps work better."])
    # two paths
    gx = x + 250 + 40
    s.arrow([(x + 250, by + 50), (gx, by + 50)], color="#2E8B57", marker="arr-green")
    s.arrow([(x + 250, by + 110), (gx, by + 110)], color="#C0392B", marker="arr-red")
    s.box(gx, by - 20, W - 50 - gx, 95, "good", "Corrected path (used in the study)",
          ["Take the query gradient from the copy, average it over the",
           "4 tasks, write it onto θ, clip, Adam step. θ moves every round."], title_size=15, body_size=12.5)
    s.box(gx, by + 85, W - 50 - gx, 95, "bad", "Broken path (kept as a control)",
          ["Back-propagate on the copy, then step the optimiser on θ. θ has",
           "no gradient, the step does nothing, θ never leaves its start."], title_size=15, body_size=12.5)
    # instrument strip
    iy = by + 200
    s.box(50, iy, W - 100, 115, "gate", "Instrument: the size of the change in θ at every round, ‖θ_new − θ_old‖",
          ["Corrected: about 0.1 per round on every dataset. Broken: exactly 0.000 on every round of all 25 control runs. The broken run's loss curve "
           "still goes down, because the copy keeps",
           "learning each task's support windows, and its validation loss is an ordinary-looking number. Without this instrument the two runs are "
           "indistinguishable; the only difference",
           "shows up in the score table, where the 'meta-model' from the broken run is the random network from band 2."],
          title_size=15, body_size=13)

    # ---------------------------------------------------------------- band 4: test time
    s.band(30, 1085, W - 60, 410, "4  At test time, on a stream the model has never seen", color="#C96A2B")
    by = 1125
    x = 50
    bw5, bh5, gap5 = 275, 215, 26
    s.box(x, by, bw5, bh5, "data", "First K windows",
          ["K = 1, 5, 20 or 100 normal",
           "windows from the start of the",
           "held-out stream. This is all",
           "the detector gets to learn",
           "about the new stream."])
    s.arrow([(x + bw5, by + bh5 / 2), (x + bw5 + gap5, by + bh5 / 2)])
    x += bw5 + gap5
    s.box(x, by, bw5 + 20, bh5, "model", "Adapt, at three strengths",
          ["draft: 10 steps at rate 0.01 (the",
           "usual setting in reports)",
           "matched: 5 steps at 0.1 (what",
           "the meta-model was trained for)",
           "heavy: 50 steps at 0.1",
           "The same is done to the static",
           "model, the random network and",
           "the broken-run model."])
    s.arrow([(x + bw5 + 20, by + bh5 / 2), (x + bw5 + 20 + gap5, by + bh5 / 2)])
    x += bw5 + 20 + gap5
    s.box(x, by, bw5, bh5, "score", "Score the whole stream",
          ["Every window gets its anomaly",
           "score. AUROC and AUPRC judge",
           "the ranking of windows without",
           "any threshold."])
    s.arrow([(x + bw5, by + bh5 / 2), (x + bw5 + gap5, by + bh5 / 2)])
    x += bw5 + gap5
    s.box(x, by, bw5, bh5, "score", "Alarm line, no labels",
          ["The 300 windows after the K",
           "support windows are scored and",
           "the tail of their scores is fitted",
           "(peaks-over-threshold). The line",
           "τ is where 1 normal window in",
           "100 would cross. Evaluation starts",
           "after those 300 windows."], title_size=15)
    s.arrow([(x + bw5, by + bh5 / 2), (x + bw5 + gap5, by + bh5 / 2)])
    x += bw5 + gap5
    s.box(x, by, W - 50 - x, bh5, "score", "Report",
          ["Point-wise precision, recall",
           "and F1 at τ (no point",
           "adjustment), next to the",
           "oracle best F1 so the cost",
           "of the threshold is visible.",
           "Mean ± sd over 5 seeds;",
           "paired tests on every",
           "(seed, stream, K) cell."])
    # instruments and references row
    iy = by + bh5 + 25
    s.box(50, iy, 860, 110, "gate", "Instruments on every adapted model",
          ["• relative parameter change ‖θ' − θ‖ / ‖θ‖: how far adaptation moved the network",
           "• Spearman rank correlation of the stream's scores before vs after adaptation: did the ranking of windows change at all?",
           "• mean score ratio after / before: the part of adaptation that a threshold can see"], title_size=15, body_size=13)
    s.box(930, iy, W - 50 - 930, 110, "neutral", "Compared against",
          ["Static-AE (ordinary training), Static-AE + fine-tuning, MLP-AE, Isolation Forest,",
           "the un-adapted meta-model, the broken-run model, a random network (Scratch),",
           "and Magnitude: the mean squared standardised value of the window, no model at all."],
          title_size=15, body_size=13)

    # ---------------------------------------------------------------- band 5: cross plant
    s.band(30, 1545, W - 60, 165, "5  Across plants: SWaT, WADI and HAI have different sensors, so a shared space is needed", color="#B5405E")
    by = 1580
    x = 50
    bw6, bh6, gap6 = 300, 110, 28
    s.box(x, by, bw6, bh6, "data", "Source plant",
          ["Its normal data is projected onto its",
           "own first 32 principal components,",
           "scaled to the range seen in normal data."])
    s.arrow([(x + bw6, by + bh6 / 2), (x + bw6 + gap6, by + bh6 / 2)])
    x += bw6 + gap6
    s.box(x, by, bw6, bh6, "meta", "Train on the source",
          ["Meta-train on the source's regimes",
           "(band 3) or train the static model on",
           "its pooled windows, in the 32-d space."])
    s.arrow([(x + bw6, by + bh6 / 2), (x + bw6 + gap6, by + bh6 / 2)])
    x += bw6 + gap6
    s.box(x, by, bw6, bh6, "data", "Target plant",
          ["Projected onto ITS own 32 components.",
           "K = 20 or 100 of its normal windows",
           "adapt the source model (band 4)."])
    s.arrow([(x + bw6, by + bh6 / 2), (x + bw6 + gap6, by + bh6 / 2)])
    x += bw6 + gap6
    s.box(x, by, bw6, bh6, "score", "Score the target's attacks",
          ["Same threshold rule and metrics as",
           "band 4, all six directions, 5 seeds."])
    s.arrow([(x + bw6, by + bh6 / 2), (x + bw6 + gap6, by + bh6 / 2)])
    x += bw6 + gap6
    s.box(x, by, W - 50 - x, bh6, "neutral", "Reference points",
          ["a model trained on the target itself",
           "(the ceiling) and a random network",
           "adapted on the same K windows (the floor)."])
    out = ROOT / "figures" / "obj2" / "fig_study_architecture.svg"
    s.save(out)
    render_png(out, out.with_suffix(".png"), W, H)
    print("wrote", out)


if __name__ == "__main__":
    draw_damad()
    draw_study()
