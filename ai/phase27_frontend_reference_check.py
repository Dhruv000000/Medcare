from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "frontend"


class ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        for name in ("href", "src"):
            value = attr_map.get(name)
            if value:
                self.references.append(value)


def is_local(value: str) -> bool:
    return not value.startswith(("#", "/", "//", "http:", "https:", "mailto:", "tel:", "data:", "javascript:"))


def css_urls(text: str) -> list[str]:
    values: list[str] = []
    remainder = text
    while "url(" in remainder:
        remainder = remainder.split("url(", 1)[1]
        if ")" not in remainder:
            break
        value, remainder = remainder.split(")", 1)
        values.append(value.strip().strip("'\""))
    return values


checked = 0
missing: list[str] = []
files_scanned = 0
for html_path in ROOT.rglob("*.html"):
    files_scanned += 1
    parser = ReferenceParser()
    parser.feed(html_path.read_text(encoding="utf-8"))
    references = parser.references
    for value in references:
        value = value.split("#", 1)[0].split("?", 1)[0]
        if not value or not is_local(value):
            continue
        checked += 1
        target = (html_path.parent / value).resolve()
        if not target.is_file() or (ROOT.resolve() not in target.parents and target != ROOT.resolve()):
            missing.append(f"{html_path.relative_to(ROOT)} -> {value}")

for css_path in ROOT.rglob("*.css"):
    files_scanned += 1
    for raw_value in css_urls(css_path.read_text(encoding="utf-8")):
        value = raw_value.split("#", 1)[0].split("?", 1)[0]
        if not value or not is_local(value):
            continue
        checked += 1
        target = (css_path.parent / value).resolve()
        if not target.is_file() or (ROOT.resolve() not in target.parents and target != ROOT.resolve()):
            missing.append(f"{css_path.relative_to(ROOT)} -> {value}")

result = {
    "files_scanned": files_scanned,
    "local_references_checked": checked,
    "missing_references": missing,
    "all_checks_passed": not missing,
}
print(json.dumps(result, indent=2))
raise SystemExit(0 if not missing else 1)
