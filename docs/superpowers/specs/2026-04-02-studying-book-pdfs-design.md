# Studying Book PDFs Design

**Goal:** Create a reusable Codex skill for learning from book-like PDF files without re-reading the full PDF on every turn.

## Problem

Book PDFs are expensive to revisit repeatedly. A useful skill needs to preprocess the PDF once, persist reusable artifacts, then drive a structured study workflow that adapts to the learner's goal and current level.

## Scope

The first version covers:

- Detecting when a PDF is likely a book or textbook rather than an arbitrary document
- Running a one-time preprocessing step that extracts reusable study artifacts
- Asking the learner to choose the target depth and describe the current level
- Supporting three explicit modes: `/learn`, `/ask`, and `/test`
- Persisting learning state between turns

The first version does not cover:

- OCR for scanned PDFs without extractable text
- Spaced repetition scheduling outside the current study session
- Rich UI or external databases

## User Model

The skill should guide the learner to declare:

- The desired outcome: introductory understanding, selected chapters, systematic understanding, interview readiness, project application, or deep reading
- The current level: zero background, partial familiarity, previously learned but rusty, or already partway through the book

The skill should then maintain:

- Current stage in the study flow
- Progress by chapter or topic
- Mastery estimates and weak points
- Recent `/test` outcomes

## Core Flow

1. Inspect the PDF and decide whether it looks like a book.
2. Run one-time preprocessing and write persistent artifacts beside the source PDF in a cache directory.
3. Summarize the book structure and assess apparent difficulty, density, and prerequisites.
4. Ask the user for goal depth and current level.
5. Enter explicit command-driven operation:
   - `/learn` advances the current learning stage
   - `/ask` explains a confusing passage, concept, chapter, or quoted snippet
   - `/test` checks understanding and updates progress

## Learning Stages

The skill should treat learning patterns as phases rather than mutually exclusive modes.

1. Orientation: clarify goal, level, and scope
2. Mapping: outline the book structure and dependencies
3. Understanding: chapter study with concise explanation plus plain-language restatement
4. Deepening: use guided questioning to expose gaps
5. Application: use exercises, cases, and interview-style prompts
6. Consolidation: convert key points into compact recall material
7. Assessment: triggered only when the user explicitly runs `/test`

Recommended pedagogies by stage:

- Mapping: outline-first
- Understanding: close reading + Feynman-style explanation
- Deepening: Socratic questioning
- Application: example-driven + interview Q&A
- Consolidation: flashcard-style recall

## Modes

### `/learn`

Advance the learner through the current stage. The output should be shaped by the learner goal and current mastery, not just chapter order.

### `/ask`

Handle local confusion. Support both:

- Precise input: pasted excerpt, page, or paragraph
- Loose input: chapter, concept, or theme

The response should explain:

- What the passage says
- Where the likely confusion is
- Why the author phrases it that way
- How it connects to surrounding context and the book's main line
- A clearer restatement and examples when useful

### `/test`

Run only on explicit command. Test the current stage, a chosen chapter, or the chosen target level. After testing, update mastery and recommend continue, review, or regress.

## Persistent Artifacts

The preprocessing step should create a stable cache directory for each source PDF. First version artifacts:

- `manifest.json`: source path, hash, page count, generation time
- `pages.jsonl`: extracted text per page
- `chunks.jsonl`: page-linked chunks for retrieval
- `toc_candidates.txt`: likely table-of-contents lines and headings
- `book-analysis.md`: agent-written summary of structure, difficulty, and prerequisites
- `study-state.json`: learner goal, current level, stage, progress, and test history

This design avoids re-reading the full PDF for each turn. Later turns can consult the cache files instead.

## Implementation Strategy

Use a bundled script driven by `pdftotext`, because it is available locally and avoids adding Python package dependencies. The script should normalize text, preserve page boundaries, and emit a predictable cache layout.

The skill body should instruct Codex to:

- Run the preprocessor once when the cache is missing or stale
- Read only the needed artifacts for a given mode
- Update `study-state.json` after `/learn` and `/test`
- Keep `/ask` targeted to the minimum relevant pages or chunks

## Validation

First-version validation should include:

- Skill folder structure validation via `quick_validate.py`
- Script smoke test on a small generated sample or a user-provided PDF
- Manual review that the skill description triggers on book-PDF learning requests
