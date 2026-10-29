#!/usr/bin/env python3
"""python3 lab/durations.py <voice dir> <out.json>: {"01": seconds, ...} from the narration wavs."""
import json, subprocess, sys
from pathlib import Path
voice, out = Path(sys.argv[1]), Path(sys.argv[2])
d = {}
for w in sorted(voice.glob("[0-9][0-9].wav")):
    d[w.stem] = round(float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(w)],
                                           capture_output=True, text=True).stdout), 2)
out.write_text(json.dumps(d, indent=1))
print(d, "total", round(sum(d.values()), 1))
