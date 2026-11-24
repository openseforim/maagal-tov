# Ḥida, *Ma'agal Tov*: Hebrew and English

Site: <https://openseforim.org/maagal-tov/>

Ḥayyim Yosef David Azulai (the Ḥida, 1724–1806) travelled twice as an emissary of the Jews of Hebron and the Land of
Israel, through Egypt, Italy, Germany, Holland, France, England and Tunisia. His diary, *Ma'agal Tov*, records the
money he raised, the scholars he argued with, the libraries and courts he saw, and his own grief and melancholy.
This repository holds a Hebrew text checked against the scan, an English translation paragraph by paragraph, and the
scripts that build the reader.

## Status

| Part | Scans | Status |
|---|---|---|
| 1. Tunis, Livorno and Pisa | 8–12 | 24-Nov-2026. Hebrew checked against the scan line by line; 11 paragraphs translated; 9 uncertain renderings. Allusions not verified against a concordance. |
| 2– (Florence and on) | 13–77 | OCR only (`data/he_raw/`), not checked or translated |

## Sources

- **Base text:** the printing of Przemyśl, 1885 (*Sefer Ma'agal Tov*), which holds part of the second journey, from
  Tunis to Italy. Scan: [archive.org maagaltob00azul](https://archive.org/details/maagaltob00azul) (University of
  Illinois, 650 ppi). The scan lacks the title page and starts in the middle of a passage.
- **Complete text:** A. Freimann's edition, *Ma'agal Tov ha-Shalem* (Mekize Nirdamim, Berlin 1921 and Jerusalem
  1934), holds both journeys. Its only scan found online ([HebrewBooks 21838](https://www.hebrewbooks.org/21838),
  1-bit, about 300 dpi) gave 26% wrong words with the OCR used here, so it is not used yet.
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
| `data/he/sNNNN.txt` | Checked pages, line for line as printed |
| `data/en/part-NN.en.txt`, `part-NN.notes.json` | English paragraphs and the notes for the ⚠ marks |
| `maagal_tov_1885_ocr.txt` | The whole OCR in one file, with `=== scan NNNN ===` page marks (not checked) |
| `scripts/paragraphs.py`, `scripts/build_site.py` | Paragraphs from the checked pages; the reader in `docs/` |
| `scripts/split_*.py`, `ocr_*.py`, `eval_gt.py` | OCR tools; `data/gt/` a hand transcription of one Freimann page used to score OCR |
| `NOTES.md` | OCR tests and findings |

Build: `py -3.13 -I scripts/build_site.py` (then the Open Seforim post-build runs if `../openseforim-site` is present).

## Licence

Texts, translation and data: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) (see `LICENSE`).
