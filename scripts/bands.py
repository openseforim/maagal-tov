"""Horizontal bands of one page of the 1885 scan, for checking the OCR by eye (about 5 lines a band).
  py -3.13 -I scripts/bands.py 40 OUTDIR [N_BANDS]    (image-file number; default 5 bands, 15% overlap)
Writes OUTDIR/sNNNN_b1.png ... from data/p1885/maagaltob00azul_jp2/, greyscale, 1800 px wide."""
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "p1885" / "maagaltob00azul_jp2"
n = int(sys.argv[1])
out = Path(sys.argv[2])
k = int(sys.argv[3]) if len(sys.argv) > 3 else 5
out.mkdir(parents=True, exist_ok=True)
im = ImageOps.grayscale(Image.open(SRC / f"maagaltob00azul_{n:04d}.jp2"))
w, h = im.size
im = ImageOps.autocontrast(im.crop((int(w * .03), int(h * .035), int(w * .97), int(h * .97))), cutoff=1)
w, h = im.size
step = h / k
for i in range(k):
    top = max(0, int(i * step - step * .15))
    bot = min(h, int((i + 1) * step + step * .15))
    b = im.crop((0, top, w, bot))
    b = b.resize((1800, round(b.height * 1800 / w)), Image.LANCZOS)
    p = out / f"s{n:04d}_b{i + 1}.png"
    b.save(p, optimize=True)
    print(p)
