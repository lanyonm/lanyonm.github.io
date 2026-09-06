# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal technical blog (blog.lanyonm.org) built with **Hugo** + the **Congo theme v2** (slate color scheme). Hosted on GitHub Pages via GitHub Actions. Content covers DevOps, monitoring, infrastructure, and leadership.

## Build & Development Commands

```bash
# Local development server (with live reload)
hugo serve --port 1313 --baseURL http://localhost:1313/ --appendPort=false

# Build site
hugo --gc --minify

# Serve with drafts
hugo serve --buildDrafts

# Update Congo theme to latest
hugo mod get -u
```

Deployed via `.github/workflows/deploy.yml` on push to `main` (uses `peaceiris/actions-hugo@v3`, `actions/deploy-pages@v4`, OIDC).

## Architecture

### Content Structure

```
content/
├── articles/         # Blog posts (29 articles + 2 drafts)
├── speaking/         # Conference talks (3 posts)
├── about.md          # About page (uses layout: about)
└── _index.md         # Homepage metadata
```

Permalinks use `:contentbasename` so URLs match the source filename slug:
- Articles: `/articles/<slug>/`
- Speaking: `/speaking/<slug>/`
- 32 published posts have `aliases:` redirecting from old Jekyll `/articles/YYYY/MM/DD/slug/` URLs

### Layouts (Congo overrides)

- `layouts/baseof.html` — patched for Hugo 0.158+ deprecations (`.Language.Locale`, `.Language.Direction`)
- `layouts/_partials/head.html` — patched for `site.Language.Direction`
- `layouts/_partials/schema.html` — patched for `.Site.Language.Locale`
- `layouts/_partials/sharing-links.html` — patched for `hugo.Data.sharing`
- `layouts/_partials/functions/warnings.html` — strips `.Author` warning incompatible with current Hugo
- `layouts/_partials/article-meta.html` — preserves original tag casing via `.Params.tags` (instead of `.LinkTitle`)
- `layouts/_partials/article-pagination.html` — prev/next with direction labels + ISO dates
- `layouts/_partials/header/hamburger.html` — fixed nav, ARIA, active page highlighting, social icons in overlay
- `layouts/_partials/footer.html` — copyright + GitHub/LinkedIn/Strava/RSS row
- `layouts/_partials/extend-head.html` — Google Fonts (Manrope, Literata, JetBrains Mono)
- `layouts/_partials/extend-footer.html` — loads custom.js
- `layouts/index.html` — homepage hero + recent post list
- `layouts/_default/about.html` — profile header with avatar/name/role/bio + social
- `layouts/404.html` — friendly 404 with GitHub issue reporting link
- `layouts/partials/comments.html` — date-based dual routing (Disqus pre-2025-01-01, Giscus post-cutoff)
- `layouts/shortcodes/sidebyside.html`, `speakerdeck.html` — custom shortcodes

### Assets

- `assets/css/custom.css` — design tokens (slate palette, Manrope/Literata/JetBrains Mono), nav transparency, hero gradient, post cards, profile header, ToC, dark mode (via `html.dark` class set by Congo's appearance.js)
- `assets/js/custom.js` — scroll-fade hero opacity (rAF-throttled), nav state transitions, ToC active section tracker, `close_menu()` helper, Escape key close

### Configuration

`hugo.toml` highlights:
- `theme` via Hugo modules (`github.com/jpanther/congo/v2`)
- `params.colorScheme = "slate"`, `dateFormat = "2006-01-02"`
- `params.header.layout = "hamburger"`
- `params.giscusCutoffDate = "2025-01-01"` — posts before this date use Disqus read-only, on/after use Giscus
- `services.googleAnalytics.id = "G-NN7JP65RMS"`
- `services.disqus.shortname = "lanyonm"`
- `[security].sources = ["https://speakerdeck.com"]` for SpeakerDeck embeds
- `[markup.highlight] style = "monokai"`, `noClasses = true`

### Post Front Matter

```yaml
---
title: "Post Title"
description: "Open Graph description"
date: 2024-10-15
tags: [tag1, tag2]
comments: true                                # enables comments partial
images:                                       # OG image (was Jekyll's `og.image`)
  - "/images/foo.jpg"
aliases:                                      # legacy Jekyll URL
  - "/articles/2024/10/15/post-title/"
---
```

Drafts add `draft: true`. Posts in `content/speaking/` get `/speaking/<slug>/` URL automatically.

### Key Integrations

- **Disqus** (read-only legacy): pre-2025 posts via `services.disqus.shortname = "lanyonm"`
- **Giscus** (active comments): post-2025 posts; requires `params.giscus.repoId` and `categoryId` from giscus.app — currently empty (no post-cutoff content yet)
- **Google Analytics**: GA4 `G-NN7JP65RMS` via `services.googleAnalytics.id`

### Diagram Source Files

`_assets/` contains `.dot` source files for Graphviz diagrams. Hugo ignores underscore-prefixed directories so this content is not built/published. Keep as-is.
