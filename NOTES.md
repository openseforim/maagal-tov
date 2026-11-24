# Ma'agal Tov OCR: notes (24-Nov-2026)

## Scans

| Scan | What | Quality | Result |
|---|---|---|---|
| HebrewBooks 21838 (Freimann 1921–34, complete, 223 pp.) | `openseforim-scans\scans\hida-maagal-tov\hebrewbooks_21838_freimann.pdf` | 1-bit, about 300 dpi, rough letter edges | Kraken PP-OCRv6: **26.5% of words wrong** on scan 30 (hand check, 446 words). Tesseract heb_best: 40%. Not usable without fine-tuning; set aside for now. |
| archive.org `maagaltob00azul` (Przemyśl 1885 printing, **partial**) | `openseforim-scans\scans\hida-maagal-tov\maagaltob00azul_jp2.zip`, unpacked in `data\p1885\maagaltob00azul_jp2\` | 650 ppi colour, clean; Rashi-like cursive type | Kraken PP-OCRv6: about 1 doubtful word on a 22-line page. **Used.** |

## Method that works (both books)

1. `scripts/split_image.py` (page images) or `scripts/split_lines.py` (the HebrewBooks PDF): find the lines myself from the
   row ink profile (line centres = profile peaks at the line pitch, cut at the minimum between them), cut margin
   line numbers, crop each line. Kraken's own baseline segmenter lost about a third of the lines on the Freimann pages.
2. Kraken `ocr --no-segmentation -B 16 --base-dir R --threads 10`, many `-i line.png line.R.txt` pairs in one call
   (model loaded once). `--base-dir R` gives logical order with digits the right way round; no reversing needed.
3. `scripts/ocr_images.py IMGDIR OUTDIR [--scale S] [--autocrop] [--min-height H]`: resumable, one text file per page,
   one printed line per text line.

Tests that did not help: 2x upscale + blur of the 1-bit Freimann images (same error rate as 1x, different errors).

## Scan numbering

File names here use the archive.org image-file numbers (0000–0083). The archive.org viewer leaves out image 0000 and
two at the end (81 pages), so viewer page nK = image K+1. The reader shows and links viewer numbers (`vnum` in
`scripts/build_site.py`).

## Result (24-Nov-2026)

`maagal_tov_1885_ocr.txt`: OCR of the 1885 printing, scans 7–77 (71 pages, about 12,700 words), one printed line
per line, `=== scan NNNN ===` before each page, running head removed. Starts mid-passage (title page missing in
the scan); ends with the colophon. Scans 0–6 and 78–83 are covers and blank leaves. Not proofread.

## Files

- `data/p1885/text/<page>.txt`: OCR of the 1885 printing.
- `data/gt/s030.gt.txt`: hand transcription of Freimann scan 30 (35 lines; `?` = unsure word). `scripts/eval_gt.py` scores against it.
- `scripts/make_train.py`: builds ketos training pairs from `data/gt/*.lines.tsv` (not used: fine-tuning dropped).

## Open

- Which part of the diary does the 1885 printing hold? (First pages: Tunis, the qa'id's son and the Livornese.)
  Compare with Freimann to see where it fits.
- The Ben-Yehuda word list for spelling correction: command on the shared to-do list (low priority).
