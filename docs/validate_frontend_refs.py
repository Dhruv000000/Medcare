from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1] / "frontend"
PATTERNS = [
    re.compile(r"(?:href|src)\s*=\s*['\"]([^'\"]+)['\"]", re.I),
    re.compile(r"url\(\s*['\"]?([^)'\"\s]+)", re.I),
]
IGNORED_PREFIXES = ("http://", "https://", "//", "data:", "mailto:", "javascript:", "#")

errors: list[str] = []
references = 0

for source in sorted(ROOT.rglob("*")):
    if not source.is_file() or source.suffix.lower() not in {".html", ".css"}:
        continue
    text = source.read_text(encoding="utf-8", errors="replace")
    patterns = PATTERNS if source.suffix.lower() == ".html" else [PATTERNS[1]]
    for pattern in patterns:
        for value in pattern.findall(text):
            value = value.strip()
            if not value or value.startswith(IGNORED_PREFIXES):
                continue
            value = value.split("#", 1)[0].split("?", 1)[0]
            if not value:
                continue
            references += 1
            target = (source.parent / value).resolve()
            try:
                target.relative_to(ROOT.resolve())
            except ValueError:
                errors.append(f"OUTSIDE_FRONTEND: {source.relative_to(ROOT)} -> {value}")
                continue
            if not target.exists():
                errors.append(f"MISSING: {source.relative_to(ROOT)} -> {value}")

print(f"frontend_root={ROOT}")
print(f"local_references_checked={references}")
print(f"broken_references={len(errors)}")
for error in errors:
    print(error)
raise SystemExit(1 if errors else 0)
