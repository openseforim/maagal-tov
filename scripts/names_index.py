"""Index of people and places: find the names of data/index/entities.json in the English paragraphs.

Each entity has "patterns": a regular expression, or {"rx": ..., "at": [...]} where "at" limits it to
parts ("7") or paragraphs ("7.8" = part 7, paragraph block 8 of data/en/part-07.en.txt). Short forms
such as "R. Moses" mean different people in different parts, so they are limited this way.
Where two patterns overlap, the longer match wins.

Run alone to check the index: py -3.13 scripts/names_index.py
"""
import json
import re
import sys
import unicodedata
from html import escape as e
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTITIES = ROOT / "data" / "index" / "entities.json"
GROUPS = [("family", "The Ḥida and his family"), ("person", "People"),
          ("author", "Earlier rabbis and authors"), ("place", "Places"),
          ("own-work", "The Ḥida's own works"), ("book", "Other books")]
# matches of different classes may overlap: "Tolentino of Ragusa" is a person and a place,
# "the author of Ma'avar Yabbok" an author and a book
CLASS = {"place": "place", "own-work": "book", "book": "book"}


def load():
    ents = json.loads(ENTITIES.read_text(encoding="utf-8"))
    ids = [x["id"] for x in ents]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        sys.exit(f"entities.json: duplicate ids {sorted(dup)}")
    for x in ents:
        x["_rx"] = []
        for p in x["patterns"]:
            rx, at = (p, None) if isinstance(p, str) else (p["rx"], p.get("at"))
            x["_rx"].append((re.compile(rf"(?<![\w']){rx}(?![\w])"), at))
    return ents


def in_scope(at, part, block):
    return at is None or str(part) in at or f"{part}.{block}" in at


def matches(ents, part, b, text):
    """Non-overlapping matches (start, end, id) in one paragraph. Places and names of people are
    resolved apart, so that "Tolentino of Ragusa" is both a person and the place Ragusa."""
    out = []
    for cls in ("person", "place", "book"):
        ms = []
        for x in ents:
            if CLASS.get(x["type"], "person") != cls:
                continue
            for rx, at in x["_rx"]:
                if in_scope(at, part, b):
                    ms += [(m.start(), m.end(), x["id"]) for m in rx.finditer(text)]
        ms.sort(key=lambda m: (m[0], -(m[1] - m[0])))
        end = -1
        for s, t, i in ms:
            if s >= end:
                end = t
                out.append((s, t, i))
    return out


def find(ents, parts):
    """parts: {part number: [English paragraph blocks]}. Returns {entity id: [(part, block)]}."""
    hits = {x["id"]: [] for x in ents}
    for part, blocks in parts.items():
        for b, text in enumerate(blocks):
            for _, _, i in matches(ents, part, b, text):
                if (part, b) not in hits[i]:
                    hits[i].append((part, b))
    return hits


def sortkey(name):
    n = unicodedata.normalize("NFD", name).encode("ascii", "ignore").decode().lower()
    return re.sub(r"^(the |rabbi |r\. )", "", n)


def part_order(p):
    """1885 parts (0-12) first, then the parts of the full diary ("F1", "F2" ...)."""
    return (1, int(p[1:])) if isinstance(p, str) else (0, p)


def part_label(p):
    if isinstance(p, str):
        return f"Full diary {p[1:]}"
    return "Front matter" if p == 0 else f"Part {p}"


def page(ents, hits, anchor):
    """anchor(part, block) -> (href, label). Returns the body HTML of the index page."""
    out, jump = [], []
    for t, lab in GROUPS:
        items = []
        for x in sorted((x for x in ents if x["type"] == t), key=lambda x: sortkey(x["name"])):
            hs = hits[x["id"]]
            if not hs:
                continue
            by_part = {}
            for p, b in hs:
                by_part.setdefault(p, []).append(anchor(p, b))
            links = " · ".join(
                f'<span class="ip">{part_label(p)}: '
                + ", ".join(f'<a href="{h}">{l}</a>' for h, l in v) + "</span>"
                for p, v in sorted(by_part.items(), key=lambda kv: part_order(kv[0])))
            desc = f' <span class="desc">{e(x["desc"])}</span>' if x.get("desc") else ""
            items.append(f'<li id="{x["id"]}"><b>{e(x["name"])}</b>{desc}<div class="hits">{links}</div></li>')
        jump.append(f'<a href="#t-{t}">{lab}</a> ({len(items)})')
        out.append(f'<h2 id="t-{t}">{lab} <span class="cnt">({len(items)})</span></h2>\n<ul class="idx">\n' + "\n".join(items) + "\n</ul>")
    return '<p class="toc">' + " · ".join(jump) + "</p>\n" + "\n".join(out)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.path.insert(0, str(ROOT / "scripts"))
    from build_site import read_blocks
    parts = {int(f.name[5:7]): read_blocks(f) for f in sorted((ROOT / "data" / "en").glob("part-*.en.txt"))}
    ents = load()
    hits = find(ents, parts)
    empty = [x["id"] for x in ents if not hits[x["id"]]]
    print(f"{len(ents)} entities, {sum(len(v) for v in hits.values())} references, {len(empty)} without hits: {empty}")
    # names of people in the text that no entity covers (a check, not a complete list of names)
    name = re.compile(r"(?:R\.|Rabbi|Signor|Signori|Monsieur|Madame|Madam|Mrs|Baron|Comte|Marquis|Marquise) [A-ZḤ][\w'\-]*(?: (?:de |di |of |ben |son of |ha-|ibn )?[A-ZḤ][\w'\-\.]*)*")
    miss = {}
    for part, blocks in parts.items():
        for b, text in enumerate(blocks):
            ms = matches(ents, part, b, text)
            for m in name.finditer(text):
                if not any(s < m.end() and m.start() < t for s, t, _ in ms):
                    miss.setdefault(m.group(0), []).append(f"{part}.{b}")
    print(f"{len(miss)} name forms not covered:")
    for k, v in sorted(miss.items()):
        print(f"  {k}  [{', '.join(v)}]")
