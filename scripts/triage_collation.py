"""Triage the substantive differences of data/collation/collation.json for checking by eye.

  py -3.13 -I scripts/triage_collation.py

Drops what is almost surely noise (honorifics or small words found in one text only, OCR debris in Freimann, a
one-letter difference where Freimann's form occurs nowhere else in Freimann), and ranks the rest: first the places
where the 1885 printing may be wrong (Freimann's form is common in Freimann, the 1885 form rare in 1885), then
numbers, then words and passages. Writes data/collation/TO_CHECK.md and data/collation/to_check.json."""
import collections
import difflib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from collate_freimann import NOISE, norm, skeleton  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
C = ROOT / "data" / "collation"
SMALL = set(map(norm, "ז\"ל זצ\"ל זלה\"ה יצ\"ו הי\"ו נר\"ו ת\"ו יע\"א הנז' הנז\"ל הנ\"ל ו של את על אל עם כי גם הוא היה "
                      "ה' ב' ג' ד' ה ב ל מ ש כ וכו' בס\"ד בעה\"ר ית' זיע\"א כמה".split()))


def main():
    col = json.loads((C / "collation.json").read_text(encoding="utf-8"))
    fr_words = collections.Counter(norm(w) for l in (C / "freimann_clean.txt").read_text(encoding="utf-8").splitlines()
                                   for w in l.split()[1:])
    he_words = collections.Counter(norm(w) for f in (ROOT / "data" / "he").glob("s*.txt")
                                   for w in f.read_text(encoding="utf-8").split())
    keep, dropped = [], collections.Counter()
    for r in col["paragraphs"]:
        if not r.get("found"):
            continue
        for d in r["diffs"]:
            if d["kind"] in NOISE:
                continue
            a, b = d["1885"], d["freimann"]
            na, nb = [norm(x) for x in a.split() if norm(x)], [norm(x) for x in b.split() if norm(x)]
            if d["kind"] in ("only in 1885", "only in Freimann") and all(x in SMALL for x in na + nb):
                dropped["small word"] += 1
                continue
            if re.search(r"[A-Za-z0-9]|[^א-ת\s'\".,:;()\[\]?!־׳״-]", b):
                dropped["OCR debris in Freimann"] += 1
                continue
            if d["kind"] in ("look-alike letter", "one letter") and fr_words[norm(b)] <= 1 and he_words[norm(a)] >= 2:
                dropped["Freimann OCR (rare form)"] += 1
                continue
            if d["kind"] == "passage" and len(na) == len(nb) and \
                    difflib.SequenceMatcher(None, skeleton(a), skeleton(b)).ratio() > 0.85:
                dropped["near-identical passage"] += 1
                continue
            score = 0
            if len(na) == 1 and len(nb) == 1 and fr_words[nb[0]] >= 3 and he_words[na[0]] <= 1:
                score = 3  # 1885 form rare, Freimann's common: perhaps a misprint in 1885
            elif d["kind"] in ("number/abbreviation", "transposition"):
                score = 2
            elif d["kind"] in ("word", "one letter", "look-alike letter"):
                score = 1
            keep.append(dict(d, part=r["part"], para=r["para"], score=score))
    keep.sort(key=lambda d: (-d["score"], d["part"], int(d["para"]) if d["para"].isdigit() else 0))
    (C / "to_check.json").write_text(json.dumps(keep, ensure_ascii=False, indent=1), encoding="utf-8")
    label = {3: "1885 form rare, Freimann's common", 2: "number or transposition", 1: "word", 0: "passage or omission"}
    L = ["# Differences to check by eye", "", f"{len(keep)} differences after dropping: "
         + ", ".join(f"{k} {v}" for k, v in dropped.items()) + ".", ""]
    for s in (3, 2, 1, 0):
        rows = [d for d in keep if d["score"] == s]
        L += [f"## {label[s]} ({len(rows)})", "", "| Part.para | Kind | 1885 | Freimann | at |", "|---|---|---|---|---|"]
        L += [f"| {d['part']}.{d['para']} | {d['kind']} | {d['1885'] or '—'} | {d['freimann'] or '—'} | {d['at']} |"
              for d in rows]
        L.append("")
    (C / "TO_CHECK.md").write_text("\n".join(L), encoding="utf-8")
    print(f"kept {len(keep)}; dropped {dict(dropped)}; by score {collections.Counter(d['score'] for d in keep)}")


if __name__ == "__main__":
    main()
