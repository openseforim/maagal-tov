"""Word error rate of OCR text against a hand transcription (data/gt/sNNN.gt.txt).
  py -3.13 -I scripts/eval_gt.py DIR [DIR2 ...] [--page 30] [--show]
GT words ending in '?' are uncertain and not scored. OCR lines are matched to GT by best line alignment; the
running head and footnotes (lines not in the GT) are ignored. Footnote-call digits and margin numbers are removed."""
import difflib
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1] / "data"


def norm(w):
    w = w.replace("״", '"').replace("׳", "'").replace("”", '"').replace("“", '"')
    w = re.sub(r"(?<=[א-ת'\"])\d+$", "", w)       # footnote call after a word: הנז'3
    w = re.sub(r"^\d+(?=[א-ת])", "", w)           # before a word
    return w


def words(line):
    ws = [norm(w) for w in line.split()]
    return [w for w in ws if w and not re.fullmatch(r"\d{1,2}", w) or w and re.fullmatch(r"\d+\.", w)]


def score(ocr_lines, gt_lines, show=False):
    gt_words = [w for l in gt_lines for w in l.split()]
    gt_clean = [w.rstrip("?") for w in gt_words]
    # take the OCR lines that look like GT lines (drop head and footnotes): best match per GT line
    ocr_words = []
    used = 0
    for g in gt_lines:
        best, bi = 0, None
        for i in range(used, min(len(ocr_lines), used + 4)):
            r = difflib.SequenceMatcher(None, g, ocr_lines[i]).ratio()
            if r > best:
                best, bi = r, i
        if bi is not None and best > 0.4:
            ocr_words += words(ocr_lines[bi])
            used = bi + 1
    sm = difflib.SequenceMatcher(None, gt_clean, ocr_words, autojunk=False)
    scored = sum(1 for w in gt_words if not w.endswith("?"))
    err = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        gt_part = [gt_words[i] for i in range(i1, i2) if not gt_words[i].endswith("?")]
        n = max(len(gt_part), 0 if i2 > i1 else j2 - j1)
        if tag == "replace":
            n = max(len(gt_part), 0)
        err += n
        if show and n:
            print(f"   GT: {' '.join(gt_words[i1:i2])}  |  OCR: {' '.join(ocr_words[j1:j2])}")
    return err, scored


if __name__ == "__main__":
    a = sys.argv[1:]
    show = "--show" in a
    a = [x for x in a if x != "--show"]
    page = 30
    if "--page" in a:
        i = a.index("--page"); page = int(a[i + 1]); del a[i:i + 2]
    gt = (ROOT / "gt" / f"s{page:03d}.gt.txt").read_text(encoding="utf-8").splitlines()
    for d in a:
        p = ROOT / d / f"s{page:03d}.txt" if (ROOT / d).is_dir() else Path(d)
        ocr = p.read_text(encoding="utf-8").splitlines()
        if show:
            print(f"== {d}")
        e, n = score(ocr, gt, show)
        print(f"{d}: {e} word errors in {n} scored words = WER {100 * e / n:.1f}%")
