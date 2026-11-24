"""Kraken OCR of Ma'agal Tov (Freimann ed., HebrewBooks 21838), resumable.
  py -3.13 -I scripts/ocr_kraken.py FIRST LAST [WORKERS] [--scale S] [--tag T]
  py -3.13 -I scripts/ocr_kraken.py --list 3,30,120 [WORKERS] [--scale S] [--tag T]
Page image: the PDF's own bitonal image (about 300 dpi), converted to grey and scaled by S (default 2, Lanczos).
Writes data/img/sNNN[_T].png, data/kraken[_T]/sNNN.vis.txt (visual order) and sNNN.txt (logical order).
Skips pages that already have sNNN.txt. Model: PP-OCRv6 medium (as for the Emden reader)."""
import io
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pymupdf
from PIL import Image, ImageFilter

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
PDF = Path(r"C:\Users\ezrab\Ezra Brandt\Claude\openseforim-scans\scans\hida-maagal-tov\hebrewbooks_21838_freimann.pdf")
KRAKEN = Path(r"C:\Users\ezrab\Ezra Brandt\Claude\syriac-ocr\.venv\Scripts\kraken.exe")
MODEL = Path(r"C:\Users\ezrab\AppData\Local\htrmopo\htrmopo\1980fa54-b49e-5256-95b6-928290bc48f8\medium.safetensors")
ENV = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")

args = sys.argv[1:]
SCALE, TAG = 2.0, ""
if "--scale" in args:
    i = args.index("--scale"); SCALE = float(args[i + 1]); del args[i:i + 2]
if "--tag" in args:
    i = args.index("--tag"); TAG = "_" + args[i + 1]; del args[i:i + 2]
IMG, OUT = ROOT / "data" / "img", ROOT / "data" / ("kraken" + TAG)
IMG.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)


def render(n: int) -> Path:
    img = IMG / f"s{n:03d}{TAG}.png"
    if not img.exists():
        d = pymupdf.open(PDF)
        x = d.extract_image(d[n - 1].get_images()[0][0])
        im = Image.open(io.BytesIO(x["image"])).convert("L")
        if SCALE != 1:
            im = im.resize((round(im.width * SCALE), round(im.height * SCALE)), Image.LANCZOS)
            im = im.filter(ImageFilter.GaussianBlur(0.6 * SCALE / 2))  # soften the 1-bit staircase edges
        im.save(img)
    return img


def one(n: int) -> str:
    txt = OUT / f"s{n:03d}.txt"
    if txt.exists():
        return f"s{n:03d} skip"
    vis = OUT / f"s{n:03d}.vis.txt"
    t = time.time()
    try:
        img = render(n)
    except Exception as e:  # noqa: BLE001
        return f"s{n:03d} FAILED render: {e}"
    r = subprocess.run([str(KRAKEN), "-i", str(img), str(vis), "segment", "-bl", "ocr", "-m", str(MODEL)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
    if r.returncode or not vis.exists():
        return f"s{n:03d} FAILED: {r.stderr[-400:]}"
    lines = vis.read_text(encoding="utf-8").splitlines()
    txt.write_text("\n".join(l[::-1] for l in lines) + "\n", encoding="utf-8")
    return f"s{n:03d} ok {time.time() - t:.0f}s {len(lines)} lines"


if __name__ == "__main__":
    if args[0] == "--list":
        pages = [int(x) for x in args[1].split(",") if x]
        w = int(args[2]) if len(args) > 2 else 3
    else:
        a, b = int(args[0]), int(args[1])
        w = int(args[2]) if len(args) > 2 else 3
        pages = list(range(a, b + 1))
    print(f"{len(pages)} pages, {w} workers, scale {SCALE}, out {OUT.name}", flush=True)
    done = 0
    with ThreadPoolExecutor(w) as ex:
        for msg in ex.map(one, pages):
            done += 1
            print(f"{done}/{len(pages)} {msg}", flush=True)
    print("finished", flush=True)
