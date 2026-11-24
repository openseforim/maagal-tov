"""Hebrew paragraphs of the 1885 printing from the proofread pages data/he/sNNNN.txt.
A paragraph ends at a colon (the print's end-of-entry mark). A page start is kept as the token {pNNNN}.
  py -3.13 -I scripts/paragraphs.py         -> prints the paragraphs with their numbers
Imported by build_site.py."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = re.compile(r"\{p(\d{4})\}")


def paragraphs(first=None, last=None):
    """Return a list of paragraph strings for pages first..last (default: all proofread pages)."""
    parts = []
    for f in sorted((ROOT / "data" / "he").glob("s*.txt")):
        n = int(f.stem[1:])
        if (first and n < first) or (last and n > last):
            continue
        lines = [l.strip() for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
        parts.append(f"{{p{n:04d}}} " + " ".join(lines))
    text = " ".join(parts)
    text = re.sub(r"\s+", " ", text).replace(" :", ":")
    paras = [p.strip() for p in re.split(r"(?<=:)\s+", text) if p.strip()]
    # a page token alone at the end of a paragraph belongs to the next one
    out = []
    for p in paras:
        if out and PAGE.fullmatch(out[-1].split()[-1] if out[-1].split() else ""):
            pass
        out.append(p)
    fixed = []
    for p in out:
        m = re.search(r"\s*(\{p\d{4}\})$", p)
        if m and fixed is not None:
            p = p[:m.start()]
            fixed.append(p)
            fixed.append(m.group(1))  # placeholder, merged below
        else:
            fixed.append(p)
    merged = []
    for p in fixed:
        if merged and PAGE.fullmatch(merged[-1]):
            merged[-1] = merged[-1] + " " + p
        else:
            merged.append(p)
    return merged


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for i, p in enumerate(paragraphs(), 1):
        print(f"[{i}] {p}\n")
