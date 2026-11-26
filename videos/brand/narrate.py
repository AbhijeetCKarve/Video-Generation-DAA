#!/usr/bin/env python3
"""Narration for the promo in the user's own ElevenLabs voice (one clip per scene, placed by build.py --voice).

The API key is never in this file or on the command line: the session's network proxy injects it into
requests to api.elevenlabs.io. Pass --voice-id for the voice to use.

    python3 videos/brand/narrate.py --voice-id <id> [--model eleven_multilingual_v2]
"""
import argparse
import json
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "projects" / "branding" / "voice"
LINES = {
    "intro": "Design and Analysis of Algorithms, every algorithm step by step.",
    "montage": "Backtracking. Branch and bound. P and NP. Reductions. Approximation algorithms. "
               "Ten lectures, from three point one to four point five, with every step traced on screen.",
    "promise": "Every video keeps the same promise. A real problem first. Every step traced. "
               "Proofs you can write in the exam. A practice question, with a pause. Exam tips.",
    "progress": "Ten lectures are online, with lab demos in C plus plus and Java. Network flow comes next.",
    "outro": "I'm Abhijeet Karve. Watch the full playlist on YouTube. The link is in the post.",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice-id", required=True)
    ap.add_argument("--model", default="eleven_multilingual_v2")
    ap.add_argument("--only", action="append", help="regenerate just this scene key")
    ap.add_argument("--stability", type=float, default=0.5)
    ap.add_argument("--speed", type=float, default=1.0)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    for key, text in LINES.items():
        if args.only and key not in args.only:
            continue
        body = json.dumps({"text": text, "model_id": args.model,
                           "voice_settings": {"stability": args.stability, "similarity_boost": 0.8,
                                              "style": 0.2, "use_speaker_boost": True, "speed": args.speed}}).encode()
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{args.voice_id}?output_format=mp3_44100_128",
            data=body, headers={"xi-api-key": "injected-by-proxy", "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            mp3 = OUT / f"{key}.mp3"
            mp3.write_bytes(r.read())
        wav = OUT / f"{key}.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp3), "-ac", "1", "-ar", "48000",
                        "-af", "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                               "silenceremove=start_periods=1:start_threshold=-45dB,areverse", str(wav)], check=True)
        d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of",
                                           "csv=p=0", str(wav)]).decode())
        (OUT / f"{key}.json").write_text(json.dumps({"text": text, "seconds": round(d, 2), "model": args.model}))
        print(f"{key:9s} {d:5.2f} s  {text}")


if __name__ == "__main__":
    main()
