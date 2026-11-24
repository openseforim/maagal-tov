"""Build the Ma'agal Tov reader (local): docs/part-NN.html for each translated part, docs/index.html, docs/work.json.

  py -3.13 -I scripts/build_site.py

Hebrew: proofread pages data/he/sNNNN.txt of the 1885 printing, split into paragraphs by scripts/paragraphs.py.
English: data/en/part-NN.en.txt, one paragraph for each Hebrew paragraph, a blank line between paragraphs;
⚠n marks an uncertain rendering, explained in data/en/part-NN.notes.json. Parts take the paragraphs in order:
part 1 the first k1 paragraphs, part 2 the next k2, and so on (k = the English paragraph count).
The script stops if a part has more English paragraphs than there are Hebrew paragraphs left."""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from paragraphs import PAGE, paragraphs  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
e = html.escape
IA = "https://archive.org/details/maagaltob00azul/page/n{}/mode/1up"


def vnum(image_no):
    """Scan number as the archive.org viewer counts it. The viewer leaves out image 0000 (and two images at the end),
    so viewer page nK shows image file K+1; data files keep the image-file numbers (sNNNN = image NNNN)."""
    return image_no - 1


def ia(image_no):
    return IA.format(vnum(image_no))

# part number -> (title, subtitle, scan range shown in the index)
PARTS = {
    1: ("Tunis, Livorno and Pisa",
        "News of his wife's death, kept secret; sermons and a question about Freemasons in Tunis; the voyage to Livorno, "
        "the lazaretto, and Pisa",
        "8–12"),
    2: ("Florence, Ancona and Venice",
        "Collecting in Florence; Livorno and Ancona, 1775; quarrels reported from Jerusalem; the sights of Venice, the "
        "Arsenal and the Bragadin press, autumn 1776",
        "12–18"),
    3: ("Venice, Modena, Reggio and Mantua",
        "Winter in Venice, 1776-77: the council, the ghetto wine, circumcisions and friends; manuscripts in Modena and "
        "early prints in Reggio; the graves of the Mantuan kabbalists; leaving for Avignon, summer 1777",
        "19–23"),
    4: ("Avignon, Trieste and Paris",
        "A hard day in Avignon, summer 1777; Trieste in the winter of 1777; illness; Paris in December 1777: the city, "
        "a learned gentile of the Academy, and the generosity of the Jews of Avignon",
        "24–28"),
}

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif:ital,wght@0,400;0,600;1,400&family=Noto+Serif+Hebrew:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
<link rel="stylesheet" href="/assets/os.css">
<script src="/assets/os.js" defer></script>
</head>
<body>
"""


def read_blocks(path):
    blocks, cur = [], []
    for raw in path.read_text(encoding="utf-8").split("\n"):
        line = raw.strip()
        if line:
            cur.append(line)
        elif cur:
            blocks.append(" ".join(cur))
            cur = []
    if cur:
        blocks.append(" ".join(cur))
    return blocks


def fmt_en(text):
    text = e(text, quote=False)
    text = re.sub(r"\[([^\]]+)\]", r'<span class="ref">[\1]</span>', text)
    return re.sub(r"\s*⚠(\d+)", r' <a class="warn" href="#n\1" id="r\1" title="uncertain rendering">⚠\1</a>', text)


def fmt_he(text):
    out = e(text, quote=False)
    return PAGE.sub(lambda m: f'<a class="scanlink" href="{ia(int(m.group(1)))}" title="Scan {vnum(int(m.group(1)))} on archive.org" '
                              f'data-scan-img="scans/s{int(m.group(1)):04d}.jpg" data-scan-label="Scan {vnum(int(m.group(1)))}">'
                              f'scan {vnum(int(m.group(1)))}</a>', out)


BOOK = "https://archive.org/details/maagaltob00azul"


def shown(rng):
    """An image-file range such as "8–12", in the viewer's numbering."""
    a, b = (int(x) for x in rng.replace("–", "-").split("-"))
    return f"{vnum(a)}–{vnum(b)}"


def scan_bar(scans):
    """The page scans of this part, as a row of links, and the whole book."""
    first, last = (int(x) for x in scans.replace("–", "-").split("-"))
    links = " ".join(f'<a href="{ia(n)}" rel="noopener">{vnum(n)}</a>' for n in range(first, last + 1))
    return (f'<p class="scanbar"><span class="lbl">Page scans</span> <span class="pages">{links}</span> '
            f'<a class="book" href="{BOOK}" rel="noopener">The whole book on archive.org ↗</a> '
            f'<label class="scantoggle"><input type="checkbox" class="os-scan-toggle"> Show the scan beside the text</label></p>')


def part_page(num, he_paras, start_no, para_pages):
    title, subtitle, scans = PARTS[num]
    en = read_blocks(ROOT / "data" / "en" / f"part-{num:02d}.en.txt")
    notes = json.loads((ROOT / "data" / "en" / f"part-{num:02d}.notes.json").read_text(encoding="utf-8"))
    rows = []
    for i, (h, x) in enumerate(zip(he_paras, en)):
        n = start_no + i
        missing = [pg for pg in para_pages[i] if not (DOCS / "scans" / f"s{pg:04d}.jpg").exists()]
        if missing:
            sys.exit(f"part {num}: no panel image for image files {missing}; run scripts/make_scans.py")
        sc = " ".join(f"{pg}:{vnum(pg)}" for pg in para_pages[i])  # image file : viewer number
        vs = [vnum(pg) for pg in para_pages[i]]
        lab = f'paragraph {n}, ' + (f'scan {vs[0]}' if len(vs) == 1 else f'scans {vs[0]}–{vs[-1]}')
        rows.append(f'<div class="row" id="p{n}" data-scans="{sc}" data-label="{lab}"><a class="ln" href="#p{n}">{n}</a>'
                    f'<p class="en">{fmt_en(x)}</p>'
                    f'<p class="he" lang="he" dir="rtl">{fmt_he(h)}</p></div>')
    marks = set(re.findall(r"⚠(\d+)", " ".join(en)))
    missing = marks - set(notes)
    if missing:
        sys.exit(f"part {num}: notes missing for ⚠{sorted(missing)}")
    note_rows = "\n".join(
        f'<li id="n{k}"><a href="#r{k}">⚠{k}</a> <span lang="he" dir="rtl" class="he-inline">{e(v["he"])}</span>'
        f' — {e(v["note"], quote=False)}</li>' for k, v in notes.items())
    keys = sorted(PARTS)
    i = keys.index(num)
    prev = f'<a href="part-{keys[i - 1]:02d}.html" rel="prev">← Part {keys[i - 1]}</a>' if i > 0 else ""
    nxt = f'<a href="part-{keys[i + 1]:02d}.html" rel="next">Part {keys[i + 1]} →</a>' if i + 1 < len(keys) else ""
    pn = f'<span class="pn">{prev}{nxt}</span>' if prev or nxt else ""
    page = HEAD.format(title=f"{e(title)} — Ḥida, Ma'agal Tov") + f"""<header class="chapter">
<nav class="crumb" aria-label="Parts"><span><a href="index.html">All parts</a> · Part {num}</span>{pn}</nav>
<p class="title-he" lang="he" dir="rtl">מעגל טוב</p>
<h1>{e(title)}</h1>
<p class="sub">{e(subtitle)}</p>
{scan_bar(scans)}
<details class="about"><summary>About this text</summary>
<p class="meta">{len(he_paras)} paragraphs, scans {shown(scans)} of the 1885 printing (numbered as in the archive.org viewer). One row is one paragraph of the print, which ends
each entry with a colon. Boxes marked "scan N" in the Hebrew show where a scan page begins; each links to that page on
archive.org, as do the page numbers under the title. References in <span class="ref">[gray brackets]</span> are the translator's: identifications of biblical phrases, and the civil dates of the Ḥida's dates. He dates by the weekly Torah reading: "Wednesday of the week of Re'eh" is the Wednesday before the Sabbath on which Re'eh is read (readings of the diaspora). Where the entry gives no year, it is taken from the entries around it.
<a class="warn" href="#notes">⚠</a> marks an uncertain rendering. The Hebrew was checked against the scan line by line;
abbreviations are left as printed.</p>
</details>
</header>
<main class="prose">
{chr(10).join(rows)}
</main>
<footer id="notes">
<h2>Uncertain renderings</h2>
<ul class="notes">
{note_rows}
</ul>
<nav class="crumb foot" aria-label="Parts"><span><a href="index.html">All parts</a></span>{pn}</nav>
</footer>
</body>
</html>
"""
    (DOCS / f"part-{num:02d}.html").write_text(page, encoding="utf-8")
    print(f"wrote docs/part-{num:02d}.html: {len(he_paras)} paragraphs")


def index_page(counts):
    rows = "\n".join(
        f'<tr class="done"><td><a href="part-{k:02d}.html">{k}</a></td><td><a href="part-{k:02d}.html">{e(PARTS[k][0])}</a>: {e(PARTS[k][1])}</td>'
        f'<td><a href="{ia(int(PARTS[k][2].split("–")[0]))}" rel="noopener">{shown(PARTS[k][2])}</a></td><td>{counts[k]} paragraphs</td></tr>' for k in sorted(PARTS))
    page = HEAD.format(title="Ḥida, Ma'agal Tov: Hebrew and English") + f"""<header>
<h1>Ḥida, <i>Ma'agal Tov</i></h1>
<p class="sub">The travel diary of Ḥayyim Yosef David Azulai, with an English translation paragraph by paragraph · <span lang="he" dir="rtl">מעגל טוב</span></p>
<p class="meta">Ḥayyim Yosef David Azulai (the Ḥida, 1724–1806) travelled twice as an emissary of the Jews of Hebron and the
Land of Israel, in the 1750s and the 1770s, through Egypt, Italy, Germany, Holland, France, England and Tunisia. His diary,
<i>Ma'agal Tov</i> ("the good circuit"), records the money he raised, the scholars he argued with, the libraries and courts
he saw, and his own grief and melancholy. It was not printed in his lifetime.</p>
</header>
<article>
<h2>Parts</h2>
<div class="tablewrap">
<table>
<tr><th>Part</th><th>Contents</th><th>Scans</th><th>Status</th></tr>
{rows}
<tr><td>2–</td><td>Florence and on</td><td>12–76</td><td>OCR only, not checked or translated</td></tr>
</table>
</div>
<a class="cta" href="part-01.html">Read part 1, side by side →</a>

<h2>The Hebrew text</h2>
<ul>
<li><b>Base text:</b> the printing of Przemyśl, 1885 (<i>Sefer Ma'agal Tov</i>), which holds part of the second journey,
from Tunis to Italy. Scan: <a href="https://archive.org/details/maagaltob00azul">archive.org, maagaltob00azul</a>
(University of Illinois, 650 ppi). The scan lacks the title page and starts in the middle of a passage.</li>
<li><b>OCR:</b> Kraken with the PP-OCRv6 model, line by line, then checked against the scan by eye. Spelling, abbreviations and
punctuation are as printed.</li>
<li><b>Complete text:</b> A. Freimann's edition, <i>Ma'agal Tov ha-Shalem</i> (Mekize Nirdamim, Berlin 1921 and Jerusalem 1934),
holds both journeys. Its only scan found online (HebrewBooks) is too poor for OCR at present.</li>
</ul>

<h2>Method</h2>
<ul>
<li><b>Rows.</b> One row is one paragraph of the print. The print ends each entry with a colon.</li>
<li><b>English.</b> Plain and close to the Hebrew. Dates by the weekly Torah portion are kept ("Tuesday of the week of Shemini").</li>
<li><b>Uncertain renderings</b> have the mark ⚠ and a note at the end of the page; unresolved abbreviations are left as uncertain.</li>
<li><b>Translator.</b> The translation is by Claude (Anthropic), directed and reviewed by Ezra Brand.</li>
</ul>

<h2>Translations that exist</h2>
<ul>
<li>English: B. Cymerman, <i>The Diaries of Rabbi Ha'im Yosef David Azulai</i> (Jerusalem, 1997), in copyright.</li>
<li>French: <i>Les voyageurs juifs du XVIIIe siècle</i> (1997), in copyright.</li>
</ul>
</article>
</body>
</html>
"""
    (DOCS / "index.html").write_text(page, encoding="utf-8")
    print("wrote docs/index.html")


def work_json():
    w = {
        "schema": 1, "slug": "maagal-tov", "order": 30, "kind": "translation",
        "title": "Ḥida, *Ma'agal Tov*", "short_title": "*Ma'agal Tov*", "title_he": "מעגל טוב",
        "author": "Ḥayyim Yosef David Azulai (1724–1806)",
        "status_label": "In progress · parts 1–4 (scans 7–27 of the 1885 printing)",
        "start": "part-01.html", "start_label": "Part 1, Tunis, Livorno and Pisa",
        "summary": "The Ḥida's travel diary as an emissary of the Land of Israel, with an English translation paragraph by paragraph.",
        "base_edition": {"label": "Przemyśl 1885 printing (partial)", "scan_url": "https://archive.org/details/maagaltob00azul"},
        "method": "Paragraph-aligned Hebrew and English; Hebrew from Kraken OCR checked against the scan.",
        "cite": "Ḥayyim Yosef David Azulai, *Ma'agal Tov*, Hebrew text with English translation, ed. Ezra Brand. Open Seforim",
        "url": "https://openseforim.org/maagal-tov/",
        "repo": "https://github.com/openseforim/maagal-tov",
        "doi": "10.5281/zenodo.24502156",
        "licence": {"name": "CC BY-SA 4.0", "url": "https://creativecommons.org/licenses/by-sa/4.0/"},
    }
    (DOCS / "work.json").write_text(json.dumps(w, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    DOCS.mkdir(exist_ok=True)
    he = paragraphs()
    # scan pages of each paragraph: the page it starts on, then any page that begins inside it
    pages, cur = [], None
    for p in he:
        toks = [int(t) for t in PAGE.findall(p)]
        start = toks[0] if p.startswith("{p") else cur
        pp = [start] + [t for t in toks if t != start]
        pages.append([x for x in pp if x is not None])
        cur = toks[-1] if toks else cur
    counts, pos = {}, 0
    for num in sorted(PARTS):
        k = len(read_blocks(ROOT / "data" / "en" / f"part-{num:02d}.en.txt"))
        if pos + k > len(he):
            sys.exit(f"part {num}: {k} English paragraphs, only {len(he) - pos} Hebrew paragraphs left")
        part_page(num, he[pos:pos + k], pos + 1, pages[pos:pos + k])
        counts[num] = k
        pos += k
    index_page(counts)
    work_json()


if __name__ == "__main__":
    main()
    import subprocess
    tool = ROOT.parent / "openseforim-site" / "tools" / "postbuild.py"
    if tool.exists():
        subprocess.run([sys.executable, str(tool), "maagal-tov", str(DOCS)], check=False)
