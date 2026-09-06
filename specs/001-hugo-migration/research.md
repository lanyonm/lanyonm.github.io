# Research: Migrate Blog from Jekyll to Hugo

**Branch**: `001-hugo-migration` | **Date**: 2026-04-05

## R0: Congo v2.13.0 Capability Audit Against Mockups

**Purpose**: For every visual component in the mockups (`specs/001-hugo-migration/mockups/`), classify whether Congo supports it natively, partially, or not at all. This determines the implementation approach for each component.

**Source**: Actual Congo v2.13.0 templates examined in Hugo module cache.

### Tier 1: Congo Native — Config Only

These components work out of the box with `hugo.toml` configuration. No template overrides, custom CSS, or JS needed.

| Component | Config Key | Notes |
|-----------|-----------|-------|
| Hamburger menu with slide-out panel | `[params.header] layout = "hamburger"` | Checkbox-based toggle, full-screen overlay, fade transition. Congo's built-in `menu.js` handles close-on-click. |
| Breadcrumbs on articles | `[params.article] showBreadcrumbs = true` | Recursive parent chain. Hides current page and home. |
| Table of Contents sidebar | `[params.article] showTableOfContents = true` | `<details open>` with "Table of Contents" label. Sticky on desktop (`lg:sticky lg:top-10`). No active section tracking (see Tier 3). |
| Author section on articles | `[params.article] showAuthor = true/false` | Shows avatar, name, bio, social links from `[params.author]`. |
| Heading anchor links (hover-only) | `[params.article] showHeadingAnchors = true` | `#` symbol, `opacity-0 group-hover:opacity-100`. |
| Prev/next article navigation | `[params.article] showPagination = true` | Arrows only (`←` / `→`), shows title + date. No text labels (see Tier 2). |
| Dark mode toggle | `[params.footer] showAppearanceSwitcher = true` | Moon/sun icon toggle. Also available in header via menu `action: "appearance"`. |
| Theme attribution | `[params.footer] showThemeAttribution = false` | "Powered by Hugo & Congo" — hide with `false`. |
| Scroll-to-top button | `[params.footer] showScrollToTop = true/false` | Floating `↑` in bottom-right. |
| RSS autodiscovery | `[outputs] home = ["HTML", "RSS"]` | Auto `<link rel="alternate">` tag. |
| Schema.org JSON-LD | Built-in | Article, WebSite, BreadcrumbList schemas generated automatically. |
| Skip-to-content link | Built-in | `-translate-y-8`, visible on `focus:translate-y-0`. |
| Custom fonts | Create `layouts/_partials/extend-head.html` | Add `<link>` tags for Google Fonts. Congo calls this hook from `head.html`. |
| Code syntax highlighting | `[markup.highlight] style = "monokai"` | Hugo's built-in Chroma highlighter. Set `noClasses = true` for inline dark styles. |
| Speaking section listing | `content/speaking/_index.md` exists | Congo renders default section listing. Custom post-card styling applied via the same CSS as homepage post cards. Speaking mockup (`speaking.html`) defines the visual target. |

### Tier 2: Congo Partial — Config + Minor Override

These components are partially supported. They need a small template override or config workaround to match the mockups.

| Component | What Congo Does | What's Missing | Override Approach |
|-----------|----------------|---------------|-------------------|
| Post list with descriptions | `[params.list] showSummary = true` shows summaries | Tags use `.LinkTitle` (title-cases values) | Override `_partials/article-meta.html` line 60: change `{{ .LinkTitle }}` to raw `.Params.tags` range |
| ISO date format | `dateFormat = "2006-01-02"` in `[params]` | Default is `:date_long` (January 2, 2006) | Config change only |
| Prev/next with text labels | Has arrows + title + date | No "PREVIOUS"/"NEXT" uppercase labels | Override `_partials/article-pagination.html` — add direction labels, remove dates |
| Comments section label | Renders `<hr>` then comment partial | No "COMMENTS" heading | Override `layouts/articles/single.html` — wrap comment section with heading |
| Social icons in hamburger menu | Menu items support `params.icon` | No dedicated social section; no RSS by default | Add menu items with icon params, or override header partial to add social links block |
| Footer layout | Copyright left, appearance switcher right | No social icons row | Create `_partials/extend-footer.html` with social icons, or override `_partials/footer.html` |
| Body background `#fafafa` | Default `bg-neutral` maps to scheme CSS | Congo's neutral-50 may differ from `#fafafa` | Add `body { background: #fafafa; }` in `assets/css/custom.css` |
| Tag case preservation | `.LinkTitle` title-cases all tags | `devops` → `Devops` instead of preserving front matter case | Override `_partials/article-meta.html` to range over `.Params.tags` directly |
| Profile header on about page | `profile` homepage layout has avatar, name, headline, social links | Only available as homepage layout, not standalone page layout | Create custom `layouts/_default/about.html` using Congo's profile partial as reference |
| Social icon buttons (36px squares) | `author-links.html` renders inline icons with scale-on-hover | No rounded-square box styling | Custom CSS: 36px boxes with `border-radius: 8px`, neutral-100 bg, hover primary-100 |

### Tier 3: Custom Implementation Required

These components have no Congo equivalent. They require new templates, significant CSS, and/or custom JavaScript.

| Component | Template | CSS | JS | Approach |
|-----------|----------|-----|----|---------|
| **Homepage hero** (85vh background image with gradient overlay, tagline, subtitle) | New `layouts/index.html` | Major: full-viewport positioning, gradient overlay, responsive height | Optional: scroll-fade opacity | Create custom homepage layout. Hero section with absolute-positioned bg image, gradient `::after` pseudo-element, content positioned at bottom. |
| **Article hero** (50vh background image with title/meta/tags overlaid) | Override `layouts/articles/single.html` | Major: hero positioning, gradient, breadcrumb/title/meta overlay styling | Optional: scroll-fade | Conditional rendering: when `backgroundImage` front matter is set, render hero; otherwise standard layout. |
| **Transparent nav over hero** | Override `layouts/_partials/header/hamburger.html` | Major: transparent bg, white text/icons, backdrop-filter transitions | Yes: scroll listener for class toggle | Add `.over-hero` class when hero present. CSS: transparent state (white text) and scrolled state (frosted glass). JS: detect scroll position, toggle classes. **Critical**: scope white text to nav bar only — do NOT apply to slide-out menu. |
| **Nav scroll transition** (transparent → frosted glass at 40px) | Same header override as above | Included in transparent nav CSS | Included in transparent nav JS | `backdrop-filter: blur(12px) saturate(1.4)`, `background: rgba(250,250,250,0.88)`, `box-shadow: 0 1px 0 rgba(0,0,0,0.06)`. |
| **Active page highlighting in menu** | Header partial override | Small: bold + primary-700 color for `.active` class | Optional (can use Hugo template logic) | In header partial, compare `.RelPermalink` to menu URLs using `hasPrefix`. Add `class="active"` to matching link. |
| **ToC active section tracking** | None (Congo's ToC is static HTML) | Small: `.active` border-left + font-weight on current section `<li>` | Yes: scroll listener, `IntersectionObserver` or `offsetTop` comparison | JS watches scroll position, finds current heading, adds `.active` class to corresponding ToC `<li>`. Must handle nested items: highlight parent `<li>` on outermost `<ul>`. |
| **Footer with social icons on same row** | Override `_partials/footer.html` | Small: flex row, justify-content space-between | None | Replace Congo's footer with custom: `<span class="footer-text">© YEAR Name</span>` left, `<ul class="footer-links">` with icon links right. Remove dark mode toggle and scroll-to-top from footer. |

### Key Congo Template Files for Overrides

When overriding, copy from the module cache at `~/Library/Caches/hugo_cache/modules/filecache/modules/pkg/mod/github.com/jpanther/congo/v2@v2.13.0/layouts/`:

| Override | Source File | Key Lines |
|----------|-----------|-----------|
| Header | `_partials/header/hamburger.html` | Checkbox toggle `#menu-controller`, overlay div, menu panel |
| Article single | `single.html` | Feature image (lines 24-34), taxonomies (via `article-meta.html`), pagination, comments |
| Article meta/tags | `_partials/article-meta.html` | Line 60: `{{ .LinkTitle }}` — change to raw values |
| Article pagination | `_partials/article-pagination.html` | Arrow-only nav, title + date display |
| Footer | `_partials/footer.html` | Copyright, theme attribution, appearance switcher |
| Homepage | `index.html` | Delegates to `_partials/home/page.html` or `profile.html` |
| About/profile | `_partials/home/profile.html` | Avatar, name, headline, bio, social links |

### Dark Mode Requirement

Congo uses Tailwind's `dark:` prefix throughout. All custom CSS must include `.dark` variants for every hardcoded color. Specifically:

- Body text: light `#3f3f46` → dark `#d4d4d8`
- Headings: light `#18181b` → dark `#fafafa`
- Links: light `#334155` → dark `#cbd5e1`
- List items: light `#3f3f46` → dark `#d4d4d8`
- Strong text: light `#27272a` → dark `#fafafa`
- Slide-out menu: must ALWAYS use its own colors, never inherit `.over-hero` white

### Congo's Override Mechanism

Congo uses `_partials/` (underscore prefix) for its internal templates. To override, place the file at the same path in the project's `layouts/` directory. Hugo's lookup order checks the project first, then the theme module. For partials that Congo calls with underscore paths (e.g., `partial "header/hamburger.html"`), the override must also be at `layouts/_partials/header/hamburger.html`.

---

### Known Compatibility Issues

| Issue | Versions | Workaround |
|-------|----------|------------|
| `warnings.html` uses deprecated `.Author` | Congo v2.13.0 + Hugo ≥0.159.2 | Create `layouts/_partials/functions/warnings.html` override removing `.Author` check |

---

## R1: Congo Theme — Transparent Pinned Navigation (Blowfish-style)

**Decision**: Override Congo's header partial with a custom version that adds transparent background, backdrop blur, and sticky positioning.

**Rationale**: Congo's default header layouts (basic, hamburger, hybrid) do not support transparent backgrounds. Blowfish achieves this with CSS `backdrop-filter: blur()` and `bg-transparent` on the nav. Congo's architecture supports this via Hugo's template override mechanism — copy the theme's header partial to `layouts/partials/header.html` and modify.

**Alternatives considered**:
- Use Blowfish theme instead of Congo: Rejected — Congo has superior ToC behavior (sticky sidebar with section highlighting) and better Lighthouse defaults. Transparent nav is achievable with a single partial override.
- Use Congo's `custom` header layout option: Viable if available in current Congo version; research actual availability. Fallback to full partial override.

**Implementation approach**:
- Copy `themes/congo/layouts/partials/header.html` (or from Hugo module cache) to `layouts/partials/header.html`
- Add classes: `fixed top-0 w-full z-50 bg-transparent backdrop-blur-sm`
- Add `transition-colors` for smooth background change on scroll (optional JS enhancement)
- Ensure sufficient contrast over varying content (test with both light/dark images)
- Test accessibility: keyboard nav, focus indicators visible over transparent bg

## R1b: Blowfish-style Background Image with Scroll-Fade

**Decision**: Implement a custom hero partial and scroll-fade JavaScript effect on Congo, inspired by Blowfish's background image feature.

**Rationale**: Blowfish's "background" homepage layout renders a full-viewport background image behind the page content with the image fading out as the user scrolls. Congo does not have this feature built-in. Since we're already overriding the header partial for transparent nav, adding a hero background with scroll-fade is a natural extension using the same customization pattern.

**How Blowfish implements this**:
- Blowfish uses a `hero-background` partial that places an absolutely-positioned background image behind the content area
- A scroll event listener (or IntersectionObserver) adjusts the image opacity from 1.0 → 0.0 over a defined scroll range (typically the first viewport height)
- A semi-transparent gradient overlay sits between the image and text to ensure readability
- The effect is opt-in per page via front matter (`background` or `backgroundImage` field)

**Implementation approach for Congo**:
- Create `layouts/partials/hero-background.html` partial that renders when `backgroundImage` is set in front matter
- The partial outputs a `<div>` with the background image as a CSS `background-image`, absolutely positioned and covering the hero area
- Add a gradient overlay (`linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.6))`) for text contrast
- JavaScript in `assets/js/custom.js`:
  - On scroll, calculate opacity as `1 - (scrollY / fadeDistance)` where `fadeDistance` is roughly one viewport height
  - Use `requestAnimationFrame` for smooth performance
  - Set `will-change: opacity` on the background element for GPU compositing
- The partial is included in the base layout (or homepage layout override) conditionally
- Images should be optimized: use Hugo's image processing to resize for viewport, serve WebP

**Accessibility considerations**:
- Background image is decorative — use `role="presentation"` or `aria-hidden="true"`
- Text overlay must maintain WCAG AA contrast (4.5:1) at all scroll positions
- The gradient overlay ensures this regardless of image content
- Effect should respect `prefers-reduced-motion`: disable fade animation, show static overlay instead

**Performance considerations**:
- Background image must not exceed the 500KB page weight budget
- Use Hugo's image processing to generate appropriately-sized versions
- Lazy-load if below the fold; eager-load if it's the hero image (above the fold)
- `will-change: opacity` + `transform: translateZ(0)` for GPU-accelerated fade

## R2: Congo Theme Installation — Hugo Modules vs Git Submodule

**Decision**: Use Hugo Modules (Go modules).

**Rationale**: Hugo Modules are the recommended approach for Congo. No need to manage submodule state, simpler updates (`hugo mod get -u`), and the Congo documentation recommends this method. The constitution (Principle V) also prefers Hugo modules over vendored copies.

**Alternatives considered**:
- Git submodule: More familiar to some, but adds `.gitmodules` complexity, requires `--recurse-submodules` on clone, and submodule updates are error-prone.
- Vendored copy: Maximum control but violates Principle V (prefer modules over vendored code) and makes updates difficult.

## R3: RSS feed.xml Redirect Mechanism

**Decision**: Use a Hugo alias on a dedicated content file or a static HTML redirect file.

**Rationale**: Hugo aliases generate HTML files with `<meta http-equiv="refresh">` redirects. For `/feed.xml`, the cleanest approach is to place a static file at `static/feed.xml` containing an HTML redirect to `/index.xml`. This works on GitHub Pages without server-side configuration.

**Alternatives considered**:
- Hugo alias on a content page: Aliases work for content pages but generating an alias for a non-content path (`/feed.xml`) requires a workaround content file.
- Netlify-style `_redirects` file: Not supported by GitHub Pages.
- JavaScript redirect: Unnecessary complexity for RSS readers that may not execute JS.

**Implementation**: Create `static/feed.xml` with:
```html
<!DOCTYPE html>
<html>
<head><meta http-equiv="refresh" content="0; url=/index.xml"></head>
<body><a href="/index.xml">RSS Feed</a></body>
</html>
```
Note: RSS readers encountering this HTML instead of XML will not auto-follow the redirect. Consider also adding a `<link rel="alternate" type="application/rss+xml" href="/index.xml">` in the site `<head>` so autodiscovery points to the correct URL. Existing subscribers who hardcoded `/feed.xml` will need to update — the HTML redirect is a courtesy fallback for browsers.

## R4: Giscus Setup Requirements

**Decision**: Enable GitHub Discussions on `lanyonm/lanyonm.github.io`, create a "Blog Comments" category, configure via giscus.app.

**Rationale**: Giscus requires: (1) public repo, (2) Discussions enabled, (3) giscus app installed on the repo, (4) repo ID and category ID obtained from giscus.app. The category should be dedicated to blog comments to keep discussions organized.

**Steps**:
1. Go to repo Settings → Features → check "Discussions"
2. Create a new Discussion category "Blog Comments" (type: Announcements, so only giscus bot creates threads)
3. Visit giscus.app, enter repo name, select category, copy `data-repo-id` and `data-category-id`
4. Add values to `hugo.toml` under `[params.giscus]`

## R5: Lighthouse CI in Validation

**Decision**: Use Lighthouse CLI for local validation; defer Lighthouse CI to post-migration enhancement.

**Rationale**: For the migration itself, running `npx lighthouse http://localhost:1313 --output=json` locally is sufficient to verify scores. Adding Lighthouse CI to the GitHub Actions workflow is valuable but adds a Node.js dependency to the build pipeline, which conflicts with Principle V (Hugo binary is the only required build tool). This can be added as a separate workflow that runs post-deploy.

**Alternatives considered**:
- Lighthouse CI in build pipeline: Requires Node.js runtime, violates Principle V for the build step. Could be a separate job that doesn't gate deployment.
- PageSpeed Insights API: Requires the site to be publicly accessible, not useful for pre-merge validation.

## R6: Congo Built-in Schema.org / JSON-LD Support

**Decision**: Verify Congo's built-in structured data; add custom `extend-head.html` partial if insufficient.

**Rationale**: Hugo generates OpenGraph and Twitter Card meta tags automatically from front matter. Congo may add schema.org JSON-LD via its templates — this needs verification during Phase 6. If Congo does not include JSON-LD, Hugo's `extend-head.html` partial (which Congo supports) can inject Article/BlogPosting structured data using Hugo template variables.

## R7: Content Migration — Jekyll Syntax Conversion

**Decision**: Automated script for bulk conversion, followed by manual spot-checking.

**Rationale**: With 82 highlight blocks, 16 post_url links, and 5 gist embeds, manual conversion is error-prone. A sed/awk script or purpose-built script can handle the mechanical conversion:
- `{% highlight lang %}...{% endhighlight %}` → ` ```lang\n...\n``` `
- `{% post_url YYYY-MM-DD-slug %}` → `{{< ref "slug" >}}`
- `{% gist user/id %}` → `{{< gist user id >}}`

Each converted post should then be visually verified via `hugo serve`.
