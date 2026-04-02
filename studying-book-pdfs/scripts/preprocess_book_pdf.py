#!/usr/bin/env python3
"""Compatibility wrapper for the generic book-material preprocessor."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    script = Path(__file__).with_name("preprocess_book_material.py")
    return subprocess.call([sys.executable, str(script), *sys.argv[1:]])


if __name__ == "__main__":
    raise SystemExit(main())
