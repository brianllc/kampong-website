"""Generate the /stories/ section from the 'Stories for Ben' drafts.

Authoring tool only: reads book-order.md + Drafts/*.md from STORIES_REPO and
writes static HTML into this repo's stories/ folder. Re-run to resync.
"""
import html
import re
import shutil
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
    paras = []
    for p in re.split(r"\n\s*\n", body):
        if not p.strip():
            continue
        collapsed = " ".join(p.split())
        if re.fullmatch(r"!\[[^\]]*\]\([^)]*\)", collapsed):
            continue  # drop standalone image (images out of scope for v1)
        paras.append(collapsed)
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


FAVICON = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
    "viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' "
    "fill='%230F1A14'/%3E%3Ctext x='32' y='46' font-size='44' "
    "font-weight='bold' text-anchor='middle' fill='%23FF5C39' "
    "font-family='Arial'%3E*%3C/text%3E%3C/svg%3E"
)

_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{ogtitle}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="{ogtype}">
<meta property="og:url" content="{ogurl}">
<link rel="icon" href="{favicon}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600&family=Archivo+Black&family=Lora:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/stories/stories.css">
</head>"""

_NAV = """<nav>
  <a class="wordmark" href="/">KAMPONG<span>*</span></a>
  <a class="back" href="/stories/">← ALL STORIES</a>
</nav>"""

_FOOTER = """<footer>
  <span>© 2026 KAMPONG.COM.SG</span>
  <span>MADE WITH ❤ IN SINGAPORE</span>
</footer>"""


def nav_links(prev, nxt):
    if prev:
        left = ('<a class="prev" href="/stories/{s}/">← {t}</a>'
                .format(s=prev["slug"], t=html.escape(prev["title"], quote=False)))
    else:
        left = '<span class="prev disabled"></span>'
    if nxt:
        right = ('<a class="next" href="/stories/{s}/">{t} →</a>'
                 .format(s=nxt["slug"], t=html.escape(nxt["title"], quote=False)))
    else:
        right = '<span class="next disabled"></span>'
    return (
        '<nav class="storynav">\n  ' + left
        + '\n  <a class="collection" href="/stories/">The Collection</a>\n  '
        + right + '\n</nav>'
    )


def render_story_page(item, prev, nxt):
    esc_title = html.escape(item["title"], quote=False)
    meta = item["section"]
    if item.get("year"):
        meta += " · " + item["year"]
    parts = []
    for p in item["paras"]:
        if p == "---":
            parts.append('<hr class="story-sep">')
        else:
            parts.append("<p>{}</p>".format(md_inline(p)))
    paras = "\n".join(parts)
    head = _HEAD.format(
        title="{} — Kampong Stories".format(esc_title),
        desc=html.escape(first_sentence(item["paras"]), quote=True),
        ogtitle=html.escape(item["title"], quote=True),
        ogtype="article",
        ogurl="https://kampong.com.sg/stories/{}/".format(item["slug"]),
        favicon=FAVICON,
    )
    return """{head}
<body class="story">
{nav}
<article class="story-body">
  <p class="meta">{meta}</p>
  <h1 class="display">{title}</h1>
{paras}
</article>
{storynav}
{footer}
</body>
</html>
""".format(head=head, nav=_NAV, meta=html.escape(meta, quote=False),
           title=esc_title, paras=paras,
           storynav=nav_links(prev, nxt), footer=_FOOTER)


SUBTITLE = ("<em>The Little Boy Dreaming by the Window</em> — a Singapore "
            "childhood in the late 1980s and early 1990s, told for Ben.")


def render_index_page(groups):
    head = _HEAD.format(
        title="Stories — Kampong",
        desc="Brian's childhood in 1980s–90s Singapore, a storybook told for his son Ben.",
        ogtitle="Kampong Stories",
        ogtype="website",
        ogurl="https://kampong.com.sg/stories/",
        favicon=FAVICON,
    )
    blocks = []
    for g in groups:
        lis = []
        for s in g["stories"]:
            lis.append(
                '    <li><a href="/stories/{slug}/">'
                '<span class="st">{title}</span> '
                '<span class="sy">{year}</span></a>'
                '<p class="teaser">{teaser}</p></li>'.format(
                    slug=s["slug"],
                    title=html.escape(s["title"], quote=False),
                    year=html.escape(s["year"] or "", quote=False),
                    teaser=html.escape(s["teaser"], quote=False),
                )
            )
        blocks.append(
            '  <section class="group">\n'
            '    <h2 class="group-title">{sec}</h2>\n'
            '    <ol class="story-list">\n{items}\n    </ol>\n'
            '  </section>'.format(
                sec=html.escape(g["section"], quote=False),
                items="\n".join(lis),
            )
        )
    return """{head}
<body class="index">
{nav}
<header class="collection-hero">
  <h1 class="display">STORIES</h1>
  <p class="subtitle">{subtitle}</p>
</header>
<main>
{groups}
</main>
{footer}
</body>
</html>
""".format(head=head, nav=_NAV, subtitle=SUBTITLE,
           groups="\n".join(blocks), footer=_FOOTER)


def load_stories():
    """Return ordered list of fully-parsed story dicts from the manifest."""
    manifest = (STORIES_REPO / "book-order.md").read_text(encoding="utf-8")
    items = parse_manifest(manifest)
    stories = []
    for it in items:
        draft = (STORIES_REPO / it["src"]).read_text(encoding="utf-8")
        title, year, paras = parse_draft(draft)
        stories.append({
            "title": title,
            "slug": slugify(title),
            "section": it["section"],
            "year": year,
            "paras": paras,
            "teaser": first_sentence(paras),
        })
    return stories


def group_by_section(stories):
    groups = []
    for s in stories:
        if not groups or groups[-1]["section"] != s["section"]:
            groups.append({"section": s["section"], "stories": []})
        groups[-1]["stories"].append(s)
    return groups


def build():
    stories = load_stories()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Remove stale story subdirectories from prior runs (slugs change when
    # a story title is edited) so re-running is a clean resync.
    for child in OUT_DIR.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
    # index
    (OUT_DIR / "index.html").write_text(
        render_index_page(group_by_section(stories)), encoding="utf-8"
    )
    # story pages
    for i, s in enumerate(stories):
        prev = stories[i - 1] if i > 0 else None
        nxt = stories[i + 1] if i < len(stories) - 1 else None
        page_dir = OUT_DIR / s["slug"]
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "index.html").write_text(
            render_story_page(s, prev, nxt), encoding="utf-8"
        )
    print("Generated {} story pages + index into {}".format(len(stories), OUT_DIR))
    for s in stories:
        print("  /stories/{}/  — {}".format(s["slug"], s["title"]))


if __name__ == "__main__":
    build()
