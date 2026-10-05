#!/usr/bin/env python3
"""
Build til/index.json from the markdown files in til/.

  til/2026-10-06.md   ← one file per day, named with the date (YYYY-MM-DD.md)
  first line          ← the header shown on the website ("# architectural decisions")
  the rest            ← what you learned that day

Files starting with "_" (like _template.md) are skipped.
Numbers are given automatically: the oldest file is 1, the newest is the highest.

The deploy workflow runs this before every publish, so you only add .md files.
Run locally:  python3 scripts/build_til_index.py
"""
import json
import re
from pathlib import Path

TIL = Path(__file__).resolve().parent.parent / "til"
DATE = re.compile(r"^(\d{4}-\d{2}-\d{2})")


def header_of(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            return re.sub(r"^#+\s*", "", line).strip() or path.stem
    return path.stem


def main():
    TIL.mkdir(exist_ok=True)
    files = sorted(p for p in TIL.glob("*.md") if not p.name.startswith("_"))
    entries = []
    for n, path in enumerate(files, start=1):
        m = DATE.match(path.name)
        entries.append({
            "n": n,
            "title": header_of(path),
            "date": m.group(1) if m else None,
            "file": f"til/{path.name}",
        })
    entries.reverse()                       # newest first on the site
    (TIL / "index.json").write_text(json.dumps({"entries": entries}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"til/index.json: {len(entries)} entr{'y' if len(entries) == 1 else 'ies'}")


if __name__ == "__main__":
    main()
