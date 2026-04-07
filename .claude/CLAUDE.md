# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal technical blog (blog.lanyonm.org) built with Jekyll and hosted on GitHub Pages. Uses the Lanyon theme (built on Poole). Content covers DevOps, monitoring, infrastructure, and leadership.

## Build & Development Commands

```bash
# Install dependencies
bundle install

# Local development server (with live reload)
bundle exec jekyll serve

# Build site without serving
bundle exec jekyll build

# Serve with drafts visible
bundle exec jekyll serve --drafts
```

The site is deployed automatically by GitHub Pages on push to `master`.

## Architecture

### Layout Hierarchy

`default.html` → `post.html` / `page.html`

- **default.html**: Base layout — includes `head.html`, `sidebar.html`, wraps content, includes `scripts.html`
- **post.html**: Blog articles — adds schema.org markup, tags, dates, optional Disqus comments
- **page.html**: Static pages (About, Speaking, Tags)

### Sass Structure

`css/main.min.scss` imports in order:
1. `_sass/poole.scss` — Base Poole framework
2. `_sass/syntax.scss` — Code syntax highlighting
3. `_sass/lanyon.scss` — Lanyon theme (sidebar, masthead, layout)
4. `_sass/main.scss` — Custom styles, dark mode (`prefers-color-scheme: dark`)

### Post Front Matter

```yaml
---
layout: post
title: "Post Title"
description: "Description for meta tags and Open Graph"
category: articles    # or "speaking"
tags: [tag1, tag2]
comments: true        # enables Disqus
---
```

Posts use standard Jekyll naming: `_posts/YYYY-MM-DD-slug-title.md`. Drafts go in `_drafts/`.

### Key Integrations

- **Disqus**: Comments enabled per-post via `comments: true` in front matter (shortname: `lanyonm`)
- **Google Analytics**: GA4 (`G-NN7JP65RMS`) + legacy UA (`UA-42209870-1`)
- **External JS**: Font Awesome 5, AnchorJS 2.0 (auto-links headings)

### Jekyll Plugins

Only two plugins (both supported by GitHub Pages):
- `jekyll-gist` — Embed GitHub gists
- `jekyll-sitemap` — Auto-generate sitemap.xml
