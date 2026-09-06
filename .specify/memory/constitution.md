<!--
  Sync Impact Report
  ===================
  Version change: (none) → 1.0.0
  Modified principles: N/A (initial ratification)
  Added sections:
    - 10 Core Principles (I–X)
    - Technology Stack & Constraints
    - Quality Gates & Validation Process
    - Governance
  Removed sections: N/A
  Templates requiring updates:
    - .specify/templates/plan-template.md — ✅ compatible (Constitution Check
      section is dynamically filled; no updates needed)
    - .specify/templates/spec-template.md — ✅ compatible (user stories and
      requirements sections align with validation-driven principle)
    - .specify/templates/tasks-template.md — ✅ compatible (phase structure
      and parallel execution align; no principle-specific task types added)
    - .specify/templates/checklist-template.md — ✅ compatible (generic
      checklist structure adapts to any principle set)
    - .specify/templates/agent-file-template.md — ✅ compatible (no
      agent-specific references to update)
  Follow-up TODOs: None
-->

# blog.lanyonm.org Constitution

## Core Principles

### I. Simplicity

Every change MUST favor the simplest viable solution in both
implementation and user experience. Complexity MUST be justified in
writing before it is introduced.

- Prefer built-in Hugo features over custom code or third-party
  shortcodes.
- Layouts, partials, and templates MUST remain readable by someone
  unfamiliar with the project within five minutes.
- Remove dead code and unused assets in the same commit that makes them
  obsolete — do not accumulate technical debt.
- When two approaches achieve the same result, choose the one with fewer
  moving parts.

### II. Accessibility (WCAG Level AA)

The site MUST meet Web Content Accessibility Guidelines (WCAG) 2.1
Level AA compliance. Accessibility is not optional or deferred.

- All images MUST have meaningful `alt` text (decorative images use
  `alt=""`).
- Color contrast ratios MUST meet AA minimums (4.5:1 for normal text,
  3:1 for large text).
- All interactive elements MUST be keyboard-navigable with visible focus
  indicators.
- Semantic HTML elements (`<nav>`, `<main>`, `<article>`, `<aside>`,
  `<header>`, `<footer>`) MUST be used instead of generic `<div>` wrappers.
- Form inputs, if any, MUST have associated `<label>` elements.
- ARIA attributes MUST only be used when semantic HTML is insufficient.

### III. Discoverability (SEO & GEO)

Content MUST be optimized for search engines and generative engine
optimization (GEO) through semantic markup and structured data.

- Every page MUST include `<title>`, `meta description`, and Open Graph
  (`og:title`, `og:description`, `og:image`) tags.
- Structured data (schema.org JSON-LD) MUST be present on article pages
  at minimum (`Article` or `BlogPosting` type).
- Heading hierarchy MUST be logical: one `<h1>` per page, no skipped
  levels.
- A valid `sitemap.xml` and RSS feed (`index.xml`) MUST be generated on
  every build.
- Canonical URLs MUST be set on every page to prevent duplicate content
  indexing.
- Content MUST be written in clear, well-structured prose that serves
  both human readers and LLM-based retrieval systems.

### IV. Performance

The site MUST achieve high Lighthouse scores and a low Speed Index.

- Lighthouse Performance score MUST be ≥ 90 on mobile and desktop.
- Lighthouse Accessibility, Best Practices, and SEO scores MUST each
  be ≥ 90.
- Speed Index MUST be ≤ 3.0 seconds on a simulated mid-tier mobile
  connection.
- Images MUST be lazy-loaded and served in modern formats (WebP) where
  Hugo supports it.
- CSS and JS MUST be minified in production builds (`hugo --minify`).
- No render-blocking external JavaScript unless strictly required (e.g.,
  analytics, comment widgets loaded async/deferred).
- Total page weight for a typical article MUST remain under 500 KB
  (excluding cached assets).

### V. Open Source & Minimal Dependencies

The project MUST prefer permissively-licensed open source software and
minimize runtime dependencies.

- All dependencies (theme, modules, GitHub Actions) MUST use a
  permissive license (MIT, Apache 2.0, BSD, MPL 2.0, or ISC).
- Copyleft-licensed dependencies (GPL, AGPL, LGPL) MUST NOT be
  introduced without explicit justification and approval.
- Runtime dependencies (JavaScript loaded in the browser) MUST be kept
  to the absolute minimum. Each runtime dependency MUST be individually
  justified.
- Hugo modules or Git submodules are preferred over vendored copies of
  third-party code.
- The Hugo binary itself is the only required build tool — no Node.js,
  Ruby, or Python runtimes in the build pipeline.

### VI. Validation-Driven Development

Every change MUST include user-facing validation criteria that can be
executed before merge.

- Pull requests MUST describe how to verify the change works correctly,
  either as manual steps or automated checks.
- Changes to templates or styles MUST include before/after screenshots
  or a description of the visual change.
- Content changes MUST be previewed with `hugo serve` and spot-checked
  before commit.
- Automated checks (HTML validation, link checking, Lighthouse CI) are
  preferred over manual verification where feasible.
- The validation criteria MUST be specific enough that someone other
  than the author could execute them.

### VII. URL Continuity

Prior inbound links MUST continue to resolve gracefully when URLs
change. Broken links erode trust and SEO value.

- When a post URL changes, Hugo `aliases` MUST be added to the new
  content file to redirect from the old path.
- The old permalink structure (`/articles/YYYY/MM/DD/slug/`) MUST
  redirect to the new structure (`/articles/slug/`) via aliases.
- A custom 404 page MUST exist and provide helpful navigation.
- Link-checking MUST be part of the validation process for any change
  that modifies URL structures, moves content, or removes pages.
- Redirects MUST return HTTP 301 (permanent) semantics where possible.

### VIII. Automated Deployment

The site MUST be deployed exclusively through GitHub Actions. No manual
build-and-upload steps are permitted.

- A single push to the `main` branch MUST trigger the full
  build-and-deploy pipeline.
- The GitHub Actions workflow MUST use `hugo --minify` for production
  builds.
- The workflow MUST fail the build on Hugo errors rather than deploying
  a broken site.
- Deployment credentials MUST use GitHub's built-in OIDC (`id-token:
  write`) — no long-lived secrets or API keys.
- The workflow file (`.github/workflows/deploy.yml`) MUST be version-
  controlled and reviewed like any other code change.

### IX. GitHub Pages Hosting

The site MUST be hosted on GitHub Pages. Infrastructure decisions MUST
be compatible with GitHub Pages constraints.

- The deploy target is the `github-pages` environment using the
  `actions/deploy-pages` action.
- Custom domain (`blog.lanyonm.org`) MUST be configured via a `CNAME`
  file in the `static/` directory.
- HTTPS MUST be enforced (GitHub Pages provides this automatically for
  custom domains).
- No server-side logic, databases, or dynamic backends — the site is
  purely static.
- GitHub Pages size and rate limits MUST be respected (repository < 1 GB,
  site < 1 GB, 10 builds per hour soft limit).

### X. Hugo Best Practices

Hugo is the site framework. All development MUST follow Hugo idioms
and conventions.

- Content MUST live in `content/` organized by section (e.g.,
  `content/articles/`, `content/speaking/`).
- Layouts MUST follow Hugo's lookup order: theme defaults, then project-
  level overrides in `layouts/`.
- Configuration MUST use `hugo.toml` (not `config.toml` or `config.yml`)
  as the primary config file.
- Front matter MUST use YAML format for consistency with migrated
  content.
- Hugo shortcodes MUST be preferred over raw HTML in content files.
- Theme customization MUST use Hugo's override mechanism (copying theme
  files to project `layouts/` or `assets/`) rather than forking the
  theme.
- Hugo's built-in features (sitemap, RSS, syntax highlighting, image
  processing) MUST be used instead of external tools or plugins.
- `hugo serve` MUST produce zero warnings in local development for any
  change to be considered complete.

## Technology Stack & Constraints

- **Framework**: Hugo (extended edition) — single-binary static site
  generator with no runtime dependencies.
- **Theme**: Congo (v2) — Tailwind-based, multiple color schemes, sticky
  ToC, built-in search, Lighthouse-optimized.
- **Hosting**: GitHub Pages via GitHub Actions deployment.
- **Comments**: Dual system — Disqus for pre-2025 posts, Giscus for new
  posts (date-based routing in `comments.html` partial).
- **Analytics**: Google Analytics 4 (`G-NN7JP65RMS`).
- **Domain**: `blog.lanyonm.org` (custom domain via CNAME).
- **Source control**: Git on GitHub (`lanyonm/lanyonm.github.io`),
  `main` branch is the production branch.
- **Build requirements**: Hugo extended edition only. No Node.js, Ruby,
  Python, or other runtimes in the build pipeline.

## Quality Gates & Validation Process

Every change MUST pass these gates before merging to `main`:

1. **Build gate**: `hugo --minify` completes with zero errors and zero
   warnings.
2. **Local preview**: `hugo serve` renders the affected pages correctly,
   verified by the author.
3. **Link integrity**: No broken internal links introduced. For URL
   changes, aliases are verified to redirect correctly.
4. **Accessibility spot-check**: New or modified templates are checked
   against WCAG AA criteria (contrast, keyboard nav, semantic markup).
5. **Performance spot-check**: Lighthouse audit on affected pages shows
   no regression below the thresholds defined in Principle IV.
6. **License check**: Any new dependency has a verified permissive
   license.
7. **PR validation criteria**: The pull request description includes
   specific, reproducible steps to verify the change.

Automated CI checks SHOULD be added incrementally:
- HTML validation (e.g., `html-proofer` or equivalent Hugo-compatible
  tool)
- Lighthouse CI for performance regression detection
- Link checking on generated output

## Governance

This constitution is the authoritative source of project principles and
constraints. It supersedes ad-hoc decisions and prevails when guidance
conflicts.

- **Amendments**: Any change to this constitution MUST be documented in
  a commit with a clear rationale. Amendments follow semantic versioning
  (see below).
- **Versioning**:
  - MAJOR: Removal or backward-incompatible redefinition of a principle.
  - MINOR: New principle added or existing principle materially expanded.
  - PATCH: Clarifications, wording improvements, non-semantic changes.
- **Compliance review**: Every pull request SHOULD be checked against
  the applicable principles. The plan template's "Constitution Check"
  section MUST reference these principles for feature work.
- **Conflict resolution**: When a principle conflicts with a practical
  constraint, document the conflict, the chosen resolution, and the
  rationale in the PR description or plan's Complexity Tracking table.
- **Runtime guidance**: The `CLAUDE.md` file provides development
  guidance consistent with this constitution. If the two diverge, update
  `CLAUDE.md` to align with the constitution.

**Version**: 1.0.0 | **Ratified**: 2026-04-04 | **Last Amended**: 2026-04-04
