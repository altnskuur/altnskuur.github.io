#!/usr/bin/env python3
"""
Build collection/index.json from the markdown files in collection/  (records → collection).

  collection/1_mug-photo.md          ← <number>_<any name>.md
  collection/2_english-presentation.md

Inside a file:

  ---
  link: https://youtu.be/…        ← youtube / drive / instagram link, or images/x.jpg; leave out for a plain note
  date: 2019-06-17                ← newest date shows first
  type: video                     ← optional, only needed for drive videos
  cover: images/x.jpg             ← optional own thumbnail
  ---
  # english presentation          ← header = caption
  the good old days …             ← note shown in the pop-up

Files starting with "_" (like _template.md) are skipped.
The deploy workflow runs this before every publish. Run locally:  python3 scripts/build_collection_index.py
"""
import json
import re
from pathlib import Path

from build_til_index import parse   # same front matter + header format as today i learned

COL = Path(__file__).resolve().parent.parent / "collection"
NAME = re.compile(r"^#?(\d+)[_\- ]?(.*)\.md$", re.IGNORECASE)


def main():
    COL.mkdir(exist_ok=True)
    entries = []
    for path in COL.glob("*.md"):
        if path.name.startswith("_"):
            continue
        m = NAME.match(path.name)
        if not m:
            print(f"  skipped {path.name} (name should start with a number, like 3_MyThing.md)")
            continue
        meta, header, body = parse(path.read_text(encoding="utf-8"))
        body = re.sub(r"<!--.*?-->", "", body, flags=re.S).strip()
        entries.append({
            "n": int(m.group(1)),
            "title": header or m.group(2) or path.stem,
            "date": meta.get("date", ""),
            "link": meta.get("link", ""),
            "type": meta.get("type", ""),
            "cover": meta.get("cover", ""),
            "note": body,
            "file": path.name,
        })
    entries.sort(key=lambda e: (e["date"], e["n"]), reverse=True)     # newest date first
    (COL / "index.json").write_text(json.dumps({"entries": entries}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"collection/index.json: {len(entries)} item(s)")


if __name__ == "__main__":
    main()
