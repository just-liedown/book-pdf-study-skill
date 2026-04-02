# Cache Layout

The preprocessor writes a stable cache directory for each PDF.

## Default Location

If `--out-dir` is not supplied, write to:

```text
<pdf-parent>/.book-pdf-study/<pdf-stem>-<sha256-prefix>/
```

Use the same cache directory until the source PDF hash changes.

## Required Files

### `manifest.json`

Small machine-readable metadata:

- `source_pdf`
- `pdf_name`
- `file_hash`
- `page_count`
- `generated_at`
- `cache_dir`
- `chunk_size`
- `chunk_overlap`

### `pages.jsonl`

One JSON object per page:

```json
{"page": 1, "char_count": 1234, "text": "..."}
```

### `chunks.jsonl`

One JSON object per retrieval chunk:

```json
{"chunk_id": 1, "page_start": 1, "page_end": 1, "char_count": 950, "text": "..."}
```

### `toc_candidates.txt`

Likely table-of-contents lines and heading candidates. Use this when chapter structure is unclear.

### `book-analysis.md`

Heuristic preprocessing summary. Read this before claiming:

- likely title
- text density
- apparent difficulty
- chapter structure confidence
- probable prerequisites

This file is not ground truth. Treat it as a starting point for later reasoning.

### `study-state.json`

Persistent learner state. Keep it small and update it after learn mode and test mode.

Recommended fields:

- `target_depth`
- `current_level`
- `current_stage`
- `covered_chapters`
- `mastery`
- `weak_points`
- `test_history`

### OCR branch artifacts

If the book is scanned or image-only, keep OCR outputs in the same cache family rather than inventing a second storage layout.

Recommended additional files:

- `ocr-pages.jsonl`
- `ocr-chunks.jsonl`
- `ocr-confidence.json`

Do not claim these files exist unless an OCR workflow has actually produced them.

## Rebuild Rules

Rebuild the cache when:

- the PDF hash changed
- the cache is missing required files
- the user explicitly asks to rebuild

Do not rebuild just because the user asks a different question about the same book.

If the text cache is empty or nearly empty, treat that as a signal to route through the OCR branch instead of repeatedly retrying the same extraction.
