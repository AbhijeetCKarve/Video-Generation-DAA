#!/usr/bin/env python3
"""Cut the 49-second DAA promo: intro -> montage of ten real lesson clips -> promise -> progress -> outro,
cross-faded, with the original upbeat track and the series' own sound effects.

    python3 videos/brand/build.py [--final-dir /path/to/daa-recordings/final]
"""
import argparse
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "videos" / "lib"))
import production as pr  # noqa: E402
from kit import UNIT_COLORS  # noqa: E402

PROJ = ROOT / "projects" / "branding"
SCENES = PROJ / "build" / "videos" / "promo" / "1080p30"
FONT = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
XF = 0.4                    # cross-fade length
CLIP = 2.1                  # each montage clip, before the overlap
TARGET = 49.0               # final length in seconds
# (video, start second, crop (w, h, x, y), title) - moments that look good zoomed in
C = (1440, 810, 240, 135)
CLIPS = [("daa-3.1", 215, C, "3.1  Backtracking fundamentals"),
         ("daa-3.2-face", 306, (1440, 810, 480, 120), "3.2  8-Queens & graph coloring"),
         ("daa-3.3", 322, C, "3.3  Sum of subsets & Hamiltonian cycle"),
         ("daa-3.4", 180, (1440, 810, 100, 135), "3.4  Branch & bound: FIFO, LIFO, LC"),
         ("daa-3.5", 250, C, "3.5  0/1 Knapsack & TSP"),
         ("daa-4.1", 92, (1600, 900, 160, 120), "4.1  Polynomial vs exponential"),
         ("daa-4.2", 395, C, "4.2  P, NP, NP-hard, NP-complete"),
         ("daa-4.3", 250, C, "4.3  Polynomial-time reductions"),
         ("daa-4.4", 245, C, "4.4  Proving NP-completeness"),
         ("daa-4.5", 215, C, "4.5  Approximation algorithms")]


def dur(path):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(path)]).decode().strip())


def esc(text):
    return text.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--final-dir", default="/home/user/daa-recordings/final")
    ap.add_argument("--out", default=str(PROJ / "output" / "daa-series-promo-49s.mp4"))
    args = ap.parse_args()
    final, out = Path(args.final_dir), Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.parent / "tmp-promo"
    tmp.mkdir(exist_ok=True)

    # 1. montage clips: 75 % centre crop (keeps the face circle of 3.2 out of frame), title chip bottom-left
    segs = [SCENES / "IntroScene.mp4"]
    for i, (name, start, (cw, ch, x0, y0), title) in enumerate(CLIPS):
        unit = "III" if name.startswith("daa-3") else "IV"
        clip = tmp / f"clip{i:02d}.mp4"
        draw = (f"drawtext=fontfile={FONT}:text='{esc(title)}':fontsize=54:fontcolor=white:"
                f"box=1:boxcolor=0x{UNIT_COLORS[unit][1:]}@1.0:boxborderw=24:x=80:y=h-80-th")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(start), "-t", str(CLIP), "-i", str(final / f"{name}.mp4"),
                        "-vf", f"crop={cw}:{ch}:{x0}:{y0},scale=1920:1080:flags=lanczos,{draw},format=yuv420p",
                        "-an", "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "16", str(clip)], check=True)
        segs.append(clip)
    segs += [SCENES / "PromiseScene.mp4", SCENES / "ProgressScene.mp4", SCENES / "OutroScene.mp4"]

    # 2. cross-fade everything into one picture track
    durs = [dur(s) for s in segs]
    starts, t = [0.0], 0.0
    for d in durs[:-1]:
        t += d - XF
        starts.append(t)
    total = starts[-1] + durs[-1]
    parts = [f"[{i}:v]settb=AVTB,fps=30,format=yuv420p[s{i}]" for i in range(len(segs))]   # xfade needs equal timebases
    prev = "[s0]"
    for i in range(1, len(segs)):
        nxt = f"[v{i}]" if i < len(segs) - 1 else "[v]"
        parts.append(f"{prev}[s{i}]xfade=transition=fade:duration={XF}:offset={starts[i]:.3f}{nxt}")
        prev = nxt
    pad = max(0.0, TARGET - total)                               # scene lengths round to whole frames: hold the outro
    parts.append(f"[v]tpad=stop_mode=clone:stop_duration={pad:.3f}[vp]")
    total += pad
    inputs = sum((["-i", str(s)] for s in segs), [])
    silent = tmp / "picture.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(parts), "-map", "[vp]",
                    "-r", "30", "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", str(silent)], check=True)
    print(f"picture: {total:.2f} s, cuts at " + ", ".join(f"{s:.1f}" for s in starts))

    # 3. sound: the original track, faded, plus a whoosh on each cut, pops on each reveal, a chime on the outro
    music_wav = tmp / "music.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(ROOT / "music" / "branding-upbeat.mp3"), "-ac", "2",
                    "-ar", str(pr.SR), "-t", f"{total:.3f}", "-af", f"afade=t=in:d=0.6,afade=t=out:st={total - 2.5:.2f}:d=2.5",
                    str(music_wav)], check=True)
    music, _ = sf.read(music_wav, dtype="float32")
    events = [(s + XF / 2, "whoosh") for s in starts[1:]]
    i_promise, i_progress, i_outro = starts[-3], starts[-2], starts[-1]
    events += [(i_promise + 1.2 + 1.8 * k, "pop") for k in range(5)]
    events += [(i_progress + 1.0 + 1.6 * k, "pop") for k in range(3)] + [(i_progress + 5.8, "pop")]
    events += [(i_outro + 2.2, "chime")]
    sfx = pr.sfx_track(events, total) * 10 ** (8 / 20)          # louder than under narration: nothing else is talking
    n = len(music)
    mixed = music * 10 ** (-6 / 20)
    mixed[:, 0] += sfx[:n]
    mixed[:, 1] += sfx[:n]
    mix_wav = tmp / "mix.wav"
    sf.write(mix_wav, mixed, pr.SR)

    # 4. final: loudness-normalised to the YouTube / LinkedIn standard
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(mix_wav),
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", str(out)], check=True)
    print(f"Promo: {out} ({dur(out):.2f} s)")


if __name__ == "__main__":
    main()
