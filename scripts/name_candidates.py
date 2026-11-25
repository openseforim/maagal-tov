"""List capitalised word sequences in the English translation, with counts, as candidates for the index.

Usage: py -3.13 scripts/name_candidates.py > data/index/candidates.tsv
Not used by the build; a helper to write data/index/entities.json by hand.
"""
import collections
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
WORD = r"(?:[A-ZḤṬṢŠ][\w'’ḥṭṣšāēīōū\-]*)"
LINK = r"(?:\s(?:de|da|di|del|della|ben|bar|ha|ibn|van|von|le|la|the|of|son of|d'|ha-)\s?)"
RX = re.compile(rf"(?:R\.\s|Signor\s|Rabbi\s|Ḥakham\s|Sir\s|Mr\.?\s|Madame\s)?{WORD}(?:(?:\s|{LINK}){WORD})*")
SKIP = set("I The A An And But On In At We He She They It This That When After Before There His Her My Then So If "
           "Also Today Tomorrow Sunday Monday Tuesday Wednesday Thursday Friday Sabbath God Lord Name Torah".split())

cnt, where = collections.Counter(), collections.defaultdict(set)
for f in sorted((ROOT / "data" / "en").glob("part-*.en.txt")):
    part = int(f.name[5:7])
    for m in RX.finditer(f.read_text(encoding="utf-8")):
        s = m.group(0).strip()
        if s in SKIP or len(s) < 3:
            continue
        cnt[s] += 1
        where[s].add(part)
for s, n in sorted(cnt.items(), key=lambda x: (-x[1], x[0])):
    print(f"{n}\t{','.join(map(str, sorted(where[s])))}\t{s}")
