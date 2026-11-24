"""Page images for the reader's scan panel: docs/scans/sNNNN.jpg (image-file numbers, as data/he/), greyscale,
cropped by fixed margins, 900 px wide, from the archive.org jp2 set in data/p1885/maagaltob00azul_jp2/.
  py -3.13 -I scripts/make_scans.py 8 12        (a range of image-file numbers; existing files are kept)"""
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "p1885" / "maagaltob00azul_jp2"
OUT = ROOT / "docs" / "scans"
OUT.mkdir(parents=True, exist_ok=True)
a, b = int(sys.argv[1]), int(sys.argv[2])
for n in range(a, b + 1):
    out = OUT / f"s{n:04d}.jpg"
    if out.exists():
        continue
    im = ImageOps.grayscale(Image.open(SRC / f"maagaltob00azul_{n:04d}.jp2"))
    w, h = im.size
    im = im.crop((int(w * .03), int(h * .035), int(w * .97), int(h * .97)))  # these scans: paper fills the frame
    im = ImageOps.autocontrast(im, cutoff=1)
    im = im.resize((900, round(im.height * 900 / im.width)), Image.LANCZOS)
    im.save(out, quality=62, optimize=True, progressive=True)
    print(out.name, im.size, f"{out.stat().st_size // 1024} KB")
