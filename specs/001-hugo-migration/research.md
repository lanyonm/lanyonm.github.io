# Research: Migrate Blog from Jekyll to Hugo

**Branch**: `001-hugo-migration` | **Date**: 2026-04-05

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
