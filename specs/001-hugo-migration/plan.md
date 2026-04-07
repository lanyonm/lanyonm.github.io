# Implementation Plan: Migrate Blog from Jekyll to Hugo

**Branch**: `001-hugo-migration` | **Date**: 2026-04-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-hugo-migration/spec.md`

## Summary

Migrate blog.lanyonm.org from Jekyll 3.10.0 (EOL) to Hugo with the Congo theme. The migration covers 32 posts, 2 drafts, 54 images, URL redirects from old permalink structure, dual comment system (Disqus/Giscus), GA4 analytics, and automated GitHub Actions deployment. The Congo theme provides built-in dark mode, search, ToC, and Lighthouse-optimized output. A custom header override will replicate Blowfish-style transparent pinned navigation.

## Technical Context

**Language/Version**: Hugo extended edition (latest stable), Go templates
**Primary Dependencies**: Congo theme v2 (Tailwind-based, MIT license)
**Storage**: N/A (static site, all content in Markdown files)
**Testing**: Manual validation via `hugo serve`, Lighthouse CLI audits, link checking on generated output
**Target Platform**: GitHub Pages (static hosting, custom domain blog.lanyonm.org)
**Project Type**: Static site (content blog)
**Performance Goals**: Lighthouse ≥90 all four categories, Speed Index ≤3.0s, page weight <500KB
**Constraints**: No runtime dependencies beyond Hugo binary; GitHub Pages limits (repo <1GB, site <1GB); no server-side logic
**Scale/Scope**: 32 posts, 2 drafts, 54 images (4.3MB), 3 static pages, ~30 tags

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Simplicity | PASS | Hugo built-ins preferred; Congo provides features out of box. One custom override needed (header partial for transparent nav). |
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
├── partials/
│   ├── header.html                # Hamburger nav with transparent-to-solid scroll behavior
│   ├── hero-background.html       # Background image with scroll-fade effect
│   ├── comments.html              # Dual comment system (Disqus pre-2025, Giscus post-2025)
│   └── extend-head.html           # Custom <head> additions (if needed)
├── shortcodes/
│   ├── sidebyside.html            # Side-by-side image layout shortcode
│   └── speakerdeck.html           # SpeakerDeck embed shortcode
└── 404.html                       # Custom 404 with GitHub issue reporting link

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

**Structure Decision**: Standard Hugo site layout. Content organized by section (`articles/`, `speaking/`). Theme customization via Hugo's override mechanism — only the header partial and 404 layout are overridden. All other features come from Congo's built-in configuration.

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
12. Convert side-by-side image divs (2 occurrences in 2 posts) to a `sidebyside` Hugo shortcode:
   - Create `layouts/shortcodes/sidebyside.html` that renders a flex container with images and an optional separator
   - Usage: `{{</* sidebyside separator="+" */>}}![Alt1](url1)![Alt2](url2){{</* /sidebyside */>}}`
   - Convert `<div class="center spring-mybatis">` in `spring-4-mybatis-java-config.md`
   - Convert `<div class="center grails-travis">` in `testing-multiple-grails-versions-travis-ci.md`
13. Convert SpeakerDeck `<script>` embeds (3 occurrences in 3 speaking posts) to a Hugo shortcode:
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
14. Move static assets using `git mv` (preserves history without duplicating blobs):
   - `git mv images/ static/images/` (54 files, 4.3 MB)
   - `git mv favicon.ico static/favicon.ico`
   - `git mv CNAME static/CNAME`
15. Keep `_assets/` directory in repo (contains `.dot` source files for diagram generation). Hugo ignores underscore-prefixed directories — not built or published.

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

**Goal**: Site renders with Congo theme (slate color scheme), hamburger navigation with slide-out menu, transparent pinned nav bar, background images with scroll-fade effect, and all visual features.

**Design reference**: See `specs/001-hugo-migration/mockups/` for HTML mockups of all three page types. Colors are abstracted into CSS variables for easy theme switching.

**Steps**:
1. Configure Congo with the **slate** color scheme (cool grays with subtle warm accents)
2. Override header partial to implement Blowfish-style **hamburger navigation**:
   - Copy Congo's `layouts/partials/header.html` to project `layouts/partials/header.html`
   - Replace inline nav links with a hamburger button (three-line icon with animated X transition on open)
   - Implement a slide-out menu panel from the right side with nav links and social icons
   - Include search button and dark mode toggle alongside the hamburger in the nav bar
   - Add overlay backdrop when menu is open
   - Nav bar is transparent over hero backgrounds, gains frosted-glass (`backdrop-filter: blur`) background on scroll
   - Ensure keyboard accessibility: Escape closes menu, focus trapped in open menu, aria-expanded on toggle
3. Implement Blowfish-style background image with scroll-fade:
   - Create a hero/banner partial or override the homepage layout to support a full-width background image behind the page header
   - Add JavaScript to fade the background image opacity as the user scrolls down (opacity transitions from 1.0 at top to 0 after a defined scroll distance)
   - Support per-page opt-in via front matter (e.g., `backgroundImage: "/images/hero.jpg"`) so the effect is available on the homepage and optionally on individual posts
   - Support responsive image cropping for landscape vs portrait viewports:
     - If `backgroundImagePortrait` is set in front matter, render a `<picture>` element with `<source media="(orientation: portrait)">` for the portrait crop and the landscape image as the default `<img>`
     - If `backgroundImagePortrait` is not set, use CSS `object-position` shifts per breakpoint to reframe the landscape image for portrait viewports (default: `object-position: center 30%` landscape, `object-position: center center` portrait)
   - Ensure the background image is lazy-loaded, served in WebP where supported, and does not increase page weight beyond the 500KB budget for the page itself
4. **Accessibility: text contrast over background images** — ensure all text layered over hero images and transparent nav meets WCAG AA (4.5:1 normal text, 3:1 large text) at every scroll position and in both light and dark modes:
   - **Hero text overlay**: Apply a gradient overlay between the background image and text content. Minimum overlay: `linear-gradient(to bottom, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.6) 100%)` in light mode. Dark mode may use a lighter or adjusted gradient — test and tune.
   - **Nav bar (transparent state)**: Always apply `backdrop-filter: blur(12px)` even before the scroll threshold, so nav text is readable over any image content from initial page load. The blur provides a minimum contrast floor regardless of the underlying image.
   - **Nav bar (scroll transition)**: The frosted-glass background (`rgba(250,250,250,0.88)` light / `rgba(24,24,27,0.88)` dark) must fully engage by 40px scroll. During the 0–40px transition zone, the persistent backdrop blur ensures no contrast dip.
   - **Dark mode adjustments**: Hero overlay gradient values must be tested separately in dark mode. The gradient may need to be lighter (less black opacity) or shifted to avoid making the hero area too dark. Nav frosted-glass background switches to dark surface color.
   - **Validation method**: Test with at least two contrasting hero images (one bright/light, one dark) in both light and dark modes. Use browser dev tools color picker or a contrast checker to verify 4.5:1 on hero title text and nav text. Lighthouse Accessibility audit catches most issues but may miss dynamic scroll states — manual check required.
   - **`prefers-reduced-motion`**: When reduced motion is preferred, disable the scroll-fade animation and show the hero image at a static reduced opacity (e.g., 0.6) with the full gradient overlay applied, ensuring contrast is always met without requiring scroll interaction.
5. Add custom CSS in `assets/css/custom.css` for:
   - Hamburger icon animation (three lines → X on toggle)
   - Slide-out menu panel (fixed right, 300px width, transform transition)
   - Menu overlay backdrop (semi-transparent black)
   - Nav backdrop-filter blur (always on when over hero) + frosted-glass background (on scroll)
   - Background image fade-on-scroll transitions
   - Hero gradient overlay (light mode and dark mode variants via `prefers-color-scheme` or Congo's theme class)
   - `prefers-reduced-motion` overrides (static opacity, no transitions)
6. Add custom JS in `assets/js/custom.js` (or inline in a partial) for:
   - Hamburger toggle: open/close slide-out menu, overlay, aria-expanded state
   - Escape key closes menu, focus management (trap focus in open menu)
   - Scroll event listener: nav transparent→solid transition + background image opacity fade
   - Throttled/debounced for performance (requestAnimationFrame or IntersectionObserver)
7. Configure social icons: LinkedIn, GitHub, Strava in slide-out menu and footer. About page retains full social link list (GitHub, Bitbucket, LinkedIn, Stack Overflow, SpeakerDeck, Medium, Flickr, Instagram, Strava) — replace Font Awesome `<i>` markup with Congo's icon system or labeled text links.
8. Configure footer with appearance switcher

**Validation** (with app running):
- Hamburger icon visible in nav bar; clicking opens slide-out menu from right
- Menu contains all nav links (Articles, Speaking, About, Tags) and social icons
- Clicking overlay or pressing Escape closes the menu
- Hamburger icon animates to X when menu is open
- Navigation bar has backdrop blur from initial load; gains frosted-glass solid background after 40px scroll
- Background image (homepage hero, article hero when `backgroundImage` set) fades smoothly on scroll
- **Contrast check (light mode)**: Nav text over hero image ≥4.5:1 at 0px scroll (blur only) and at 40px+ scroll (frosted glass). Hero title text ≥4.5:1 with gradient overlay. Test with a bright image and a dark image.
- **Contrast check (dark mode)**: Same checks with dark mode active. Gradient overlay and frosted-glass background use dark mode values.
- **Reduced motion check**: With `prefers-reduced-motion: reduce` enabled, hero image shows at static opacity with full overlay — no scroll animation. Text still meets 4.5:1.
- Background image does not cause layout shift or exceed 500KB page weight budget
- Dark mode toggle works (in nav bar)
- Social icons in slide-out menu and footer render and link correctly
- Keyboard navigation: Tab through nav buttons, Enter opens menu, Escape closes, focus returns to hamburger
- Test on mobile viewport: slide-out menu works; background image scales appropriately
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

No constitution violations requiring justification. The transparent pinned nav (Phase 3) is the only custom override — justified by explicit user requirement and achievable with a single partial override + CSS, consistent with Principle I (Simplicity).
