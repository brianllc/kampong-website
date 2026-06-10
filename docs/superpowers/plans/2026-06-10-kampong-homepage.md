# Kampong Homepage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the coming-soon page at kampong.com.sg with the approved "Modern Tropical Bold / Story Scroll" homepage celebrating Singapore food, culture, and heritage.

**Architecture:** A single static `index.html` (embedded CSS + ~20 lines of vanilla JS) served by GitHub Pages with no build step. Four Unsplash photos are downloaded once, committed under `assets/img/`, and referenced locally. Scroll-reveal uses IntersectionObserver; all motion is disabled under `prefers-reduced-motion`.

**Tech Stack:** Plain HTML/CSS/JS, Google Fonts (Archivo Black + Archivo), GitHub Pages. No frameworks, no build tools, no test framework (verification is via local HTTP serving and curl checks).

**Spec:** `docs/superpowers/specs/2026-06-10-kampong-homepage-design.md`

---

## File Structure

- `assets/img/hero.jpg` — hawker food court photo (hero, ~2000px wide)
- `assets/img/food.jpg` — wok flame photo (~1600px wide)
- `assets/img/culture.jpg` — lion dance photo (~1600px wide)
- `assets/img/heritage.jpg` — Peranakan shophouses photo (~1600px wide)
- `index.html` — the entire page: markup, embedded styles, embedded reveal script (full replacement of the current coming-soon page)
- `CNAME` — untouched

There is no test directory: this repo is a zero-tooling static site. Each task ends with explicit verification commands instead of unit tests.

---

### Task 1: Download and commit the four photos

**Files:**
- Create: `assets/img/hero.jpg`, `assets/img/food.jpg`, `assets/img/culture.jpg`, `assets/img/heritage.jpg`

- [ ] **Step 1: Download the four images from Unsplash**

Run (from the repo root):

```bash
mkdir -p assets/img
curl -sSL -o assets/img/hero.jpg     "https://images.unsplash.com/photo-1739857554154-80c15b7b1af7?w=2000&q=80&fm=jpg&fit=crop"
curl -sSL -o assets/img/food.jpg     "https://images.unsplash.com/photo-1575664579788-0ce4503c7e89?w=1600&q=80&fm=jpg&fit=crop"
curl -sSL -o assets/img/culture.jpg  "https://images.unsplash.com/photo-1551693654-b336ccb0c17f?w=1600&q=80&fm=jpg&fit=crop"
curl -sSL -o assets/img/heritage.jpg "https://images.unsplash.com/photo-1615392105814-c9fbad4d25a2?w=1600&q=80&fm=jpg&fit=crop"
```

- [ ] **Step 2: Verify the files are real JPEGs of sane size**

Run: `file assets/img/*.jpg && ls -lh assets/img/`
Expected: all four report `JPEG image data`; each file is roughly 100 KB–400 KB. None should be tiny (<20 KB suggests an error page) or huge (>600 KB).

If any file exceeds 400 KB, re-download that one with `q=70` instead of `q=80` and re-verify.

- [ ] **Step 3: Commit**

```bash
git add assets/img
git commit -m "Add homepage photography (Unsplash, free license)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: Replace index.html with the new homepage

**Files:**
- Modify: `index.html` (full replacement — the old coming-soon page is retired)

- [ ] **Step 1: Write the new index.html**

Replace the entire contents of `index.html` with:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Kampong — Everything Singapore</title>
<meta name="description" content="Kampong is a love letter to Singapore — its food, culture and heritage. From hawker stalls to shophouses, stories from the Little Red Dot.">
<meta property="og:title" content="Kampong — Everything Singapore">
<meta property="og:description" content="A love letter to Singapore — its food, culture and heritage.">
<meta property="og:image" content="https://kampong.com.sg/assets/img/hero.jpg">
<meta property="og:url" content="https://kampong.com.sg/">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600&family=Archivo+Black&display=swap" rel="stylesheet">
<style>
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
body{font-family:'Archivo',sans-serif;background:var(--ink);color:var(--paper)}
.display{font-family:'Archivo Black',sans-serif}
a:focus-visible{outline:2px solid var(--palm);outline-offset:3px;border-radius:4px}

/* === Nav === */
nav{display:flex;justify-content:space-between;align-items:center;gap:1rem;padding:22px 5vw;border-bottom:1px solid var(--line);position:sticky;top:0;background:rgba(15,26,20,.92);backdrop-filter:blur(8px);z-index:50}
.wordmark{font-family:'Archivo Black',sans-serif;font-size:1.1rem;letter-spacing:.06em}
.wordmark span{color:var(--chili)}
nav .links{display:flex;gap:1.6rem;font-size:.8rem;font-weight:600;letter-spacing:.12em}
nav .links a{color:var(--paper);text-decoration:none;opacity:.8;transition:opacity .2s,color .2s}
nav .links a:hover{opacity:1;color:var(--palm)}
nav .coords{font-size:.7rem;color:var(--palm);letter-spacing:.08em}

/* === Hero === */
.hero{min-height:88vh;display:flex;flex-direction:column;justify-content:center;padding:6vh 5vw 0}
.hero h1{font-size:clamp(3rem,11vw,9rem);line-height:.95;letter-spacing:-.01em}
.hero h1 .t{color:var(--chili)}
.hero h1 .p{color:var(--palm)}
.hero .sub{margin-top:1.6rem;max-width:34rem;font-size:1.05rem;line-height:1.6;opacity:.75}
.pills{display:flex;gap:.7rem;margin-top:2.2rem;flex-wrap:wrap}
.pill{font-size:.78rem;font-weight:600;letter-spacing:.1em;padding:.55rem 1.3rem;border-radius:100px;color:var(--ink);text-decoration:none;transition:transform .2s}
.pill:hover{transform:translateY(-2px)}
.pill.f{background:var(--chili)} .pill.c{background:var(--palm)} .pill.h{background:var(--mustard)}

.hero-photo{margin:6vh 5vw 0;height:52vh;border-radius:18px;overflow:hidden;position:relative;background:var(--ink-2)}
.hero-photo img{width:100%;height:100%;object-fit:cover;display:block}
.hero-photo::after{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(15,26,20,.1),rgba(15,26,20,.4))}

/* === Ticker === */
.ticker{border-top:1px solid var(--line);border-bottom:1px solid var(--line);overflow:hidden;white-space:nowrap;padding:.85rem 0;margin-top:7vh}
.ticker .inner{display:inline-block;animation:tick 32s linear infinite;font-size:.85rem;font-weight:600;letter-spacing:.18em;color:var(--mustard)}
@keyframes tick{from{transform:translateX(0)}to{transform:translateX(-50%)}}

/* === Chapters === */
.chapter{display:grid;grid-template-columns:1fr 1fr;gap:4vw;align-items:center;padding:12vh 5vw;border-bottom:1px solid var(--line)}
.chapter.rev .photo{order:2}
.chapter .num{font-size:.8rem;letter-spacing:.25em;font-weight:600;margin-bottom:1rem}
.chapter h2{font-size:clamp(2.2rem,5vw,4rem);line-height:1;margin-bottom:1.4rem}
.chapter p{font-size:1rem;line-height:1.7;opacity:.75;max-width:30rem}
.chapter .photo{height:56vh;border-radius:18px;overflow:hidden;position:relative;background:var(--ink-2)}
.chapter .photo img{width:100%;height:100%;object-fit:cover;display:block}
.chapter .photo::after{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(15,26,20,0),rgba(15,26,20,.3))}
.soon{display:inline-flex;align-items:center;gap:.5rem;margin-top:1.8rem;font-size:.75rem;font-weight:600;letter-spacing:.14em;border:1px solid var(--line);padding:.55rem 1.2rem;border-radius:100px;opacity:.85}
.soon .dot{width:7px;height:7px;border-radius:50%;animation:pulse 1.8s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.ch-food .num,.ch-food .soon{color:var(--chili)} .ch-food .dot{background:var(--chili)}
.ch-culture .num,.ch-culture .soon{color:var(--palm)} .ch-culture .dot{background:var(--palm)}
.ch-heritage .num,.ch-heritage .soon{color:var(--mustard)} .ch-heritage .dot{background:var(--mustard)}

/* === Outro / footer === */
.outro{padding:14vh 5vw;text-align:center}
.outro h2{font-size:clamp(2rem,6vw,4.5rem);line-height:1.05}
.outro h2 em{font-style:normal;color:var(--chili)}
.outro p{margin-top:1.2rem;opacity:.7}
footer{display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap;padding:1.6rem 5vw;border-top:1px solid var(--line);font-size:.75rem;opacity:.55;letter-spacing:.06em}

/* === Scroll reveal (classes applied by JS) === */
.reveal{opacity:0;transform:translateY(28px);transition:opacity .8s ease,transform .8s ease}
.reveal.visible{opacity:1;transform:translateY(0)}

/* === Mobile === */
@media(max-width:760px){
  nav .coords{display:none}
  nav .links{gap:1rem}
  .chapter{grid-template-columns:1fr}
  .chapter.rev .photo{order:0}
  .chapter .photo{height:34vh}
}

/* === Reduced motion === */
@media(prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  .ticker .inner{animation:none}
  .soon .dot{animation:none}
  .reveal{opacity:1;transform:none;transition:none}
}
</style>
</head>
<body>

<nav>
  <div class="wordmark">KAMPONG<span>*</span></div>
  <div class="links">
    <a href="#food">FOOD</a><a href="#culture">CULTURE</a><a href="#heritage">HERITAGE</a>
  </div>
  <div class="coords">SG · 1.3521° N</div>
</nav>

<header class="hero">
  <h1 class="display">EVERY<span class="t">THING</span><br>SINGA<span class="p">PORE</span></h1>
  <p class="sub">From the first hiss of the wok at dawn to the last MRT home — Kampong is a love letter to the food, culture and heritage of the Little Red Dot.</p>
  <div class="pills">
    <a class="pill f" href="#food">FOOD</a>
    <a class="pill c" href="#culture">CULTURE</a>
    <a class="pill h" href="#heritage">HERITAGE</a>
  </div>
</header>

<div class="hero-photo">
  <img src="assets/img/hero.jpg" alt="Crowds dining at a bustling Singapore hawker centre" fetchpriority="high">
</div>

<div class="ticker" aria-hidden="true"><div class="inner">
  LAKSA &nbsp;·&nbsp; SHOPHOUSES &nbsp;·&nbsp; NATIONAL DAY &nbsp;·&nbsp; CHICKEN RICE &nbsp;·&nbsp; MERLION &nbsp;·&nbsp; HDB VOID DECKS &nbsp;·&nbsp; PERANAKAN TILES &nbsp;·&nbsp; KOPI-O &nbsp;·&nbsp; GARDENS BY THE BAY &nbsp;·&nbsp; SINGLISH &nbsp;·&nbsp;
  LAKSA &nbsp;·&nbsp; SHOPHOUSES &nbsp;·&nbsp; NATIONAL DAY &nbsp;·&nbsp; CHICKEN RICE &nbsp;·&nbsp; MERLION &nbsp;·&nbsp; HDB VOID DECKS &nbsp;·&nbsp; PERANAKAN TILES &nbsp;·&nbsp; KOPI-O &nbsp;·&nbsp; GARDENS BY THE BAY &nbsp;·&nbsp; SINGLISH &nbsp;·&nbsp;
</div></div>

<section class="chapter ch-food" id="food">
  <div>
    <div class="num">CHAPTER 01 — FOOD</div>
    <h2 class="display">THE NATIONAL OBSESSION</h2>
    <p>Michelin stars in hawker stalls. Breakfast debates that last generations. We're documenting the dishes, the uncles and aunties behind them, and where to find the good stuff.</p>
    <span class="soon"><span class="dot"></span>STORIES COOKING — COMING SOON</span>
  </div>
  <div class="photo"><img src="assets/img/food.jpg" alt="Flames leaping from a wok during stir-frying" loading="lazy"></div>
</section>

<section class="chapter ch-culture rev" id="culture">
  <div>
    <div class="num">CHAPTER 02 — CULTURE</div>
    <h2 class="display">FOUR LANGUAGES, ONE VOICE</h2>
    <p>Malay, Chinese, Indian, Eurasian and everything in between — festivals that light up the whole street, Singlish that says more in one "lah" than a paragraph ever could.</p>
    <span class="soon"><span class="dot"></span>STORIES BREWING — COMING SOON</span>
  </div>
  <div class="photo"><img src="assets/img/culture.jpg" alt="A vivid red Chinese lion dance costume" loading="lazy"></div>
</section>

<section class="chapter ch-heritage" id="heritage">
  <div>
    <div class="num">CHAPTER 03 — HERITAGE</div>
    <h2 class="display">FROM KAMPONG TO SKYLINE</h2>
    <p>Shophouse shutters, dragon kilns, the last villages. How a fishing settlement became a metropolis in one lifetime — and what we're keeping along the way.</p>
    <span class="soon"><span class="dot"></span>STORIES UNEARTHED — COMING SOON</span>
  </div>
  <div class="photo"><img src="assets/img/heritage.jpg" alt="Pastel-coloured Peranakan shophouse facades" loading="lazy"></div>
</section>

<section class="outro">
  <h2 class="display">THE KAMPONG IS <em>GATHERING</em></h2>
  <p>Something good is on the way. Check back soon, can?</p>
</section>

<footer>
  <span>© 2026 KAMPONG.COM.SG</span>
  <span>MADE WITH ❤ IN SINGAPORE</span>
</footer>

<script>
(function () {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var targets = document.querySelectorAll('.chapter > div, .chapter .photo, .outro');
  targets.forEach(function (el) { el.classList.add('reveal'); });
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });
  targets.forEach(function (el) { io.observe(el); });
})();
</script>

</body>
</html>
```

- [ ] **Step 2: Serve locally and verify all assets resolve**

Run:

```bash
python3 -m http.server 8642 >/dev/null 2>&1 &
sleep 1
for p in / /assets/img/hero.jpg /assets/img/food.jpg /assets/img/culture.jpg /assets/img/heritage.jpg; do
  echo "$p -> $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8642$p)"
done
kill %1
```

Expected: all five lines end in `200`.

- [ ] **Step 3: Sanity-check required markup is present**

Run:

```bash
grep -c 'prefers-reduced-motion' index.html
grep -c 'IntersectionObserver' index.html
grep -c 'loading="lazy"' index.html
grep -c 'alt="' index.html
```

Expected: `2` (one CSS block + one JS check), `1`, `3`, `4` respectively.

- [ ] **Step 4: Commit**

```bash
git add index.html
git commit -m "Replace coming-soon page with Everything Singapore homepage

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: Visual verification pass

**Files:** none modified (verification only; fix-ups go in follow-up commits if needed)

- [ ] **Step 1: Open the page in a real browser**

Run: `python3 -m http.server 8642` (leave running), then open `http://localhost:8642` in a browser — or use the project's browser tooling/screenshot capability if available.

Check against the spec:
- Hero headline renders in Archivo Black with chili "THING" and palm "PORE"
- All four photos display with gradient overlays; no broken images in the console
- Ticker scrolls continuously without a visible jump at the loop seam
- Chapters fade up on scroll; Culture chapter has photo on the left (desktop)
- Anchor pills/nav links land on the right chapters
- "Coming soon" pill dots pulse

- [ ] **Step 2: Check responsive layouts**

Using browser devtools, verify at 375px, 768px, 1440px widths:
- ≤760px: chapters stack with photo above text, nav coordinates hidden, no horizontal scrollbar
- 1440px: hero type is large but not clipped; chapter grid is two-column

- [ ] **Step 3: Check reduced motion**

In devtools, emulate `prefers-reduced-motion: reduce` (Rendering tab in Chrome) and reload.
Expected: ticker static, dots not pulsing, chapters fully visible without scroll animation.

- [ ] **Step 4: HTML validity pass**

Run: `tidy -q -e index.html` (ships with macOS; if unavailable, skip with a note)
Expected: no errors. Warnings about CSS custom properties or `fetchpriority` being unknown to older tidy versions are acceptable; fix any genuine errors (unclosed tags, duplicate IDs) and commit the fix.

- [ ] **Step 5: Stop the server and confirm clean tree**

Run: `git status`
Expected: clean working tree (any fixes discovered above should have been committed with a short message, e.g. `fix: prevent ticker seam jump`).

Note: pushing to GitHub (which publishes to kampong.com.sg) is deliberately NOT part of this plan — ask the user before pushing.
