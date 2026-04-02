#!/usr/bin/env python3
"""Preprocess a book-like PDF or Markdown file into a reusable study cache."""

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
MARKDOWN_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
MARKDOWN_FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n?", re.DOTALL)


@dataclass
class Unit:
    unit_index: int
    unit_type: str
    label: str
    text: str


@dataclass
class Chunk:
    chunk_id: int
    unit_start: int
    unit_end: int
    unit_type: str
    label_start: str
    label_end: str
    text: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract text from a PDF or Markdown file and build a reusable study cache."
    )
    parser.add_argument("source", help="Path to the source PDF or Markdown file")
    parser.add_argument(
        "--out-dir",
        help="Optional cache directory. Defaults to a hash-based folder beside the source file.",
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


def detect_source_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return "pdf"
    if suffix in {".md", ".markdown"}:
        return "markdown"
    raise SystemExit(
        f"Unsupported source type: {path.suffix or '(none)'}. "
        "This version supports .pdf, .md, and .markdown."
    )


def require_pdftotext() -> None:
    try:
        subprocess.run(
            ["pdftotext", "-v"],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError as exc:
        raise SystemExit("pdftotext is required for PDF preprocessing but is not on PATH.") from exc


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def default_cache_dir(source_path: Path, file_hash: str) -> Path:
    return source_path.parent / ".book-pdf-study" / f"{source_path.stem}-{file_hash[:12]}"


def normalize_text(text: str) -> str:
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


def extract_pdf_units(source_path: Path) -> list[Unit]:
    require_pdftotext()
    result = subprocess.run(
        ["pdftotext", "-layout", "-enc", "UTF-8", str(source_path), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    pages = result.stdout.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    units = [
        Unit(unit_index=index, unit_type="page", label=f"Page {index}", text=normalize_text(text))
        for index, text in enumerate(pages, start=1)
    ]
    if not any(unit.text.strip() for unit in units):
        raise SystemExit(
            "Extracted text is empty. The PDF appears scanned or image-only and should "
            "go through an OCR step before learn mode, ask mode, or test mode can use it."
        )
    return units


def strip_markdown_frontmatter(text: str) -> str:
    return MARKDOWN_FRONTMATTER_RE.sub("", text, count=1)


def extract_markdown_units(source_path: Path) -> list[Unit]:
    text = source_path.read_text(encoding="utf-8")
    text = strip_markdown_frontmatter(text)
    text = normalize_text(text)
    if not text:
        raise SystemExit("The Markdown file is empty after normalization.")

    lines = text.splitlines()
    units: list[Unit] = []
    current_label = source_path.stem.replace("-", " ").strip() or "Document"
    current_lines: list[str] = []
    unit_index = 1

    def flush_current() -> None:
        nonlocal unit_index, current_lines
        section_text = "\n".join(current_lines).strip()
        if section_text:
            units.append(
                Unit(
                    unit_index=unit_index,
                    unit_type="section",
                    label=current_label,
                    text=section_text,
                )
            )
            unit_index += 1
        current_lines = []

    for line in lines:
        match = MARKDOWN_HEADING_RE.match(line)
        if match:
            flush_current()
            current_label = match.group(2).strip()
            continue
        current_lines.append(line)

    flush_current()
    if not units:
        units.append(Unit(unit_index=1, unit_type="section", label=current_label, text=text))
    return units


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def find_toc_candidates(source_kind: str, units: list[Unit]) -> list[str]:
    if source_kind == "markdown":
        return [unit.label for unit in units[:200]]

    candidates: list[str] = []
    for unit in units[:20]:
        for line in unit.text.splitlines():
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


def chunk_units(units: list[Unit], chunk_size: int, chunk_overlap: int) -> list[Chunk]:
    chunks: list[Chunk] = []
    chunk_id = 1
    for unit in units:
        if not unit.text:
            continue
        start = 0
        while start < len(unit.text):
            end = min(len(unit.text), start + chunk_size)
            if end < len(unit.text):
                split = unit.text.rfind("\n\n", start, end)
                if split <= start:
                    split = unit.text.rfind("\n", start, end)
                if split > start + max(100, chunk_size // 3):
                    end = split
            chunk_text = unit.text[start:end].strip()
            if chunk_text:
                chunks.append(
                    Chunk(
                        chunk_id=chunk_id,
                        unit_start=unit.unit_index,
                        unit_end=unit.unit_index,
                        unit_type=unit.unit_type,
                        label_start=unit.label,
                        label_end=unit.label,
                        text=chunk_text,
                    )
                )
                chunk_id += 1
            if end >= len(unit.text):
                break
            start = max(end - chunk_overlap, start + 1)
    return chunks


def likely_title(source_path: Path, source_kind: str, units: list[Unit]) -> str | None:
    if source_kind == "markdown" and units:
        return units[0].label
    for line in "\n".join(unit.text for unit in units[:3]).splitlines():
        stripped = line.strip()
        if 5 <= len(stripped) <= 120:
            return stripped
    if units:
        return units[0].label
    return source_path.stem


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
    source_path: Path,
    source_kind: str,
    units: list[Unit],
    toc_candidates: list[str],
    chunks: list[Chunk],
) -> str:
    title = likely_title(source_path, source_kind, units)
    nonempty_units = [unit for unit in units if unit.text.strip()]
    avg_chars = sum(len(unit.text) for unit in nonempty_units) / max(1, len(nonempty_units))
    heading_count = len(toc_candidates)
    difficulty = difficulty_label(avg_chars, heading_count)
    unit_label = "Page" if source_kind == "pdf" else "Section"
    lines = [
        f"# Book Analysis: {source_path.name}",
        "",
        f"- Source kind: {source_kind}",
        f"- Likely title: {title or 'Unknown'}",
        f"- {unit_label} count: {len(units)}",
        f"- Non-empty {unit_label.lower()}s: {len(nonempty_units)}",
        f"- Average characters per non-empty {unit_label.lower()}: {int(avg_chars)}",
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


def initial_state(source_path: Path, source_kind: str, file_hash: str) -> dict[str, object]:
    return {
        "source_path": str(source_path.resolve()),
        "source_kind": source_kind,
        "file_hash": file_hash,
        "target_depth": None,
        "current_level": None,
        "current_stage": "orientation",
        "covered_chapters": [],
        "mastery": {},
        "weak_points": [],
        "test_history": [],
    }


def write_unit_views(out_dir: Path, source_kind: str, units: list[Unit]) -> None:
    write_jsonl(
        out_dir / "units.jsonl",
        [
            {
                "unit_index": unit.unit_index,
                "unit_type": unit.unit_type,
                "label": unit.label,
                "char_count": len(unit.text),
                "text": unit.text,
            }
            for unit in units
        ],
    )
    if source_kind == "pdf":
        write_jsonl(
            out_dir / "pages.jsonl",
            [{"page": unit.unit_index, "char_count": len(unit.text), "text": unit.text} for unit in units],
        )
    if source_kind == "markdown":
        write_jsonl(
            out_dir / "sections.jsonl",
            [
                {
                    "section": unit.unit_index,
                    "label": unit.label,
                    "char_count": len(unit.text),
                    "text": unit.text,
                }
                for unit in units
            ],
        )


def main() -> int:
    args = parse_args()
    source_path = Path(args.source).expanduser().resolve()
    if not source_path.is_file():
        raise SystemExit(f"Source file not found: {source_path}")

    source_kind = detect_source_kind(source_path)
    file_hash = sha256_file(source_path)
    out_dir = (
        Path(args.out_dir).expanduser().resolve()
        if args.out_dir
        else default_cache_dir(source_path, file_hash)
    )
    manifest_path = out_dir / "manifest.json"

    if manifest_path.exists() and not args.force:
        print(str(out_dir))
        return 0

    if source_kind == "pdf":
        units = extract_pdf_units(source_path)
    else:
        units = extract_markdown_units(source_path)

    chunks = chunk_units(units, args.chunk_size, args.chunk_overlap)
    toc_candidates = find_toc_candidates(source_kind, units)

    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        manifest_path,
        {
            "source_path": str(source_path),
            "source_name": source_path.name,
            "source_kind": source_kind,
            "file_hash": file_hash,
            "unit_count": len(units),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "cache_dir": str(out_dir),
            "chunk_size": args.chunk_size,
            "chunk_overlap": args.chunk_overlap,
        },
    )
    write_unit_views(out_dir, source_kind, units)
    write_jsonl(
        out_dir / "chunks.jsonl",
        [
            {
                "chunk_id": chunk.chunk_id,
                "unit_start": chunk.unit_start,
                "unit_end": chunk.unit_end,
                "unit_type": chunk.unit_type,
                "label_start": chunk.label_start,
                "label_end": chunk.label_end,
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
        build_analysis(source_path, source_kind, units, toc_candidates, chunks),
        encoding="utf-8",
    )
    write_json(out_dir / "study-state.json", initial_state(source_path, source_kind, file_hash))

    print(str(out_dir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
