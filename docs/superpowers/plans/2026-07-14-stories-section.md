# Stories Section Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish Brian's 14-story childhood collection as a warm, readable `/stories/` section on kampong.com.sg, generated from the drafts in the separate `Stories for Ben` repo.

**Architecture:** A stdlib-only Python generator (`scripts/build_stories.py`) reads `book-order.md` (manifest) + `Drafts/*.md` from the Stories repo and emits static HTML into `stories/` in this repo: a dark on-brand index and 14 light "storybook" reading pages. A hand-authored `stories/stories.css` styles them. Deploy stays pure-static (`git push master`); re-running the generator is the resync mechanism.

**Tech Stack:** Python 3 (stdlib `re`, `html`, `pathlib`, `unittest` — no third-party deps), static HTML/CSS, Google Fonts (Archivo, Archivo Black, Lora).

## Global Constraints

- **Served site stays zero-build static HTML.** The generator is an authoring tool; only its static HTML output plus the hand-authored CSS are served.
- **Python: stdlib only.** No pip installs. Tests use `unittest`, run with `python3 -m unittest`.
- **Source of truth is the Stories repo**, default path `/Users/luicheng/Hobby Projects/Stories for Ben` — a `STORIES_REPO` constant in the generator; never edit files there.
- **URL slugs derive from the book title** (lowercase, punctuation dropped, spaces→hyphens). Links and asset refs are absolute (`/stories/...`, `/stories/stories.css`) — the custom domain serves at root.
- **Palette (reuse verbatim):** `--ink:#0F1A14; --ink-2:#16241C; --paper:#F4F1E8; --chili:#FF5C39; --palm:#7BE0AD; --mustard:#E8C547; --line:#2A3D32`.
- **Publish all 14 drafts as-is**; strip the `<!-- status: … -->` comment. Years shown verbatim (e.g. "~1987"); a `year: ?` is omitted.
- **Commits use the repo-local noreply email** (`28775822+brianllc@users.noreply.github.com`); pushing `master` publishes live (GH007 rejects other emails).
- **Favicon (reuse homepage data-URI):** `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%230F1A14'/%3E%3Ctext x='32' y='46' font-size='44' font-weight='bold' text-anchor='middle' fill='%23FF5C39' font-family='Arial'%3E*%3C/text%3E%3C/svg%3E`

---

### Task 1: Pure parsing & text helpers (TDD)

Build and test the pure functions that turn manifest + draft text into structured data. No file I/O yet.

**Files:**
- Create: `scripts/build_stories.py`
- Test: `scripts/test_build_stories.py`

**Interfaces:**
- Produces (used by Tasks 3 & 4):
  - `slugify(title: str) -> str`
  - `clean_section(label: str) -> str`
  - `parse_manifest(text: str) -> list[dict]` — each dict `{"order": int, "title": str, "src": str, "section": str}` in book order
  - `parse_draft(text: str) -> tuple[str, str|None, list[str]]` — `(title, year_or_None, paragraphs)`
  - `md_inline(text: str) -> str` — HTML-escaped with `**bold**`/`*italic*` converted
  - `first_sentence(paras: list[str]) -> str` — plain-text teaser (first sentence of first paragraph)

- [ ] **Step 1: Write the failing tests**

```python
# scripts/test_build_stories.py
import unittest
import build_stories as b


class TestSlugify(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(b.slugify("Primary One"), "primary-one")

    def test_punctuation_and_number(self):
        self.assertEqual(
            b.slugify("Getting Better in Chinese, Part 1"),
            "getting-better-in-chinese-part-1",
        )

    def test_ampersand(self):
        self.assertEqual(b.slugify("Spoons & Balloons"), "spoons-and-balloons")


class TestCleanSection(unittest.TestCase):
    def test_strips_parenthetical_and_titlecases(self):
        self.assertEqual(b.clean_section("Lower primary (P1 to P3)"), "Lower Primary")

    def test_plain(self):
        self.assertEqual(b.clean_section("Kindergarten"), "Kindergarten")


MANIFEST = """# Book Order

## 1. Kindergarten

1. Kindergarten — `Drafts/my-first-day-at-kindergarten.md`
2. Spoons and Balloons — `Drafts/spoons-and-balloons.md`

## 2. Lower primary (P1 to P3)

4. Primary One — `Drafts/first-day-of-primary-school.md` *(placement tentative)*
"""


class TestParseManifest(unittest.TestCase):
    def test_order_and_fields(self):
        items = b.parse_manifest(MANIFEST)
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]["title"], "Kindergarten")
        self.assertEqual(items[0]["src"], "Drafts/my-first-day-at-kindergarten.md")
        self.assertEqual(items[0]["section"], "Kindergarten")
        self.assertEqual(items[2]["title"], "Primary One")
        self.assertEqual(items[2]["section"], "Lower Primary")
        self.assertEqual(items[2]["src"], "Drafts/first-day-of-primary-school.md")


DRAFT = """# Spoons and Balloons
<!-- status: awaiting read · level: K · year: ~1987 -->

One evening, Brian sat down.

He drew a spoon.
"""

DRAFT_NO_YEAR = """# Mystery
<!-- status: awaiting read · level: K (placement tentative) · year: ? -->

A paragraph.
"""


class TestParseDraft(unittest.TestCase):
    def test_title_year_paragraphs(self):
        title, year, paras = b.parse_draft(DRAFT)
        self.assertEqual(title, "Spoons and Balloons")
        self.assertEqual(year, "~1987")
        self.assertEqual(paras, ["One evening, Brian sat down.", "He drew a spoon."])

    def test_unknown_year_is_none(self):
        title, year, paras = b.parse_draft(DRAFT_NO_YEAR)
        self.assertIsNone(year)
        self.assertEqual(title, "Mystery")


class TestMdInline(unittest.TestCase):
    def test_escapes_then_emphasis(self):
        self.assertEqual(
            b.md_inline("**Author's note:** really *Chrysopogon* & <b>x</b>"),
            "<strong>Author's note:</strong> really <em>Chrysopogon</em> "
            "&amp; &lt;b&gt;x&lt;/b&gt;",
        )


class TestFirstSentence(unittest.TestCase):
    def test_first_sentence(self):
        self.assertEqual(
            b.first_sentence(["One evening, Brian sat down. He drew a spoon."]),
            "One evening, Brian sat down.",
        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd "/Users/luicheng/Hobby Projects/Kampong Website/scripts" && python3 -m unittest test_build_stories -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'build_stories'` (or AttributeError once the file exists but functions don't).

- [ ] **Step 3: Write the minimal implementation**

```python
# scripts/build_stories.py
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd "/Users/luicheng/Hobby Projects/Kampong Website/scripts" && python3 -m unittest test_build_stories -v`
Expected: PASS — all tests OK.

- [ ] **Step 5: Commit**

```bash
cd "/Users/luicheng/Hobby Projects/Kampong Website"
git add scripts/build_stories.py scripts/test_build_stories.py
git commit -m "Add stories generator: parsing & text helpers"
```

---

### Task 2: Hand-author stories.css (light story page + dark index)

Author the shared stylesheet both page types link. Verified visually during Task 4; no unit test.

**Files:**
- Create: `stories/stories.css`

**Interfaces:**
- Produces (class contract the renderers in Task 3 must match):
  - Shared `nav` with `.wordmark` (+ `span`) and `.back`
  - Story page: `body.story`, `article.story-body`, `.story-body .meta`, `h1.display`, `nav.storynav` with `.prev`/`.next`/`.collection` and `.disabled`
  - Index page: `body.index`, `header.collection-hero`, `h1.display`, `.subtitle`, `section.group`, `.group-title`, `ol.story-list`, `.story-list li a`, `.st`, `.sy`, `.teaser`
  - Shared `footer`

- [ ] **Step 1: Write the stylesheet**

```css
/* stories/stories.css — Kampong stories section */
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{
  --ink:#0F1A14;
  --ink-2:#16241C;
  --paper:#F4F1E8;
  --chili:#FF5C39;
  --palm:#7BE0AD;
  --mustard:#E8C547;
  --line:#2A3D32;
}
html{scroll-behavior:smooth}
.display{font-family:'Archivo Black',sans-serif}
a:focus-visible{outline:2px solid var(--palm);outline-offset:3px;border-radius:4px}

/* === Shared nav === */
nav{display:flex;justify-content:space-between;align-items:center;gap:1rem;padding:20px 5vw;position:sticky;top:0;z-index:50;backdrop-filter:blur(8px)}
nav .wordmark{font-family:'Archivo Black',sans-serif;font-size:1.05rem;letter-spacing:.06em;text-decoration:none}
nav .wordmark span{color:var(--chili)}
nav .back{font-family:'Archivo',sans-serif;font-size:.75rem;font-weight:600;letter-spacing:.14em;text-decoration:none;opacity:.8;transition:opacity .2s,color .2s}
nav .back:hover{opacity:1;color:var(--chili)}

/* === Story page (light "storybook") === */
body.story{font-family:'Lora',Georgia,serif;background:var(--paper);color:var(--ink)}
body.story nav{border-bottom:1px solid rgba(15,26,20,.12);background:rgba(244,241,232,.9)}
body.story nav .wordmark{color:var(--ink)}
body.story nav .back{color:var(--ink)}
.story-body{max-width:38rem;margin:0 auto;padding:8vh 6vw 6vh}
.story-body .meta{font-family:'Archivo',sans-serif;font-size:.72rem;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:var(--chili);margin-bottom:1rem}
.story-body h1.display{font-size:clamp(2rem,7vw,3.4rem);line-height:1.02;color:var(--ink);margin-bottom:2.4rem}
.story-body p{font-size:1.15rem;line-height:1.78;margin-bottom:1.4rem}
.story-body h1+p::first-letter{font-family:'Archivo Black',sans-serif;float:left;font-size:3.4rem;line-height:.8;padding:.1em .12em 0 0;color:var(--chili)}
.story-body strong{font-weight:600}

/* prev/next footer nav */
nav.storynav{position:static;backdrop-filter:none;display:flex;justify-content:space-between;align-items:center;gap:1rem;max-width:44rem;margin:0 auto;padding:2.4rem 6vw 6vh;font-family:'Archivo',sans-serif;font-size:.8rem;font-weight:600;letter-spacing:.06em;border-top:1px solid rgba(15,26,20,.12)}
nav.storynav a{color:var(--ink);text-decoration:none;opacity:.85;max-width:40%;transition:opacity .2s,color .2s}
nav.storynav a:hover{opacity:1;color:var(--chili)}
nav.storynav .collection{opacity:.6;letter-spacing:.14em;text-transform:uppercase;font-size:.7rem}
nav.storynav .prev.disabled,nav.storynav .next.disabled{visibility:hidden}

/* === Index page (dark, on-brand) === */
body.index{font-family:'Archivo',sans-serif;background:var(--ink);color:var(--paper)}
body.index nav{border-bottom:1px solid var(--line);background:rgba(15,26,20,.92)}
body.index nav .wordmark{color:var(--paper)}
body.index nav .back{color:var(--paper)}
.collection-hero{padding:12vh 5vw 6vh}
.collection-hero h1.display{font-size:clamp(2.6rem,12vw,7rem);line-height:.95;letter-spacing:-.01em}
.collection-hero .subtitle{margin-top:1.4rem;max-width:34rem;font-size:1.05rem;line-height:1.6;opacity:.75}
.collection-hero .subtitle em{color:var(--palm);font-style:italic}
main{padding:0 5vw 8vh}
section.group{padding:5vh 0;border-top:1px solid var(--line)}
.group-title{font-family:'Archivo Black',sans-serif;font-size:.85rem;letter-spacing:.22em;text-transform:uppercase;color:var(--mustard);margin-bottom:2rem}
ol.story-list{list-style:none}
.story-list li{padding:1.3rem 0;border-bottom:1px solid var(--line)}
.story-list li:last-child{border-bottom:none}
.story-list li a{display:flex;flex-wrap:wrap;align-items:baseline;gap:.9rem;text-decoration:none;color:var(--paper)}
.story-list li a .st{font-family:'Archivo Black',sans-serif;font-size:clamp(1.3rem,4vw,2rem);line-height:1.1;transition:color .2s}
.story-list li a:hover .st{color:var(--chili)}
.story-list li a .sy{font-size:.78rem;font-weight:600;letter-spacing:.1em;color:var(--palm);opacity:.85}
.story-list .teaser{margin-top:.5rem;font-size:.95rem;line-height:1.6;opacity:.6;max-width:38rem}

/* === Shared footer === */
footer{display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap;padding:1.6rem 5vw;border-top:1px solid var(--line);font-size:.72rem;opacity:.55;letter-spacing:.06em}
body.story footer{border-top-color:rgba(15,26,20,.12);font-family:'Archivo',sans-serif}

/* === Mobile === */
@media(max-width:600px){
  .story-body{padding-top:6vh}
  nav.storynav{flex-direction:column;align-items:flex-start;gap:.8rem}
  nav.storynav a{max-width:100%}
}

/* === Reduced motion === */
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
```

- [ ] **Step 2: Sanity-check the file exists and is non-empty**

Run: `wc -l "/Users/luicheng/Hobby Projects/Kampong Website/stories/stories.css"`
Expected: a line count > 60.

- [ ] **Step 3: Commit**

```bash
cd "/Users/luicheng/Hobby Projects/Kampong Website"
git add stories/stories.css
git commit -m "Add stories section stylesheet"
```

---

### Task 3: HTML renderers (TDD)

Add template rendering to the generator: one story page, the index page, and the prev/next nav. Assert key substrings.

**Files:**
- Modify: `scripts/build_stories.py` (append renderers + template constants)
- Test: `scripts/test_build_stories.py` (append render tests)

**Interfaces:**
- Consumes: all Task 1 helpers.
- Produces (used by Task 4 `main`):
  - `render_story_page(item, prev, nxt) -> str` where `item` is a dict `{"title","slug","section","year","paras"}`, `prev`/`nxt` are `{"title","slug"}` or `None`
  - `render_index_page(groups) -> str` where `groups` is a list of `{"section": str, "stories": [{"title","slug","year","teaser"}]}`
  - `nav_links(prev, nxt) -> str`

- [ ] **Step 1: Write the failing tests**

```python
# append to scripts/test_build_stories.py

class TestRenderStory(unittest.TestCase):
    def _item(self):
        return {
            "title": "Spoons and Balloons",
            "slug": "spoons-and-balloons",
            "section": "Kindergarten",
            "year": "~1987",
            "paras": ["One evening, Brian sat down.", "**Note:** *ok*."],
        }

    def test_contains_title_meta_and_prose(self):
        html_out = b.render_story_page(
            self._item(),
            prev={"title": "Kindergarten", "slug": "kindergarten"},
            nxt=None,
        )
        self.assertIn("<title>Spoons and Balloons — Kampong Stories</title>", html_out)
        self.assertIn('class="meta">Kindergarten · ~1987<', html_out)
        self.assertIn("<h1 class=\"display\">Spoons and Balloons</h1>", html_out)
        self.assertIn("<p>One evening, Brian sat down.</p>", html_out)
        self.assertIn("<strong>Note:</strong> <em>ok</em>.", html_out)
        self.assertIn('href="/stories/stories.css"', html_out)
        self.assertIn('href="/stories/kindergarten/">← Kindergarten', html_out)
        self.assertIn('class="next disabled"', html_out)

    def test_meta_without_year(self):
        item = self._item()
        item["year"] = None
        html_out = b.render_story_page(item, None, None)
        self.assertIn('class="meta">Kindergarten<', html_out)


class TestRenderIndex(unittest.TestCase):
    def test_groups_and_links(self):
        groups = [{
            "section": "Kindergarten",
            "stories": [{
                "title": "Spoons and Balloons",
                "slug": "spoons-and-balloons",
                "year": "~1987",
                "teaser": "One evening, Brian sat down.",
            }],
        }]
        html_out = b.render_index_page(groups)
        self.assertIn("<title>Stories — Kampong</title>", html_out)
        self.assertIn(">Kindergarten</h2>", html_out)
        self.assertIn('href="/stories/spoons-and-balloons/"', html_out)
        self.assertIn(">Spoons and Balloons</span>", html_out)
        self.assertIn(">~1987</span>", html_out)
        self.assertIn("One evening, Brian sat down.", html_out)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd "/Users/luicheng/Hobby Projects/Kampong Website/scripts" && python3 -m unittest test_build_stories -v`
Expected: FAIL — `AttributeError: module 'build_stories' has no attribute 'render_story_page'`.

- [ ] **Step 3: Append the implementation**

```python
# append to scripts/build_stories.py

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
    paras = "\n".join("<p>{}</p>".format(md_inline(p)) for p in item["paras"])
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd "/Users/luicheng/Hobby Projects/Kampong Website/scripts" && python3 -m unittest test_build_stories -v`
Expected: PASS — all tests OK.

- [ ] **Step 5: Commit**

```bash
cd "/Users/luicheng/Hobby Projects/Kampong Website"
git add scripts/build_stories.py scripts/test_build_stories.py
git commit -m "Add stories HTML renderers"
```

---

### Task 4: Wire main(), generate real pages, verify in browser

Assemble the pipeline, generate all 15 pages from the real drafts, and verify the output visually.

**Files:**
- Modify: `scripts/build_stories.py` (append `build()` + `__main__`)
- Create (generated output): `stories/index.html`, `stories/<slug>/index.html` ×14

**Interfaces:**
- Consumes: all prior helpers/renderers, `STORIES_REPO`, `OUT_DIR`.
- Produces: `build() -> None` (reads manifest + drafts, writes files, prints a summary).

- [ ] **Step 1: Append the build pipeline**

```python
# append to scripts/build_stories.py

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
```

- [ ] **Step 2: Confirm tests still pass, then run the generator**

Run:
```bash
cd "/Users/luicheng/Hobby Projects/Kampong Website/scripts" && python3 -m unittest test_build_stories -v && python3 build_stories.py
```
Expected: tests PASS; generator prints "Generated 14 story pages + index" and 14 `/stories/<slug>/` lines. Titles include "Primary One", "Summer Snow", "Fire Grass", "A Hidden Find", "Ten Cents", "The Missing Line", "South East Australia", "Electric Science Daydreams".

- [ ] **Step 3: Verify the file tree**

Run: `cd "/Users/luicheng/Hobby Projects/Kampong Website" && find stories -type f | sort`
Expected: `stories/index.html`, `stories/stories.css`, and 14 `stories/<slug>/index.html` files.

- [ ] **Step 4: Verify in the browser (use the run/verify skills or a local server)**

Serve and open the index + a couple of stories:
```bash
cd "/Users/luicheng/Hobby Projects/Kampong Website" && python3 -m http.server 8000
```
Check in a browser (or Chrome automation tools):
- `http://localhost:8000/stories/` — dark index, three section groups, all 14 titles with years + teasers, links work.
- `http://localhost:8000/stories/primary-one/` — light storybook page, Lora serif body, drop-cap, meta "Lower Primary · 1989", working prev/next.
- `http://localhost:8000/stories/getting-better-in-chinese-part-1/` — Chinese characters (七龙珠, 朋友) render correctly.
- `http://localhost:8000/stories/fire-grass/` — the Author's note renders **bold** and *italic* correctly (not literal asterisks).
- First story (`kindergarten`) has no "previous"; last story (`electric-science-daydreams`) has no "next".
Stop the server (Ctrl-C) when done.

- [ ] **Step 5: Commit**

```bash
cd "/Users/luicheng/Hobby Projects/Kampong Website"
git add scripts/build_stories.py stories/
git commit -m "Generate stories section (14 stories + index)"
```

- [ ] **Step 6: Deploy (only on user's go-ahead)**

Publishing is live. On explicit approval:
```bash
cd "/Users/luicheng/Hobby Projects/Kampong Website" && git push origin master
```
Then confirm `https://kampong.com.sg/stories/` serves within ~1 minute.

---

## Notes for the implementer

- **Do not edit anything in the `Stories for Ben` repo** — it is read-only input.
- If a draft's status line format ever varies, `parse_draft` falls back to `year=None` (meta shows section only) — acceptable.
- Re-running `python3 scripts/build_stories.py` fully regenerates the section; this is the resync mechanism when drafts change.
- `.gitignore` currently ignores `.DS_Store` only; the generated `stories/` output is intentionally committed.
