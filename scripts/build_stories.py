"""Generate the /stories/ section from the 'Stories for Ben' drafts.

Authoring tool only: reads book-order.md + Drafts/*.md from STORIES_REPO and
writes static HTML into this repo's stories/ folder. Re-run to resync.
"""
import html
import re
from pathlib import Path

STORIES_REPO = Path("/Users/luicheng/Hobby Projects/Stories for Ben")
REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "stories"

_SECTION_RE = re.compile(r"^##\s+\d+\.\s+(.+?)\s*$")
_ITEM_RE = re.compile(r"^\d+\.\s+(.+?)\s+—\s+`([^`]+)`")
_YEAR_RE = re.compile(r"year:\s*(.+?)\s*-->")


def slugify(title):
    s = title.strip().lower().replace("&", " and ")
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")


def clean_section(label):
    label = re.sub(r"\s*\(.*?\)\s*", "", label).strip()
    return label.title()


def parse_manifest(text):
    items = []
    section = None
    order = 0
    for line in text.splitlines():
        sm = _SECTION_RE.match(line)
        if sm:
            section = clean_section(sm.group(1))
            continue
        im = _ITEM_RE.match(line.strip())
        if im and section:
            order += 1
            items.append({
                "order": order,
                "title": im.group(1).strip(),
                "src": im.group(2).strip(),
                "section": section,
            })
    return items


def parse_draft(text):
    lines = text.splitlines()
    title = lines[0].lstrip("#").strip()
    year = None
    body_start = 1
    if len(lines) > 1 and lines[1].strip().startswith("<!--"):
        ym = _YEAR_RE.search(lines[1])
        if ym:
            raw = ym.group(1).strip()
            year = None if raw == "?" else raw
        body_start = 2
    body = "\n".join(lines[body_start:]).strip()
    paras = [
        " ".join(p.split())
        for p in re.split(r"\n\s*\n", body)
        if p.strip()
    ]
    return title, year, paras


def md_inline(text):
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text


def first_sentence(paras):
    if not paras:
        return ""
    m = re.search(r"^(.+?[.!?])(?:\s|$)", paras[0])
    return m.group(1) if m else paras[0]
