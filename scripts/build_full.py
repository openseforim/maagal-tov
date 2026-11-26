"""The full diary: docs/full-NN.html from Freimann's edition (Ma'agal Tov ha-Shalem, pp. 1-180), called by build_site.py.

Input: data/fr/uNN.json (one per unit of five printed pages, see scripts/fr_units.py and data/fr/work/BRIEF.md),
data/fr/parts.json (the part division: the paragraph each part starts with, title, subtitle), and
data/fr/map_1885.json (which Freimann page:line range each 1885 paragraph matches; written from
data/collation/collation.json by scripts/collate_freimann.py's output when that file is present).

Paragraph numbers: "103.2" = the second paragraph that begins on Freimann's p. 103 (anchor #fr103-2). They do not
depend on the part division, so links stay valid when parts are regrouped."""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
FR = ROOT / "data" / "fr"
e = html.escape
FR_SCAN = "https://www.nli.org.il/he/books/NNL_ALEPH990011568950205171/NLI"
FR_PAGE = re.compile(r"\{f(\d{1,3})\}")


def pl(s):
    a, b = s.split(":")
    return int(a), int(b)


def load_paras():
    paras = []
    for f in sorted(FR.glob("u[0-9][0-9].json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        for p in d["paras"]:
            p["_unit"] = d["unit"]
            paras.append(p)
    # a heading the OCR dropped can share its start line with the paragraph after it; the heading comes first
    paras.sort(key=lambda p: (pl(p["start"]), not p.get("head")))
    seen, k = set(), {}
    for p in paras:
        key = (p["start"], bool(p.get("head")))
        if key in seen:
            sys.exit(f"full diary: two paragraphs start at {p['start']}")
        seen.add(key)
        pg = pl(p["start"])[0]
        k[pg] = k.get(pg, 0) + 1
        p["no"] = f"{pg}.{k[pg]}"
        p["anchor"] = f"fr{pg}-{k[pg]}"
    return paras


def map_1885():
    """[(part, para, (from), (to))] for the 1885 paragraphs found in Freimann. Refreshes map_1885.json from the
    local collation when it is there."""
    out = FR / "map_1885.json"
    col = ROOT / "data" / "collation" / "collation.json"
    if col.exists():
        rows = []
        for x in json.loads(col.read_text(encoding="utf-8"))["paragraphs"]:
            if x.get("found") and x.get("freimann"):
                a, b = x["freimann"].split("–")
                rows.append({"part": x["part"], "para": x["para"], "from": a, "to": b})
        out.write_text(json.dumps(rows, ensure_ascii=False, indent=0) + "\n", encoding="utf-8")
    return [(r["part"], r["para"], pl(r["from"]), pl(r["to"])) for r in json.loads(out.read_text(encoding="utf-8"))]


def roman_to_int(s):
    vals = {"i": 1, "v": 5, "x": 10}
    n = 0
    for i, ch in enumerate(s):
        v = vals[ch]
        n += -v if i + 1 < len(s) and vals[s[i + 1]] > v else v
    return n


def href_1885(part, para):
    if part == 0:
        return f"part-00.html#f{roman_to_int(para)}", para
    return f"part-{part:02d}.html#p{para}", str(para)


def fmt_en(text, offset):
    text = e(text, quote=False)
    text = re.sub(r"\[([^\]]+)\]", r'<span class="ref">[\1]</span>', text)
    seen = set()  # one note can be marked at several words; only the first mark gets the back-link id

    def mark(m):
        n = offset + int(m.group(1))
        ident = "" if n in seen else f' id="r{n}"'
        seen.add(n)
        return f' <a class="warn" href="#n{n}"{ident} title="uncertain rendering">⚠{n}</a>'
    return re.sub(r"\s*⚠(\d+)", mark, text)


def fmt_he(text):
    out = e(text, quote=False)
    return FR_PAGE.sub(lambda m: f'<a class="scanlink" href="{FR_SCAN}" rel="noopener" title="Freimann p. {m.group(1)}: '
                       f'the scan is at the National Library of Israel">p. {m.group(1)}</a>', out)


def build(head_html, roman):
    """Write docs/full-NN.html and return (rows for the index page, {(part key, block): (href, label)},
    {1885 (part, para): [(href, label)]} for links back from the 1885 parts, {part key: [English]} for the names index).
    Part keys of the full diary are "F1", "F2" ...; roman is unused (kept for the 1885 builder's signature)."""
    paras = load_paras()
    if not paras:
        return [], {}, {}, {}
    parts = json.loads((FR / "parts.json").read_text(encoding="utf-8"))
    starts = [pl(p["start"]) for p in parts]
    m = map_1885()
    # each Freimann paragraph covers its start up to the next paragraph's start
    for i, p in enumerate(paras):
        a = pl(p["start"])
        b = pl(paras[i + 1]["start"]) if i + 1 < len(paras) else (999, 0)
        p["x1885"] = [(pt, pa) for pt, pa, f, t in m if f < b and t >= a]
    groups = [[] for _ in parts]
    for p in paras:
        k = max(i for i, s in enumerate(starts) if s <= pl(p["start"])) if any(s <= pl(p["start"]) for s in starts) else 0
        groups[k].append(p)
    index_rows, anchors, back, blocks = [], {}, {}, {}
    for i, (part, ps) in enumerate(zip(parts, groups)):
        num = i + 1
        fname = f"full-{num:02d}.html"
        rows, notes, off = [], [], 0
        for b, p in enumerate(ps):
            loc = {int(k): v for k, v in p.get("notes", {}).items()}
            marks = {int(x) for x in re.findall(r"⚠(\d+)", p["en"])}
            if marks != set(loc):
                sys.exit(f"full diary {p['start']}: ⚠ marks {sorted(marks)} but notes {sorted(loc)}")
            for k in sorted(loc):
                notes.append((off + k, loc[k]))
            links = [href_1885(pt, pa) for pt, pa in p["x1885"]]
            x = ""
            if links:
                x = (' <span class="x1885">1885 printing: '
                     + ", ".join(f'<a href="{h}">{lab}</a>' for h, lab in links) + "</span>")
            for pt, pa in p["x1885"]:
                back.setdefault((pt, str(pa)), []).append((f"{fname}#{p['anchor']}", p["no"]))
            head = bool(p.get("head"))
            rows.append(f'<div class="row{" head" if head else ""}" id="{p["anchor"]}" data-label="Freimann p. {p["no"].split(".")[0]}, paragraph {p["no"]}">'
                        f'<a class="ln" href="#{p["anchor"]}">{p["no"]}</a>'
                        f'<p class="en">{fmt_en(p["en"], off)}{x}</p>'
                        f'<p class="he" lang="he" dir="rtl">{fmt_he(p["he"])}</p></div>')
            off += max(loc) if loc else 0
            anchors[(f"F{num}", b)] = (f"{fname}#{p['anchor']}", p["no"])
            blocks.setdefault(f"F{num}", []).append(p["en"])
        first, last = pl(ps[0]["start"])[0], ps[-1]
        last_pg = max([pl(last["start"])[0]] + [int(t) for t in FR_PAGE.findall(last["he"])])
        nm = lambda k: f"Full diary {k}"  # noqa: E731
        prev = f'<a href="full-{num - 1:02d}.html" rel="prev">← {nm(num - 1)}</a>' if num > 1 else ""
        nxt = f'<a href="full-{num + 1:02d}.html" rel="next">{nm(num + 1)} →</a>' if num < len(parts) else ""
        pn = f'<span class="pn">{prev}{nxt}</span>' if prev or nxt else ""
        note_rows = "\n".join(
            f'<li id="n{k}"><a href="#r{k}">⚠{k}</a> <span lang="he" dir="rtl" class="he-inline">{e(v["he"])}</span>'
            f' — {e(v["note"], quote=False)}</li>' for k, v in notes)
        page = head_html.format(title=f"{e(part['title'])} — Ḥida, Ma'agal Tov, the full diary") + f"""<header class="chapter">
<nav class="crumb" aria-label="Parts"><span><a href="index.html">All parts</a> · {nm(num)}</span>{pn}</nav>
<p class="title-he" lang="he" dir="rtl">מעגל טוב השלם</p>
<h1>{e(part['title'])}</h1>
<p class="sub">{e(part['subtitle'])}</p>
<p class="scanbar"><span class="lbl">Freimann, pp. {first}–{last_pg}</span> <a class="book" href="{FR_SCAN}" rel="noopener">The scan at the National Library of Israel ↗</a></p>
<details class="about"><summary>About this text</summary>
<p class="meta">{len(ps)} paragraphs from A. Freimann's edition of the whole diary, <i>Ma'agal Tov ha-Shalem</i> (Berlin 1921,
Jerusalem 1934), pp. {first}–{last_pg}. One row is one paragraph of that edition; the number "103.2" means the second paragraph that
begins on Freimann's p. 103. The Hebrew is the Ḥida's text only: Freimann's notes are left out. It was read by OCR and checked
against the scan line by line; spelling and abbreviations are as printed. Where the 1885 printing has the same entry, the row
links to it ("1885 printing: 55"); that text was edited by the Livorno editors and can differ in wording, order and dates.
References in <span class="ref">[gray brackets]</span> are the translator's: civil dates and biblical references.
<a class="warn" href="#notes">⚠</a> marks an uncertain rendering.</p>
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
<nav class="crumb foot" aria-label="Parts"><span><a href="index.html">All parts</a> · <a href="names.html">Index of people, places and books</a></span>{pn}</nav>
</footer>
</body>
</html>
"""
        (DOCS / fname).write_text(page, encoding="utf-8")
        print(f"wrote docs/{fname}: {len(ps)} paragraphs")
        index_rows.append((num, fname, part, first, last_pg, len(ps)))
    return index_rows, anchors, back, blocks
