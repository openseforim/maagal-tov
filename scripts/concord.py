"""Concordance: each hit of a regex in the English, with part, paragraph number and context.

Usage: py -3.13 scripts/concord.py "R\\. Moses(?! \\w)" [width]
Not used by the build; a helper for data/index/entities.json.
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_site import read_blocks  # noqa: E402

rx = re.compile(sys.argv[1])
w = int(sys.argv[2]) if len(sys.argv) > 2 else 90
n = 0
for f in sorted((ROOT / "data" / "en").glob("part-*.en.txt")):
    part = int(f.name[5:7])
    for i, b in enumerate(read_blocks(f)):
        for m in rx.finditer(b):
            s, t = max(0, m.start() - w), m.end() + w
            print(f"{part}.{i}\t…{b[s:t]}…")
            n += 1
print(f"[{n} hits]")
