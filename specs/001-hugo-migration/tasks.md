# Tasks: Migrate Blog from Jekyll to Hugo

**Input**: Design documents from `/specs/001-hugo-migration/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Not explicitly requested — no test tasks included. Validation is manual via `hugo serve` and Lighthouse CLI per the plan.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase Mapping (plan.md ↔ tasks.md)

| plan.md Phase | tasks.md Phase | Title |
|---|---|---|
| Phase 1 | Phase 1 + Phase 2 | Hugo Scaffold (split: setup config + foundational asset moves) |
| Phase 2 | Phase 3 | Content Migration (US1+US2) |
| Phase 3 | Phase 6 | Theme Customization (US5 — moved later for parallel execution) |
| Phase 4 | Phase 4 | Comments (US4) |
| Phase 5 | Phase 7 | Special Pages & Feed (US6) |
| Phase 6 | Phase 8 | SEO & Structured Data |
| Phase 7 | Phase 5 | GitHub Actions Deployment (US3 — earlier in tasks for parallelism) |
| Phase 8 | Phase 9 | Jekyll Cleanup |
| Phase 9 | Phase 10 | Final Validation & Lighthouse |
| Phase 10 | Phase 11 | Cutover |

The reordering in tasks.md groups by user story priority and parallelism, while plan.md groups by logical implementation order. Both are valid lenses on the same work.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Hugo scaffold, theme installation, and base configuration

- [ ] T001 Scaffold Hugo site into repo root (`hugo new site . --force`)
- [ ] T002 Initialize Hugo modules and install Congo theme v2 (`hugo mod init github.com/lanyonm/lanyonm.github.io && hugo mod get github.com/jpanther/congo/v2`)
- [ ] T003 Create base `hugo.toml` with site metadata (`baseURL`, `title = "Michael Lanyon"`, `languageCode`, `params.description = "Notes and thoughts from LanyonM"`, `params.author.name = "Michael Lanyon"`, `dateFormat = "2006-01-02"`), permalink structure (`articles = "/articles/:slug/"`, `speaking = "/speaking/:slug/"`), taxonomies (`tag = "tags"`), and Congo slate color scheme config, `[markup.goldmark.renderer] unsafe = true` (required for inline HTML in migrated content), `[markup.highlight] style = "monokai"` with `noClasses = true` for dark code blocks per Design Tokens. Verify Hugo/Congo generates unique <title> per page in format "Post Title · Michael Lanyon".
- [ ] T004 Configure Congo theme params in `hugo.toml`: dark mode auto-switch, search, ToC, code copy, reading time, lazy loading, WebP, article sharing links (`article.showShare = true`), footer copyright (`footer.showCopyright = true`), taxonomy display (`taxonomy.showTermCount = true`, `article.showTaxonomies = true`), `article.showComments = true` (required for Congo to render any comments partial), `article.showAuthor = false` (no author block per mockup), `article.showBreadcrumbs = true`, article.showCodeCopy = true (Congo built-in)
- [ ] T005 Configure GA4 analytics in `hugo.toml` (`services.googleAnalytics.id = "G-NN7JP65RMS"`)
- [ ] T006 Configure Disqus in `hugo.toml` (`services.disqus.shortname = "lanyonm"`) and Giscus params (`[params.giscus]` with repo, cutoff date `2025-01-01` — leave repoId/categoryId empty until Phase 5)
- [ ] T007 Add `speakerdeck.com` to Hugo security policy in `hugo.toml` under `[security]`
- [ ] T007a Mockup comparison: verify nav renders with correct font (Manrope), site title "Michael Lanyon", hamburger icon position — compare against all three mockups' nav section
- [ ] T007b Update `.gitignore`: add `public/`, `.hugo_build.lock`, `resources/_gen/`; remove Jekyll-specific entries (`.sass-cache`, `.jekyll-metadata`, `Gemfile.lock`)
- [ ] T007c Verify Congo v2.13.0 compatibility with Hugo v0.159.2+: if build fails due to deprecated `.Author` in Congo's `warnings.html`, create `layouts/_partials/functions/warnings.html` override removing the `.Author` check
- [ ] T007d Verify Congo generates a skip-to-content link targeting `#main-content`. Press Tab on page load — skip link should appear and focus main content on activation. If absent, implement in `layouts/_partials/extend-head.html`.

**Checkpoint**: `hugo serve` runs with zero errors, serves empty Congo site at localhost:1313

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Move static assets and create custom shortcodes that content migration depends on

**CRITICAL**: No content migration can begin until static assets and shortcodes are in place

- [ ] T008 Move `images/` → `static/images/` using `git mv` (54 files, 4.3 MB — git mv preserves history without duplicating blobs)
- [ ] T009 [P] Move `favicon.ico` → `static/favicon.ico` using `git mv`
- [ ] T010 [P] Move `CNAME` → `static/CNAME` using `git mv`
- [ ] T011 [P] Create `layouts/shortcodes/sidebyside.html` — flex container with images and optional separator param, per plan Phase 2 step 8
- [ ] T012 [P] Create `layouts/shortcodes/speakerdeck.html` — SpeakerDeck embed with `data-id` and `data-ratio` params, per plan Phase 2 step 9
- [ ] T012a Keep `_assets/` directory in repo as-is (contains `.dot` source files for diagrams). Hugo ignores underscore-prefixed directories — they are not built or published. No action needed beyond verifying it is not deleted during Jekyll cleanup.

**Checkpoint**: `hugo serve` still runs, static assets accessible at `/images/*`, shortcodes available for content

---

## Phase 3: User Story 1 - All Existing Content Renders Correctly (Priority: P1) + User Story 2 - Existing URLs Continue to Work (Priority: P1)

**Goal**: All 32 posts + 2 drafts render with full content fidelity. All old-format URLs redirect to new URLs. About and Speaking pages render at expected paths.

**Independent Test**: Visit each of the 32 posts locally — text, code blocks, images, gists, internal links, blockquotes, side-by-side images, and SpeakerDeck embeds all render. Request old-format URLs and verify redirects. Visit `/about/` and `/speaking/`.

**Why combined**: US1 and US2 are tightly coupled — URL aliases are added during front matter migration, and both stories require the same content files to exist. They cannot be tested independently of each other.

### Content File Migration

- [ ] T013 Move 29 article posts from `_posts/*.md` → `content/articles/` stripping date prefix from filenames (exclude 3 speaking posts)
- [ ] T013a Create `content/articles/_index.md` with `title: "Articles"` and `description: "Technical articles about DevOps, monitoring, infrastructure, and leadership."`
- [ ] T014 Move 3 speaking posts from `_posts/*.md` → `content/speaking/` stripping date prefix (`web-performance-monitoring-devopsdays-minneapolis.md`, `innovation-creative-company-devopsdays-newyork.md`, `creative-and-technology-a-partnership-devopsdays-msn.md`)
- [ ] T015 Move `_drafts/*.md` → `content/articles/` with `draft: true` AND `date` field added to front matter (2 files: `not-invented-here-bias.md` → `date: 2013-06-05`, `python-sphinx-build-watch-script.md` → `date: 2014-12-01`)

### Front Matter Updates (all 34 content files)

- [ ] T016 Remove `layout:` field from all post front matter
- [ ] T017 Remove `category:` field from all post front matter
- [ ] T018 Add `aliases:` with old-format URL to all 32 published posts (e.g., `aliases: ["/articles/2016/01/24/slug/"]` for articles, `aliases: ["/speaking/2016/11/02/slug/"]` for speaking posts)
- [ ] T018a Convert `og:` front matter blocks in 12 posts to Congo's `images:` format: replace `og: { image: 'filename.jpg', ... }` with `images: ["/images/filename.jpg"]`. For external URLs, keep as-is. Remove `og:` block entirely.

### Jekyll Syntax Conversion

- [ ] T019 Convert 82 `{% highlight lang %}...{% endhighlight %}` blocks to fenced code blocks (` ```lang `) across 20 posts
- [ ] T019a Override `layouts/_partials/article-meta.html`: replace `{{ .LinkTitle }}` taxonomy rendering with `{{ range .Params.tags }}` to preserve original front matter tag casing
- [ ] T019b Audit all content files for `#` (h1) headings in body — Congo renders title as h1, so body headings must start at `##`. Convert and adjust sub-headings to maintain hierarchy.
- [ ] T020 [P] Convert 16 `{% post_url YYYY-MM-DD-slug %}` links to `{{< ref "slug" >}}` across 11 posts
- [ ] T021 [P] Convert 5 `{% gist user/id %}` embeds to `{{< gist user id >}}` across 4 posts
- [ ] T022 [P] Convert 3 `<div class="center quote">` blocks to Markdown blockquotes (`> "Quote text"`) in 2 posts
- [ ] T022a [P] Convert 39 `<div class="center"><figure>` blocks to Hugo `{{< figure >}}` shortcode across 14 posts — use `src`, `link`, and `caption` params. Hugo's built-in `figure` produces semantic `<figure>` + `<figcaption>` natively. Preserve existing alt text from img attributes; if no alt exists, derive from caption text. Decorative images use alt="".
- [ ] T022b [P] Replace 32 `{{ site.url }}/images/` Liquid template references with `/images/` (relative paths) across 9 posts — these are inside the figure blocks converted by T022a
- [ ] T022c [P] Convert 2 float-right `<div class="right"><figure>` blocks to Hugo `{{< figure >}}` shortcode with `class="right"` in `a-participants-conference-devopsdays-chicago.md`
- [ ] T023 [P] Convert 2 side-by-side image divs to `{{< sidebyside separator="+" >}}` shortcode in `spring-4-mybatis-java-config.md` and `testing-multiple-grails-versions-travis-ci.md`
- [ ] T024 [P] Convert 3 SpeakerDeck `<script>` embeds to `{{< speakerdeck id="..." ratio="..." >}}` shortcode in the 3 speaking posts
- [ ] T024a [P] Convert YouTube iframe embed to Hugo `{{< youtube ku3O4HnMXrM >}}` shortcode in `web-performance-monitoring-devopsdays-minneapolis.md`. If start time offset (t=400) is needed, may require raw HTML with responsive CSS instead.

### Special Pages

- [ ] T025 [P] Create `content/about.md` from existing `about.md` with Hugo-compatible front matter. Restructure content under mockup section headings: "About This Blog" (leadership/teams paragraph), "Professional Background" (DEPT role, DevOps community), "Beyond Work" (bike racing, 606 Racing), "Get in Touch" (social links as markdown list). Preserve personal voice — reorganize, don't rewrite.
- [ ] T026 [P] Create `content/speaking/_index.md` as section listing page — match `specs/001-hugo-migration/mockups/speaking.html` mockup (same post card design as homepage, active "Speaking" nav link). The speaking listing page must NOT display the "speaking" tag on post cards (it is redundant on a page that only shows speaking posts).
- [ ] T027 [P] Create `layouts/404.html` with friendly message, GitHub issue reporting link (pre-filled title "LanyonM Blog Broken Link", label "bug"), homepage link, and JavaScript to inject `window.location.href` into the issue body at runtime (Hugo's `{{ .RelPermalink }}` renders as `/404.html` at build time) — match `specs/001-hugo-migration/mockups/404.html` mockup for layout, button CTA styling, and tone

### Validation

- [ ] T028 Run `hugo serve` and verify zero errors, zero warnings
- [ ] T029 Spot-check all 32 posts: text, code highlighting, images, internal links render correctly
- [ ] T029a Audit all images in migrated content for alt text: every figure shortcode and img must have meaningful alt text or alt="" for decorative images. No missing alt attributes allowed.
- [ ] T030 Verify gist embeds load on the 4 posts that use them
- [ ] T031 Verify blockquotes render on the 2 posts with former pull-quotes
- [ ] T032 Verify side-by-side images render on the 2 posts that use them
- [ ] T033 Verify SpeakerDeck embeds load on the 3 speaking posts
- [ ] T033a Verify figure images with captions render correctly on the 14 posts that use Hugo `figure` shortcode
- [ ] T033b Verify float-right images display correctly on `a-participants-conference-devopsdays-chicago.md`
- [ ] T033c Verify YouTube embed loads on `web-performance-monitoring-devopsdays-minneapolis.md`
- [ ] T034 Verify drafts are NOT visible in production build (`hugo` without `--buildDrafts`)
- [ ] T035 Verify old-format URLs redirect to new URLs via aliases (spot-check 5+ posts)
- [ ] T036 Verify `/about/` and `/speaking/` render at expected paths
- [ ] T037 Verify 404 page renders for nonexistent URLs with issue reporting link
- [ ] T037a Edge case (FR-031): simulate gist API failure (block requests to `gist.github.com` in DevTools) on a post with a gist embed — verify the rest of the post still renders without a broken layout or visible error.
- [ ] T037b Edge case (FR-031): load homepage and an article with JavaScript disabled — verify text, images, code blocks, and internal links remain readable. Search and comment widgets are expected to be unavailable; layout MUST NOT collapse.
- [ ] T037c Edge case (FR-032): render a post that has no `tags:` in front matter — verify no empty tag section, separator, or stray punctuation appears in the post card or article hero.
- [ ] T038 Grep for remaining Jekyll syntax (`{% highlight`, `{% post_url`, `{% gist`, `{% endhighlight`): must return zero matches
- [ ] T038a Verify homepage at `/` displays recent posts in reverse-chronological order (FR-022)
- [ ] T038b Mockup comparison: serve mockups at localhost:8889 and built site at localhost:1313. Compare homepage post list, article prose styling, and about page against respective mockups. Report all discrepancies before proceeding.

**Checkpoint**: All 32 posts render correctly. Old URLs redirect. About, Speaking, and 404 pages work. Zero Jekyll syntax remains.

---

## Phase 4: User Story 4 - Comments Work on Old and New Posts (Priority: P2)

**Goal**: Pre-2025 posts show Disqus in read-only mode. Post-2025 posts show Giscus with active commenting.

**Independent Test**: Load a pre-2025 post with `comments: true` — Disqus widget appears, no comment form. Load a post-2025 post — Giscus widget appears. Load a post without `comments` — no comment section.

### Implementation

- [ ] T039 Create `layouts/partials/comments.html` with date-based routing: Disqus (read-only) for posts before `giscusCutoffDate`, Giscus for posts on/after cutoff, nothing if `comments` is false/unset. In `layouts/articles/single.html`, wrap the comments area with `<div class="comments-section"><div class="comments-label">Comments</div>...</div>` per HTML Class Contract. Include a visible "Read-only — new comments disabled" indicator in the Disqus section per FR-009a.
- [ ] T040 Configure Disqus read-only mode in the comments partial using `this.page.disableNewComments = true` in the Disqus embed config
- [ ] T041 Set up Giscus: enable GitHub Discussions on `lanyonm/lanyonm.github.io`, create "Blog Comments" category (Announcements type), visit giscus.app to get repo ID and category ID
- [ ] T041a Verify Disqus shortname `lanyonm` is still active by loading the existing Disqus admin or fetching `https://lanyonm.disqus.com/embed.js` — confirm 200 response. (plan.md Phase 4 step 4)
- [ ] T042 Update `hugo.toml` with Giscus `repoId` and `categoryId` values from giscus.app

### Validation

- [ ] T043 Verify pre-2025 post with `comments: true` shows Disqus with existing comments but no comment form
- [ ] T044 Verify post-2025 post with `comments: true` shows Giscus widget allowing new comments
- [ ] T045 Verify post without `comments` shows no comment section
- [ ] T046 Verify both comment widgets load async/deferred (no render blocking)
- [ ] T046a Verify graceful degradation when Disqus is blocked by an ad blocker: page renders normally, no broken layout or empty placeholder visible

**Checkpoint**: Dual comment system works. Old threads preserved read-only. New posts can receive comments.

---

## Phase 5: User Story 3 - Site Deploys Automatically (Priority: P2)

**Goal**: Push to main triggers automated build and deploy to blog.lanyonm.org.

**Independent Test**: Push to feature branch, verify GitHub Actions workflow runs and build succeeds.

### Implementation

- [ ] T047 Create `.github/workflows/deploy.yml`: trigger on push to `main`, checkout with `actions/checkout@v4` (no `submodules: true` — we use Hugo modules, not git submodules), install Hugo extended via `peaceiris/actions-hugo@v3`, run `hugo --minify`, fail on errors, upload artifact via `actions/upload-pages-artifact@v3`, deploy via `actions/deploy-pages@v4`, use OIDC credentials (`id-token: write`)

### Validation

- [ ] T048 Push to `001-hugo-migration` branch and verify workflow runs and build succeeds
- [ ] T049 Verify build output artifact is created in the workflow run
- [ ] T050 Verify workflow fails if Hugo produces errors (introduce intentional error, confirm failure, then revert)

**Checkpoint**: CI/CD pipeline builds Hugo site successfully. Ready for cutover.

---

## Phase 6: User Story 5 - Modern Reading Experience (Priority: P3)

**Goal**: Slate-themed site with hamburger navigation, transparent pinned nav, background image scroll-fade, dark mode, ToC, search, and responsive design.

**Independent Test**: Verify hamburger menu opens/closes, nav transitions from transparent to solid on scroll, hero background fades, dark mode toggles, ToC navigates, search returns results, mobile layout is responsive.

### Typography Setup

- [ ] T050a Create `layouts/_partials/extend-head.html` with Google Fonts `<link>` tags for Manrope, Literata, and JetBrains Mono. Add font-family overrides in `assets/css/custom.css`: body → Literata, headings/nav/labels → Manrope, code → JetBrains Mono (including `pre code`).

### Navigation (Congo Native Overlay + Customizations)

- [ ] T051 Configure `[params.header] layout = "hamburger"` in `hugo.toml` and add main menu items (Articles, Speaking, About, Tags) via `[[menus.main]]` entries
- [ ] T052 Override `layouts/_partials/header/hamburger.html` to add: active page highlighting via `.RelPermalink` comparison, social icon links (GitHub, LinkedIn, Strava, RSS) with `aria-label` on each. Ensure hamburger label has `aria-expanded` (toggled via JS), menu wrapper has `role="dialog"` `aria-label="Site menu"` `aria-modal="true"`, close label has `aria-label="Close menu"`, dark mode toggle has `aria-label="Toggle dark mode"`, search button has `aria-label="Search"`.
- [ ] T053 Add navigation CSS to `assets/css/custom.css`: transparent nav over hero (`.site-header.over-hero > nav` white text — scoped to nav only, NOT overlay), frosted-glass scroll transition (`.site-header.scrolled`), active menu link styling, all with `.dark` variants per Design Tokens

### Article Navigation Override

- [ ] T053a Override `layouts/_partials/article-pagination.html`: two-column grid (`.article-nav`), "← PREVIOUS" / "NEXT →" uppercase direction labels (`.article-nav-direction`), article title (`.article-nav-title`), date (`.article-nav-date`). Solid border-top separator. Hover: bg neutral-100 with border-radius 8px.

### Hero Background with Scroll-Fade

- [ ] T054 Create `layouts/partials/hero-background.html` partial: renders when `backgroundImage` is set in front matter, outputs absolutely-positioned background with gradient overlay, supports `<picture>` with `backgroundImagePortrait` or CSS `object-position` fallback. Hero background images MUST have role="presentation" and aria-hidden="true" (decorative).
- [ ] T055 Include hero-background partial in base layout (or homepage/article layout overrides) conditionally based on `backgroundImage` param

### About Page Profile Header

- [ ] T055a Create `layouts/_default/about.html` with profile header: avatar (`.profile-avatar`, 140px rounded square with "ML" initials), name (`.profile-name`), role line (`.profile-role`), bio from `.Description` (`.profile-bio`), social icon buttons (`.profile-social`, 36px rounded squares). Render `.Content` in prose wrapper below. Hide date, reading time, and author section.
- [ ] T055b Add profile header CSS to `assets/css/custom.css`: avatar gradient, name/role/bio typography, social button styling (36px, border-radius 8px, neutral-100 bg, hover primary-100/primary-700), all with `.dark` variants per Design Tokens
- [ ] T055c Update `content/about.md` front matter: add `layout: about`, `showAuthor: false`, `showDate: false`, `showReadingTime: false`, `build: { list: never, publishResources: true, render: always }` (excludes from RSS), update description for profile bio text

### Homepage Layout

- [ ] T055d Create `layouts/index.html` custom homepage: 85vh hero section (`.hero`) with background image, gradient overlay, h1 "Notes & thoughts from LanyonM", subtitle paragraph. Below hero: `.content-wrapper` with `.section-label` "Recent Articles" and `.post-list` of `.post-card` elements showing date (ISO format), reading time, title, summary, and tags
- [ ] T055e Add homepage CSS to `assets/css/custom.css`: hero 85vh/520px min-height (mobile 70vh/400px), content-wrapper 780px max-width, section-label, post-card styling per Design Tokens, all with `.dark` variants
- [ ] T055f Create `content/_index.md` with homepage metadata

### Accessibility: Text Contrast Over Background Images

- [ ] T056 Add hero gradient overlay CSS to `assets/css/custom.css`: minimum `linear-gradient(to bottom, rgba(15,23,42,0.4), rgba(15,23,42,0.5) 50%, rgba(15,23,42,0.8))` in light mode — 0.4 minimum at top guarantees 4.5:1 for white text over any image. Separate dark mode variant. Test with both bright and dark hero images.
- [ ] T057 Add nav backdrop-filter CSS to `assets/css/custom.css`: always-on `backdrop-filter: blur(12px)` when over hero, frosted-glass background (`rgba(250,250,250,0.88)` light / `rgba(24,24,27,0.88)` dark) engaging by 40px scroll
- [ ] T058 Add `prefers-reduced-motion` overrides to `assets/css/custom.css`: disable scroll-fade animation, show hero at static 0.6 opacity with full gradient overlay

### Custom JavaScript

- [ ] T059 Create `assets/js/custom.js` with: scroll listener for nav transparent→solid transition + background image opacity fade (requestAnimationFrame throttled), `close_menu()` helper for Congo's checkbox toggle, Escape key listener, ToC active section tracking (detect scroll position, add `.active` class to top-level `<li>`, `.active-child` to nested items)

### Footer

- [ ] T053b Override `layouts/_partials/footer.html`: copyright left (`.footer-text`), social icons right (`.footer-links` with GitHub, LinkedIn, Strava, RSS), same row (`.footer-inner` with flex space-between). Remove dark mode toggle, theme attribution, and scroll-to-top from footer. Set `showAppearanceSwitcher = false`, `showThemeAttribution = false`, `showScrollToTop = false` in `[params.footer]`.
- [ ] T053c Add footer CSS to `assets/css/custom.css`: `.site-footer` border-top, `.footer-inner` max-width + flex, `.footer-links` icon sizing (18px), hover colors, `.dark` variants, mobile column layout at 640px.

### Skip-to-Content

- [ ] T053e Add `#the-top { overflow: hidden; height: 0; }` to `assets/css/custom.css` to prevent the skip-to-content link from being visually exposed by the body padding-top.
- [ ] T053f Add `:focus-visible` styling to `assets/css/custom.css`: `outline: 2px solid` primary-500, `outline-offset: 2px` on all interactive elements (links, buttons, menu items, social icons, ToC links). Must be visible in both light and dark modes. Constitution MUST (Principle II).

### Validation

- [ ] T060 Verify hamburger icon opens Congo's full-screen overlay menu with nav links and social icons (GitHub, LinkedIn, Strava, RSS)
- [ ] T061 Verify Escape key closes the menu; overlay click closes the menu
- [ ] T062 Verify nav has backdrop blur from initial load; gains frosted-glass background after 40px scroll
- [ ] T063 Verify hero background image fades on scroll (test on homepage with `backgroundImage` set)
- [ ] T064 Contrast check (light mode): nav text ≥4.5:1 at 0px and 40px+ scroll; hero title ≥4.5:1 with overlay (test with bright AND dark images). UI component contrast: hamburger icon lines, social button icons (neutral-500 on neutral-100), tag badge text all ≥3:1 against backgrounds.
- [ ] T065 Contrast check (dark mode): same checks with dark mode active
- [ ] T066 Reduced motion check: `prefers-reduced-motion: reduce` shows static opacity, no animation, text still ≥4.5:1
- [ ] T067 Verify dark mode auto-detection and manual toggle work
- [ ] T068 Verify ToC displays on long posts with section navigation
- [ ] T069 Verify client-side search returns relevant results. Verify keyboard accessible: opens via search button, input auto-focused, results navigable with keyboard, Escape closes, focus returns to trigger button.
- [ ] T070 Verify responsive layout on 320px, 768px, and 2560px viewports
- [ ] T070a Mobile UX validation on 320px viewport: verify ToC collapsed by default, all touch targets ≥44px, hero scales without cropping, hamburger overlay usable with touch
- [ ] T071 Verify page without `backgroundImage` renders with solid nav (no transparent state)
- [ ] T072 Keyboard navigation: Tab through nav buttons, Enter opens menu, Escape closes, focus returns to hamburger
- [ ] T072a Mockup comparison: compare homepage hero, nav over hero, footer, and about profile header against respective mockups. Toggle dark mode and verify all text contrast per Design Tokens palette. Verify ToC active state has both color AND non-color cues (font-weight 600 + left border). Test with color blindness simulation (Chrome DevTools rendering emulation).
- [ ] T072b Dark mode validation: toggle to dark mode on homepage, article, and about pages. Verify all prose text, headings, links, tags, ToC, footer, and nav use the dark-mode colors specified in the Design Tokens palette.
- [ ] T072c Dark mode persistence: select dark mode, navigate to 3 pages, close browser, reopen — verify dark mode persists without flash of light mode

**Checkpoint**: Full Blowfish-style reading experience with accessible hamburger nav, hero backgrounds, dark mode, search, and ToC.

---

## Phase 7: User Story 6 - Tag and Feed Discovery (Priority: P3)

**Goal**: Tag archive page lists all tags with counts. RSS feed at `/index.xml` is valid. `/feed.xml` redirects to `/index.xml`.

**Independent Test**: Visit `/tags/` — all tags listed with counts. Fetch `/index.xml` — valid RSS. Fetch `/feed.xml` — redirects.

### Implementation

- [ ] T073 Verify tag taxonomy auto-generates at `/tags/` from Congo config (no custom template needed)
- [ ] T074 Verify RSS feed generates at `/index.xml` by default (Hugo built-in)
- [ ] T075 Create `static/feed.xml` as HTML meta-refresh redirect to `/index.xml` per research R3
- [ ] T076 Add `<link rel="alternate" type="application/rss+xml" href="/index.xml">` in site head (verify Congo includes this or add via `layouts/partials/extend-head.html`)

### Validation

- [ ] T077 Verify `/tags/` lists all tags with post counts. Congo's default is an alphabetized text list (e.g., "devops · 13") linking to individual tag pages — this replaces the current Jekyll anchor-linked layout with a cleaner UX. If layout customization is needed, override `layouts/taxonomy/taxonomy.html`.
- [ ] T078 Verify clicking a tag shows all posts with that tag
- [ ] T079 Verify `/index.xml` returns valid RSS containing all published posts
- [ ] T080 Verify `/feed.xml` redirects to `/index.xml`
- [ ] T081 Validate RSS against RSS 2.0 specification

**Checkpoint**: Tags browsable. RSS feed valid. Old feed URL redirects.

---

## Phase 8: SEO & Structured Data

**Purpose**: Verify and ensure canonical URLs, OpenGraph tags, schema.org JSON-LD, and sitemap across all pages

- [ ] T082 Verify Hugo/Congo generates canonical `<link rel="canonical">` on all pages
- [ ] T083 Verify OpenGraph meta tags (og:title, og:description, og:image, og:type) generate from front matter on 3 representative posts
- [ ] T084 Verify or create schema.org JSON-LD structured data (Article/BlogPosting type): check if Congo includes this; if not, create `layouts/partials/extend-head.html` with JSON-LD template
- [ ] T085 Verify `sitemap.xml` generates with all pages listed
- [ ] T086 Verify heading hierarchy: one `<h1>` per page, no skipped levels on 3 representative posts
- [ ] T087 Validate structured data using Google Rich Results Test or Schema.org validator on 2 posts

**Checkpoint**: All SEO markup present and valid across the site.

---

## Phase 9: Jekyll Cleanup

**Purpose**: Remove all Jekyll artifacts from the repository

- [ ] T088 Delete Jekyll directories: `_layouts/`, `_includes/`, `_sass/`, `css/`
- [ ] T089 Delete original content directories: `_posts/`, `_drafts/` (content already moved to `content/`)
- [ ] T090 [P] Delete Jekyll files: `Gemfile`, `Gemfile.lock`, `_config.yml`, `index.html`, `tags.html`, `speaking.html`, `feed.xml`
- [ ] T091 [P] Delete `.tool-versions` (Ruby no longer needed)
- [ ] T092 Verify `hugo serve` still runs with zero errors after cleanup
- [ ] T093 Verify `grep -r "{% " content/` returns zero matches
- [ ] T094 Verify no `Gemfile`, `_config.yml`, or `_layouts/` exist in the repo
- [ ] T094c Update `.claude/CLAUDE.md` from Jekyll to Hugo: build commands, content structure, theme, config, custom layouts, deployment via GitHub Actions.

**Checkpoint**: Repository contains only Hugo files. No Jekyll artifacts remain.

---

## Phase 10: Final Validation & Lighthouse Audit

**Purpose**: Validate all success criteria with the site running locally

- [ ] T094a Mockup comparison (final): serve mockups and built site side-by-side in Playwright. Compare every element on all three page types per Validation Protocol in plan.md. This is the FIRST validation step — before Lighthouse, grep, or functional checks.
- [ ] T094b Verify rendered HTML uses class names from the HTML Class Contract table in plan.md: check `.site-footer > .footer-inner`, `.article-hero`, `.post-card`, `.profile-header`, `.article-nav`, `.comments-section > .comments-label`, `li.active` in ToC.
- [ ] T095 Visit all 32 posts and verify content fidelity (SC-001)
- [ ] T096 Request all 32 old-format URLs and verify redirects (SC-002)
- [ ] T097 Run Lighthouse CLI on homepage — desktop AND mobile presets, all 4 scores ≥90 each (SC-004)
- [ ] T098 Run Lighthouse CLI on a code-heavy article — desktop AND mobile presets, all 4 scores ≥90 each (SC-004)
- [ ] T099 Run Lighthouse CLI on about page — desktop AND mobile presets, all 4 scores ≥90 each (SC-004)
- [ ] T100 Verify Lighthouse Speed Index ≤3.0s on simulated mobile (SC-007)
- [ ] T101 Verify `/index.xml` validates and contains all posts (SC-005)
- [ ] T102 Verify zero Jekyll syntax remaining: `grep -r "{% " content/` (SC-006)
- [ ] T103 Check responsive rendering on 320px, 768px, 2560px viewports (SC-008)
- [ ] T103a Re-verify homepage displays recent posts in reverse-chronological order after Jekyll cleanup (FR-022 — duplicates T038a intentionally as a post-cleanup smoke check)
- [ ] T104 WCAG AA spot-check: color contrast ≥4.5:1, keyboard navigation, semantic HTML, alt text on images, verify <html lang="en"> present on all rendered pages
- [ ] T104a Run HTML validation (W3C Nu HTML Checker or html-proofer) on homepage, a code-heavy article, and about page. Resolve all errors.
- [ ] T104b Test 200% browser zoom on homepage, article, and about pages — verify no horizontal scroll, no content loss, no text overlap.
- [ ] T105 Verify page weight <500KB on a typical article (excluding cached assets)
- [ ] T105a Verify GA4 tracking script (`G-NN7JP65RMS`) appears in rendered page source on homepage and an article page (FR-014)
- [ ] T106 Verify GitHub Actions workflow duration <5 min on feature branch (SC-003)

**Checkpoint**: All 8 success criteria pass. Site is ready for cutover.

---

## Phase 11: Cutover

**Purpose**: Merge to main and go live

- [ ] T107 Open PR from `001-hugo-migration` → `main` with full migration diff
- [ ] T108 Review PR — confirm Jekyll files removed, Hugo structure complete, all validation passed
- [ ] T109 Merge PR to `main`
- [ ] T110 Switch GitHub Pages source: Settings → Pages → "GitHub Actions"
- [ ] T111 Verify `curl -I https://blog.lanyonm.org` returns 200
- [ ] T112 Spot-check 3–4 posts, tag page, about page, `/index.xml` on live site
- [ ] T113 Run Lighthouse on live site — all 4 scores ≥90

**Rollback plan**: Revert merge commit on `main`, switch Pages source back to "Deploy from branch"

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS content migration
- **US1+US2 (Phase 3)**: Depends on Phase 2 — BLOCKS all other user stories (content must exist)
- **US4 Comments (Phase 4)**: Depends on Phase 3 (needs posts with `comments: true` to test)
- **US3 Deploy (Phase 5)**: Depends on Phase 1 (needs hugo.toml and build to work) — can run in parallel with Phases 3–4
- **US5 Reading Experience (Phase 6)**: Depends on Phase 3 (needs content to validate against) — can run in parallel with Phases 4–5
- **US6 Tags & Feed (Phase 7)**: Depends on Phase 3 (needs content for tag generation and RSS)
- **SEO (Phase 8)**: Depends on Phases 3 + 6 (needs content and theme to verify markup)
- **Jekyll Cleanup (Phase 9)**: Depends on Phase 3 (content must be migrated before deleting originals)
- **Validation (Phase 10)**: Depends on all prior phases
- **Cutover (Phase 11)**: Depends on Phase 10

### User Story Dependencies

- **US1+US2 (P1)**: Start after Foundational — no dependencies on other stories
- **US3 (P2)**: Can start after Setup — independent of content migration
- **US4 (P2)**: Start after US1+US2 — needs posts to test comment rendering
- **US5 (P3)**: Can start after US1+US2 — needs content for visual validation
- **US6 (P3)**: Start after US1+US2 — needs posts for tag/feed generation

### Parallel Opportunities

```
Phase 1 (Setup)
    │
Phase 2 (Foundational: T008-T012 all [P])
    │
Phase 3 (US1+US2: Content Migration)
    ├──────────────────┬──────────────────┬─────────────────┐
Phase 4 (US4)    Phase 5 (US3)    Phase 6 (US5)    Phase 7 (US6)
    │                 │                 │                 │
    └─────────────────┴─────────────────┴─────────────────┘
                              │
                    Phase 8 (SEO)
                              │
                    Phase 9 (Jekyll Cleanup)
                              │
                    Phase 10 (Validation)
                              │
                    Phase 11 (Cutover)
```

### Within Phase 3 (Content Migration)

```
# These can run in parallel (different files):
T020 (post_url conversion) ║ T021 (gist conversion) ║ T022 (blockquotes) ║ T023 (sidebyside) ║ T024 (speakerdeck)

# These can run in parallel (different files):
T025 (about.md) ║ T026 (speaking/_index.md) ║ T027 (404.html)
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: US1 + US2 (Content Migration)
4. **STOP and VALIDATE**: All posts render, URLs redirect, about/speaking/404 work
5. This delivers a functional blog with all content — the core migration

### Incremental Delivery

1. Setup + Foundational → Hugo scaffold ready
2. US1 + US2 → Content migrated, URLs work → **MVP!**
3. US4 (Comments) → Reader engagement preserved
4. US3 (Deploy) → CI/CD pipeline ready (can be done in parallel with US4)
5. US5 (Reading Experience) → Visual polish, Blowfish features
6. US6 (Tags & Feed) → Discoverability restored
7. SEO + Cleanup + Validation → Production-ready
8. Cutover → Live!

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- US1 and US2 are combined into one phase because aliases (US2) are added during content migration (US1) — they cannot be independently tested
- Commit after each task or logical group
- Stop at any checkpoint to validate progress
- Phase 5 (US3/Deploy) can start as early as after Phase 1 if you want to verify the build pipeline independently
