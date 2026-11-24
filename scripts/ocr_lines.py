"""OCR of the line images from split_lines.py, with Kraken in no-segmentation mode (PP-OCRv6 medium).
  py -3.13 -I scripts/ocr_lines.py FIRST LAST [--variant s1|s2] [--batch PAGES] [--out DIR] [--threads N]
For each scan page NNN: split into lines (if not done), then one Kraken call per batch of pages (the model is
loaded once per call). Writes data/<out>/sNNN.txt (logical order, one line per printed line). Resumable."""
import os
import subprocess
import sys
import time
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).parent))
import split_lines as S  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
KRAKEN = Path(r"C:\Users\ezrab\Ezra Brandt\Claude\syriac-ocr\.venv\Scripts\kraken.exe")
MODEL = Path(r"C:\Users\ezrab\AppData\Local\htrmopo\htrmopo\1980fa54-b49e-5256-95b6-928290bc48f8\medium.safetensors")
ENV = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")

args = sys.argv[1:]
BATCH, OUTNAME, VARIANT, THREADS = 4, None, "s1", 8
if "--variant" in args:
    i = args.index("--variant"); VARIANT = args[i + 1]; del args[i:i + 2]
if "--threads" in args:
    i = args.index("--threads"); THREADS = int(args[i + 1]); del args[i:i + 2]
if "--batch" in args:
    i = args.index("--batch"); BATCH = int(args[i + 1]); del args[i:i + 2]
if "--out" in args:
    i = args.index("--out"); OUTNAME = args[i + 1]; del args[i:i + 2]
S.set_variant(VARIANT)
OUTNAME = OUTNAME or f"ocr_{VARIANT}"
OUT = ROOT / "data" / OUTNAME
OUT.mkdir(parents=True, exist_ok=True)
first, last = int(args[0]), int(args[1])
doc = pymupdf.open(S.PDF)
todo = [n for n in range(first, last + 1) if not (OUT / f"s{n:03d}.txt").exists()]
print(f"{len(todo)} pages to do ({first}-{last}), batch {BATCH}, out data/{OUTNAME}", flush=True)
t_all = time.time()
for k in range(0, len(todo), BATCH):
    pages = todo[k:k + BATCH]
    t = time.time()
    cmd, per_page = [str(KRAKEN), "--threads", str(THREADS)], {}
    for n in pages:
        d = S.OUT / f"s{n:03d}"
        if not d.exists() or not any(d.glob("*.png")):
            try:
                S.split(n, doc)
            except Exception as e:  # noqa: BLE001
                print(f"s{n:03d} SPLIT FAILED: {e}", flush=True)
                continue
        imgs = sorted(d.glob("[0-9][0-9].png"))
        per_page[n] = imgs
        for im in imgs:
            cmd += ["-i", str(im), str(im.with_suffix(".R.txt"))]
    cmd += ["ocr", "-m", str(MODEL), "--no-segmentation", "-B", "16", "--base-dir", "R"]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
    for n, imgs in per_page.items():
        if not imgs:
            (OUT / f"s{n:03d}.txt").write_text("", encoding="utf-8")
            print(f"s{n:03d} blank page", flush=True)
            continue
        lines, missing = [], 0
        for im in imgs:
            f = im.with_suffix(".R.txt")
            if f.exists():
                lines.append(f.read_text(encoding="utf-8").strip())  # --base-dir R: already logical order
            else:
                lines.append("")
                missing += 1
        if missing == len(imgs):
            print(f"s{n:03d} FAILED (rc {r.returncode}): {r.stderr[-300:]}", flush=True)
            continue
        (OUT / f"s{n:03d}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"s{n:03d} ok {len(imgs)} lines{f', {missing} missing' if missing else ''}", flush=True)
    done = k + len(pages)
    rate = (time.time() - t_all) / done
    print(f"  batch {time.time() - t:.0f}s; {done}/{len(todo)} pages; about {rate * (len(todo) - done) / 60:.0f} min left", flush=True)
print("finished", flush=True)
