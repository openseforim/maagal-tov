# Ḥida, *Ma'agal Tov*: Hebrew and English

Site: <https://openseforim.org/maagal-tov/>

Ḥayyim Yosef David Azulai (the Ḥida, 1724–1806) travelled twice as an emissary of the Jews of Hebron and the Land of
Israel, through Egypt, Italy, Germany, Holland, France, England and Tunisia. His diary, *Ma'agal Tov*, records the
money he raised, the scholars he argued with, the libraries and courts he saw, and his own grief and melancholy.
This repository holds a Hebrew text checked against the scan, an English translation paragraph by paragraph, and the
scripts that build the reader.

## Status

**The full diary (Freimann), 26-Nov-2026: complete.** Both journeys, A. Freimann's pp. 1–180, in 17 parts
(`docs/full-NN.html`), 907 paragraphs, Hebrew proofread against the NLI scan line by line and translated paragraph by
paragraph. Each row links to the matching 1885 paragraph and back (123 paragraphs of the 1885 printing are found in
Freimann). Decisions on base text, layout, copyright and numbering: [issue 2](https://github.com/openseforim/maagal-tov/issues/2).

The 1885 printing:

| Part | Scans | Status |
|---|---|---|
| 1. Tunis, Livorno and Pisa | 7–11 | 24-Nov-2026. Hebrew checked against the scan line by line; 11 paragraphs translated; 9 uncertain renderings. Allusions not verified against a concordance. |
| 2. Florence, Ancona and Venice | 11–17 | 24-Nov-2026. Hebrew checked against the scan line by line; 17 paragraphs translated; 12 uncertain renderings. Dates by the weekly reading given in brackets (diaspora readings, Hebcal). |
| 3. Venice, Modena, Reggio and Mantua | 18–22 | 24-Nov-2026. Hebrew checked against the scan line by line (scan 20 read from the image; its OCR failed); 15 paragraphs translated; 12 uncertain renderings. Dates in brackets. |
| 4. Avignon, Trieste and Paris | 23–27 | 24-Nov-2026. Hebrew checked against the scan line by line; 15 paragraphs translated; 11 uncertain renderings. Dates in brackets. |
| 5. Paris and Versailles | 27–32 | 24-Nov-2026. Hebrew checked against the scan line by line (scans 30 and 32 read from the image); 7 paragraphs translated; 10 uncertain renderings. Dates in brackets. |
| 6. Amsterdam: winter and Purim | 33, 40–44 | 25-Nov-2026. Hebrew checked against the scan line by line; 17 paragraphs translated; 20 uncertain renderings. Dates in brackets. |
| 7. Amsterdam: Passover to Sivan | 45–50 | 25-Nov-2026. As part 6; 18 paragraphs; 32 uncertain renderings. |
| 8. The Hague, Rotterdam and Paris again | 50–56 | 25-Nov-2026. As part 6; 13 paragraphs; 29 uncertain renderings. |
| 9. Turin, the return to Livorno, and later years | 57–61 | 25-Nov-2026. As part 6; 10 paragraphs; 27 uncertain renderings. The diary ends in 1793. |
| 10. *Shem Tov*: memories of the Ḥida | 62–67 | 25-Nov-2026. The editors' section of family stories; 13 paragraphs; 12 uncertain renderings. |
| 11. *Sefer ha-Zikkaron* | 67–70 | 25-Nov-2026. The Ḥida's private notes, 1773–78; 7 paragraphs; 17 uncertain renderings. Years from the chronograms in brackets. |
| 12. Stories of the Ḥida | 71–76 | 25-Nov-2026. The editors' closing stories and colophon; 9 paragraphs; 12 uncertain renderings. |
| Front matter | 34–39 | 25-Nov-2026. Title page, imprint, the Livorno editor's preface, the Ḥida's preface, and the opening of the diary (1764, 1773); 14 paragraphs; 36 uncertain renderings. The prefaces have torn page edges: gaps are marked […]. |

The 1885 printing is complete in the reader. Scans 34–37, 71 and 74 were read from the image because their OCR failed;
scans 62, 71, 74 and 75 were checked a second time by another reader.

**Order of the leaves.** The scanned copy is bound out of order. Scans 34–37 are the title page, the publisher's notice
and the two prefaces; 38–39 (printed leaf ג) are the opening of the diary; the leaves after them are lost, and scan 7
takes up the text in Tunis. Scan 33 goes on directly to scan 40 (catchword אור, leaf יח). `scripts/paragraphs.py`
holds the reading order (`FRONT`, `MAIN`); the front matter is part 0 (`docs/part-00.html`), with paragraphs numbered
i, ii, iii…

**Scan numbers** are those of the archive.org viewer (its counter, e.g. "7/81", and links `page/n7`). The viewer
leaves out the first image file, so scan N is image file N+1; the data files keep the image-file numbers
(`data/he/s0008.txt` = image 0008 = scan 7).

## Sources

- **Base text:** the printing of Przemyśl, 1885 (*Sefer Ma'agal Tov*), a reprint of the Livorno printing of 1879 (Eliyahu Ben Amozegh), edited by Joseph Shabbetai Farḥi. It
  holds the second journey (1773–1778) with a few later entries to 1793, then the editors' additions (*Shem Tov*,
  *Sefer ha-Zikkaron*, stories). Scan: [archive.org maagaltob00azul](https://archive.org/details/maagaltob00azul)
  (University of Illinois, 650 ppi); see "Order of the leaves" above.
- **Complete text:** A. Freimann's edition, *Ma'agal Tov ha-Shalem* (Mekize Nirdamim, Berlin 1921 and Jerusalem
  1934), holds both journeys; it is the text of the full diary. Scan: the National Library of Israel copy, shelfmark
  S 32 V 929 ([NLI](https://www.nli.org.il/he/books/NNL_ALEPH990011568950205171/NLI)); OCR by Kraken with baseline
  segmentation (`../openseforim-scans/kaggle`). Only the Ḥida's text is used: Freimann's notes and introduction are
  not reproduced, and no page images of his edition are published (the 1934 fascicle may be protected in the US to the
  end of 2029). In this copy the lower corner of the leaf with pp. 119–120 is torn away; the lost words are marked
  [...]. The HebrewBooks scan ([21838](https://www.hebrewbooks.org/21838)) is too poor for OCR (26% wrong words).
  The autograph (JTS MS 5388–5389) was not consulted.
- **Translations that exist:** English by B. Cymerman (1997) and French (1997), both in copyright. Three Hebrew editions
  of 2022 (Raviv; Mekhon ha-Maor; Mandelbaum) are in copyright and are not used.

## Method

- **OCR:** [Kraken](https://kraken.re/) with the PP-OCRv6 medium model, line by line. Lines are found from the row ink
  profile (`scripts/split_image.py`), not by Kraken's segmenter, then read with `ocr --no-segmentation --base-dir R`
  (`scripts/ocr_images.py`). About 1 doubtful word on a 22-line page.
- **Checking:** every line compared with the scan by eye. Spelling, abbreviations and punctuation are as printed;
  the catchword at the foot of each page is dropped. Typical OCR errors in this type: צ read as ל, a lost first or
  last word of a line, missing full stops.
- **Translation:** by Claude (Anthropic), directed and reviewed by Ezra Brand. One English paragraph for each Hebrew
  paragraph; the print ends each entry with a colon. Uncertain renderings are marked ⚠ and explained at the end of
  each page.

## Layout

| Path | Contents |
|---|---|
| `data/he_raw/sNNNN.txt` | OCR of each scan page (running head removed), not checked |
| `data/he/sNNNN.txt` | Checked pages, line for line as printed; a line that starts with `# ` is a heading (its own paragraph) |
| `data/en/part-NN.en.txt`, `part-NN.notes.json` | English paragraphs and the notes for the ⚠ marks |
| `maagal_tov_1885_ocr.txt` | The whole OCR in one file, with `=== scan NNNN ===` marks by image-file number (not checked) |
| `scripts/paragraphs.py`, `scripts/build_site.py` | Paragraphs from the checked pages; the reader in `docs/` |
| `docs/scans/sNNNN.jpg`, `docs/app.js`, `scripts/make_scans.py` | Page images for the "Show the scan beside the text" panel (greyscale, 900 px; made from the archive.org jp2 set), and the panel script. `build_site.py` stops if a paragraph's page image is missing. |
| `scripts/split_*.py`, `ocr_*.py`, `eval_gt.py` | OCR tools; `data/gt/` a hand transcription of one Freimann page used to score OCR |
| `NOTES.md` | OCR tests and findings |
| `data/fr/uNN.json` | The full diary, one file per unit of five Freimann pages: paragraphs with `start` (page:line), proofread Hebrew (`{f107}` = page 107 begins), English and notes |
| `data/fr/parts.json`, `data/fr/map_1885.json` | The part division of the full diary; the Freimann range of each 1885 paragraph (from the collation) |
| `scripts/fr_units.py`, `fr_check.py`, `build_full.py` | Unit inputs (to `data/fr/work/`, not committed; the agents' brief is `data/fr/BRIEF.md`); checks against the OCR; the full-diary pages |
| `scripts/bands.py` | Horizontal bands of a page at 1800 px, for checking the OCR by eye |
| `scripts/hebdate.py` | Civil dates and weekly readings (diaspora) for the bracketed dates; needs `pyluach` |

Build: `py -3.13 -I scripts/build_site.py` (then the Open Seforim post-build runs if `../openseforim-site` is present).

## Licence

Texts, translation and data: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) (see `LICENSE`).
