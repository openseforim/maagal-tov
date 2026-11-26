"""Work units for the full diary (Freimann, Ma'agal Tov ha-Shalem, pp. 1-180): five printed pages per unit.

  py -3.13 -I scripts/fr_units.py            -> writes data/fr/work/uNN/input.txt for all 36 units, and the glossary
  py -3.13 -I scripts/fr_units.py status     -> which units have an output file data/fr/uNN.json

input.txt holds the cleaned OCR lines (running head, footnotes, margin numbers, note numbers and folio marks removed,
see collate_freimann.clean_page) of the unit's pages and of the next page, as "[page:line] text". The page images
are openseforim-scans/kaggle/freimann/pages/freimann/pNNN.jpeg with NNN = printed page + 23.
data/fr/work/ is not committed (it holds Freimann's OCR); the units' output data/fr/uNN.json is."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import collate_freimann as C  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
FR = ROOT / "data" / "fr"
WORK = FR / "work"
IMG = ROOT.parent / "openseforim-scans" / "kaggle" / "freimann" / "pages" / "freimann"
PER = 5
LAST = 180


def units():
    return [(i + 1, a, min(a + PER - 1, LAST)) for i, a in enumerate(range(1, LAST + 1, PER))]


def image(page):
    return IMG / f"p{page + 23:03d}.jpeg"


def write_inputs():
    for u, a, b in units():
        d = WORK / f"u{u:02d}"
        d.mkdir(parents=True, exist_ok=True)
        out = []
        for p in range(a, min(b + 1, LAST) + 1):
            out.append(f"=== page {p} (image {image(p)}){'  [next unit: read only to finish the last paragraph]' if p > b else ''}")
            out += [f"[{p}:{ln}] {t}" for ln, t in C.clean_page(p)]
        (d / "input.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
    ents = json.loads((ROOT / "data" / "index" / "entities.json").read_text(encoding="utf-8"))
    g = ["# Names as the 1885 translation writes them (data/index/entities.json)", ""]
    g += [f"- {x['name']} ({x['type']})" for x in ents]
    (WORK / "glossary.md").write_text("\n".join(g) + "\n", encoding="utf-8")
    print(f"wrote {len(units())} inputs and the glossary in {WORK}")


def status():
    done = [u for u, _, _ in units() if (FR / f"u{u:02d}.json").exists()]
    print(f"{len(done)}/{len(units())} done; missing: {[u for u, _, _ in units() if u not in done]}")


if __name__ == "__main__":
    status() if sys.argv[1:] == ["status"] else write_inputs()
