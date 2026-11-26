#!/usr/bin/env python3
"""Cut the native vertical promo: nine scenes on hard cuts, narration, burned-in word captions, the original
track ducked under the voice (side-chain), the series' effects on the cuts and word punches.

    python3 videos/brand/short2_build.py
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
from short_build import ass_time, captions, chunk_words, dur  # noqa: E402  (same caption format as the first cut)

PROJ = ROOT / "projects" / "branding"
SCENES = PROJ / "build-short2" / "videos" / "short2" / "1920p30"
VOICE = PROJ / "voice-short"
ORDER = ["HookScene", "ProblemScene", "StepBacktrack", "StepBranch", "StepTSP", "StepNP", "StepApprox", "PromiseScene", "CTAScene"]
BAR = 60 / 104 * 4
GAP = 0.12
CAPTION = {"s3": "TSP."}                    # spoken as letters, written as the word


def half_bars(seconds, at_least):
    """Scene length in bars, on half-bar cuts, long enough for its narration plus a breath."""
    import math
    return max(at_least, math.ceil((seconds + 0.5) / (BAR / 2)) / 2)


def vdur(key):
    return json.load(open(VOICE / f"{key}.json"))["seconds"]


BARS = [half_bars(vdur("hook") + 0.3, 2.5), half_bars(vdur("problem") + 0.2, 2.5), 1, 1, 1, 1, 1,
        half_bars(vdur("promise") + 0.2, 2), half_bars(vdur("cta") + 0.2, 1.5)]
TARGET = round(sum(BARS) * BAR, 3)


def main():
    out = PROJ / "output" / "daa-series-short-30s.mp4"
    tmp = PROJ / "output" / "tmp-short2"
    tmp.mkdir(parents=True, exist_ok=True)

    # 1. every scene trimmed to its exact bar count, then hard-cut together
    cuts, t = [], 0.0
    lst = tmp / "list.txt"
    lines = []
    for name, bars in zip(ORDER, BARS):
        seg = tmp / f"{name}.mp4"
        length = bars * BAR
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(SCENES / f"{name}.mp4"), "-t", f"{length:.4f}",
                        "-vf", f"tpad=stop_mode=clone:stop_duration=1,trim=duration={length:.4f},setpts=PTS-STARTPTS,fps=30,format=yuv420p",
                        "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "15", str(seg)], check=True)
        lines.append(f"file '{seg.resolve()}'")
        cuts.append(t)
        t += length
    lst.write_text("\n".join(lines) + "\n")
    picture = tmp / "picture.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-vf", f"tpad=stop_mode=clone:stop_duration=1,trim=duration={TARGET},setpts=PTS-STARTPTS",
                    "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", str(picture)], check=True)
    total = dur(picture)
    print(f"bars {BARS}; picture {total:.2f} s, cuts at " + ", ".join(f"{c:.2f}" for c in cuts))

    # 2. narration on the timeline + caption cues from its word timings
    n = int(TARGET * pr.SR)
    voice = np.zeros(n, dtype="float32")
    plan = [("hook", 0.3), ("problem", cuts[1] + 0.1), ("s1", cuts[2] + 0.05), ("s2", cuts[3] + 0.05), ("s3", cuts[4] + 0.05),
            ("s4", cuts[5] + 0.05), ("s5", cuts[6] + 0.05), ("s6", cuts[6] + 1.0), ("promise", cuts[7] + 0.15), ("cta", cuts[8] + 0.1)]
    cues, prev_end = [], 0.0
    for key, planned in plan:
        y, sr = sf.read(VOICE / f"{key}.wav", dtype="float32")
        meta = json.load(open(VOICE / f"{key}.json"))
        t0 = max(planned, prev_end + GAP)
        i0 = int(t0 * sr)
        voice[i0:i0 + len(y)] += y[:max(0, n - i0)]
        prev_end = t0 + len(y) / sr
        words = [(w, a + t0, b + t0) for w, a, b in meta["words"]]
        if key in CAPTION:
            words = [(CAPTION[key], words[0][1], words[-1][2])]
        cues += chunk_words(words)
        print(f"voice {key:8s} {t0:5.2f} -> {prev_end:5.2f} s")
    assert prev_end <= TARGET - 0.1, f"narration runs to {prev_end:.1f} s"
    cues.sort()
    cues = [(a, min(b, cues[i + 1][0] - 0.04) if i + 1 < len(cues) else b, tx) for i, (a, b, tx) in enumerate(cues)]
    voice = voice / (np.abs(voice).max() + 1e-9) * 10 ** (-2 / 20)
    ass = tmp / "captions.ass"
    captions(cues, ass)

    # 3. effects: a whoosh on every cut, pops on the word punches, the stamp, the button
    beat = BAR / 4
    events = [(c, "whoosh") for c in cuts[1:]]
    events += [(beat, "pop"), (3 * beat, "pop"), (5 * beat, "pop"), (7 * beat, "kill")]
    p = cuts[1]
    events += [(p, "pop"), (p + 0.25, "pop"), (p + beat, "pop"), (p + BAR + beat + 0.12, "pop"), (p + BAR + 3 * beat, "pop")]
    for c in cuts[2:7]:
        events.append((c + 0.02, "pop"))
    q = cuts[7]
    events += [(q, "pop"), (q + beat, "pop"), (q + 2 * beat, "pop"), (q + BAR, "place"), (q + BAR + 2 * beat, "pop")]
    r = cuts[8]
    events += [(r, "pop"), (r + 0.3, "pop"), (r + 2 * beat, "chime")]
    sfx = pr.sfx_track(events, TARGET)[:n] * 10 ** (5 / 20)
    fg = np.column_stack([voice + sfx, voice + sfx]).astype("float32")
    fg_wav, voice_wav = tmp / "fg.wav", tmp / "voice.wav"
    sf.write(fg_wav, fg, pr.SR)
    sf.write(voice_wav, voice, pr.SR)
    end = min(TARGET, max(cuts[-1] + 1.5 * BAR, prev_end + 0.7))     # no dead tail after the last line
    music_wav = tmp / "music.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(ROOT / "music" / "branding-upbeat.mp3"), "-ac", "2", "-ar", str(pr.SR),
                    "-t", f"{end:.3f}", "-af", f"volume=-11dB,afade=t=in:d=0.2,afade=t=out:st={end - 1.6:.2f}:d=1.6", str(music_wav)], check=True)

    # 4. final: music ducked by the voice, captions burned in, loudness-normalised
    fc = ("[2:a][1:a]sidechaincompress=threshold=0.02:ratio=9:attack=12:release=320:level_sc=1.5[duck];"
          "[duck][0:a]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(fg_wav), "-i", str(voice_wav), "-i", str(music_wav), "-i", str(picture),
                    "-filter_complex", fc, "-map", "3:v", "-map", "[a]", "-vf", f"subtitles={ass}",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                    "-t", f"{end:.3f}", "-movflags", "+faststart", str(out)], check=True)
    print(f"Short: {out} ({dur(out):.2f} s)")


if __name__ == "__main__":
    main()
