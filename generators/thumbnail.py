#!/usr/bin/env python3
"""YouTube thumbnail (1280x720 PNG) for the N-Queens explainer.

    python3 generators/thumbnail.py --author "Abhijeet Karve" --out projects/nqueens/output/thumbnail.png

Big, high-contrast words that stay readable at phone size, the solved board
as the picture, and an author credit strip.
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "generators"))
from nqueens import trace  # noqa: E402
from vedit import find_font  # noqa: E402

W, H = 1280, 720
BG_TOP, BG_BOTTOM = (11, 18, 34), (22, 36, 66)
WHITE, MUTED, YELLOW = "#FFFFFF", "#94A3B8", "#FACC15"
BLUE = "#3B82F6"
LIGHT, DARK = "#E2E8F0", "#94A3B8"


def font(name, size):
    return ImageFont.truetype(find_font(name), size)


def fit(draw, text, name, size, max_w):
    """Largest font size <= size at which text fits max_w."""
    while size > 20:
        f = font(name, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 4
    return font(name, size)


def board(n, size):
    """The solved board: one queen per row, highlighted green."""
    _, sol = trace(n)
    cell = size // n
    size = cell * n
    img = Image.new("RGBA", (size, size))
    d = ImageDraw.Draw(img)
    for r in range(n):
        for c in range(n):
            d.rectangle([c * cell, r * cell, (c + 1) * cell, (r + 1) * cell],
                        fill=LIGHT if (r + c) % 2 == 0 else DARK)
    over = Image.new("RGBA", img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(over)
    for r, c in enumerate(sol):
        od.rectangle([c * cell, r * cell, (c + 1) * cell, (r + 1) * cell], fill=(34, 197, 94, 190))
    img = Image.alpha_composite(img, over)
    d = ImageDraw.Draw(img)
    qf = font("DejaVu Sans", int(cell * 0.78))
    for r, c in enumerate(sol):
        d.text(((c + 0.5) * cell, (r + 0.5) * cell), "♛", font=qf, fill="#0B1220", anchor="mm",
               stroke_width=3, stroke_fill="#FFFFFF")
    return img


def graph_card(size=300):
    """Small 3-coloured graph (the graph-coloring example) on a white card."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=28, fill="#FFFFFF")
    s = size / 300
    pos = {1: (70, 80), 2: (230, 80), 3: (150, 150), 4: (70, 225), 5: (230, 225)}
    pos = {k: (x * s, y * s) for k, (x, y) in pos.items()}
    edges = [(1, 2), (1, 3), (2, 3), (2, 5), (3, 4), (3, 5), (4, 5)]
    colors = {1: "#EF4444", 2: "#22C55E", 3: "#3B82F6", 4: "#22C55E", 5: "#EF4444"}
    for a, b in edges:
        d.line([pos[a], pos[b]], fill="#334155", width=int(7 * s))
    r = 30 * s
    for k, (x, y) in pos.items():
        d.ellipse([x - r, y - r, x + r, y + r], fill=colors[k], outline="#0B1220", width=int(5 * s))
        d.text((x, y), str(k), font=font("Inter:extrabold", int(30 * s)), fill="#FFFFFF", anchor="mm")
    return img


def tree_card(w=490, h=470):
    """A state space tree on a white card: dead branches crossed out in red, the answer path in green."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=30, fill="#FFFFFF")
    ys = [70, 185, 300, 410]
    root = (w / 2, ys[0])
    lv1 = [(w * x, ys[1]) for x in (0.2, 0.56, 0.86)]
    nodes = [(root, None, "ok")] + [(p, root, k) for p, k in zip(lv1, ("path", "ok", "dead"))]
    a, b = lv1[0], lv1[1]
    lv2 = [((a[0] - 50, ys[2]), a, "dead"), ((a[0] + 50, ys[2]), a, "path"),
           ((b[0] - 32, ys[2]), b, "dead"), ((b[0] + 52, ys[2]), b, "ok")]
    lv3 = [((a[0] + 18, ys[3]), lv2[1][0], "dead"), ((a[0] + 82, ys[3]), lv2[1][0], "path"),
           ((b[0] + 52, ys[3]), lv2[3][0], "ok")]
    nodes += lv2 + lv3
    colors = {"ok": "#334155", "path": "#22C55E", "dead": "#EF4444"}
    for pos, parent, kind in nodes:
        if parent:
            d.line([parent, pos], fill=colors["path"] if kind == "path" else "#94A3B8", width=8 if kind == "path" else 5)
    for pos, parent, kind in nodes:
        r = 26 if kind != "dead" else 22
        x, y = pos
        if kind == "dead":
            d.ellipse([x - r, y - r, x + r, y + r], fill="#FFFFFF", outline=colors["dead"], width=6)
            d.line([x - 12, y - 12, x + 12, y + 12], fill=colors["dead"], width=6)
            d.line([x - 12, y + 12, x + 12, y - 12], fill=colors["dead"], width=6)
        else:
            d.ellipse([x - r, y - r, x + r, y + r], fill=colors[kind], outline="#0B1220", width=4)
    return img


def cycle_card(w=490, h=470):
    """A 5-city road map on a white card, with its Hamiltonian cycle drawn in green."""
    import math
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=30, fill="#FFFFFF")
    cx, cy, R = w / 2, h / 2 + 10, 165
    pos = {k + 1: (cx + R * math.sin(2 * math.pi * k / 5), cy - R * math.cos(2 * math.pi * k / 5)) for k in range(5)}
    roads = [(1, 2), (1, 3), (1, 5), (2, 3), (2, 4), (3, 5), (4, 5)]
    cycle = [(1, 2), (2, 4), (4, 5), (5, 3), (3, 1)]
    for a, b in roads:
        d.line([pos[a], pos[b]], fill="#CBD5E1", width=9)
    for a, b in cycle:
        d.line([pos[a], pos[b]], fill="#22C55E", width=14)
    for k, (x, y) in pos.items():
        r = 34
        d.ellipse([x - r, y - r, x + r, y + r], fill="#1E293B" if k != 1 else "#EF4444", outline="#0B1220", width=4)
        d.text((x, y), str(k), font=font("Inter:extrabold", 34), fill="#FFFFFF", anchor="mm")
    return img


def bb_card(w=490, h=470):
    """A branch-and-bound tree on a white card: c-hat on every node, a killed branch, the cheapest answer in green."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=30, fill="#FFFFFF")
    pos = {1: (245, 80), 2: (95, 220), 3: (245, 220), 4: (395, 220), 7: (190, 370), 8: (300, 370)}
    for a, b in [(1, 2), (1, 3), (1, 4), (3, 7), (3, 8)]:
        d.line([pos[a], pos[b]], fill="#22C55E" if (a, b) in [(1, 3), (3, 7)] else "#CBD5E1", width=12 if (a, b) in [(1, 3), (3, 7)] else 8)
    cost = {1: "10", 2: "16", 3: "10", 4: "21", 7: "12", 8: "15"}
    for k, (x, y) in pos.items():
        r = 38
        fill = "#22C55E" if k in (3, 7) else "#1E293B"
        if k in (7, 8):
            d.rounded_rectangle([x - r, y - r, x + r, y + r], radius=10, fill=fill, outline="#0B1220", width=4)
        else:
            d.ellipse([x - r, y - r, x + r, y + r], fill=fill, outline="#0B1220", width=4)
        d.text((x, y), cost[k], font=font("Inter:extrabold", 30), fill="#FFFFFF", anchor="mm")
    x, y = pos[4]                                     # killed: c-hat 21 > U
    d.line([x - 34, y - 34, x + 34, y + 34], fill="#EF4444", width=10)
    d.line([x - 34, y + 34, x + 34, y - 34], fill="#EF4444", width=10)
    d.text((x, y), "21", font=font("Inter:extrabold", 30), fill="#FFFFFF", anchor="mm", stroke_width=4, stroke_fill="#1E293B")
    d.rounded_rectangle([330, 300, 470, 350], radius=16, fill="#FACC15")
    d.text((400, 325), "U = 12", font=font("Inter:extrabold", 28), fill="#0F172A", anchor="mm")
    return img


def matrix_card(w=490, h=470):
    """A 5x5 cost matrix on a white card, one row reduced and the chosen road highlighted."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=30, fill="#FFFFFF")
    vals = [["∞", "20", "30", "10", "11"], ["15", "∞", "16", "4", "2"], ["3", "5", "∞", "2", "4"],
            ["19", "6", "18", "∞", "3"], ["16", "4", "7", "16", "∞"]]
    cell, x0, y0 = 72, 70, 45
    for r in range(5):
        for c in range(5):
            x, y = x0 + c * cell, y0 + r * cell
            fill = "#22C55E" if (r, c) == (0, 3) else ("#FEF3C7" if r == 0 else "#F1F5F9")
            d.rectangle([x, y, x + cell - 6, y + cell - 6], fill=fill, outline="#CBD5E1", width=2)
            d.text((x + (cell - 6) / 2, y + (cell - 6) / 2), vals[r][c], font=font("Inter:extrabold", 28),
                   fill="#FFFFFF" if (r, c) == (0, 3) else "#1E293B", anchor="mm")
    d.rounded_rectangle([300, 452 - 40, 470, 452], radius=14, fill="#FACC15")
    d.text((385, 432), "ĉ = 25", font=font("Inter:extrabold", 26), fill="#0F172A", anchor="mm")
    return img


def growth_card(w=490, h=470):
    """Axes with a flat polynomial curve (green) and an exploding exponential one (red)."""
    import math
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, w - 1, h - 1], radius=30, fill="#FFFFFF")
    x0, y0, x1, y1 = 90, 400, 400, 60                      # plot area (y grows upwards)
    d.line([(x0, y1 - 10), (x0, y0), (x1 + 10, y0)], fill="#1E293B", width=5)
    d.polygon([(x1 + 22, y0), (x1 + 4, y0 - 9), (x1 + 4, y0 + 9)], fill="#1E293B")
    d.polygon([(x0, y1 - 24), (x0 - 9, y1 - 6), (x0 + 9, y1 - 6)], fill="#1E293B")
    d.text((x1 + 10, y0 + 14), "n", font=font("Inter:extrabold", 26), fill="#475569", anchor="mt")
    d.text((x0 + 16, y1 - 22), "time", font=font("Inter:extrabold", 24), fill="#475569", anchor="lt")
    span = y0 - y1 - 20
    poly = [(x0 + t * (x1 - x0), y0 - span * 0.42 * t ** 3) for t in [i / 60 for i in range(61)]]
    expo = [(x0 + t * (x1 - x0), y0 - span * (2 ** (10 * t) - 1) / (2 ** 10 - 1)) for t in [i / 60 for i in range(61)]]
    expo = [q for q in expo if q[1] >= y1]
    d.line(poly, fill="#22C55E", width=9, joint="curve")
    d.line(expo, fill="#EF4444", width=9, joint="curve")
    f = font("Inter:extrabold", 34)
    d.text((x1 + 12, poly[-1][1]), "n³", font=f, fill="#16A34A", anchor="lm")
    d.text((expo[-1][0] + 14, y1 + 4), "2ⁿ", font=f, fill="#DC2626", anchor="lt")
    d.rounded_rectangle([150, 90, 150 + 230, 90 + 46], radius=14, fill="#FACC15")
    d.text((150 + 115, 90 + 23), "polynomial?", font=font("Inter:extrabold", 26), fill="#0F172A", anchor="mm")
    return img


def make(n, author, out, tag="DAA  \u00b7  BACKTRACKING", title=("N-QUEENS", "PROBLEM"),
         subtitle="Solved step by step", credit="PREPARED BY", tag_color=BLUE, visual="board"):
    img = Image.new("RGB", (W, H))
    px = ImageDraw.Draw(img)
    for y in range(H):                            # vertical gradient background
        t = y / H
        px.line([(0, y), (W, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(BG_TOP, BG_BOTTOM)))

    # board (or state space tree) on the right, tilted slightly, with a soft glow behind it
    b = {"tree": tree_card, "cycle": cycle_card, "bb": bb_card, "matrix": matrix_card, "growth": growth_card}.get(visual, lambda: board(n, 470))()
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle([730, 105, 730 + b.width + 50, 105 + b.height + 50],
                                           radius=30, fill=(59, 130, 246, 150))
    img.paste(glow.filter(ImageFilter.GaussianBlur(40)), (0, 0), glow.filter(ImageFilter.GaussianBlur(40)))
    frame = Image.new("RGBA", (b.width + 16, b.height + 16), "#FFFFFF")
    frame.paste(b, (8, 8), b)
    frame = frame.rotate(-4, resample=Image.BICUBIC, expand=True)
    img.paste(frame, (735, 95), frame)
    if "graph" in visual:                         # the second topic, overlapping the board's corner
        g = graph_card(250).rotate(5, resample=Image.BICUBIC, expand=True)
        shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).rounded_rectangle([655, 420, 655 + 255, 420 + 255], radius=30, fill=(0, 0, 0, 140))
        img.paste(shadow.filter(ImageFilter.GaussianBlur(14)), (0, 0), shadow.filter(ImageFilter.GaussianBlur(14)))
        img.paste(g, (640, 400), g)

    d = ImageDraw.Draw(img)
    x = 64
    # topic pill
    pf = font("Inter:extrabold", 30)
    w = d.textlength(tag, font=pf)
    d.rounded_rectangle([x, 58, x + w + 44, 112], radius=27, fill=tag_color)
    d.text((x + 22, 85), tag, font=pf, fill=WHITE, anchor="lm")

    # title: up to two huge lines (white, then yellow)
    max_w = 560 if "graph" in visual else 660
    y = 130
    for i, line in enumerate(title[:2]):
        f = fit(d, line, "Inter Display:black", 170 if len(title) == 2 else 190, max_w)
        d.text((x - 4, y), line, font=f, fill=WHITE if i == 0 else YELLOW, stroke_width=2, stroke_fill="#0B1220")
        y += int(f.size * 1.0) + 8
    if subtitle:
        d.text((x, max(y + 14, 470)), subtitle, font=font("Inter:semibold", 40), fill="#CBD5E1")

    # author strip
    d.rectangle([x, 580, x + 8, 662], fill=YELLOW)
    d.text((x + 28, 578), credit, font=font("Inter:bold", 26), fill=MUTED)
    d.text((x + 28, 608), author, font=fit(d, author, "Inter:extrabold", 50, 560), fill=WHITE)

    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, optimize=True)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--author", required=True)
    ap.add_argument("--n", type=int, default=6, help="board size of the picture")
    ap.add_argument("--out", required=True)
    ap.add_argument("--tag", default="DAA  \u00b7  BACKTRACKING", help="text in the pill")
    ap.add_argument("--tag-color", default=BLUE, help="pill colour (e.g. the unit colour)")
    ap.add_argument("--title", default="N-QUEENS|PROBLEM", help="one or two title lines, split with |")
    ap.add_argument("--subtitle", default="Solved step by step")
    ap.add_argument("--credit", default="PREPARED BY", help="label above the author name")
    ap.add_argument("--visual", default="board", choices=["board", "board+graph", "tree", "cycle", "bb", "matrix", "growth"])
    args = ap.parse_args()
    out = make(args.n, args.author, args.out, args.tag, args.title.split("|"), args.subtitle, args.credit,
               args.tag_color, args.visual)
    print(f"Wrote {out} ({out.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
