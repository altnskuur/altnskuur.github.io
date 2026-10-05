#!/usr/bin/env python3
"""
Sync the Notion "Knowledge DB" into this repo.

Only pages whose Status is "Published" are copied. For each one we write
  knowledge/<slug>.md                 the page body as markdown
  knowledge/assets/<page-id>/...      images (Notion image links expire, so we download them)
  knowledge/index.json                list of pages + their properties (the website reads this)

Pages that are no longer "Published" are removed on the next run.

Needs two environment variables (set them as GitHub Actions secrets):
  NOTION_TOKEN        the secret of a Notion integration that has access to Knowledge DB
  NOTION_KNOWLEDGE_DB the database id (default: altnskuur's Knowledge DB)

Run locally:  NOTION_TOKEN=secret_xxx python3 scripts/notion_sync.py
"""
import json
import os
import re
import shutil
import sys
import time
import unicodedata
from pathlib import Path

import requests

NOTION_VERSION = "2022-06-28"
API = "https://api.notion.com/v1"
DEFAULT_DB = "343945c9dc43805c9ea8fc84b5861fd6"
PUBLISH_STATUS = "Published"

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "knowledge"
ASSETS = OUT / "assets"


# --------------------------------------------------------------------------- api

class Notion:
    def __init__(self, token):
        self.s = requests.Session()
        self.s.headers.update({
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        })
        self._pages = {}

    def _req(self, method, path, **kw):
        for attempt in range(6):
            r = self.s.request(method, API + path, timeout=30, **kw)
            if r.status_code == 429 or r.status_code >= 500:      # rate limit / hiccup: back off
                time.sleep(float(r.headers.get("Retry-After", 2 ** attempt)))
                continue
            if not r.ok:
                raise RuntimeError(f"Notion API {r.status_code} on {path}: {r.text[:300]}")
            time.sleep(0.35)                                      # stay under ~3 requests/second
            return r.json()
        raise RuntimeError(f"Notion API kept failing on {path}")

    def query_published(self, db_id):
        body = {"filter": {"property": "Status", "status": {"equals": PUBLISH_STATUS}}, "page_size": 100}
        pages, cursor = [], None
        while True:
            if cursor:
                body["start_cursor"] = cursor
            data = self._req("POST", f"/databases/{db_id}/query", json=body)
            pages += data["results"]
            if not data.get("has_more"):
                return pages
            cursor = data["next_cursor"]

    def page(self, page_id):
        """One page with its properties (cached: parents are looked up many times)."""
        if page_id not in self._pages:
            self._pages[page_id] = self._req("GET", f"/pages/{page_id}")
        return self._pages[page_id]

    def children(self, block_id):
        out, cursor = [], None
        while True:
            q = f"?page_size=100" + (f"&start_cursor={cursor}" if cursor else "")
            data = self._req("GET", f"/blocks/{block_id}/children{q}")
            out += data["results"]
            if not data.get("has_more"):
                return out
            cursor = data["next_cursor"]


# ------------------------------------------------------------------ rich text → md

def rich(rt_list):
    """Notion rich text array → inline markdown."""
    out = []
    for rt in rt_list or []:
        if rt["type"] == "equation":
            out.append(f"${rt['equation']['expression']}$")
            continue
        text = rt.get("plain_text", "")
        if not text:
            continue
        a = rt.get("annotations", {})
        if a.get("code"):
            text = f"`{text}`"
        else:
            # keep leading/trailing spaces outside the markers so **x ** doesn't break
            lead = text[: len(text) - len(text.lstrip())]
            trail = text[len(text.rstrip()):]
            core = text.strip()
            if core:
                if a.get("bold"):
                    core = f"**{core}**"
                if a.get("italic"):
                    core = f"*{core}*"
                if a.get("strikethrough"):
                    core = f"~~{core}~~"
            text = lead + core + trail
        href = rt.get("href")
        if href:
            text = f"[{text}]({href})"
        out.append(text)
    return "".join(out)


def plain(rt_list):
    return "".join(rt.get("plain_text", "") for rt in rt_list or [])


# ---------------------------------------------------------------- blocks → md

class Converter:
    def __init__(self, notion, page_id):
        self.n = notion
        self.page_id = page_id
        self.img_dir = ASSETS / page_id
        self.img_count = 0

    def image(self, block):
        img = block["image"]
        caption = plain(img.get("caption"))
        if img["type"] == "external":
            return f"![{caption}]({img['external']['url']})"
        url = img["file"]["url"]
        ext = os.path.splitext(url.split("?")[0])[1].lower() or ".png"
        if ext not in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"):
            ext = ".png"
        self.img_count += 1
        self.img_dir.mkdir(parents=True, exist_ok=True)
        name = f"{self.img_count:02d}{ext}"
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        (self.img_dir / name).write_bytes(r.content)
        return f"![{caption}](knowledge/assets/{self.page_id}/{name})"

    def table(self, block):
        rows = self.n.children(block["id"])
        cells = [[rich(c).replace("|", "\\|").replace("\n", " ") for c in r["table_row"]["cells"]] for r in rows]
        if not cells:
            return ""
        width = max(len(r) for r in cells)
        cells = [r + [""] * (width - len(r)) for r in cells]
        head = cells[0] if block["table"].get("has_column_header") else [""] * width
        body = cells[1:] if block["table"].get("has_column_header") else cells
        lines = ["| " + " | ".join(head) + " |", "|" + "---|" * width]
        lines += ["| " + " | ".join(r) + " |" for r in body]
        return "\n".join(lines)

    LIST_TYPES = ("bulleted_list_item", "numbered_list_item", "to_do")

    def blocks(self, block_id, depth=0):
        """Convert a block's children to markdown lines.
        depth = list nesting level (only list items indent their children)."""
        lines = []
        indent = "  " * depth
        number = 0
        prev = None
        for b in self.n.children(block_id):
            t = b["type"]
            number = number + 1 if t == "numbered_list_item" else 0
            if prev in self.LIST_TYPES and t not in self.LIST_TYPES:
                lines.append("")                    # close the list before the next block
            prev = t
            d = b.get(t, {})
            child_depth = depth + 1 if t in self.LIST_TYPES else depth
            sub = self.blocks(b["id"], child_depth) if b.get("has_children") and t not in ("table", "child_page", "child_database") else []

            if t == "paragraph":
                lines += [indent + rich(d["rich_text"]), ""] + sub
            elif t in ("heading_1", "heading_2", "heading_3"):
                level = {"heading_1": "#", "heading_2": "##", "heading_3": "###"}[t]
                lines += [f"{level} {rich(d['rich_text'])}", ""]
                if sub:                      # toggle headings keep their content
                    lines += sub
            elif t == "bulleted_list_item":
                lines += [f"{indent}- {rich(d['rich_text'])}"] + sub
            elif t == "numbered_list_item":
                lines += [f"{indent}{number}. {rich(d['rich_text'])}"] + sub
            elif t == "to_do":
                box = "x" if d.get("checked") else " "
                lines += [f"{indent}- [{box}] {rich(d['rich_text'])}"] + sub
            elif t == "quote":
                lines += ["> " + rich(d["rich_text"]).replace("\n", "\n> "), ""] + sub
            elif t == "callout":
                icon = (d.get("icon") or {}).get("emoji", "")
                lines += [f"> {icon} {rich(d['rich_text'])}".rstrip()] + ["> " + s for s in sub if s.strip()] + [""]
            elif t == "toggle":
                lines += [f"**{rich(d['rich_text'])}**", ""] + sub + [""]
            elif t == "code":
                lang = (d.get("language") or "").replace("plain text", "")
                lines += [f"```{lang}", plain(d["rich_text"]), "```", ""]
            elif t == "equation":
                lines += ["$$", d["expression"], "$$", ""]
            elif t == "divider":
                lines += ["---", ""]
            elif t == "image":
                lines += [self.image(b), ""]
            elif t == "table":
                lines += [self.table(b), ""]
            elif t in ("bookmark", "embed", "link_preview"):
                url = d.get("url", "")
                if url:
                    lines += [f"[{plain(d.get('caption')) or url}]({url})", ""]
            elif t == "column_list":
                lines += sub
            elif t == "column":
                lines += sub
            elif t in ("child_page", "child_database", "table_of_contents", "breadcrumb", "synced_block", "unsupported"):
                lines += sub
            else:
                txt = rich(d.get("rich_text")) if isinstance(d, dict) else ""
                if txt:
                    lines += [indent + txt, ""]
                lines += sub
        return lines


# ---------------------------------------------------------------------- helpers

def slugify(title, page_id):
    s = title.replace("ı", "i").replace("İ", "I")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()[:60] or "page"
    return f"{s}-{page_id.replace('-', '')[:8]}"


def prop(page, name):
    p = page["properties"].get(name)
    if not p:
        return None
    t = p["type"]
    if t == "title":
        return plain(p["title"])
    if t == "rich_text":
        return plain(p["rich_text"]) or None
    if t in ("select", "status"):
        return (p[t] or {}).get("name")
    if t == "last_edited_time":
        return p["last_edited_time"]
    return None


def parent_id(page):
    """The page's "Parent item" relation (one page at most), as a dash-less id."""
    p = page["properties"].get("Parent item")
    if not p or p["type"] != "relation" or not p["relation"]:
        return None
    return p["relation"][0]["id"].replace("-", "")


def ancestors(n, page, published):
    """Parents from nearest to the top, as (id, title, domain). Unpublished parents
    are fetched from Notion too, so a published child still knows where it belongs."""
    chain, seen = [], {page["id"].replace("-", "")}
    pid = parent_id(page)
    while pid and pid not in seen and len(chain) < 8:
        seen.add(pid)
        try:
            parent = published.get(pid) or n.page(pid)
        except RuntimeError:
            break                                   # parent deleted / no access: stop here
        if parent.get("archived") or parent.get("in_trash"):
            break
        chain.append((pid, prop(parent, "Name") or "untitled", prop(parent, "Domain")))
        pid = parent_id(parent)
    return chain


def tidy(lines):
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


# ------------------------------------------------------------------------- main

def main():
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        sys.exit("NOTION_TOKEN is not set")
    db = os.environ.get("NOTION_KNOWLEDGE_DB", DEFAULT_DB).replace("-", "")
    n = Notion(token)

    pages = n.query_published(db)
    print(f"{len(pages)} published page(s)")

    OUT.mkdir(exist_ok=True)
    if ASSETS.exists():
        shutil.rmtree(ASSETS)                 # rebuilt from scratch each run
    keep, items = set(), []
    published = {p["id"].replace("-", ""): p for p in pages}

    for page in pages:
        pid = page["id"].replace("-", "")
        title = prop(page, "Name") or "untitled"
        chain = ancestors(n, page, published)
        # no Domain of its own → use the nearest parent's
        domain = prop(page, "Domain") or next((d for _, _, d in chain if d), None)
        slug = slugify(title, pid)
        body = tidy(Converter(n, pid).blocks(page["id"]))
        (OUT / f"{slug}.md").write_text(body, encoding="utf-8")
        keep.add(f"{slug}.md")
        items.append({
            "id": pid,
            "slug": slug,
            "title": title,
            # parent = nearest PUBLISHED ancestor (the site nests the page under it);
            # path = every ancestor title from the top, published or not (shown as a breadcrumb)
            "parent": next((a for a, _, _ in chain if a in published), None),
            "path": [t for _, t, _ in reversed(chain)],
            "domain": domain,
            "confidence": prop(page, "Confidence Level"),
            "summary": prop(page, "Summary"),
            "updated": (page.get("last_edited_time") or "")[:10],
            "edited": page.get("last_edited_time"),     # full timestamp, the site sorts by it
            "file": f"knowledge/{slug}.md",
        })
        print(f"  ✓ {title}")

    for f in OUT.glob("*.md"):                # drop pages that are no longer published
        if f.name not in keep:
            f.unlink()
            print(f"  ✗ removed {f.name}")

    items.sort(key=lambda i: (i["domain"] or "~", [t.lower() for t in i["path"]], i["title"].lower()))
    index = {"items": items}                  # no timestamp, so unchanged content = no new commit
    (OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
