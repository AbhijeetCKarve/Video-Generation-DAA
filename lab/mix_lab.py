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
# where does the picture start? (end of the leading black)
bd = subprocess.run(["ffmpeg", "-i", video, "-vf", "blackdetect=d=0.3:pix_th=0.05", "-an", "-f", "null", "-"],
                    capture_output=True, text=True).stderr
t0 = 0.0
for line in bd.splitlines():
    if "black_start:0" in line:
        t0 = float(line.split("black_end:")[1].split()[0])
        break
print(f"title card appears at {t0:.2f}s in the recording")
SR = 48000
total = m["total"] / 1000 + t0 + 1.0
mix = np.zeros(int(total * SR), dtype=np.float32)
for n, ms in m["marks"]:
    y, sr = sf.read(voice / f"{n:02d}.wav", dtype="float32")
    if y.ndim > 1:
        y = y.mean(axis=1)
    if sr != SR:
        y = np.interp(np.arange(0, len(y), sr / SR), np.arange(len(y)), y).astype(np.float32)
    at = int((t0 + ms / 1000) * SR)
    mix[at:at + len(y)] += y[:len(mix) - at]
narr = rec / "narration.wav"
sf.write(narr, mix, SR)
cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", str(narr),
       "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", "30", "-pix_fmt", "yuv420p",
       "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(out)]
subprocess.run(cmd, check=True)
print("wrote", out)
