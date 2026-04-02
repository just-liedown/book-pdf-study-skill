# Scanned PDFs And OCR

Use this branch when preprocessing shows that the PDF is scanned, image-only, or otherwise yields little usable text.

## Detection Signals

Treat the PDF as a scanned or image-heavy document when one or more of these are true:

- `pdftotext` returns empty text
- extracted text is nearly empty for most pages
- the learner already says the PDF is a scan or page photos

## First-Version Policy

This skill's first version does not implement OCR itself. It should:

1. detect the scanned-PDF condition
2. stop the normal text-study flow
3. explain that OCR is required before learn mode, ask mode, and test mode
4. continue only after OCR text is available

Do not pretend that image pages are readable text.

## Recommended OCR Output Contract

If OCR is added later, write outputs that mirror the normal cache layout:

- `ocr-pages.jsonl`
- `ocr-chunks.jsonl`
- `ocr-confidence.json`

That keeps downstream retrieval logic simple.

## Response Rules After OCR

When teaching from OCR text:

- say when OCR quality might limit confidence
- treat formulas, code, tables, and niche terminology as high-risk zones
- ask for a page image or quoted snippet when the OCR text looks wrong

## Local Recovery Suggestions

If the environment lacks OCR support, suggest one of these paths:

- run OCR outside the skill, then re-enter the normal study flow
- provide page images or a quoted excerpt for targeted explanation
- provide a text-exported version of the same book PDF
