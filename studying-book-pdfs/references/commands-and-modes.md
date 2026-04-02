# Commands And Modes

This skill uses explicit commands so the learner stays in control.

## `/learn`

Use `/learn` to continue the planned study flow.

### Required inputs

- learner target depth
- learner current level
- current stage from `study-state.json`

### Preferred reads

- `study-state.json`
- `book-analysis.md`
- selected sections from `chunks.jsonl`

### Expected output

- a short statement of the current stage
- the lesson itself
- optional next-step recommendation
- a state update written back to `study-state.json`

If the source text came from OCR, make that explicit when OCR quality could affect correctness.

## `/ask`

Use `/ask` for a confusing passage, concept, chapter, or statement.

### Supported entry styles

- pasted quote
- page number
- chapter or section name
- concept or topic

### Preferred reads

- only relevant chunks or pages
- `study-state.json` if the answer should adapt to the learner level

### Expected output

- direct explanation
- likely confusion point
- why the book phrases it that way
- relation to surrounding context
- clearer restatement and examples when useful

If OCR text is the source:

- mention that the answer is based on OCR text
- be extra careful with symbols, formulas, code, and tables
- ask the learner for an image snippet if the extracted text looks suspicious

## `/test`

Use `/test` only when the learner explicitly asks for it.

### Target types

- current stage
- selected chapter
- target depth

### Expected output

- compact test items
- answer review or scoring
- mastery update
- recommendation: continue, review, or regress

Do not run `/test` on obviously corrupted OCR text without warning the learner that input quality may distort the result.

## Stage Ordering

Default stage order:

1. Orientation
2. Mapping
3. Understanding
4. Deepening
5. Application
6. Consolidation

Assessment is an overlay triggered by `/test`, not a permanently active stage.

## OCR Branch

If preprocessing yields empty or near-empty text:

1. Say that the PDF appears scanned or image-only.
2. Say that the normal study flow should pause until OCR text exists.
3. If no OCR workflow is available in the current environment, say so directly.
4. Resume `/learn`, `/ask`, and `/test` only after OCR output is available.
