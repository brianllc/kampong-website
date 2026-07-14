# Design — /stories/ section: *The Little Boy Dreaming by the Window*

**Date:** 2026-07-14
**Status:** Approved design (pending user review)

## Purpose

Publish Brian's childhood-memory storybook (14 stories, written for his son Ben; Totto-chan in tone, third-person "Brian") as a reading section on the live site at `kampong.com.sg/stories/`. Ben — and eventually other readers — can read the collection straight through in book order.

The stories are the "childhood stories" content the user asked to host under a `/stories/` folder (chosen over a `stories.` subdomain for simplicity: one repo, no DNS change).

## Source of truth & sync model

- **Source of truth:** the drafts in the *separate* repo `/Users/luicheng/Hobby Projects/Stories for Ben/` (`Drafts/*.md` + `book-order.md`). That project keeps its own workflow (drafts → promote → Final).
- **This site holds generated copies.** Publishing copies the draft text in as static HTML. Editing a draft later does **not** auto-update the site.
- **Resync = re-run the generator.** A one-off generator script reads the drafts and regenerates the static HTML. The *served site stays pure static HTML* — no build step on deploy, consistent with the repo's zero-build ethos.
- The 14 drafts currently carry `<!-- status: awaiting read -->`. The user has approved publishing all 14 as-is; the generator strips the status comment.

## URL structure

```
/stories/                       → collection index
/stories/<slug>/index.html      → one story (folder + index.html ⇒ clean URL, no .html)
```

- **Slugs derive from the book title, not the filename** (titles differ from filenames). Examples:
  - `first-day-of-primary-school.md` → title "Primary One" → `/stories/primary-one/`
  - `primary-school-field-and-big-tree.md` → "Summer Snow" → `/stories/summer-snow/`
  - `growing-fire-grass-on-the-hills.md` → "Fire Grass" → `/stories/fire-grass/`
- Slug rule: lowercase the title, replace non-alphanumerics with hyphens, collapse repeats, trim. "Getting Better in Chinese, Part 1" → `getting-better-in-chinese-part-1`.

## The manifest: book-order.md

`book-order.md` (in the Stories repo) is parsed as the manifest. It already encodes everything the generator needs:

- `## 1. Kindergarten` etc. → the three **sections** (Kindergarten / Lower Primary / Upper Primary) and their order.
- `4. Primary One — `Drafts/first-day-of-primary-school.md`` → per-story **order number**, **title**, and **source draft path**.

Reading order (book order) is the manifest's order and drives prev/next links.

## Components

### A. Story page — warm storybook (light)

Per-story reading page optimized for comfortable long-form reading by a ~10-year-old.

- **Background:** `--paper` (#F4F1E8) cream. **Body text:** `--ink` (#0F1A14), **serif** (Lora).
- **Reading column:** ~62ch max-width, generous line-height (~1.75), comfortable paragraph spacing.
- **Title:** Archivo Black display (brand cohesion). Above it, a small meta line: *Section · Year* (e.g. "Kindergarten · 1989"), year taken verbatim from the draft's status comment (including approximate forms like "~1987"; "year: ?" is omitted).
- **Top nav:** the Kampong nav bar, re-styled for the light background (ink text/links, chili wordmark accent). Wordmark links to `/`.
- **Footer nav:** `← previous · The Collection · next →` in book order. First story has no previous; last has no next.
- Chinese characters in prose render via existing UTF-8 charset.

### B. Collection index — bold + dark (on-brand)

- Uses the dark brand look (matches homepage): `--ink` background, `--paper` text, Archivo.
- Header: **STORIES** (Archivo Black) with the book subtitle ("*The Little Boy Dreaming by the Window* — a Singapore childhood, for Ben").
- The 14 stories grouped under their three book sections. Each entry: order number, **title** (links to the story), **year**, and a **one-line teaser** = the story's first sentence.
- Kampong nav on top (dark), wordmark → `/`.

### C. Shared stylesheet

- `/stories/stories.css` holds all styles for both the index and story pages (light + dark rules). Linked by every generated page. Removes 15× inline-CSS duplication while staying static/zero-build.
- Reuses the homepage's CSS-variable palette. Respects `prefers-reduced-motion` (no essential animation here anyway).

### D. Fonts

- Add **Lora** (serif, body) alongside the existing **Archivo / Archivo Black** via a Google Fonts `<link>`, same pattern as the homepage. `preconnect` included.

### E. Generator script

- **Location:** committed to this repo at `scripts/build_stories.py`.
- **Language:** Python 3 (stdlib only, no third-party deps) — matches the Stories repo's Python tooling and macOS's `python3`.
- **Input:** a configurable `STORIES_REPO` path constant (default: `/Users/luicheng/Hobby Projects/Stories for Ben`). Reads `book-order.md` (manifest) + the referenced `Drafts/*.md`.
- **Per story:** parse `# Title` (line 1) and status comment (line 2, for year); strip both; split remaining text on blank lines into paragraphs; HTML-escape; wrap each in `<p>`. Compute slug from title; wire prev/next from manifest order.
- **Output (into this repo):**
  - `stories/index.html`
  - `stories/<slug>/index.html` ×14
  - `stories/stories.css`
- **Idempotent & re-runnable:** running it regenerates all pages from current drafts (the resync mechanism). Emits a summary of what it wrote.
- Edge cases handled: title/status parsing, empty year (`year: ?`), any inline list/emphasis in a draft is verified during implementation and rendered faithfully or flagged.

## Homepage

**Unchanged for now** (user decision). `/stories/` is reachable by direct URL only; a nav link can be added later.

## Out of scope (v1, YAGNI)

- Per-story illustrations / images (text only).
- Search, RSS/feeds, pagination, comments.
- Any framework, bundler, or deploy-time build.
- Auto-sync between the Stories repo and this site (resync is a manual re-run).

## Success criteria

- `kampong.com.sg/stories/` shows all 14 stories grouped in book order with working links.
- Each story reads as a comfortable light "storybook" page with correct title, section·year meta, prose, and prev/next in book order.
- Chinese characters render correctly.
- Re-running `scripts/build_stories.py` after a draft edit updates the site with no other manual steps.
- Deploy remains a plain `git push master` of static files.

## Deploy note

Commits must use the repo-local noreply email (`28775822+brianllc@users.noreply.github.com`) or GitHub rejects the push (GH007). Pushing `master` publishes live.
