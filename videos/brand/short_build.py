#!/usr/bin/env python3
"""Cut the 30-second vertical promo (1080x1920, YouTube Shorts / LinkedIn): hook -> problem -> five lesson clips in
motion -> promise -> sign-off, with narration, burned-in word captions, the original track and the series' effects.

    python3 videos/brand/short_build.py
"""
import json
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
SCENES = PROJ / "build-short" / "videos" / "short" / "1920p30"
VOICE = PROJ / "voice-short"
FINAL = Path("/home/user/daa-recordings/final")
FONT = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
W, H = 1080, 1920
XF, CLIP, TARGET = 0.3, 2.6, 30.0
BOX_W, BOX_H, BOX_Y = 1080, 608, 500                  # the 16:9 clip window inside the vertical frame
# (video, start, crop (w,h,x,y) of the 1920x1080 lesson frame, caption, unit)
CLIPS = [("daa-3.2-face", 190, (1600, 900, 300, 165), "BACKTRACKING  ·  8-QUEENS", "III"),
         ("daa-3.4", 170, (1600, 900, 160, 165), "BRANCH & BOUND", "III"),
         ("daa-3.5", 239, (1600, 900, 160, 165), "TSP  ·  REDUCED COST MATRIX", "III"),
         ("daa-4.4", 234, (1600, 900, 160, 165), "NP-COMPLETENESS  ·  3-SAT → CLIQUE", "IV"),
         ("daa-4.5", 206, (1600, 900, 160, 165), "APPROXIMATION  ·  VERTEX COVER", "IV")]
# narration: (clip key, planned start); each line starts at its planned time or 0.25 s after the previous ends
VOICE_PLAN = [("hook", 0.3), ("problem", 4.9), ("clips", 10.0), ("promise", 20.4), ("cta", 25.9)]


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                          str(p)]).decode())


def esc(t):
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def ass_time(t):
    h, m = divmod(t, 3600)
    m, s = divmod(m, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def captions(cues, path):
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter,78,&H00FFFFFF,&H00FFFFFF,&H002A170F,&H80000000,-1,0,0,0,100,100,0,0,1,5,0,2,60,60,230,1
Style: Hot,Inter,78,&H0015CCFA,&H00FFFFFF,&H002A170F,&H80000000,-1,0,0,0,100,100,0,0,1,5,0,2,60,60,230,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    body = "".join(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Cap,,0,0,0,,{t}\n" for a, b, t in cues)
    path.write_text(head + body)


def chunk_words(words, max_words=3, max_span=1.3):
    """[(word, start, end)] -> caption cues of 2-3 words, breaking at punctuation and long gaps."""
    cues, cur = [], []
    for w, a, b in words:
        if cur and (len(cur) >= max_words or a - cur[0][1] > max_span or a - cur[-1][2] > 0.45):
            cues.append(cur)
            cur = []
        cur.append((w, a, b))
        if w[-1] in ".?!":
            cues.append(cur)
            cur = []
    if cur:
        cues.append(cur)
    out = []
    for i, c in enumerate(cues):
        end = cues[i + 1][0][1] - 0.04 if i + 1 < len(cues) else c[-1][2] + 0.6
        out.append((c[0][1], min(end, c[-1][2] + 0.9), " ".join(w for w, _, _ in c).upper()))
    return out


def main():
    out = PROJ / "output" / "daa-series-short-30s.mp4"
    tmp = PROJ / "output" / "tmp-short"
    tmp.mkdir(parents=True, exist_ok=True)

    # 1. lesson clips -> vertical cards: dark canvas, the clip window, a topic chip under it
    segs = [SCENES / "HookScene.mp4", SCENES / "ProblemScene.mp4"]
    for i, (name, start, (cw, ch, x0, y0), cap, unit) in enumerate(CLIPS):
        clip = tmp / f"clip{i}.mp4"
        colour = UNIT_COLORS[unit][1:]
        vf = (f"[0:v]crop={cw}:{ch}:{x0}:{y0},scale={BOX_W}:{BOX_H}:flags=lanczos[c];"
              f"color=c=0x0F172A:s={W}x{H}:r=30:d={CLIP}[bg];[bg][c]overlay=0:{BOX_Y}[v1];"
              f"[v1]drawtext=fontfile={FONT}:text='{esc(cap)}':fontsize=40:fontcolor=white:box=1:boxcolor=0x{colour}@1.0:"
              f"boxborderw=22:x=(w-tw)/2:y={BOX_Y + BOX_H + 56},format=yuv420p[v]")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(start), "-t", str(CLIP), "-i", str(FINAL / f"{name}.mp4"),
                        "-filter_complex", vf, "-map", "[v]", "-an", "-r", "30", "-c:v", "libx264", "-preset", "fast", "-crf", "16",
                        str(clip)], check=True)
        segs.append(clip)
    segs += [SCENES / "PromiseScene.mp4", SCENES / "CTAScene.mp4"]

    # 2. cross-fade into one picture track, padded to exactly 30 s
    durs = [dur(s) for s in segs]
    starts, t = [0.0], 0.0
    for d in durs[:-1]:
        t += d - XF
        starts.append(t)
    total = starts[-1] + durs[-1]
    parts = [f"[{i}:v]settb=AVTB,fps=30,format=yuv420p[s{i}]" for i in range(len(segs))]
    prev = "[s0]"
    for i in range(1, len(segs)):
        nxt = f"[v{i}]" if i < len(segs) - 1 else "[v]"
        parts.append(f"{prev}[s{i}]xfade=transition=fade:duration={XF}:offset={starts[i]:.3f}{nxt}")
        prev = nxt
    pad = max(0.0, TARGET - total)
    parts.append(f"[v]tpad=stop_mode=clone:stop_duration={pad:.3f}[vp]")
    total += pad
    picture = tmp / "picture.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *sum((["-i", str(s)] for s in segs), []), "-filter_complex", ";".join(parts),
                    "-map", "[vp]", "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", str(picture)], check=True)
    print(f"picture {total:.2f} s, cuts at " + ", ".join(f"{s:.1f}" for s in starts))

    # 3. narration placed on the timeline; captions follow the words
    n = int(total * pr.SR) + pr.SR
    voice = np.zeros(n, dtype="float32")
    cues, prev_end = [], 0.0
    for key, planned in VOICE_PLAN:
        y, sr = sf.read(VOICE / f"{key}.wav", dtype="float32")
        meta = json.load(open(VOICE / f"{key}.json"))
        t0 = max(planned, prev_end + 0.25)
        i0 = int(t0 * sr)
        voice[i0:i0 + len(y)] += y[:n - i0]
        prev_end = t0 + len(y) / sr
        cues += chunk_words([(w, a + t0, b + t0) for w, a, b in meta["words"]])
        print(f"voice {key:8s} {t0:5.2f} -> {prev_end:5.2f} s")
    assert prev_end <= total - 0.3, f"narration runs to {prev_end:.1f} s"
    cues.sort()
    cues = [(a, min(b, cues[i + 1][0] - 0.04) if i + 1 < len(cues) else b, t) for i, (a, b, t) in enumerate(cues)]
    voice = voice / (np.abs(voice).max() + 1e-9) * 10 ** (-3 / 20)
    ass = tmp / "captions.ass"
    captions(cues, ass)

    # 4. music + effects, then the final encode with captions burned in
    music_wav = tmp / "music.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(ROOT / "music" / "branding-upbeat.mp3"), "-ac", "2", "-ar", str(pr.SR),
                    "-t", f"{total:.3f}", "-af", f"afade=t=in:d=0.4,afade=t=out:st={total - 2.0:.2f}:d=2.0", str(music_wav)], check=True)
    music, _ = sf.read(music_wav, dtype="float32")
    events = [(s + XF / 2, "whoosh") for s in starts[1:]]
    events += [(0.5, "pop"), (1.5, "pop"), (2.5, "pop"), (3.3, "kill")]                       # hook lines
    events += [(starts[-2] + 0.2, "pop"), (starts[-2] + 1.0, "pop"), (starts[-2] + 1.9, "pop")]  # promise lines
    events += [(starts[-1] + 1.7, "chime")]
    sfx = pr.sfx_track(events, total) * 10 ** (4 / 20)
    m = len(music)
    mixed = music * 10 ** (-20 / 20)
    mixed[:, 0] += sfx[:m] + voice[:m]
    mixed[:, 1] += sfx[:m] + voice[:m]
    mix_wav = tmp / "mix.wav"
    sf.write(mix_wav, mixed, pr.SR)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(picture), "-i", str(mix_wav),
                    "-vf", f"subtitles={ass}", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", str(out)], check=True)
    print(f"Short: {out} ({dur(out):.2f} s)")


if __name__ == "__main__":
    main()
