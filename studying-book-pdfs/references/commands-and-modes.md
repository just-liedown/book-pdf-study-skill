# Commands And Modes

This skill uses explicit mode requests in normal language so the learner stays in control. Avoid slash commands because some chat surfaces reserve `/...` for platform commands before the skill can see them.

These mode rules are source-agnostic. The same learn, ask, and test behavior should work after preprocessing a PDF or a Markdown file.

## Accepted Mode Requests

Prefer plain text such as:

- `learn mode`
- `ask mode`
- `test mode`
- `enter learn mode`
- `进入学习模式`
- `进入问题模式`
- `进入测试模式`

## Learn Mode

Use learn mode to continue the planned study flow.

### Required inputs

- learner target depth
- learner current level
- current stage from `study-state.json`

### Preferred reads

- `study-state.json`
- `book-analysis.md`
- selected chunks from `chunks.jsonl`

### Expected output

- a short statement of the current stage
- the lesson itself
- optional next-step recommendation
- a state update written back to `study-state.json`

Default teaching rule:

- teach as if the learner is not looking at the source
- rewrite the content in clearer language
- use the book only as source material, not as the primary presentation layer

If the source text came from OCR, make that explicit when OCR quality could affect correctness.

## Ask Mode

Use ask mode for a confusing passage, concept, chapter, or statement.

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

Default explanation rule:

- answer the confusion directly in your own words
- do not require side-by-side reading of the original source
- quote or dissect the original wording only when the learner explicitly asks for that style

If OCR text is the source:

- mention that the answer is based on OCR text
- be extra careful with symbols, formulas, code, and tables
- ask the learner for an image snippet if the extracted text looks suspicious

## Test Mode

Use test mode only when the learner explicitly asks for it.

### Target types

- current stage
- selected chapter
- target depth

### Expected output

- compact test items
- answer review or scoring
- mastery update
- recommendation: continue, review, or regress

Do not run test mode on obviously corrupted OCR text without warning the learner that input quality may distort the result.

## Stage Ordering

Default stage order:

1. Orientation
2. Mapping
3. Understanding
4. Deepening
5. Application
6. Consolidation

Assessment is an overlay triggered by test mode, not a permanently active stage.

## OCR Branch

If preprocessing yields empty or near-empty text:

1. Say that the PDF appears scanned or image-only.
2. Say that the normal study flow should pause until OCR text exists.
3. If no OCR workflow is available in the current environment, say so directly.
4. Resume learn mode, ask mode, and test mode only after OCR output is available.
