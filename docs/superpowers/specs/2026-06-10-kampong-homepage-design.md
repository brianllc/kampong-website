# Kampong Homepage Design — kampong.com.sg

**Date:** 2026-06-10
**Status:** Approved by user (visual direction, layout, photos, and full-page mockup all validated via visual companion session)
**Mockup reference:** `.superpowers/brainstorm/18612-1781085345/content/homepage-mockup-v2.html`

## Purpose

Replace the current coming-soon page with a beautiful, content-forward homepage for Kampong — a passion-project content site about everything Singapore: food, culture, and heritage. Deeper content pages do not exist yet; the homepage teases them with "coming soon" notes.

## Scope

- Homepage only (`index.html`). No section pages, no blog system, no build step.
- Static site hosted on GitHub Pages with custom domain (keep `CNAME` untouched).
- The existing coming-soon `index.html` is fully replaced.

## Visual Direction: Modern Tropical Bold

Chosen over "Peranakan Editorial" and "Kopitiam Nostalgia" alternatives.

- **Palette:** dark tropical green base `#0F1A14` (ink), secondary surface `#16241C`, off-white `#F4F1E8` (paper), chili red `#FF5C39`, palm green `#7BE0AD`, mustard `#E8C547`, hairline `#2A3D32`.
- **Typography:** Google Fonts — `Archivo Black` for display headlines, `Archivo` (500/600) for everything else. Huge confident type, e.g. hero headline at `clamp(3rem, 11vw, 9rem)`.
- **Accent system:** each chapter owns one accent color — Food = chili, Culture = palm, Heritage = mustard. Used for chapter numbers, "coming soon" pills, and pill CTAs.

## Layout: Story Scroll

Page structure, top to bottom:

1. **Sticky nav** — `KAMPONG*` wordmark (asterisk in chili), anchor links FOOD / CULTURE / HERITAGE, `SG · 1.3521° N` coordinate detail in palm green. Translucent dark background with backdrop blur.
2. **Hero** — full-viewport: headline "EVERYTHING SINGAPORE" with "THING" in chili and "PORE" in palm; one-line intro ("From the first hiss of the wok at dawn to the last MRT home — Kampong is a love letter to the food, culture and heritage of the Little Red Dot."); three category pills anchor-linking to chapters.
3. **Hero photo** — full-width rounded-corner photo (hawker food court), subtle dark gradient overlay.
4. **Ticker marquee** — infinite horizontal scroll of Singapore icons in mustard: LAKSA · SHOPHOUSES · NATIONAL DAY · CHICKEN RICE · MERLION · HDB VOID DECKS · PERANAKAN TILES · KOPI-O · GARDENS BY THE BAY · SINGLISH. Content duplicated once; CSS animation translates −50%.
5. **Chapter 01 — FOOD:** "THE NATIONAL OBSESSION" + blurb + wok-flame photo. Text left, photo right.
6. **Chapter 02 — CULTURE:** "FOUR LANGUAGES, ONE VOICE" + blurb + lion-dance photo. Reversed (photo left).
7. **Chapter 03 — HERITAGE:** "FROM KAMPONG TO SKYLINE" + blurb + shophouse photo. Text left, photo right.
8. **Outro** — centered "THE KAMPONG IS GATHERING" (GATHERING in chili) + "Something good is on the way. Check back soon, can?"
9. **Footer** — `© 2026 KAMPONG.COM.SG` left, `MADE WITH ❤ IN SINGAPORE` right.

Each chapter: small letterspaced chapter number (`CHAPTER 01 — FOOD`), display headline, body blurb (max-width ~30rem), and an animated "coming soon" pill with pulsing dot ("STORIES COOKING — COMING SOON" / "STORIES BREWING…" / "STORIES UNEARTHED…"). Copy as in the approved mockup.

## Photography

Four photos from Unsplash (free Unsplash license), **downloaded and committed to the repo** under `assets/img/` — not hotlinked — so the site never breaks:

| Slot | Unsplash photo ID | Subject |
|---|---|---|
| Hero | `photo-1739857554154-80c15b7b1af7` | Hawker food court crowd |
| Food | `photo-1575664579788-0ce4503c7e89` | Wok flame |
| Culture | `photo-1551693654-b336ccb0c17f` | Red lion dance costume |
| Heritage | `photo-1615392105814-c9fbad4d25a2` | Pastel Peranakan shophouses |

Download at ~1600–2000px wide, `q=80`, JPEG. Target well under ~400 KB per image. Each photo gets a dark gradient overlay for label/text legibility and meaningful `alt` text. Photos below the hero are lazy-loaded.

## Technical Architecture

- **Single `index.html`** with embedded `<style>` and a small embedded `<script>` — keeps the zero-build GitHub Pages setup.
- **Assets:** `assets/img/hero.jpg`, `assets/img/food.jpg`, `assets/img/culture.jpg`, `assets/img/heritage.jpg`.
- **Fonts:** Google Fonts via `<link>` with preconnect (same pattern as current page).
- **JS (vanilla, ~20 lines):** IntersectionObserver scroll-reveal — chapters and outro fade/translate up on first entry into viewport. No libraries.
- **Motion safety:** all animations (ticker, pulse, reveals) disabled under `prefers-reduced-motion: reduce`.
- **Responsive:** chapters collapse to single column under 760px (photo above text); type scales via `clamp()`; under 760px the nav hides the coordinate detail and tightens link spacing (no hamburger menu — three links fit).
- **SEO/meta:** proper `<title>` ("Kampong — Everything Singapore"), meta description, Open Graph tags using the hero image.
- **Semantics/a11y:** `nav`/`header`/`section`/`footer` landmarks, one `h1`, `h2` per chapter, visible focus styles, contrast-checked text on photos.

## Error Handling

Static page — minimal failure surface. Images carry background-color fallbacks (each chapter's dark tone) so a failed load still looks intentional. No external runtime dependencies beyond Google Fonts (degrades to system sans-serif).

## Testing / Verification

- Open locally and verify all four images load from `assets/` (no network 404s in console).
- Check breakpoints: ~375px, ~768px, ~1440px.
- Verify anchor links scroll to correct chapters with sticky-nav offset.
- Verify reduced-motion media query kills ticker/pulse/reveal animations.
- Run a quick HTML validity pass.

## Out of Scope (YAGNI)

- Section/article pages, blog tooling, static site generators.
- Email signup, analytics, social links.
- Dark/light theme toggle (site is dark by design).
