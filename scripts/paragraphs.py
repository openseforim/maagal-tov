"""Hebrew paragraphs of the 1885 printing from the proofread pages data/he/sNNNN.txt.
A paragraph ends at a colon (the print's end-of-entry mark). A line that starts with "# " is a heading: it ends the
paragraph before it and is a paragraph of its own (heading lines in a row are joined). A page start is kept as the
token {pNNNN}.
  py -3.13 -I scripts/paragraphs.py         -> prints the paragraphs of the main text with their numbers
  py -3.13 -I scripts/paragraphs.py front   -> the same for the front matter
Imported by build_site.py.

Reading order. The leaves of the scanned copy are bound out of order. Image files 35-38 are the title page, the
publisher's notice and the two prefaces, and 39-40 are the opening of the diary (printed leaf ג); the leaves after 40
are lost, and image 8 takes up the text in Tunis. Image 34 goes on directly to image 41 (catchword אור, leaf יח).
FRONT holds 35-40; MAIN holds the rest of the text in reading order."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = re.compile(r"\{p(\d{4})\}")
FRONT = list(range(35, 41))
MAIN = list(range(8, 35)) + list(range(41, 78))
HEAD = "\u0001"  # marks a heading paragraph inside this module; removed before return


def paragraphs(order=None):
    """Return a list of paragraph strings for the image files in `order` (default MAIN) that have a proofread page.
    A heading paragraph starts with "# "."""
    order = MAIN if order is None else order
    parts = []
    for n in order:
        f = ROOT / "data" / "he" / f"s{n:04d}.txt"
        if not f.exists():
            continue
        out, heads = [], []
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("# "):
                heads.append(line[2:].strip())
                continue
            if heads:
                out.append(f" {HEAD}{' '.join(heads)}{HEAD} ")
                heads = []
            out.append(line)
        if heads:
            out.append(f" {HEAD}{' '.join(heads)}{HEAD} ")
        parts.append(f"{{p{n:04d}}} " + " ".join(out))
    text = " ".join(parts)
    text = re.sub(r"\s+", " ", text).replace(" :", ":")
    # split after each colon, and around each heading
    paras = []
    for chunk in re.split(rf"(?<=:)\s+|\s*({HEAD}[^{HEAD}]*{HEAD})\s*", text):
        if chunk and chunk.strip():
            c = chunk.strip()
            paras.append("# " + c.strip(HEAD).strip() if c.startswith(HEAD) else c)
    # a page token left alone (at the end of a paragraph, or before a heading) belongs to the next paragraph
    merged, carry = [], ""
    for p in paras:
        m = re.search(r"\s*(\{p\d{4}\})$", p)
        if PAGE.fullmatch(p):
            carry = (carry + " " + p).strip()
            continue
        if m:
            p, tok = p[:m.start()], m.group(1)
        else:
            tok = ""
        if carry:
            p = (f"# {carry} " + p[2:]) if p.startswith("# ") else f"{carry} {p}"
            carry = ""
        merged.append(p)
        carry = tok
    if carry and merged:
        merged[-1] += " " + carry
    return merged


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    which = FRONT if sys.argv[1:] == ["front"] else MAIN
    for i, p in enumerate(paragraphs(which), 1):
        print(f"[{i}] {p}\n")
