#!/usr/bin/env python3
"""Lay the narration over the screen recording: python3 lab/mix_lab.py <rec dir> <voice dir> <out.mp4> [--music]

rec dir holds marks.json (from driver.js) and the .webm; voice dir holds NN.wav. The recording starts with a black
stretch; the first non-black frame is the title card, which is where the driver's clock started.
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np, soundfile as sf

rec, voice, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
m = json.loads((rec / "marks.json").read_text())
video = m["video"]
# find the 6-px marker flashes (one per narration line) in the video: exact times, immune to recording drift
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", video, "-vf", "crop=6:6:0:0,scale=1:1", "-r", "50",
                      "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
lum = np.frombuffer(raw, dtype=np.uint8)
on = lum > 160
flashes = [i / 50 for i in range(1, len(on)) if on[i] and not on[i - 1]]
print(f"{len(flashes)} marker flashes found for {len(m['marks'])} lines")
if len(flashes) == len(m["marks"]):
    starts = {n: t for (n, _), t in zip(m["marks"], flashes)}
else:                                                     # fall back to wall-clock after the leading black
    bd = subprocess.run(["ffmpeg", "-i", video, "-vf", "blackdetect=d=0.3:pix_th=0.05", "-an", "-f", "null", "-"],
                        capture_output=True, text=True).stderr
    t0 = next((float(l.split("black_end:")[1].split()[0]) for l in bd.splitlines() if "black_start:0" in l), 0.0)
    starts = {n: t0 + ms / 1000 for n, ms in m["marks"]}
    print(f"WARNING: using wall-clock times from {t0:.2f}s")
vdur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                            capture_output=True, text=True).stdout)
SR = 48000
mix = np.zeros(int((vdur + 1.0) * SR), dtype=np.float32)
for n, _ in m["marks"]:
    y, sr = sf.read(voice / f"{n:02d}.wav", dtype="float32")
    if y.ndim > 1:
        y = y.mean(axis=1)
    if sr != SR:
        y = np.interp(np.arange(0, len(y), sr / SR), np.arange(len(y)), y).astype(np.float32)
    at = int(starts[n] * SR)
    mix[at:at + len(y)] += y[:len(mix) - at]
narr = rec / "narration.wav"
sf.write(narr, mix, SR)
cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", str(narr),
       "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", "30", "-pix_fmt", "yuv420p",
       "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(out)]
subprocess.run(cmd, check=True)
print("wrote", out)
