---
name: studying-book-pdfs
description: Use when a user provides a long PDF that appears to be a book, textbook, manual, or study guide and wants structured learning help rather than one-off extraction. Trigger for requests that need one-time preprocessing, persistent study progress, goal-based depth selection, or explicit learning, question, and testing modes expressed in normal language.
---

# Studying Book PDFs

## Overview

Use this skill to turn a book-like PDF into a reusable study workspace. Preprocess the PDF once, persist the cache, confirm the learner's target depth and current level, then operate through learn mode, ask mode, and test mode without re-reading the whole document each turn. If the PDF is scanned or image-only, route it through the OCR branch before entering the study modes.

## Fit Check

Use this skill only when the PDF is clearly book-like or the user intends to study it as a book.

Strong signals:

- Dozens of pages with chapter-like headings
- A table of contents or numbered sections
- Repeated teaching structure: definitions, examples, exercises, summaries
- User asks to learn, study, review, master, prepare for interviews, or understand selected chapters

Weak fit:

- One-off reports, invoices, forms, slides, or papers the user only wants summarized once
- Pure OCR image scans with no extractable text and no OCR workflow available

If the fit is weak, say so and fall back to a normal PDF-reading workflow instead of forcing this skill.

## Quick Start

1. Check whether a cache already exists and still matches the PDF hash.
2. If the cache is missing or stale, run:

```bash
python3 /path/to/studying-book-pdfs/scripts/preprocess_book_pdf.py "/path/to/book.pdf"
```

3. If preprocessing reports that the extracted text is empty or nearly empty, stop the normal flow and switch to the OCR branch:
   - explain that the PDF appears scanned or image-only
   - explain that learn mode, ask mode, and test mode should wait until OCR text exists
   - if no OCR workflow is available, say so explicitly instead of pretending the text is readable
4. Read these files first:
   - `manifest.json`
   - `book-analysis.md`
   - `study-state.json`
   - `toc_candidates.txt` if the structure is still unclear
5. Confirm two things before teaching:
   - the target depth
   - the learner's current level
6. Work only through the explicit modes below.

Use natural-language mode requests instead of slash commands. Good examples:

- `learn mode`
- `ask mode`
- `test mode`
- `进入学习模式`
- `进入问题模式`
- `进入测试模式`

Detailed cache rules live in `references/cache-layout.md`.

## Target Depth

Always confirm the learner's goal before starting. Offer concrete options when the user has not specified one:

- Introductory understanding
- Selected chapters only
- Systematic understanding
- Interview readiness
- Project application
- Deep reading

Also confirm the current level:

- Zero background
- Slight familiarity
- Learned before but rusty
- Already partway through the book

Record both in `study-state.json`.

## Teaching Stance

Do not assume the learner is reading along with the PDF.

Default teaching behavior:

- explain in your own words first
- reorganize the material into a clearer teaching order
- prefer plain language over the book's phrasing
- use fresh examples, analogies, and restatements
- mention original terms, chapter names, or page locations only as optional reference points

Avoid turning the interaction into guided book annotation unless the learner explicitly asks for close reading.

## Study Modes

Detailed mode behavior lives in `references/commands-and-modes.md`.

### Learn Mode

Advance the learner through the current stage. Treat learning styles as phases, not mutually exclusive switches:

1. Orientation
2. Mapping
3. Understanding
4. Deepening
5. Application
6. Consolidation

Default teaching styles by phase:

- Mapping: outline-first
- Understanding: close reading plus Feynman-style explanation
- Deepening: Socratic questioning
- Application: worked examples plus interview-style Q&A
- Consolidation: flashcard-style recall

Default output should feel like a teacher re-explaining the ideas, not like a summary that assumes the learner is looking at the PDF.

After each learn-mode turn, update `study-state.json` with the current stage, covered chapters, and mastery notes.

### Ask Mode

Use this for local confusion. Support both:

- Precise references: pasted text, page number, paragraph, or quoted passage
- Loose references: chapter, concept, topic, or theme

When answering, cover:

- what the passage says
- where the likely confusion is
- why the author might phrase it that way
- how it connects to surrounding context and the whole book
- a clearer restatement, and examples or counterexamples when useful

Prefer targeted retrieval. Read only the relevant chunks or pages rather than the whole cache.

Answer the confusion directly. Do not make the learner compare your answer against the original wording unless they explicitly ask for a line-by-line explanation.

If the active text came from OCR:

- say that the explanation is based on OCR text
- be cautious with formulas, code, tables, and uncommon terms
- ask for an image snippet or quoted passage when the OCR text looks unreliable

### Test Mode

Run testing only on explicit user command. Test either:

- the current stage
- a chosen chapter
- the chosen target depth

After testing:

- update mastery estimates
- record weak points
- recommend continue, review, or regress to an earlier stage

Do not repeatedly interrupt the learner to ask whether they want a test.

## Persistent State

Keep the state file small and practical. It should at least track:

- source PDF identity
- target depth
- current level
- active stage
- chapter or topic progress
- mastery notes
- test history

If a state file already exists, continue from it unless the user asks to reset.

## Retrieval Rules

- Read `book-analysis.md` before making claims about difficulty or prerequisites.
- Read `chunks.jsonl` or selected pages for ask mode and focused learn mode.
- Read `study-state.json` before every response after preprocessing.
- Avoid re-running the preprocessor unless the PDF changed or the user requests a rebuild.
- If the preprocessor indicates OCR is required, do not invent a normal-text reading path.

## Failure Handling

- If `pdftotext` is missing, explain that preprocessing cannot run and suggest installing Poppler tools.
- If the extracted text is nearly empty, explain that the PDF appears scanned or image-only and should go through the OCR branch before study modes begin.
- If OCR text exists but is visibly noisy, keep answers conservative and say that OCR quality may be the limiting factor.
- If the book structure is unclear, say that the structure confidence is low instead of inventing chapters.

## Resources

### `scripts/preprocess_book_pdf.py`

Use this script for deterministic preprocessing and cache creation.

### `references/cache-layout.md`

Read when you need the exact artifact contract or rebuild rules.

### `references/commands-and-modes.md`

Read when you need the exact expectations for learn mode, ask mode, and test mode.

### `references/scanned-pdfs-and-ocr.md`

Read when preprocessing suggests the PDF is scanned or image-only, or when the learner provides page images instead of extractable text.
