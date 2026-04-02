# Studying Book PDFs Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a user-installable Codex skill that preprocesses book-like PDFs once, then supports `/learn`, `/ask`, and `/test` workflows with persistent study state.

**Architecture:** The skill lives under the user skill directory and bundles one deterministic preprocessing script plus lightweight reference files. The script creates a stable cache layout beside each source PDF; the SKILL.md then instructs Codex how to trigger preprocessing, analyze the book, maintain state, and respond in each mode without repeatedly reading the entire PDF.

**Tech Stack:** Markdown, YAML frontmatter, Python 3 standard library, `pdftotext`, Codex skill folder conventions

---

## Chunk 1: Skill Scaffold And Plan Artifacts

### Task 1: Create the skill skeleton

**Files:**
- Create: `/home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs/`
- Create: `/home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs/SKILL.md`
- Create: `/home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs/agents/openai.yaml`
- Create: `/home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs/scripts/`
- Create: `/home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs/references/`

- [ ] **Step 1: Run the skill initializer**

Run: `python3 /root/.codex/skills/.system/skill-creator/scripts/init_skill.py studying-book-pdfs --path /root/.codex/skills --resources scripts,references --interface display_name='Study Book PDFs' --interface short_description='Learn from long book-style PDF files' --interface default_prompt='Use $studying-book-pdfs to help me study this book PDF.'`
Expected: a new skill directory with `SKILL.md`, `agents/openai.yaml`, and selected resource folders

- [ ] **Step 2: Inspect generated files**

Run: `find /home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs -maxdepth 3 -type f | sort`
Expected: generated skill files exist and no unexpected placeholders remain

### Task 2: Define cache contract and preprocessing behavior

**Files:**
- Create: `/home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs/references/cache-layout.md`
- Create: `/home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs/references/commands-and-modes.md`

- [ ] **Step 1: Write the cache layout reference**

Document: cache folder naming, required artifact files, and update rules

- [ ] **Step 2: Write the mode reference**

Document: `/learn`, `/ask`, `/test` semantics, required state updates, and minimal artifact reads per mode

## Chunk 2: Preprocessor Script

### Task 3: Add a deterministic PDF preprocessor

**Files:**
- Create: `/home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs/scripts/preprocess_book_pdf.py`

- [ ] **Step 1: Write a failing smoke test command**

Run: `python3 /home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs/scripts/preprocess_book_pdf.py --help`
Expected: if script is absent, command fails with file not found

- [ ] **Step 2: Write minimal script**

Implement: parse args, call `pdftotext`, split pages, write manifest/pages/chunks/toc candidates

- [ ] **Step 3: Verify script help works**

Run: `python3 /home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs/scripts/preprocess_book_pdf.py --help`
Expected: PASS and usage text appears

- [ ] **Step 4: Run a smoke test on a tiny generated PDF**

Run: a local smoke test that generates a tiny PDF or uses a provided sample, then executes the script and inspects created artifacts
Expected: cache directory contains the required files

## Chunk 3: Skill Authoring

### Task 4: Replace the generated skill template with production instructions

**Files:**
- Modify: `/home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs/SKILL.md`
- Modify: `/home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs/agents/openai.yaml`

- [ ] **Step 1: Write trigger-focused frontmatter**

Describe when the skill should load for book-style PDF learning tasks, not the workflow

- [ ] **Step 2: Write the skill body**

Cover: detection of book PDFs, preprocessing rules, goal/depth confirmation, persistent state, and `/learn` `/ask` `/test`

- [ ] **Step 3: Align UI metadata**

Ensure `display_name`, `short_description`, and `default_prompt` still match the final skill

## Chunk 4: Validation

### Task 5: Validate and smoke-test the finished skill

**Files:**
- Validate: `/home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs/`

- [ ] **Step 1: Run structural validation**

Run: `python3 /root/.codex/skills/.system/skill-creator/scripts/quick_validate.py /home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs`
Expected: PASS with no frontmatter or naming issues

- [ ] **Step 2: Review generated artifacts**

Run: `find /home/lmh/lmh/C++/book-pdf-study-skill/studying-book-pdfs -maxdepth 3 -type f | sort`
Expected: only intended files remain

- [ ] **Step 3: Record verification limits**

Document whether subagent forward-testing was skipped because the current harness policy does not allow spawning subagents without explicit user request
