"""Collate the 1885 printing (data/he, scripts/paragraphs.py) with Freimann's Ma'agal Tov ha-Shalem (Kraken OCR of
the NLI scan; openseforim-scans/kaggle/freimann-results/out/freimann/text/pNNN.txt, printed page = NNN - 23).

  py -3.13 -I scripts/collate_freimann.py

1. Cleans Freimann: drops the running head and page number, the footnote block, margin line numbers, folio marks
   such as (71b) and note numbers; keeps each word's printed page and line.
2. Finds each 1885 paragraph in Freimann by shared three-word sequences, then diffs it word by word (difflib).
3. Lists the stretches of Freimann that no 1885 paragraph covers (passages the Livorno editors left out).
Writes data/collation/freimann_clean.txt, data/collation/collation.json and data/collation/REPORT.md.
Freimann's OCR has its own errors (in fascicle 2 often ג read as נ), so a difference is a place to check on the
scans, not a correction."""
import collections
import difflib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_site as B  # noqa: E402
import paragraphs as P  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
FR = ROOT.parent / "openseforim-scans" / "kaggle" / "freimann-results" / "out" / "freimann" / "text"
OUT = ROOT / "data" / "collation"
HEB = re.compile(r"[א-ת]")
FINAL = str.maketrans("ךםןףץ", "כמנפצ")
CONFUSABLE = [set(x) for x in ("גנ", "בכ", "הח", "סמ", "וי", "דר", "לצ", "הס", "כנ", "מת", "וז", "טמ")]


def norm(w):
    w = re.sub(r"[^א-ת]", "", w)
    return w.translate(FINAL)


def clean_page(n):
    """Body lines of printed page n as [(line_no, text)]."""
    lines = [l.rstrip() for l in (FR / f"p{n + 23:03d}.txt").read_text(encoding="utf-8").splitlines() if l.strip()]
    body, k = [], 0
    for i, l in enumerate(lines):
        if i < 3 and (re.search(r"(מעגל|מענל|מעגל) טוב|מפתח|הקדמה", l) and len(l) < 30 or re.fullmatch(r"\s*\d{1,3}\s*", l)):
            continue  # running head, page number
        if body and (re.match(r"^\s*\(?1\)", l) or len(re.findall(r"\d{1,2}\)|\(\d{1,2}(?!\d)", l)) >= 2):
            break  # footnote block
        if len(HEB.findall(l)) < 3:
            continue
        k += 1
        l = re.sub(r"^\s*(?:[1-4]?[05])\s+", "", l)          # margin number at the start
        l = re.sub(r"\s+(?:[1-4]?[05])\s*$", "", l)          # or at the end
        l = re.sub(r"\(\s*\d{1,3}\s*[abש6ס8]?\s*\)", " ", l)  # folio marks (71b), often read (716)
        l = re.sub(r"(?<=[א-ת'\".])\d{1,2}\b", "", l)  # note numbers stuck to a word
        l = re.sub(r"\s\d{1,2}(?=\s|$)", " ", l)              # free-standing note numbers
        body.append((k, re.sub(r"\s+", " ", l).strip()))
    return body


def freimann():
    words = []  # (normalized, original, page, line)
    pages = {}
    for n in range(1, 181):
        pages[n] = clean_page(n)
        for ln, l in pages[n]:
            for w in l.split():
                nw = norm(w)
                if nw:
                    words.append((nw, w, n, ln))
    return words, pages


def para_words(text):
    text = re.sub(r"\{p\d{4}\}", " ", text.removeprefix("# "))
    return [(norm(w), w) for w in text.split() if norm(w)]


def locate(pw, idx, nfr):
    """Most likely start position in Freimann for paragraph words pw, by three-word sequences."""
    votes = collections.Counter()
    for i in range(len(pw) - 2):
        key = (pw[i][0], pw[i + 1][0], pw[i + 2][0])
        for pos in idx.get(key, ()):
            votes[(pos - i) // 20] += 1
    if not votes:
        return None, 0
    (bucket, n), = votes.most_common(1)
    return max(0, bucket * 20), n


def skeleton(w):
    """Spelling-blind form: no matres lectionis (ו, י), final א/ה alike, no doubled letters."""
    s = norm(w)
    s = re.sub(r"[אה]$", "א", s)
    s = re.sub(r"(?<=.)[וי]", "", s)
    return re.sub(r"(.)\1", r"\1", s)


def abbreviates(short, full):
    """True if `short` (with ' or ") abbreviates `full` (a word or words), e.g. ישר' ~ ישראל, ר' ~ רבי, כ"י ~ כתיבת יד."""
    if not re.search(r"['\"״׳]", short):
        return False
    s, fw = norm(short), [norm(x) for x in full.split()]
    if len(fw) == 1:
        return bool(s) and fw[0].startswith(s[:max(1, len(s))]) or fw[0].startswith(s.rstrip("א"))
    return "".join(x[:1] for x in fw) == s


def kind(a, b):
    """Class of a difference between the 1885 text (a) and Freimann (b)."""
    if skeleton(a.replace(" ", "")) == skeleton(b.replace(" ", "")):
        return "spelling"
    if abbreviates(a, b) or abbreviates(b, a):
        return "abbreviation"
    if " " in a or " " in b:
        return "passage"
    if any(ch.isdigit() for ch in a + b) or re.search(r"[\"'״׳]", a + b) and len(norm(a)) <= 4 and len(norm(b)) <= 4:
        return "number/abbreviation"
    na, nb = norm(a), norm(b)
    if len(na) == len(nb):
        d = [(x, y) for x, y in zip(na, nb) if x != y]
        if len(d) == 1 and d[0] == ("ג", "נ"):
            return "Freimann OCR ג→נ"
    if len(na) == len(nb):
        diff = [(x, y) for x, y in zip(na, nb) if x != y]
        if len(diff) == 1 and any({diff[0][0], diff[0][1]} <= c for c in CONFUSABLE):
            return "look-alike letter"
        if len(diff) == 1:
            return "one letter"
        if sorted(na) == sorted(nb):
            return "transposition"
    return "word"


MONTHS = "ניסן|אייר|סיון|סיוון|תמוז|אב|אלול|תשרי|חשון|חשוון|כסליו|כסלו|טבת|שבט|אדר"
GEM = dict(zip("אבגדהוזחטיכלמנסעפצקרשת", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 300, 400]))
NOISE = {"spelling", "abbreviation", "Freimann OCR ג→נ"}


def report(results, gaps, nwords, ncovered):
    """data/collation/REPORT.md: what to check on the scans, most important first."""
    found = [r for r in results if r["found"]]
    sub = lambda r: [d for d in r["diffs"] if d["kind"] not in NOISE]  # noqa: E731
    L = ["# Collation: the 1885 printing against Freimann, *Ma'agal Tov ha-Shalem*", "",
         "Made by `scripts/collate_freimann.py` from the proofread 1885 text and the Kraken OCR of Freimann (NLI scan). "
         "References to Freimann are printed page:line. **A difference is a place to check on both scans, not a "
         "correction**: Freimann's OCR has its own errors.", "",
         "## Summary", "",
         f"- 1885 paragraphs: {len(results)}; found in Freimann: {len(found)}. Not found: "
         + ", ".join(f"{r['part']}.{r['para']}" for r in results if not r["found"] and r["words"] >= 4)
         + " (most are the editors' additions: the title page, the notices, Shem Tov, Sefer ha-Zikkaron, the stories).",
         f"- Freimann's text, pp. 1–180: about {nwords:,} words; the 1885 paragraphs cover {ncovered:,} of them. The first "
         "journey (pp. 1–48) is not in the 1885 printing at all.",
         f"- Differences: {sum(len(r['diffs']) for r in found)}, of which {sum(len(sub(r)) for r in found)} are not mere "
         "spelling, abbreviation or Freimann's ג/נ OCR error.", ""]
    dd = [r for r in found if r.get("date_differs")]
    L += ["## 1. Dates that differ", "", "| Part, para | 1885 | Freimann (nearest heading) |", "|---|---|---|"]
    L += [f"| {r['part']}.{r['para']} | {r['date_1885']} | {r['date_freimann']} |" for r in dd]
    od = [r for r in found if r.get("order") or r["agree"] < 0.6]
    L += ["", "## 2. Paragraphs to look at as a whole", "",
          "Out of Freimann's order (rearranged by the Livorno editors, or matched wrongly), or low agreement.", "",
          "| Part, para | Freimann | Agreement | Note |", "|---|---|---|---|"]
    L += [f"| {r['part']}.{r['para']} | {r['freimann']} | {r['agree']:.2f} | {r.get('order', '')} |" for r in od]
    L += ["", "## 3. Substantive differences, paragraph by paragraph", "",
          "Spelling, abbreviations and Freimann's ג→נ are left out here (they are in collation.json).", ""]
    for r in found:
        s = sub(r)
        if not s:
            continue
        L += [f"### {'Front matter' if r['part'] == 0 else 'Part ' + str(r['part'])}, paragraph {r['para']} "
              f"(Freimann {r['freimann']}, agreement {r['agree']:.2f})", "",
              "| Kind | 1885 | Freimann | at |", "|---|---|---|---|"]
        L += [f"| {d['kind']} | {d['1885'] or '—'} | {d['freimann'] or '—'} | {d['at']} |" for d in s]
        L.append("")
    sec = [g for g in gaps if int(g["from"].split(":")[0]) >= 49]
    L += ["## 4. Passages of the second journey not in the 1885 printing", "",
          f"{len(sec)} stretches of 12 words or more in Freimann pp. 49–180 that no 1885 paragraph covers "
          f"({sum(g['words'] for g in sec):,} words).", "",
          "| Freimann | Words | Begins |", "|---|---|---|"]
    L += [f"| {g['from']}–{g['to']} | {g['words']} | {g['start']} |" for g in sec]
    (OUT / "REPORT.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    words, pages = freimann()
    (OUT / "freimann_clean.txt").write_text(
        "\n".join(f"[{n}:{ln}] {l}" for n in pages for ln, l in pages[n]) + "\n", encoding="utf-8")
    idx = collections.defaultdict(list)
    for i in range(len(words) - 2):
        idx[(words[i][0], words[i + 1][0], words[i + 2][0])].append(i)

    # 1885 paragraphs with their part and paragraph label
    paras = []
    fr = P.paragraphs(P.FRONT)
    for i, t in enumerate(fr):
        paras.append((0, B.roman(i + 1), t))
    he, pos = P.paragraphs(), 0
    for k in sorted(x for x in B.PARTS if x):
        n = len(B.read_blocks(ROOT / "data" / "en" / f"part-{k:02d}.en.txt"))
        for j in range(n):
            paras.append((k, str(pos + j + 1), he[pos + j]))
        pos += n

    covered = [False] * len(words)
    results = []
    for part, label, text in paras:
        pw = para_words(text)
        rec = {"part": part, "para": label, "words": len(pw), "found": False}
        if len(pw) < 4 or text.startswith("# "):
            results.append(rec)
            continue
        start, votes = locate(pw, idx, len(words))
        if start is None or votes < 2:
            results.append(rec)
            continue
        lo, hi = max(0, start - 40), min(len(words), start + int(len(pw) * 1.4) + 60)
        win = words[lo:hi]
        sm = difflib.SequenceMatcher(None, [w[0] for w in pw], [w[0] for w in win], autojunk=False)
        blocks = [b for b in sm.get_matching_blocks() if b.size]
        if not blocks:
            results.append(rec)
            continue
        f0, f1 = blocks[0].b, blocks[-1].b + blocks[-1].size
        sm = difflib.SequenceMatcher(None, [w[0] for w in pw], [w[0] for w in win[f0:f1]], autojunk=False)
        diffs, same = [], 0
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "equal":
                same += i2 - i1
                continue
            a = " ".join(w[1] for w in pw[i1:i2])
            b = " ".join(w[1] for w in win[f0 + j1:f0 + j2])
            where = f"{win[f0 + j1][2]}:{win[f0 + j1][3]}" if j2 > j1 else f"{win[f0 + max(j1 - 1, 0)][2]}:{win[f0 + max(j1 - 1, 0)][3]}"
            k = ("only in Freimann" if tag == "insert" else "only in 1885" if tag == "delete" else kind(a, b))
            diffs.append({"1885": a, "freimann": b, "at": where, "kind": k})
        if same / max(len(pw), 1) < 0.3:
            results.append(rec)  # a chance match, not this paragraph
            continue
        for j in range(lo + f0, lo + f1):
            covered[j] = True
        rec.update(found=True, freimann=f"{win[f0][2]}:{win[f0][3]}–{win[f1 - 1][2]}:{win[f1 - 1][3]}",
                   agree=round(same / max(len(pw), 1), 3), diffs=diffs)
        results.append(rec)

    # stretches of Freimann that no 1885 paragraph covers
    gaps, i = [], 0
    while i < len(words):
        if covered[i]:
            i += 1
            continue
        j = i
        while j < len(words) and not covered[j]:
            j += 1
        if j - i >= 12:
            gaps.append({"from": f"{words[i][2]}:{words[i][3]}", "to": f"{words[j - 1][2]}:{words[j - 1][3]}",
                         "words": j - i, "start": " ".join(w[1] for w in words[i:i + 14])})
        i = j
    # dates: the 1885 day and month at the start of a paragraph against Freimann's nearest date heading before it
    for r, (part, label, text) in zip(results, paras):
        if not r["found"]:
            continue
        m = re.search(rf"(?:^|\s)([א-ת]{{0,2}}['\"׳״][א-ת]?|[א-ת])\s+({MONTHS})\b",
                      re.sub(r"\{p\d+\}", "", text)[:80])
        pg, ln = map(int, r["freimann"].split("–")[0].split(":"))
        head = None
        for n2, l2 in [(p, l) for p in (pg - 1, pg) if p in pages for l in pages[p] if (p, l[0]) <= (pg, ln)][::-1]:
            h = re.search(rf"({MONTHS})\s*(\d{{1,2}})\b", l2[1])
            if h:
                head = (h.group(1), int(h.group(2)), f"{n2}:{l2[0]}")
                break
        if m and head:
            num = m.group(1)
            day = 10 if norm(num) == "יוד" else sum(GEM.get(c, 0) for c in norm(num))
            if not 1 <= day <= 30:
                continue
            r["date_1885"], r["date_freimann"] = f"{day} {m.group(2)}", f"{head[1]} {head[0]} ({head[2]})"
            near = [(int(h.group(2)), h.group(1)[:3]) for p in (pg - 1, pg, pg + 1) if p in pages
                    for _, l2 in pages[p] for h in re.finditer(rf"({MONTHS})\s*(\d{{1,2}})\b", l2)]
            if (day, m.group(2)[:3]) not in near:  # no heading with the 1885 date within a page
                r["date_differs"] = True
    # order: paragraphs outside the longest run that follows Freimann's order (diary parts only)
    seq = [r for r in results if r["found"] and 0 < r["part"] < 10 or r["found"] and r["part"] == 0 and r["para"] in
           ("xii", "xiii", "xiv", "xv")]
    key = [tuple(map(int, r["freimann"].split("–")[0].split(":"))) for r in seq]
    best = [1] * len(seq)
    prev = [-1] * len(seq)
    for i in range(len(seq)):
        for j in range(i):
            if key[j] <= key[i] and best[j] + 1 > best[i]:
                best[i], prev[i] = best[j] + 1, j
    keep, i = set(), max(range(len(seq)), key=lambda k: best[k]) if seq else -1
    while i >= 0:
        keep.add(i)
        i = prev[i]
    for i, r in enumerate(seq):
        if i not in keep:
            r["order"] = "out of Freimann's order"
    json.dump({"paragraphs": results, "omitted_in_1885": gaps}, open(OUT / "collation.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    report(results, gaps, len(words), sum(covered))

    found = [r for r in results if r["found"]]
    kinds = collections.Counter(d["kind"] for r in found for d in r["diffs"])
    print(f"1885 paragraphs: {len(results)}; found in Freimann: {len(found)}; not found: "
          f"{[(r['part'], r['para']) for r in results if not r['found'] and r['words'] >= 4]}")
    print("median agreement:", sorted(r["agree"] for r in found)[len(found) // 2] if found else "-")
    print("differences by kind:", dict(kinds))
    print(f"Freimann words: {len(words)}; covered by 1885: {sum(covered)}; uncovered stretches >= 12 words: {len(gaps)}, "
          f"{sum(g['words'] for g in gaps)} words")


if __name__ == "__main__":
    main()
