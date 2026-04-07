# Data Model: Migrate Blog from Jekyll to Hugo

**Branch**: `001-hugo-migration` | **Date**: 2026-04-05

This project is a static site — there is no database. The "data model" is the content structure defined by Hugo front matter and directory organization.

## Entities

### Post (content/articles/*.md)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| title | string | Yes | Post title, used in `<title>` and OG tags |
| date | date (YYYY-MM-DD) | Yes | Publication date, determines sort order |
| description | string | Yes | Used for meta description and OG description |
| tags | list[string] | No | Taxonomy labels; empty list or omitted if none |
| comments | boolean | No | Enables comment widget; defaults to false if omitted |
| draft | boolean | No | If true, excluded from production builds |
| aliases | list[string] | Yes (migrated posts) | Old-format URL(s) for redirect: `/articles/YYYY/MM/DD/slug/` |
| og.image | string | No | Custom OpenGraph image path (from existing `og` hash) |
| backgroundImage | string | No | Path to hero background image (landscape crop); enables scroll-fade effect on the page |
| backgroundImagePortrait | string | No | Path to portrait crop of hero image; if set, served via `<picture>` element on portrait viewports. If omitted, CSS `object-position` reframes the landscape image. |

**Section**: `articles` — determines permalink `/articles/:slug/`

### Draft Post (content/articles/*.md with draft: true)

Same schema as Post. The `draft: true` field excludes it from production builds. Visible with `hugo serve --buildDrafts`.

### Static Page (content/about.md, content/speaking/_index.md)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| title | string | Yes | Page title |
| description | string | No | Meta description |
| menu.main | object | No | Adds page to site navigation menu |

### Tag (auto-generated taxonomy)

Tags are not defined as content files. Hugo generates taxonomy pages automatically from the `tags` field in post front matter. Each unique tag value gets a listing page at `/tags/{tag-name}/`.

### Site Configuration (hugo.toml)

Key configuration sections:

| Section | Purpose |
|---------|---------|
| `[permalinks]` | URL structure per section |
| `[taxonomies]` | Tag taxonomy definition |
| `[params]` | Congo theme parameters, Giscus config, GA4, cutoff date |
| `[params.giscus]` | Giscus comment widget configuration |
| `[menus]` | Navigation menu items and social links |
| `[markup]` | Syntax highlighting, table of contents settings |

## Relationships

```
Post ──< Tag          (many-to-many via tags field)
Post ──> CommentThread (one-to-one, system chosen by date vs giscusCutoffDate)
Section ──< Post      (one-to-many, determined by content directory)
```

## Content Lifecycle

```
Draft ──(remove draft:true)──> Published ──(build)──> Rendered HTML
                                    │
                                    └──(add alias)──> Old URL redirects to new URL
```

No content deletion or archival workflow — posts are permanent once published.
