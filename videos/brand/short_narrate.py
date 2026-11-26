#!/usr/bin/env python3
"""Narration for the 30-second vertical promo, with word timings for burned-in captions.

ElevenLabs returns character-level timings; the API key is injected by the session's proxy, never stored here.
The sign-off name is your own recording (projects/daa-4.5/voice-real/04.wav), not the clone.

    python3 videos/brand/short_narrate.py --voice-id <id>
"""
import argparse
import base64
import json
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "projects" / "branding" / "voice-short"
SR = 48000
SPEED = 1.08          # a touch brisk: promo pace, still natural
LINES = {
    "hook": "Two hundred cities, vans leaving at eight, and no computer can find the best route in time.",
    "problem": "Students don't fail because algorithms are hard, they fail because the textbook skips the steps.",
    "s1": "Backtracking.",
    "s2": "Branch and bound.",
    "s3": "T, S, P.",
    "s4": "NP-completeness.",
    "s5": "Approximation.",
    "s6": "As you'd write it in the exam.",
    "promise": "Ten lectures. Free. Every step, the way the examiner expects.",
    "cta_tail": "Playlist link below.",
}
NAME_SRC, NAME_CUT = ROOT / "projects" / "daa-4.5" / "voice-real" / "04.wav", (1.05, 2.03)   # "I am Abhijeet Karve"


def tts(voice_id, text, model):
    import urllib.request
    settings = {"stability": 0.55, "similarity_boost": 0.8, "speed": SPEED}
    if not model.startswith("eleven_v4"):
        settings.update({"style": 0.2, "use_speaker_boost": True})
    body = json.dumps({"text": text, "model_id": model, "voice_settings": settings}).encode()
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"
                                 "?output_format=mp3_44100_128", data=body,
                                 headers={"xi-api-key": "injected-by-proxy", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        d = json.load(r)
    return base64.b64decode(d["audio_base64"]), d["alignment"]


def words_from(alignment):
    """character timings -> [(word, start, end)]"""
    out, cur, s0 = [], "", None
    for ch, a, b in zip(alignment["characters"], alignment["character_start_times_seconds"],
                        alignment["character_end_times_seconds"]):
        if ch.isspace():
            if cur:
                out.append((cur, s0, prev_end))
            cur, s0 = "", None
        else:
            cur += ch
            s0 = a if s0 is None else s0
            prev_end = b
    if cur:
        out.append((cur, s0, prev_end))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice-id", required=True)
    ap.add_argument("--model", default="eleven_multilingual_v2")
    ap.add_argument("--only", action="append")
    ap.add_argument("--clone-name", action="store_true", help="say the sign-off name with the clone too (no splice)")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    lines = dict(LINES)
    if args.clone_name:
        lines.pop("cta_tail")
        lines["cta"] = "I am Abhijeet Karve. Playlist link below."
    for key, text in lines.items():
        if args.only and key not in args.only:
            continue
        mp3, al = tts(args.voice_id, text, args.model)
        (OUT / f"{key}.mp3").write_bytes(mp3)
        words = words_from(al)
        # trim leading silence so timings start at the first word
        lead = words[0][1]
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{max(0, lead - 0.05):.3f}", "-i", str(OUT / f"{key}.mp3"),
                        "-ac", "1", "-ar", str(SR), "-af", "areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse",
                        str(OUT / f"{key}.wav")], check=True)
        shift = max(0, lead - 0.05)
        words = [(w, round(a - shift, 3), round(b - shift, 3)) for w, a, b in words]
        dur = len(sf.read(OUT / f"{key}.wav")[0]) / SR
        json.dump({"text": text, "seconds": round(dur, 2), "words": words}, open(OUT / f"{key}.json", "w"))
        print(f"{key:9s} {dur:5.2f} s  {text}")
    if not args.clone_name and (not args.only or "cta" in args.only):
        y, sr = sf.read(NAME_SRC, dtype="float32")
        y = y.mean(1) if y.ndim > 1 else y
        a, b = NAME_CUT
        name = y[int(a * sr):int(b * sr)].copy()
        f = int(0.025 * sr)
        name[:f] *= np.linspace(0, 1, f)
        name[-f:] *= np.linspace(1, 0, f)
        tail, _ = sf.read(OUT / "cta_tail.wav", dtype="float32")
        rms = lambda x: float(np.sqrt((x ** 2).mean()))  # noqa: E731
        name *= rms(tail) / rms(name)
        gap = 0.35
        cta = np.concatenate([name, np.zeros(int(gap * sr), dtype="float32"), tail]).astype("float32")
        cta /= max(1.0, np.abs(cta).max() / 0.95)
        sf.write(OUT / "cta.wav", cta, sr)
        off = len(name) / sr + gap
        tw = json.load(open(OUT / "cta_tail.json"))["words"]
        words = [("I", 0.0, 0.25), ("am", 0.25, 0.4), ("Abhijeet", 0.4, 0.7), ("Karve.", 0.7, len(name) / sr)]
        words += [(w, round(s + off, 3), round(e + off, 3)) for w, s, e in tw]
        json.dump({"text": "I am Abhijeet Karve. Playlist link below.", "seconds": round(len(cta) / sr, 2), "words": words},
                  open(OUT / "cta.json", "w"))
        print(f"cta       {len(cta) / sr:5.2f} s  I am Abhijeet Karve (your recording) + tail")


if __name__ == "__main__":
    main()
