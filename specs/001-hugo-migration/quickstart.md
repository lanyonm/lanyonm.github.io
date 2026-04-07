# Quickstart: Migrate Blog from Jekyll to Hugo

**Branch**: `001-hugo-migration` | **Date**: 2026-04-05

## Prerequisites

- Hugo extended edition installed (`brew install hugo`)
- Go installed (required for Hugo Modules: `brew install go`)
- Git

## Local Development

```bash
# Clone and switch to feature branch
git checkout 001-hugo-migration

# Install/update Hugo module dependencies (Congo theme)
hugo mod get

# Start local dev server
hugo serve

# Start with drafts visible
hugo serve --buildDrafts

# Production build (minified)
hugo --minify
```

The site will be available at `http://localhost:1313`.

## Key Files

| File | Purpose |
|------|---------|
| `hugo.toml` | All site configuration |
| `content/articles/*.md` | Blog posts |
| `content/about.md` | About page |
| `content/speaking/_index.md` | Speaking section |
| `layouts/partials/comments.html` | Dual comment system routing |
| `layouts/partials/header.html` | Custom transparent pinned nav |
| `layouts/404.html` | Custom 404 page |
| `assets/css/custom.css` | Custom styles (transparent nav, scroll-fade) |
| `assets/js/custom.js` | Scroll-fade background image effect |
| `.github/workflows/deploy.yml` | CI/CD deployment |

## Writing a New Post

```bash
hugo new content articles/my-new-post.md
```

Edit the generated file in `content/articles/my-new-post.md`. Front matter template:

```yaml
---
title: "Post Title"
date: 2026-04-05
description: "Brief description for meta tags"
tags: [tag1, tag2]
comments: true
draft: true
backgroundImage: "/images/hero.jpg"              # optional: enables scroll-fade background
backgroundImagePortrait: "/images/hero-port.jpg" # optional: portrait crop for mobile
---
```

Remove `draft: true` when ready to publish.

## Validation Commands

```bash
# Build and check for errors/warnings
hugo --minify 2>&1 | grep -E "WARN|ERROR"

# Check for remaining Jekyll syntax in content
grep -r "{% " content/

# Run Lighthouse audit (requires Node.js for npx)
# Start hugo serve in another terminal first
npx lighthouse http://localhost:1313 --output=json --output-path=./lighthouse-report.json

# Validate RSS feed
curl -s http://localhost:1313/index.xml | head -5
```

## Deployment

Deployment is automatic via GitHub Actions on push to `main`. No manual steps required.

To test the build workflow on the feature branch:
```bash
git push -u origin 001-hugo-migration
# Check Actions tab for build status
```
