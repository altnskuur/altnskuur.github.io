#!/usr/bin/env python3
"""
Build til/index.json from the markdown files in til/.

  til/1_HelloWorld.md            ← <number>_<any name>.md  (a leading "#" is allowed too)
  til/2_StructureofStg.md
  til/4_MyBelgradAdvanture.md

Inside a file:

  ---
  technical: true                ← optional: also show this note under stl → til
  ---
  # structure of stg             ← first line after the block = the header on the website
  what i learned …

Every note shows under records → til; notes with "technical: true" also show under stl → til.
The number in the file name is the number on the site (newest = highest, listed first).
Files starting with "_" (like _template.md) are skipped.

The deploy workflow runs this before every publish. Run locally:  python3 scripts/build_til_index.py
"""
import json
import re
from pathlib import Path

TIL = Path(__file__).resolve().parent.parent / "til"
NAME = re.compile(r"^#?(\d+)[_\- ]?(.*)\.md$", re.IGNORECASE)
TRUE = {"true", "yes", "1", "on"}


def parse(text):
    """→ (front matter dict, header, body)"""
    meta = {}
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                for raw in lines[1:i]:
                    if ":" in raw:
                        k, v = raw.split(":", 1)
                        meta[k.strip().lower()] = v.strip().strip("'\"")
                lines = lines[i + 1:]
                break
    header = ""
    while lines and not lines[0].strip():
        lines.pop(0)
    if lines:
        header = re.sub(r"^#+\s*", "", lines.pop(0).strip()).strip()
    return meta, header, "\n".join(lines).strip()


def main():
    TIL.mkdir(exist_ok=True)
    entries = []
    for path in TIL.glob("*.md"):
        if path.name.startswith("_"):
            continue
        m = NAME.match(path.name)
        if not m:
            print(f"  skipped {path.name} (name should start with a number, like 5_MyNote.md)")
            continue
        meta, header, _ = parse(path.read_text(encoding="utf-8"))
        entries.append({
            "n": int(m.group(1)),
            "title": header or m.group(2) or path.stem,
            "technical": meta.get("technical", "").lower() in TRUE,
            "file": path.name,
        })
    entries.sort(key=lambda e: e["n"], reverse=True)          # highest number first
    (TIL / "index.json").write_text(json.dumps({"entries": entries}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"til/index.json: {len(entries)} note(s), {sum(e['technical'] for e in entries)} technical")


if __name__ == "__main__":
    main()
