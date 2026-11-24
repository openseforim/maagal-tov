"""Collect training pairs for ketos: data/gt/sNNN.lines.tsv ('NN<TAB>text', NN = line image number in
data/lines_s1/sNNN/) -> data/train/sNNN_NN.png + .gt.txt. Pages listed in data/gt/VAL are put in data/val/.
  py -3.13 -I scripts/make_train.py"""
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1] / "data"
val_pages = set((ROOT / "gt" / "VAL").read_text().split()) if (ROOT / "gt" / "VAL").exists() else set()
for d in ("train", "val"):
    shutil.rmtree(ROOT / d, ignore_errors=True)
    (ROOT / d).mkdir()
counts = {"train": 0, "val": 0}
for tsv in sorted((ROOT / "gt").glob("s*.lines.tsv")):
    page = tsv.name.split(".")[0]
    dest = "val" if page in val_pages else "train"
    for line in tsv.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        nn, text = line.split("\t", 1)
        src = ROOT / "lines_s1" / page / f"{nn}.png"
        if not src.exists():
            print("missing", src)
            continue
        shutil.copy(src, ROOT / dest / f"{page}_{nn}.png")
        (ROOT / dest / f"{page}_{nn}.gt.txt").write_text(text.strip(), encoding="utf-8")
        counts[dest] += 1
print(counts)
