"""Compare two Kraken runs line by line: py -3.13 -I scripts/compare_runs.py kraken_s1 kraken_s2 30 [120 ...]
Prints the lines that differ and a word-agreement ratio per page."""
import difflib
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1] / "data"
a, b, pages = sys.argv[1], sys.argv[2], [int(x) for x in sys.argv[3:]]
for n in pages:
    la = (ROOT / a / f"s{n:03d}.txt").read_text(encoding="utf-8").splitlines()
    lb = (ROOT / b / f"s{n:03d}.txt").read_text(encoding="utf-8").splitlines()
    wa, wb = " ".join(la).split(), " ".join(lb).split()
    r = difflib.SequenceMatcher(None, wa, wb).ratio()
    print(f"=== s{n:03d}: {a} {len(la)} lines / {len(wa)} words; {b} {len(lb)} lines / {len(wb)} words; word agreement {r:.3f}")
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, wa, wb).get_opcodes():
        if tag != "equal":
            print(f"  {a}: {' '.join(wa[i1:i2])}  |  {b}: {' '.join(wb[j1:j2])}")
