#!/usr/bin/env python3
"""Validate repository-local Markdown links and image paths without dependencies."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")
failures: list[str] = []

for document in [ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md")), *sorted((ROOT / "demo").rglob("*.md"))]:
    text = document.read_text(encoding="utf-8")
    for raw in LINK.findall(text):
        target = raw.strip().split(maxsplit=1)[0].strip("<>")
        if not target or target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        path_text = unquote(target.split("#", 1)[0])
        if not path_text:
            continue
        resolved = (document.parent / path_text).resolve()
        try:
            resolved.relative_to(ROOT)
        except ValueError:
            failures.append(f"{document.relative_to(ROOT)}: link escapes repository: {target}")
            continue
        if not resolved.exists():
            failures.append(f"{document.relative_to(ROOT)}: missing target: {target}")

if failures:
    print("\n".join(failures))
    sys.exit(1)

print("Documentation links and image paths are valid.")
