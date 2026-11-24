"""Line images from any page image (grey or colour), using split_lines' line finder.
  py -3.13 -I scripts/split_image.py IMAGE OUTDIR [SCALE]   (Otsu threshold; SCALE default 1)"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).parent))
import split_lines as S  # noqa: E402

def otsu(a):
    h = np.bincount(a.ravel(), minlength=256).astype(float)
    p = h / h.sum(); w = np.cumsum(p); m = np.cumsum(p * np.arange(256)); mt = m[-1]
    s = (mt * w - m) ** 2 / (w * (1 - w) + 1e-9)
    return int(np.argmax(s))

def paper_crop(im):
    """Keep the light paper area: the longest run of columns (rows) whose mean is light, then cut a further
    2% to drop the shadowed page edge."""
    a = np.asarray(im)
    dark = a < 110
    def span(frac):
        light = frac < 0.4
        best, cur, start = (0, len(frac)), 0, 0
        bl = 0
        for i, v in enumerate(list(light) + [False]):
            if v:
                if cur == 0:
                    start = i
                cur += 1
            else:
                if cur > bl:
                    bl, best = cur, (start, i)
                cur = 0
        return best
    x0, x1 = span(dark.mean(0)); y0, y1 = span(dark.mean(1))
    dx, dy = int(0.02 * (x1 - x0)), int(0.01 * (y1 - y0))
    return im.crop((x0 + dx, y0 + dy, x1 - dx, y1 - dy))


def run(img, out, scale=1.0, autocrop=False):
    im = Image.open(img).convert("L")
    if autocrop:
        im = paper_crop(im)
    if scale != 1:
        im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    a = np.asarray(im)
    thr = otsu(a)
    ink = a < (thr if thr >= 20 else 128)   # 1-bit images: Otsu is undefined
    lines, med = S.find_lines(ink)
    exts = [S.x_extent(ink[x:y], med) for x, y in lines]
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    for f in out.glob("*.png"):
        f.unlink()
    prev = im.convert("RGB"); dr = ImageDraw.Draw(prev); k = 0
    for (y0, y1), e in zip(lines, exts):
        if not e:
            continue
        k += 1
        pad_y, pad_x = int(0.12 * med), int(0.5 * med)
        box = (max(0, e[0] - pad_x), max(0, y0 - pad_y), min(im.width, e[1] + pad_x), min(im.height, y1 + pad_y))
        im.crop(box).save(out / f"{k:02d}.png")
        dr.rectangle(box, outline=(255, 0, 0), width=3)
    prev.resize((prev.width // 3, prev.height // 3)).save(out.parent / f"{out.name}_boxes.png")
    return k, med

if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if x != "--autocrop"]
    k, med = run(a[0], a[1], float(a[2]) if len(a) > 2 else 1.0, "--autocrop" in sys.argv)
    print(f"{k} lines, line height {med}px")
