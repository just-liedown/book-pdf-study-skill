#!/usr/bin/env python3
"""Preprocess a book-like PDF into a reusable study cache."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


HEADING_RE = re.compile(
    r"^\s*((chapter|part|section|appendix)\b|(\d+(\.\d+){0,3}\s+\S+))",
    re.IGNORECASE,
)
TOC_RE = re.compile(r"\.{2,}\s*\d+\s*$|^\s*\d+(\.\d+){0,3}\s+\S+")


@dataclass
class Chunk:
    chunk_id: int
    page_start: int
    page_end: int
    text: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract text from a PDF and build a reusable study cache."
    )
    parser.add_argument("pdf", help="Path to the source PDF")
    parser.add_argument(
        "--out-dir",
        help="Optional cache directory. Defaults to a hash-based folder beside the PDF.",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1200,
        help="Target character size for retrieval chunks. Default: 1200",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=150,
        help="Character overlap between adjacent chunks. Default: 150",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Rebuild the cache even if files already exist.",
    )
    return parser.parse_args()


def require_pdftotext() -> None:
    try:
        subprocess.run(
            ["pdftotext", "-v"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError as exc:
        raise SystemExit("pdftotext is required but not installed or not on PATH.") from exc


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def default_cache_dir(pdf_path: Path, file_hash: str) -> Path:
    return pdf_path.parent / ".book-pdf-study" / f"{pdf_path.stem}-{file_hash[:12]}"


def extract_text(pdf_path: Path) -> list[str]:
    result = subprocess.run(
        ["pdftotext", "-layout", "-enc", "UTF-8", str(pdf_path), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    pages = result.stdout.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    return [normalize_page_text(page) for page in pages]


def normalize_page_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.rstrip() for line in text.splitlines()]
    collapsed: list[str] = []
    blank_run = 0
    for line in lines:
        if line.strip():
            blank_run = 0
            collapsed.append(line)
            continue
        blank_run += 1
        if blank_run <= 1:
            collapsed.append("")
    return "\n".join(collapsed).strip()


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def find_toc_candidates(pages: list[str]) -> list[str]:
    candidates: list[str] = []
    for page in pages[:20]:
        for line in page.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if TOC_RE.search(stripped) or HEADING_RE.search(stripped):
                candidates.append(stripped)
    seen: set[str] = set()
    unique: list[str] = []
    for line in candidates:
        if line in seen:
            continue
        seen.add(line)
        unique.append(line)
    return unique[:200]


def chunk_pages(pages: list[str], chunk_size: int, chunk_overlap: int) -> list[Chunk]:
    chunks: list[Chunk] = []
    chunk_id = 1
    for page_number, page_text in enumerate(pages, start=1):
        if not page_text:
            continue
        text = page_text
        start = 0
        while start < len(text):
            end = min(len(text), start + chunk_size)
            if end < len(text):
                split = text.rfind("\n\n", start, end)
                if split <= start:
                    split = text.rfind("\n", start, end)
                if split > start + max(100, chunk_size // 3):
                    end = split
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(
                    Chunk(
                        chunk_id=chunk_id,
                        page_start=page_number,
                        page_end=page_number,
                        text=chunk_text,
                    )
                )
                chunk_id += 1
            if end >= len(text):
                break
            start = max(end - chunk_overlap, start + 1)
    return chunks


def likely_title(pages: list[str]) -> str | None:
    for line in "\n".join(pages[:3]).splitlines():
        stripped = line.strip()
        if len(stripped) < 5:
            continue
        if len(stripped) > 120:
            continue
        return stripped
    return None


def difficulty_label(avg_chars: float, heading_count: int) -> str:
    if avg_chars > 2500 and heading_count > 30:
        return "high"
    if avg_chars > 1200:
        return "medium"
    return "low"


def prerequisite_guess(title: str | None, toc_candidates: list[str]) -> str:
    haystack = " ".join(filter(None, [title] + toc_candidates[:40])).lower()
    if any(word in haystack for word in ["advanced", "compiler", "distributed", "optimization"]):
        return "Likely requires prior domain knowledge."
    if any(word in haystack for word in ["introduction", "beginner", "basics", "fundamentals"]):
        return "Likely beginner-friendly with limited prerequisites."
    return "Prerequisites unclear from preprocessing alone."


def build_analysis(
    pdf_path: Path, pages: list[str], toc_candidates: list[str], chunks: list[Chunk]
) -> str:
    title = likely_title(pages)
    nonempty_pages = [page for page in pages if page.strip()]
    avg_chars = sum(len(page) for page in nonempty_pages) / max(1, len(nonempty_pages))
    heading_count = sum(
        1 for line in toc_candidates if HEADING_RE.search(line) or TOC_RE.search(line)
    )
    difficulty = difficulty_label(avg_chars, heading_count)
    lines = [
        f"# Book Analysis: {pdf_path.name}",
        "",
        f"- Likely title: {title or 'Unknown'}",
        f"- Page count: {len(pages)}",
        f"- Non-empty pages: {len(nonempty_pages)}",
        f"- Average characters per non-empty page: {int(avg_chars)}",
        f"- Retrieval chunks: {len(chunks)}",
        f"- Structure confidence: {'medium' if toc_candidates else 'low'}",
        f"- Difficulty guess: {difficulty}",
        f"- Prerequisite guess: {prerequisite_guess(title, toc_candidates)}",
        "",
        "## Notes",
        "",
        "- This file is heuristic and should be refined during later study turns.",
        "- Use toc_candidates.txt and chunks.jsonl before claiming chapter boundaries are exact.",
    ]
    return "\n".join(lines) + "\n"


def initial_state(pdf_path: Path, file_hash: str) -> dict[str, object]:
    return {
        "source_pdf": str(pdf_path.resolve()),
        "file_hash": file_hash,
        "target_depth": None,
        "current_level": None,
        "current_stage": "orientation",
        "covered_chapters": [],
        "mastery": {},
        "weak_points": [],
        "test_history": [],
    }


def main() -> int:
    args = parse_args()
    require_pdftotext()

    pdf_path = Path(args.pdf).expanduser().resolve()
    if not pdf_path.is_file():
        raise SystemExit(f"PDF not found: {pdf_path}")

    file_hash = sha256_file(pdf_path)
    out_dir = (
        Path(args.out_dir).expanduser().resolve()
        if args.out_dir
        else default_cache_dir(pdf_path, file_hash)
    )
    manifest_path = out_dir / "manifest.json"

    if manifest_path.exists() and not args.force:
        print(str(out_dir))
        return 0

    pages = extract_text(pdf_path)
    if not any(page.strip() for page in pages):
        raise SystemExit("Extracted text is empty. The PDF may be scanned or image-only.")

    chunks = chunk_pages(pages, args.chunk_size, args.chunk_overlap)
    toc_candidates = find_toc_candidates(pages)

    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        manifest_path,
        {
            "source_pdf": str(pdf_path),
            "pdf_name": pdf_path.name,
            "file_hash": file_hash,
            "page_count": len(pages),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "cache_dir": str(out_dir),
            "chunk_size": args.chunk_size,
            "chunk_overlap": args.chunk_overlap,
        },
    )
    write_jsonl(
        out_dir / "pages.jsonl",
        [
            {"page": index, "char_count": len(text), "text": text}
            for index, text in enumerate(pages, start=1)
        ],
    )
    write_jsonl(
        out_dir / "chunks.jsonl",
        [
            {
                "chunk_id": chunk.chunk_id,
                "page_start": chunk.page_start,
                "page_end": chunk.page_end,
                "char_count": len(chunk.text),
                "text": chunk.text,
            }
            for chunk in chunks
        ],
    )
    (out_dir / "toc_candidates.txt").write_text(
        "\n".join(toc_candidates) + ("\n" if toc_candidates else ""),
        encoding="utf-8",
    )
    (out_dir / "book-analysis.md").write_text(
        build_analysis(pdf_path, pages, toc_candidates, chunks), encoding="utf-8"
    )
    write_json(out_dir / "study-state.json", initial_state(pdf_path, file_hash))

    print(str(out_dir))
    return 0


if __name__ == "__main__":
    sys.exit(main())
