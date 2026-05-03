# Implementation Plan: Migrate Blog from Jekyll to Hugo

**Branch**: `001-hugo-migration` | **Date**: 2026-04-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-hugo-migration/spec.md`

## Summary

Migrate blog.lanyonm.org from Jekyll 3.10.0 (EOL) to Hugo with the Congo theme. The migration covers 32 posts, 2 drafts, 54 images, URL redirects from old permalink structure, dual comment system (Disqus/Giscus), GA4 analytics, and automated GitHub Actions deployment. The Congo theme provides built-in dark mode, search, ToC, hamburger overlay menu, and Lighthouse-optimized output. Custom overrides add transparent nav scroll transition, hero background images, homepage/article/about page layouts, footer social icons, and ToC active section tracking (see research.md R0 for full Tier 1/2/3 classification).

## Technical Context

**Language/Version**: Hugo extended edition (latest stable), Go templates
**Primary Dependencies**: Congo theme v2 (Tailwind-based, MIT license)
**Storage**: N/A (static site, all content in Markdown files)
**Testing**: Manual validation via `hugo serve`, Lighthouse CLI audits, link checking on generated output
**Target Platform**: GitHub Pages (static hosting, custom domain blog.lanyonm.org)
**Project Type**: Static site (content blog)
**Performance Goals**: Lighthouse ≥90 all four categories, Speed Index ≤3.0s, page weight <500KB
**Constraints**: No runtime dependencies beyond Hugo binary; GitHub Pages limits (repo <1GB, site <1GB); no server-side logic
**Scale/Scope**: 32 posts (29 articles + 3 speaking talks), 2 drafts, 54 images (4.3MB), 1 standalone page (About), 1 section listing (Speaking), 1 taxonomy page (Tags), 1 special page (404), ~30 tags

## Design Tokens (extracted from mockups)

All custom CSS must use these values. Every color must include a `.dark` variant. These tokens are the shared contract between template and CSS work — both must reference the same class names and values.

### Font Stacks

| Token | Value | Usage |
|-------|-------|-------|
| `--font-display` | `'Manrope', sans-serif` | Headings, nav, labels, buttons, tags, ToC, meta |
| `--font-body` | `'Literata', Georgia, serif` | Body text, paragraphs |
| `--font-mono` | `'JetBrains Mono', monospace` | Code blocks, inline code, dates, reading time |

Load via Google Fonts in `layouts/_partials/extend-head.html`.

### Color Palette

| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| Body background | `#fafafa` | `rgb(var(--color-neutral-800))` | Page background |
| Body text | `#3f3f46` (neutral-700) | `#d4d4d8` (neutral-300) | Prose paragraphs, list items |
| Headings h2 | `#18181b` (neutral-900) | `#fafafa` (neutral-50) | Section headings |
| Headings h3 | `#27272a` (neutral-800) | `#e4e4e7` (neutral-200) | Subsection headings |
| Strong text | `#27272a` (neutral-800) | `#fafafa` (neutral-50) | Bold text |
| Links | `#334155` (primary-700) | `#cbd5e1` (primary-300) | Prose links |
| Link underline | `#e2e8f0` (primary-200) | `#94a3b8` (primary-400) | Default underline color |
| Link underline hover | `#475569` (primary-600) | `#cbd5e1` (primary-300) | Hover underline color |
| List markers | `#94a3b8` (primary-400) | `#94a3b8` (primary-400) | `li::marker` color |
| Meta text (dates, reading time) | `#71717a` (neutral-500) | `#a1a1aa` (neutral-400) | Post metadata |
| Muted text (ToC links, labels) | `#a1a1aa` (neutral-400) | `#a1a1aa` (neutral-400) | Secondary text |
| Section label | `#64748b` (primary-500) | `#94a3b8` (primary-400) | "RECENT ARTICLES" |
| Tag text | `#475569` (primary-600) | `#cbd5e1` (primary-300) | Tag badges |
| Tag background | `#f8fafc` (primary-50) | `rgb(var(--color-neutral-700))` | Tag badge bg |
| Border | `#e4e4e7` (neutral-200) | `#71717a` (neutral-500) | Separators, card borders, ToC marker — must meet 3:1 on dark bg |
| Nav scrolled bg | `rgba(250,250,250,0.88)` | `rgba(24,24,27,0.88)` | Frosted glass nav |
| Footer text | `#a1a1aa` (neutral-400) | `#a1a1aa` (neutral-400) | Copyright |
| Footer icon | `#a1a1aa` (neutral-400) | `#a1a1aa` (neutral-400) | Social icons |
| Footer icon hover | `#475569` (primary-600) | `rgb(var(--color-primary-400))` | Social icon hover |
| Profile role text | `#475569` (primary-600) | `#94a3b8` (primary-400) | "Engineering Leader • DevOps • Madison, WI" |
| Code block bg | `#18181b` (neutral-900) | `#18181b` (neutral-900) | Same in both modes |
| Code block text | `#e5e7eb` | `#e5e7eb` | Same in both modes |
| Inline code bg | `#f4f4f5` (neutral-100) | `rgb(var(--color-neutral-700))` | Inline `code` |
| Inline code text | `#1e293b` (primary-800) | `#e4e4e7` (neutral-200) | Inline `code` |
| Hero gradient (light) | `rgba(15,23,42,0.4) → 0.5 → 0.8` | — | Light mode overlay stops |
| Hero gradient (dark) | — | `rgba(15,23,42,0.3) → 0.4 → 0.7` | Dark mode — lower opacity prevents hero from becoming too dark |

### Typography Scale

| Element | Font | Size | Weight | Line-height | Letter-spacing |
|---------|------|------|--------|-------------|----------------|
| Body text | body | `1rem` | 400 | 1.85 | normal |
| H2 | display | `1.4rem` | 700 | 1.3 | `-0.02em` |
| H3 | display | `1.1rem` | 600 | 1.3 | normal |
| Homepage hero h1 | display | `clamp(2.25rem, 5vw, 3.5rem)` | 700 | 1.15 | `-0.03em` |
| Homepage hero subtitle | body | `1.1rem` | 400 | 1.65 | normal |
| Article hero title | display | `clamp(1.75rem, 4vw, 2.5rem)` | 700 | 1.2 | `-0.03em` |
| Post card title | display | `1.25rem` | 600 | 1.35 | `-0.015em` |
| Post card description | body | `0.95rem` | 400 | 1.6 | normal |
| Post date | mono | `0.78rem` | 400 | normal | `-0.01em` |
| Reading time | display | `0.72rem` | 500 | normal | normal |
| Section label | display | `0.75rem` | 600 | normal | `0.08em` |
| Tag badge | display | `0.7rem` | 600 | normal | `0.01em` |
| ToC link | display | `0.78rem` | 500 | 1.4 | normal |
| Nav title | display | `1.1rem` | 700 | normal | `-0.02em` |
| Footer text | display | `0.8rem` | 400 | normal | normal |
| Code block | mono | `0.82rem` | 400 | 1.7 | normal |
| Inline code | mono | `0.85em` | 400 | normal | normal |
| Prev/next direction | display | `0.72rem` | 600 | normal | `0.06em` |
| Prev/next title | display | `0.9rem` | 600 | 1.35 | normal |
| Prev/next date | mono | `0.72rem` | 400 | normal | normal |
| Profile name | display | `2rem` | 700 | 1.2 | `-0.03em` |
| Profile role | display | `0.95rem` | 500 | normal | normal |
| Profile bio | body | `0.95rem` | 400 | 1.7 | normal |
| Comments label | display | `0.75rem` | 600 | normal | `0.08em` |

**Date format decision**: ISO dates (`2006-01-02`) are the final format. Chosen for compactness in the monospace meta styling, international readability, and visual consistency across the post card and article hero designs.

### Spacing & Layout

| Component | Value |
|-----------|-------|
| Nav height | `64px` |
| Nav z-index | `100` |
| Body padding-top | `4rem` (for fixed nav) |
| Homepage hero height | `85vh`, min `520px` (mobile: `70vh`, min `400px`) |
| Article hero height | `50vh`, min `320px` |
| Content wrapper max-width | `780px` (homepage), `1060px` (article with ToC), `680px` (about) |
| Post card padding | `2rem 0`, first child `padding-top: 0` |
| Post card border | `1px solid neutral-200` bottom |
| Footer padding | `2.5rem clamp(1.5rem, 4vw, 2rem)` |
| Footer margin-top | `3rem` |
| Profile avatar | `140px × 140px`, `border-radius: 16px` |
| Profile social buttons | `36px × 36px`, `border-radius: 8px` |
| ToC border-left | `2px solid neutral-200` |
| ToC active marker | `2px solid primary-500` |
| Scroll-margin-top on headings | `calc(64px + 1.5rem)` ≈ `5rem` |
| Article nav grid | `1fr 1fr`, gap `1.5rem` |
| Footer icon size | `18px × 18px` |
| Speaking page max-width | `780px` (same as homepage post list) |

**Hero image scope (final)**: FR-025 defines the `backgroundImage` capability for any page. For the initial migration, only the homepage uses a hero image (`/images/dod-msn-lanyonm-talk.jpg`). No article posts have hero images enabled — the non-hero layout is the reading experience for all 32 posts. The article mockup demonstrates the hero-enabled layout for reference; the implementation must support both hero and non-hero article rendering. This is a capability decision, not a gap.

### Hover & Interactive States

| Element | Default | Hover |
|---------|---------|-------|
| Prose link underline | `primary-200` | `primary-600` (transition `0.2s`) |
| ToC link | `neutral-400`, no underline | `primary-700`, underline with `3px` offset |
| ToC active | `primary-700`, weight `600`, left border `primary-500` | — |
| Post card title | No underline | Underline with `primary-500` decoration |
| Tag badge | — | — (no hover defined in mockup) |
| Nav button | No background | `rgba(255,255,255,0.15)` over hero; `neutral-100` when scrolled |
| Menu link | `neutral-700` | `primary-600`, underline `2px` with `primary-500` |
| Footer social icon | `neutral-400` | `primary-600` (transition `0.2s`) |
| Profile social button | bg `neutral-100`, icon `neutral-500` | bg `primary-100`, icon `primary-700` |
| Profile social button (dark) | bg `neutral-700`, icon `neutral-300` | bg `primary-800`, icon `primary-300` |
| Prev/next card | No background | bg `neutral-100`, `border-radius: 8px` |
| H2 anchor `#` | `opacity: 0` | `opacity: 1` on heading hover (transition `0.2s`) |
| Focus ring (`:focus-visible`) | Not visible | `outline: 2px solid primary-500`, `outline-offset: 2px`. Must be visible in both light and dark modes. Custom CSS must not suppress Congo's defaults. |

**Focus ring implementation note**: The `:focus-visible` outline MUST be applied to all interactive elements: links, buttons, form inputs, menu items, social icon buttons, and ToC links. Congo provides default focus styles — custom CSS must preserve or improve them, never suppress. Dark mode focus ring uses the same `primary-500` color (sufficient contrast on dark backgrounds). This is a constitution MUST requirement (Principle II), not optional polish.

### HTML Class Contract

Template and CSS work must use these class names. If templates are written first and CSS second, the CSS agent must read the rendered HTML to verify selectors.

| Component | Class Names |
|-----------|------------|
| Site footer | `.site-footer > .footer-inner > .footer-text` + `.footer-links` |
| Homepage hero | `.hero > .hero-bg` + `.hero-content` |
| Article hero | `.article-hero > .article-hero-bg` + `.article-hero-content` |
| Hero breadcrumb | `.article-hero-breadcrumb` |
| Hero title | `.article-hero-title` |
| Hero meta | `.article-hero-meta > .article-hero-date` + `.article-hero-reading` |
| Hero tags | `.article-hero-tags > .tag-light` |
| Post list | `.content-wrapper > .section-label` + `.post-list > .post-card` |
| Post card elements | `.post-meta > .post-date` + `.post-reading-time` / `.post-title` / `.post-description` / `.post-tags > .tag` |
| About profile | `.profile-header > .profile-avatar` + `.profile-info > .profile-name` + `.profile-role` + `.profile-bio` + `.profile-social` |
| Article nav | `.article-nav > .article-nav-link > .article-nav-direction` + `.article-nav-title` + `.article-nav-date` |
| Comments section | `.comments-section > .comments-label` |
| ToC active state | `li.active` (top-level), `li.active-child` (nested) |
| Nav hero state | `.site-header.over-hero` (transparent), `.site-header.scrolled` (frosted) |
| 404 page | `.error-content > h1 + p + .error-actions > .btn-primary` + `.error-home-link` |
| Skip-to-content | `#the-top { overflow: hidden; height: 0; }` |

**Nav structure note**: The nav uses Congo's native hamburger layout classes (`.nav-right`, `.nav-btn`, `.nav-icon`, `.hamburger-label`, `#menu-controller`, `#menu-wrapper`, `.menu-list`, `.menu-close`, `.menu-social`). These are NOT custom — they come from Congo's template. Only `.site-header.over-hero` and `.site-header.scrolled` are custom additions for the transparent nav scroll behavior.

**ARIA requirements for nav override (WCAG 4.1.2, 2.5.3)**: The hamburger menu override MUST include:
- Hamburger label/button: `aria-label="Toggle navigation menu"`, `aria-expanded="false"` (toggled to `"true"` when menu opens via JS or CSS `:checked` state)
- Menu wrapper: `role="dialog"`, `aria-label="Site menu"`, `aria-modal="true"`
- Close button/label: `aria-label="Close menu"`
- Dark mode toggle: `aria-label="Toggle dark mode"` (not just `title`)
- Search button: `aria-label="Search"` (not just `title`)
- All social icon links: `aria-label` matching the `title` (e.g., `aria-label="GitHub"`)

**Disqus mockup note**: The article mockup's Disqus classes (`.disqus-read-only`, `.disqus-placeholder`, `.disqus-logo`, `.disqus-comment-*`) are illustrative — the actual Disqus embed renders its own DOM. No custom CSS targets these classes. The `.comments-section > .comments-label` wrapper is the only custom element around the Disqus embed.

**Code copy note**: The article mockup's code copy button is illustrative of Congo's built-in code copy feature (`showCodeCopy = true` in `hugo.toml`). Congo renders its own copy button with its own styling. No custom template or CSS is needed.

**ToC label note**: Congo renders the label text as "Table of Contents" via its i18n system. CSS `text-transform: uppercase` displays it as "TABLE OF CONTENTS". The article mockup uses "On this page" as placeholder text — the implementation uses Congo's i18n label.

## Validation Protocol

Every implementation phase that produces visible output must include a **mockup comparison** as its first validation step, before any functional checks (build errors, link checks, Lighthouse).

**Procedure**:
1. Serve the mockup via a local HTTP server (`python3 -m http.server 8889 --directory specs/001-hugo-migration/mockups`)
2. Serve the built site via `hugo serve`
3. Open both in Playwright (or side-by-side browser windows)
4. For each page type affected by the phase, compare every element: fonts, sizes, colors, spacing, borders, hover states, active states
5. Any mismatch against the design tokens (above) or mockup layout is a defect that must be fixed before proceeding

**What to compare per page**:
- **Homepage**: Hero (height, gradient, text), nav (transparent/white over hero), post cards (date format, reading time, title, description, tags), section label, footer
- **Article**: Hero (if `backgroundImage` set), prose text (font, size, color, line-height), headings (h2/h3 sizes, anchor hover), links (underline color, hover transition), lists (markers, indentation), code blocks (dark bg, mono font), ToC (label, active state, border), prev/next nav (labels, dates, hover bg), comments label, footer
- **About**: Profile header (avatar, name, role, bio, social buttons), prose styling, solid nav (not transparent), footer

**Dark mode**: After light mode comparison passes, toggle to dark mode and verify all text maintains readable contrast. Every custom color must have a `.dark` variant per the Design Tokens palette. Verify dark mode preference persists across page navigation and browser sessions (Congo stores in localStorage). Verify no "flash of wrong theme" on page reload — Congo's inline appearance script in `<head>` prevents this. If custom CSS load order causes a flash, it is a defect.

**HTML validation**: Run W3C Nu HTML Checker or `html-proofer` on 3 representative pages (homepage, article, about). All errors must be resolved.

**200% zoom test**: Test 200% browser zoom on homepage, article, and about pages. Verify no horizontal scrolling, no content loss, no text overlap. This is distinct from viewport width testing — zoom affects text size while viewport testing affects layout.

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Simplicity | PASS | Congo native features used where available (14 Tier 1 components). 7 Tier 3 custom overrides justified by mockup requirements — see Complexity Tracking. |
| II. Accessibility (WCAG AA) | PASS | Congo is WCAG-aware; spec requires Lighthouse Accessibility ≥90. FR-023 requires semantic markup. |
| III. Discoverability (SEO & GEO) | PASS | Constitution already references `index.xml`. Redirect from `/feed.xml` to `/index.xml` satisfies subscriber continuity. All SEO requirements (OG, schema.org, canonical URLs, sitemap) are met. |
| IV. Performance | PASS | Congo optimized for Lighthouse; `hugo --minify` in production; lazy loading and WebP built-in. |
| V. Open Source & Minimal Dependencies | PASS | Congo is MIT-licensed. Giscus client JS is MIT. Disqus is the only non-open runtime JS (legacy, pre-2025 posts only). No Node/Ruby/Python in build. |
| VI. Validation-Driven Development | PASS | Plan includes validation steps for each phase using `hugo serve` and Lighthouse audits. |
| VII. URL Continuity | PASS | Hugo `aliases` redirect all 32 old-format URLs. Custom 404 with issue reporting link preserved. |
| VIII. Automated Deployment | PASS | GitHub Actions workflow with `hugo --minify`, OIDC credentials, fail-on-error. |
| IX. GitHub Pages Hosting | PASS | Deploy via `actions/deploy-pages`. CNAME in `static/`. HTTPS enforced. |
| X. Hugo Best Practices | PASS | Content in `content/`, `hugo.toml` config, YAML front matter, Hugo shortcodes, theme override mechanism for customization. |

**Gate result**: PASS — no violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/001-hugo-migration/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
hugo.toml                          # Primary Hugo configuration
content/
├── articles/                      # Blog posts (migrated from _posts/)
│   ├── post-slug.md               # Posts without date prefix (Hugo reads date from front matter)
│   └── ...                        # 32 posts + 2 drafts
├── speaking/
│   └── _index.md                  # Speaking section listing
└── about.md                       # About page

layouts/
├── _partials/
│   ├── header/
│   │   └── hamburger.html        # Active page highlighting + social icons (Congo override)
│   ├── hero-background.html      # Background image with scroll-fade effect
│   ├── article-meta.html         # Tag case preservation override
│   ├── article-pagination.html   # Prev/next with direction labels + dates
│   ├── footer.html               # Copyright left, social icons right
│   ├── extend-head.html          # Google Fonts loading
│   └── extend-footer.html        # Custom JS loading
├── partials/
│   └── comments.html             # Dual comment system (Disqus pre-2025, Giscus post-2025)
├── index.html                    # Custom homepage with hero + post list
├── _default/
│   └── about.html                # About page with profile header
├── articles/
│   └── single.html               # Article layout with hero support + comments label
├── shortcodes/
│   ├── sidebyside.html           # Side-by-side image layout shortcode
│   └── speakerdeck.html          # SpeakerDeck embed shortcode
└── 404.html                      # Custom 404 with GitHub issue reporting link

assets/
├── css/
│   └── custom.css                 # Custom styles for transparent nav, backdrop blur, scroll-fade
└── js/
    └── custom.js                  # Scroll-fade background image effect

static/
├── images/                        # Migrated from images/ (54 files, 4.3 MB)
├── CNAME                          # Custom domain: blog.lanyonm.org
└── favicon.ico                    # Favicon

.github/
└── workflows/
    └── deploy.yml                 # Hugo build + GitHub Pages deploy
```

**Structure Decision**: Theme customization via Hugo's override mechanism. Congo's native hamburger overlay menu is used with minimal overrides for active-page highlighting. Custom layouts for homepage (hero + post list), about (profile header), and article (hero support). Footer overridden for social icons layout. See research.md R0 for full Tier 1/2/3 classification.

## Implementation Phases

### Phase 1: Hugo Scaffold & Configuration

**Goal**: Empty Hugo site builds and serves with zero errors.

**Steps**:
1. Install Hugo extended edition (`brew install hugo`)
2. Scaffold Hugo site into the repo root (`hugo new site . --force`)
3. Install Congo theme as a Hugo module (`hugo mod init github.com/lanyonm/lanyonm.github.io && hugo mod get github.com/jpanther/congo/v2`)
4. Create `hugo.toml` with:
   - `baseURL = "https://blog.lanyonm.org/"`, `params.description`, `params.author = "Michael Lanyon"`
   - Permalink structure: `articles = "/articles/:slug/"`
   - Taxonomies: `tag = "tags"`
   - RSS output format (default `index.xml`)
   - Congo theme params: slate color scheme, dark mode auto-switch, appearance switcher, search, ToC, code copy, reading time, lazy loading, WebP, article sharing links (`article.showShare = true`), footer copyright (`footer.showCopyright = true`)
   - GA4 config: `services.googleAnalytics.id = "G-NN7JP65RMS"`
   - Disqus config: `services.disqus.shortname = "lanyonm"`
   - Giscus params (repo, repoId, category, categoryId, mapping, theme)
   - Giscus cutoff date param: `giscusCutoffDate = "2025-01-01"`
   - Date format: `dateFormat = "2006-01-02"` (ISO format per Design Tokens)

**Validation** (with app running):
- `hugo serve` runs with zero errors and zero warnings
- Site loads at localhost:1313 with Congo theme rendering
- Dark mode toggle works
- Search feature is accessible

---

### Phase 2: Content Migration

**Goal**: All 32 posts + 2 drafts render correctly with full content fidelity.

**Steps**:
1. Move `_posts/*.md` → `content/articles/` stripping date prefix from filenames, EXCEPT posts with `category: speaking` (3 posts) which go to `content/speaking/`
2. Move `_drafts/*.md` → `content/articles/` with `draft: true` in front matter
3. Update front matter in each post:
   - Remove `layout:` field
   - Remove `category:` field (Hugo uses directory-based sections)
   - Keep `title`, `description`, `tags`, `comments`, `og`
   - Add `aliases:` with old-format URL (`/articles/YYYY/MM/DD/slug/`)
4. Convert Jekyll syntax (82 highlight blocks → fenced code blocks)
5. Convert `{% post_url %}` links (16 occurrences → `{{< ref "slug" >}}`)
6. Convert `{% gist user/id %}` embeds (5 occurrences → `{{< gist user id >}}`)
7. Convert `<div class="center quote">` blocks (3 occurrences in 2 posts) to Markdown blockquotes (`> "Quote text"`)
8. Convert `<div class="center"><figure>` blocks (39 occurrences in 14 posts) to Hugo's built-in `figure` shortcode:
   - `{{</* figure src="/images/foo.jpg" link="/images/foo.jpg" caption="Caption text" */>}}`
   - Also replace `{{ site.url }}/images/` with `/images/` in src/link paths (32 Liquid template references across 9 posts)
   - Hugo's `figure` shortcode produces semantic `<figure>` + `<figcaption>` markup natively; no custom shortcode needed
9. Convert `<div class="right"><figure>` float-right images (2 occurrences in 1 post) to Hugo `figure` shortcode with class param:
   - `{{</* figure src="/images/foo.jpg" link="/images/foo.jpg" class="right" */>}}`
   - Add `.right` figure CSS to `assets/css/custom.css` (`float: right; max-width: 331px; margin: 0 0 1rem 1.5rem;`)
10. Convert YouTube iframe embed (1 occurrence in 1 speaking post) to Hugo's built-in `youtube` shortcode:
    - `{{</* youtube ku3O4HnMXrM */>}}`
    - Note: start time offset (t=400) may need raw HTML fallback if Hugo's shortcode doesn't support it
11. Convert side-by-side image divs (2 occurrences in 2 posts) to a `sidebyside` Hugo shortcode:
   - Create `layouts/shortcodes/sidebyside.html` that renders a flex container with images and an optional separator
   - Usage: `{{</* sidebyside separator="+" */>}}![Alt1](url1)![Alt2](url2){{</* /sidebyside */>}}`
   - Convert `<div class="center spring-mybatis">` in `spring-4-mybatis-java-config.md`
   - Convert `<div class="center grails-travis">` in `testing-multiple-grails-versions-travis-ci.md`
12. Convert SpeakerDeck `<script>` embeds (3 occurrences in 3 speaking posts) to a Hugo shortcode:
   - Create `layouts/shortcodes/speakerdeck.html` that renders the SpeakerDeck embed script with configurable `data-id` and `data-ratio` params
   - Usage: `{{</* speakerdeck id="1aaef89e52d0487489a2adb6e0020917" ratio="1.77777777777778" */>}}`
   - Add `speakerdeck.com` to Hugo's security policy in `hugo.toml` to allow the external script:
     ```
     [security.exec]
     [security.funcs]
     [security.http]
     [security.integrity]
       hashes = []
       sources = ["https://speakerdeck.com"]
     ```
13. Move static assets using `git mv` (preserves history without duplicating blobs):
   - `git mv images/ static/images/` (54 files, 4.3 MB)
   - `git mv favicon.ico static/favicon.ico`
   - `git mv CNAME static/CNAME`
14. Keep `_assets/` directory in repo (contains `.dot` source files for diagram generation). Hugo ignores underscore-prefixed directories — not built or published.

**Validation** (with app running):
- `hugo serve` — zero errors, zero warnings
- Spot-check all 32 posts: text, code highlighting, images, internal links
- Verify gist embeds load on the 4 posts that use them
- Verify blockquotes render with Congo's default styling on the 2 posts that had pull-quotes
- Verify side-by-side images render correctly on the 2 posts that use them
- Verify SpeakerDeck embeds load on the 3 speaking posts
- Verify figure images with captions render correctly on the 14 posts that use them (Hugo `figure` shortcode)
- Verify float-right images display correctly on the 1 post that uses them
- Verify YouTube embed loads on the 1 speaking post that uses it
- Verify drafts are not visible in production build (`hugo` without `--buildDrafts`)
- Verify old-format URLs redirect to new URLs via aliases
- Grep for any remaining Jekyll syntax (`{% highlight`, `{% post_url`, `{% gist`, `{% endhighlight`): must return zero matches

---

### Phase 3: Theme Customization — Congo with Blowfish-style Features

**Goal**: Site renders with Congo theme (slate color scheme), hamburger navigation with Congo's native overlay menu, transparent pinned nav bar, background images with scroll-fade effect, and all visual features.

**Design reference**: See `specs/001-hugo-migration/mockups/` for HTML mockups of all three page types. Colors are abstracted into CSS variables for easy theme switching.

**Steps**:
1. Configure Congo with the **slate** color scheme (cool grays with subtle warm accents)
2. Configure Congo's native hamburger menu layout (`[params.header] layout = "hamburger"`).
   Congo's hamburger uses a full-screen frosted-glass overlay with right-aligned links (see mockups).
   No header partial override is needed for the menu itself — configure via `hugo.toml` menus.
   Add menu items: Articles, Speaking, About, Tags, plus social icons (GitHub, LinkedIn, Strava, RSS)
   via menu entries with `params.icon`.
3. Override `layouts/_partials/header/hamburger.html` ONLY to add:
   - Active page highlighting (compare `.RelPermalink` to menu URLs, add `class="active"`)
   - Social icon links in the overlay (GitHub, LinkedIn, Strava, RSS) if Congo's menu config doesn't support icon-only social links in the desired position
   Note: Do NOT replace Congo's checkbox-based overlay with a custom slide-out panel.
4. Implement Blowfish-style background image with scroll-fade:
   - Create a hero/banner partial or override the homepage layout to support a full-width background image behind the page header
   - Add JavaScript to fade the background image opacity as the user scrolls down (opacity transitions from 1.0 at top to 0 after a defined scroll distance)
   - Support per-page opt-in via front matter (e.g., `backgroundImage: "/images/hero.jpg"`) so the effect is available on the homepage and optionally on individual posts
   - Support responsive image cropping for landscape vs portrait viewports:
     - If `backgroundImagePortrait` is set in front matter, render a `<picture>` element with `<source media="(orientation: portrait)">` for the portrait crop and the landscape image as the default `<img>`
     - If `backgroundImagePortrait` is not set, use CSS `object-position` shifts per breakpoint to reframe the landscape image for portrait viewports (default: `object-position: center 30%` landscape, `object-position: center center` portrait)
   - Ensure the background image is lazy-loaded, served in WebP where supported, and does not increase page weight beyond the 500KB budget for the page itself
5. **Accessibility: text contrast over background images** — ensure all text layered over hero images and transparent nav meets WCAG AA (4.5:1 normal text, 3:1 large text) at every scroll position and in both light and dark modes:
   - **Hero text overlay**: Apply a gradient overlay between the background image and text content. Minimum overlay: `linear-gradient(to bottom, rgba(15,23,42,0.4) 0%, rgba(15,23,42,0.5) 50%, rgba(15,23,42,0.8) 100%)` in light mode — the 0.4 minimum at top guarantees 4.5:1 contrast for white text even over bright images. Dark mode may use adjusted values. The gradient values in the homepage and article mockups must match this minimum.
   - **Nav bar (transparent state)**: Always apply `backdrop-filter: blur(12px)` even before the scroll threshold, so nav text is readable over any image content from initial page load. The blur provides a minimum contrast floor regardless of the underlying image.
   - **Nav bar (scroll transition)**: The frosted-glass background (`rgba(250,250,250,0.88)` light / `rgba(24,24,27,0.88)` dark) must fully engage by 40px scroll. During the 0–40px transition zone, the persistent backdrop blur ensures no contrast dip.
   - **Dark mode adjustments**: Hero overlay gradient values must be tested separately in dark mode. The gradient may need to be lighter (less black opacity) or shifted to avoid making the hero area too dark. Nav frosted-glass background switches to dark surface color.
   - **Validation method**: Test with at least two contrasting hero images (one bright/light, one dark) in both light and dark modes. Use browser dev tools color picker or a contrast checker to verify 4.5:1 on hero title text and nav text. Lighthouse Accessibility audit catches most issues but may miss dynamic scroll states — manual check required.
   - **`prefers-reduced-motion`**: When reduced motion is preferred, disable the scroll-fade animation and show the hero image at a static reduced opacity (e.g., 0.6) with the full gradient overlay applied, ensuring contrast is always met without requiring scroll interaction.
6. Add custom CSS in `assets/css/custom.css` for:
   - Nav transparent-to-frosted-glass scroll transition (`.site-header.over-hero` white text scoped to `> nav` only, never to overlay menu; `.site-header.scrolled` frosted glass)
   - Active menu link styling (`.active` class: primary-700, weight 600)
   - Background image fade-on-scroll transitions
   - Hero gradient overlay (light and dark mode variants)
   - `prefers-reduced-motion` overrides
   - All colors must include `.dark` variants per Design Tokens palette
   Do NOT add slide-out panel CSS — Congo's native overlay handles this.
7. Add custom JS in `assets/js/custom.js` for:
   - Scroll event listener: nav transparent→solid transition + background image opacity fade
   - ToC active section tracking
   - `close_menu()` helper and Escape key listener for Congo's checkbox toggle
   - Throttled via requestAnimationFrame
   Do NOT add hamburger toggle JS — Congo's checkbox-based toggle handles open/close natively.
8. Configure social icons: GitHub, LinkedIn, Strava, RSS in overlay menu.
   Footer social icons via custom footer override.
   About page retains full social link list via profile header.
9. Remove appearance switcher from footer (`showAppearanceSwitcher = false`).
   Dark mode toggle is in the nav header menu.

**Validation** (with app running):
- Hamburger icon visible in nav bar; clicking opens Congo's full-screen overlay menu
- Menu contains all nav links (Articles, Speaking, About, Tags) and social icons (GitHub, LinkedIn, Strava, RSS)
- Clicking overlay or pressing Escape closes the menu
- Navigation bar has backdrop blur from initial load; gains frosted-glass solid background after 40px scroll
- Background image (homepage hero, article hero when `backgroundImage` set) fades smoothly on scroll
- **Contrast check (light mode)**: Nav text over hero image ≥4.5:1 at 0px scroll (blur only) and at 40px+ scroll (frosted glass). Hero title text ≥4.5:1 with gradient overlay. Test with a bright image and a dark image.
- **Contrast check (dark mode)**: Same checks with dark mode active. Gradient overlay and frosted-glass background use dark mode values.
- **Reduced motion check**: With `prefers-reduced-motion: reduce` enabled, hero image shows at static opacity with full overlay — no scroll animation. Text still meets 4.5:1.
- Background image does not cause layout shift or exceed 500KB page weight budget
- Dark mode toggle works (in nav bar)
- Social icons in overlay menu and footer render and link correctly
- Keyboard navigation: Tab through nav buttons, Enter opens menu, Escape closes, focus returns to hamburger
- Test on mobile viewport: overlay menu works; background image scales appropriately
- Page without `backgroundImage` renders with solid nav (no transparent state)
- Slate color scheme renders correctly in both light and dark modes

---

### Phase 4: Comments — Dual System

**Goal**: Pre-2025 posts show Disqus; post-2025 posts show Giscus.

**Steps**:
1. Create `layouts/partials/comments.html` with date-based routing:
   - If post date < `giscusCutoffDate`: render Disqus via Hugo internal template in read-only mode
   - If post date ≥ `giscusCutoffDate`: render Giscus script tag
   - If `comments` param is false or unset: render nothing
2. Disable new Disqus comments:
   - In Disqus admin (lanyonm.disqus.com), close comments on all existing threads, OR
   - Use Disqus `this.page.disableNewComments = true` config in the Disqus embed script to disable the comment form while still displaying existing threads
3. Set up Giscus:
   - Enable GitHub Discussions on `lanyonm/lanyonm.github.io`
   - Visit giscus.app to get repo ID and category ID
   - Add IDs to `hugo.toml` params
4. Verify Disqus shortname `lanyonm` is still active

**Validation** (with app running):
- Load a pre-2025 post with `comments: true` → Disqus widget appears with existing comments visible but no comment form / new comments disabled
- Load a post-2025 post with `comments: true` → Giscus widget appears allowing new comments
- Load a post without `comments` → no comment section
- Both comment widgets load async/deferred (no render blocking)

---

### Phase 5: Special Pages & Feed

**Goal**: About, Speaking, Tags, 404, and RSS feed all render correctly.

**Steps**:
1. Create `content/about.md` from existing `about.md` — preserve disclaimer ("opinions expressed here are my own"), full social links list (replace Font Awesome icons with Congo icon system or labeled text links)
2. Create `content/speaking/_index.md` from existing speaking content
3. Create `layouts/404.html` with:
   - Friendly message
   - Link to create GitHub issue (pre-filled: title "LanyonM Blog Broken Link", body placeholder, label "bug")
   - Link to homepage
4. Configure RSS: Hugo generates `/index.xml` by default — no override needed
5. Create redirect from `/feed.xml` → `/index.xml`:
   - Add `static/feed.xml` as an HTML meta-refresh redirect, OR
   - Use a Hugo alias on a content page, OR
   - Add a `_redirects` file if supported
6. Verify tag taxonomy auto-generation at `/tags/`:
   - Congo's default taxonomy page displays an alphabetized text list with post counts (e.g., "devops · 13") — similar to the current Jekyll tags page but without anchor-link sections
   - Configure `taxonomy.showTermCount = true` and `article.showTaxonomies = true` in hugo.toml
   - The current Jekyll tags page uses anchor-linked sections grouped by tag with full post listings under each; Congo's approach (flat list → click → individual tag page with posts) is a better UX for 30+ tags
   - If the alphabetized list layout needs customization, override `layouts/taxonomy/taxonomy.html` using Hugo's `.Data.Terms.Alphabetical` method

**Validation** (with app running):
- `/about/` renders with correct content
- `/speaking/` renders section listing
- `/tags/` lists all tags with post counts
- Navigate to a nonexistent URL → custom 404 with issue reporting link and homepage link
- Fetch `/index.xml` → valid RSS with all published posts
- Fetch `/feed.xml` → redirects to `/index.xml`
- Validate RSS against RSS 2.0 spec (use an RSS validator)

---

### Phase 6: SEO & Structured Data Verification

**Goal**: Every post has canonical URL, OpenGraph tags, and schema.org structured data.

**Steps**:
1. Verify Hugo/Congo generates canonical `<link>` tags automatically
2. Verify OpenGraph tags are generated from front matter (`title`, `description`, `og` hash)
3. Verify or add schema.org JSON-LD structured data:
   - Congo may include this by default — verify
   - If not, create `layouts/partials/extend-head.html` with Article/BlogPosting JSON-LD
4. Verify `sitemap.xml` is generated
5. Verify heading hierarchy: one `<h1>` per page, no skipped levels

**Validation** (with app running):
- View page source on 3 representative posts: confirm `<link rel="canonical">`, OG meta tags, JSON-LD script block
- Validate structured data using Google's Rich Results Test or Schema.org validator
- Fetch `/sitemap.xml` — all pages listed
- Inspect heading hierarchy in browser dev tools on 3 posts

---

### Phase 7: GitHub Actions Deployment

**Goal**: Push to main triggers automated build and deploy to blog.lanyonm.org.

**Steps**:
1. Create `.github/workflows/deploy.yml`:
   - Trigger on push to `main`
   - Checkout with `actions/checkout@v4` (no `submodules: true` — we use Hugo modules, not git submodules)
   - Install Hugo extended via `peaceiris/actions-hugo@v3`
   - Run `hugo --minify`
   - Fail build on Hugo errors
   - Upload artifact via `actions/upload-pages-artifact`
   - Deploy via `actions/deploy-pages`
   - Use OIDC credentials (`id-token: write`)
2. Test workflow on the feature branch (builds but does not deploy to production)

**Validation**:
- Push to `001-hugo-migration` branch → workflow runs, build succeeds
- Verify build output artifact is created
- Verify workflow would fail if Hugo produces errors (test with intentional error, then revert)

---

### Phase 8: Jekyll Cleanup

**Goal**: Remove all Jekyll artifacts from the repository.

**Steps**:
1. Delete Jekyll directories: `_layouts/`, `_includes/`, `_sass/`, `css/`, `_posts/`, `_drafts/`
2. Delete Jekyll files: `Gemfile`, `Gemfile.lock`, `_config.yml`, `index.html`, `tags.html`, `speaking.html`, `feed.xml`
3. Delete `.tool-versions` (no longer need Ruby)
4. Keep `LICENSE.md`, `README.md`, `_assets/` (diagram source files — Hugo ignores underscore-prefixed directories)
5. Verify no Jekyll files remain

**Validation**:
- `hugo serve` still runs with zero errors after cleanup
- `grep -r "jekyll\|liquid\|{% " content/` returns zero matches
- No `Gemfile`, `_config.yml`, or `_layouts/` exist in the repo

---

### Phase 9: Final Validation & Lighthouse Audit

**Goal**: All success criteria pass with the site running locally.

**Validation** (with app running — `hugo serve`):

| Success Criterion | How to Validate |
|---|---|
| SC-001: 100% content fidelity | Visit all 32 posts, verify text/code/images/gists/links |
| SC-002: 100% URL redirects | Request all 32 old-format URLs, verify redirect to new URLs |
| SC-003: Deploy <5 min | Verify GitHub Actions workflow duration on feature branch build |
| SC-004: Lighthouse ≥90 all categories | Run `lighthouse` CLI against localhost on 3 representative pages (homepage, a code-heavy post, about page) — all 4 scores ≥90 |
| SC-005: Valid RSS | Fetch `/index.xml`, validate with RSS validator, verify all posts present |
| SC-006: Zero Jekyll syntax | `grep -r "{% " content/` returns zero matches |
| SC-007: Page load <3s | Lighthouse Speed Index ≤3.0s on simulated mobile |
| SC-008: Responsive 320px–2560px | Browser dev tools responsive mode check on 3 viewports (320px, 768px, 2560px) |

Additional constitution-required checks:
- WCAG AA: Color contrast ≥4.5:1, keyboard navigation, semantic HTML, alt text on images
- SEO: Canonical URLs, OG tags, JSON-LD on all posts, valid sitemap.xml
- Heading hierarchy: One h1 per page, no skipped levels
- Page weight: <500KB per article (excluding cached assets)

---

### Phase 10: Cutover

**Goal**: Live site serves Hugo output at blog.lanyonm.org.

**Steps**:
1. Open PR from `001-hugo-migration` → `main` with full migration diff
2. Review PR — confirm Jekyll files removed, Hugo structure complete, all validation passed
3. Merge PR to `main`
4. Switch GitHub Pages source: Settings → Pages → "GitHub Actions"
5. Verify: `curl -I https://blog.lanyonm.org` returns 200
6. Spot-check 3–4 posts, tag page, about page, feed
7. Run Lighthouse on live site

**Rollback**: Revert merge commit on `main`, switch Pages source back to "Deploy from branch"

## Complexity Tracking

Research R0 classifies 7 components as Tier 3 (fully custom): homepage hero, article hero, transparent nav scroll transition, active page highlighting, ToC active section tracking, footer layout, and about page profile header. All are justified by explicit mockup requirements and achievable with template overrides + CSS, consistent with Principle I (Simplicity). Congo's native features handle the remaining 14 Tier 1 and 10 Tier 2 components.
