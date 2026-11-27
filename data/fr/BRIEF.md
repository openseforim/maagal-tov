# Brief: proofread and translate one unit of the Ḥida's *Ma'agal Tov* (Freimann's edition)

You work on the Open Seforim reader of the Ḥida's travel diary *Ma'agal Tov* (Ḥayyim Yosef David Azulai, 1724–1806).
The 1885 printing is already translated (C:\Users\ezrab\Ezra Brandt\Claude\maagal-tov\data\en\part-NN.en.txt). Now we add
the full diary from A. Freimann's edition, *Ma'agal Tov ha-Shalem* (Berlin 1921, Jerusalem 1934), pp. 1–180: the first
journey (1753–58, pp. 1–48) and the second journey (1772–78, pp. 49–180). Your unit is five printed pages.

Use `py -3.13` for Python (never `python`), and put `sys.stdout.reconfigure(encoding="utf-8")` at the top of every script.
Write scripts and crops only inside your unit folder `data\fr\work\uNN\`. Do not edit any other file of the repository,
do not run git, and do not use the network.

## Inputs

- `data\fr\work\uNN\input.txt`: Kraken OCR of your pages, already cleaned (running head, footnote block, margin line
  numbers, note numbers and Freimann's folio marks such as (57a) removed), one line per printed line as `[page:line] text`.
  It also holds the page after your unit, only to finish your last paragraph.
- The page images, named in input.txt (`...\pages\freimann\pNNN.jpeg`, 1093×1489 px). To read them, crop each page into
  about four horizontal strips with a small overlap and upscale them 2× with PIL (LANCZOS), save in your unit folder,
  and Read the crops. Read at most about 8 images per Read batch.
- `data\fr\work\glossary.md`: names as the 1885 translation spells them. Use the same English forms.
- Style model: read the first 40 lines of `data\en\part-04.en.txt` and `data\en\part-04.notes.json` before you start.

## 1. Proofread the Hebrew

- Compare every OCR line with the image and correct it. Known OCR errors in this scan: ג read as נ (very frequent,
  above all in the 1934 fascicle: נדול → גדול, נבריאל → גבריאל), and also ה/ח, ס/ם, ד/ר, ו/י, ב/כ, ש/ע. Decide by the image
  first, then by sense.
- Keep spelling, abbreviations and punctuation as printed (do not expand ר"מ, ה"י, etc.). Keep Freimann's
  brackets and question marks that are printed in the text line.
- Remove: footnote reference numbers or signs (small raised numbers; the OCR often shows them as digits or "?"
  stuck to a word), the margin line numbers, and Freimann's folio marks of the autograph such as (57a) or (57b).
- Freimann's footnotes (below the line) are his, not the Ḥida's: never put them in the Hebrew or copy them into notes.
  You may use them only to identify a place or person in your own words.
- Where you cannot read a word even in the crop, keep the OCR form and add a note.

## 2. Paragraphs

- One paragraph = one paragraph of Freimann's print: a new line, usually starting with a date (`אב 17.`, `אלול ר"ח.`).
  A long undated stretch that the print breaks with a new indented line is a new paragraph too.
- A heading line (a journey or year title, e.g. a centered line) is its own paragraph with `"head": true`.
- Start with the first paragraph that begins on your first page. Skip the lines at the top of your first page that
  finish a paragraph from the page before (the previous unit does them), **except in unit 1**. Finish the paragraph that
  is still open at the end of your last page, reading on into the next page as far as needed.
- Where a new printed page begins inside a paragraph, put the token `{f107}` (for page 107) in the Hebrew at that point.
  The token goes in the Hebrew only, never in the English.
- A letter that the OCR dropped but the image shows (for example a weekday letter) is simply restored in the Hebrew.
  A note is needed only if the print itself is unclear.

Abbreviations met so far (from unit 22): אש"ג = אושפיזא של גוים, a gentile inn; ה"י = may God (protect/heal) him or her;
ש' = שלום (greeting) or לשלום; הנז' / הנז"ל = mentioned above; בעה"ב = the master of the house, the host; ק"ק = holy
congregation; סי' = Signor; פ"א = the first time (his first journey); ג'יקולאטי = chocolate; לוידור = louis d'or. Leave
unresolved name abbreviations (ר"ם דר"ם) as initials in the English with a note. You work in parallel with other units,
so you do not know the people of the pages before yours: identify people from your own pages and the glossary.

## 3. Translate

- Plain English, close to the Hebrew, as in the 1885 parts. Keep the Ḥida's first person, his dates by weekly reading,
  and his blessings and formulas short ("may God heal her", "praise God").
- Dates: Freimann's entries begin "Month Day. Weekday". Render as `17 Av [Wednesday 20 August 1777]:` — Hebrew day and
  month as written, then the civil date in gray brackets. Work out the civil date and check the weekday with
  `py -3.13 -I C:\Users\ezrab\Ezra Brandt\Claude\maagal-tov\scripts\hebdate.py <year> <month> <day>` (months: Nisan=1 …
  Elul=6, Tishrei=7 … Adar=12, Adar II=13). Find the Jewish year from the year headings and the previous entries; the
  weekday must agree. Night (ליל, בתחילת הלילה) belongs to the next Hebrew day: give the civil evening ("[the evening of
  …]"). Where the weekday does not fit, say so in a note.
- Other translator's additions in [brackets]: Bible verse references, civil years for years in the text.
- Names: glossary forms; otherwise a plain transliteration (Signor, R., the gevir). Places by their usual English or
  French/Italian name (Nîmes, Montpellier, Carpentras).
- Mark an uncertain rendering with ⚠1, ⚠2 … (numbered from 1 in **each paragraph**) and give a note for each:
  `{"he": "<the Hebrew words>", "note": "<why it is uncertain; your best reading>"}`. Use notes also for unresolved
  abbreviations, unreadable words, and dates that do not fit. Keep notes short and factual; no notes on things you are sure of.

### What the first pass missed (reviews of parts 2–5, 27-Nov-2026)

Four outside reviews and one own review of parts 2–5 found the same two faults again and again. Check for both before
you write "uncertain", "not resolved" or "read as":

1. **Rabbinic allusions, above all the Talmud.** The first pass found most Bible verses, but it missed the Mishnah,
   the Talmud, Onkelos and the prayer book. A phrase that looks strange, or a legal term in a travel story, is nearly
   always a quotation. Examples: שונא לטעון (Bava Metzia 32b; it was "emended" to שונה), שתוקו לא אומר לכם (m. Shevi'it
   8:9; it was translated as its opposite), ריוח בין הדבקים (Berakhot 15b), מחיים תפיסנא (Ketubot 85a), לא ישב אדם לפני
   הספר (m. Shabbat 1:2), גדול המעשה (Bava Batra 9a), פרידה טובה (Bava Kamma 38b, "a good dove", not "a good parting"),
   ריש בריוני (Gittin 56a), נפקין בריש גלי (Onkelos, Exod 14:8), מלאים זיו ומפיקים נגה (the hymn El Adon), נפשות רבות
   וחסרונן (the blessing after food), יזכה ויבחין (Berakhot 58a). Never emend a word before you search for the phrase
   as a quotation.
2. **Gershayim mark a word play, not only an abbreviation.** The Ḥida puts the marks inside a word where he changed one
   letter of a known phrase, or where the word has two senses. Do not expand such a word as initials. Find the phrase
   he changed, then say what the change does. Examples: בצע"ריך for בשעריך (Deut 17:8, "sorrows" for "gates"; it was
   read as צרכי), נ"ר רשעים (the number 250 and Prov 13:9), פארו"ת הטובות (paras and the cows of Gen 41:26), מט"ה משה
   (מטה כלפי חסד, Rosh Hashanah 17a, and the staff of Moses), החסר"ים for החצרים (Lev 25:31), הב"ל for אבל (Gen 37:35),
   חיכ"י for חיקי (Ps 35:13), חיי"ם (life, and his own name Ḥayyim), לטע"ון (to load, to plead), הספור for הספר.
   Often the changed word is a homophone (צ/ש, כ/ק, ס/ש, ח/ה, ע/א) of the word in the source.

Three smaller patterns: a verb next to חיי"ם, יוסף or דוד usually tells what happened to the writer himself; ליל ה'
is the evening before Thursday, so do not write "Thursday night"; and Freimann's footnotes often settle a name or a
date, so read them before you mark a name as not identified (say "Freimann:" in the note).

## 4. Output

Write `C:\Users\ezrab\Ezra Brandt\Claude\maagal-tov\data\fr\uNN.json` (UTF-8, `ensure_ascii=False`, indent 1):

```json
{"unit": 22, "pages": [106, 110],
 "paras": [
  {"start": "106:5", "head": false,
   "he": "אב 17. ד' אחר חצות ה' שעות נסעתי ...",
   "en": "17 Av [Wednesday 20 August 1777]: five hours after midday I set out ...",
   "notes": {"1": {"he": "...", "note": "..."}}}
 ],
 "report": "two or three sentences: pages done, kinds of OCR errors fixed, anything the editor should check"}
```

`start` is the printed page and line (as in input.txt) where the paragraph begins. Then check your file: load it with
json, check that every ⚠n in each `en` has a note n in that paragraph and the reverse, that the paragraphs follow in page
order and that no line of your pages is lost or doubled. Reply with the report and the paragraph count only.
