"""Check the full-diary units data/fr/uNN.json against the OCR: lost or doubled text, page tokens, notes.

  py -3.13 -I scripts/fr_check.py

For each paragraph, the Hebrew word count is compared with the OCR words from its start line up to the next
paragraph's start line (collate_freimann.clean_page). A ratio far from 1 means lines are lost or doubled, or a paragraph
boundary is wrong between two units. Also checks that the {fNNN} tokens are the pages after the start page, in order,
and that every ⚠n has a note n."""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_full as F  # noqa: E402
import collate_freimann as C  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")


def main():
    paras = F.load_paras()
    lines = {}
    for p in range(1, 181):
        for ln, t in C.clean_page(p):
            lines[(p, ln)] = len(t.split())
    keys = sorted(lines)
    bad = 0
    for i, p in enumerate(paras):
        a = F.pl(p["start"])
        b = F.pl(paras[i + 1]["start"]) if i + 1 < len(paras) else (181, 0)
        ocr = sum(lines[k] for k in keys if a <= k < b)
        he = len(F.FR_PAGE.sub(" ", p["he"]).split())
        ratio = he / ocr if ocr else 0
        toks = [int(t) for t in F.FR_PAGE.findall(p["he"])]
        exp = list(range(a[0] + 1, b[0] + 1 if b[1] > 1 else b[0]))
        if b[0] == 181:
            exp = toks
        problems = []
        if not 0.8 <= ratio <= 1.25 and abs(he - ocr) > 6:
            problems.append(f"words {he} vs OCR {ocr}")
        if toks != exp:
            problems.append(f"page tokens {toks}, expected {exp}")
        marks = {int(x) for x in re.findall(r"⚠(\d+)", p["en"])}
        if marks != {int(k) for k in p.get("notes", {})}:
            problems.append("notes do not match ⚠ marks")
        if a not in lines:
            problems.append("start line not in the OCR")
        if problems:
            bad += 1
            print(f"u{p['_unit']:02d} {p['start']} (next {b[0]}:{b[1]}): " + "; ".join(problems))
    units = sorted({p["_unit"] for p in paras})
    print(f"{len(paras)} paragraphs in {len(units)} units; {bad} with problems")



def unmatched_lines():
    """Raw OCR lines (before cleaning) whose words are mostly not in the output Hebrew of that page: lines lost by the
    cleaning step or by a unit, or Freimann's Hebrew footnotes (which are left out on purpose).
      py -3.13 -I scripts/fr_check.py lines"""
    paras = F.load_paras()
    words = {}
    for p in paras:
        pg = F.pl(p["start"])[0]
        for chunk in re.split(r"(\{f\d+\})", p["he"]):
            m = F.FR_PAGE.fullmatch(chunk)
            if m:
                pg = int(m.group(1))
                continue
            for w in chunk.split():
                words.setdefault(pg, set()).add(C.norm(w))
    n = 0
    for pg in range(1, 181):
        raw = (C.FR / f"p{pg + 23:03d}.txt").read_text(encoding="utf-8").splitlines()
        have = words.get(pg, set()) | words.get(pg - 1, set()) | words.get(pg + 1, set())
        for i, l in enumerate(raw):
            ws = [C.norm(w) for w in l.split() if len(C.norm(w)) >= 3]
            if len(ws) < 4:
                continue
            hit = sum(1 for w in ws if w in have) / len(ws)
            if hit < 0.4:
                n += 1
                print(f"p{pg} raw line {i + 1} ({hit:.0%}): {l.strip()[:90]}")
    print(f"{n} raw lines not found in the output")


if __name__ == "__main__":
    unmatched_lines() if sys.argv[1:] == ["lines"] else main()
