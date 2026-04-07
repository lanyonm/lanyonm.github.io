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

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Hugo scaffold, theme installation, and base configuration

- [ ] T001 Scaffold Hugo site into repo root (`hugo new site . --force`)
- [ ] T002 Initialize Hugo modules and install Congo theme v2 (`hugo mod init github.com/lanyonm/lanyonm.github.io && hugo mod get github.com/jpanther/congo/v2`)
- [ ] T003 Create base `hugo.toml` with site metadata (`baseURL`, `title`, `languageCode`, `params.description = "Notes and thoughts from LanyonM"`, `params.author = "Michael Lanyon"`), permalink structure (`articles = "/articles/:slug/"`, `speaking = "/speaking/:slug/"`), taxonomies (`tag = "tags"`), and Congo slate color scheme config
- [ ] T004 Configure Congo theme params in `hugo.toml`: dark mode auto-switch, appearance switcher, search, ToC, code copy, reading time, lazy loading, WebP, article sharing links (`article.showShare = true`), footer copyright (`footer.showCopyright = true`), taxonomy display (`taxonomy.showTermCount = true`, `article.showTaxonomies = true`)
- [ ] T005 Configure GA4 analytics in `hugo.toml` (`services.googleAnalytics.id = "G-NN7JP65RMS"`)
- [ ] T006 Configure Disqus in `hugo.toml` (`services.disqus.shortname = "lanyonm"`) and Giscus params (`[params.giscus]` with repo, cutoff date `2025-01-01` — leave repoId/categoryId empty until Phase 5)
- [ ] T007 Add `speakerdeck.com` to Hugo security policy in `hugo.toml` under `[security]`

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
- [ ] T014 Move 3 speaking posts from `_posts/*.md` → `content/speaking/` stripping date prefix (`web-performance-monitoring-devopsdays-minneapolis.md`, `innovation-creative-company-devopsdays-newyork.md`, `creative-and-technology-a-partnership-devopsdays-msn.md`)
- [ ] T015 Move `_drafts/*.md` → `content/articles/` with `draft: true` added to front matter (2 files)

### Front Matter Updates (all 34 content files)

- [ ] T016 Remove `layout:` field from all post front matter
- [ ] T017 Remove `category:` field from all post front matter
- [ ] T018 Add `aliases:` with old-format URL to all 32 published posts (e.g., `aliases: ["/articles/2016/01/24/slug/"]` for articles, `aliases: ["/speaking/2016/11/02/slug/"]` for speaking posts)

### Jekyll Syntax Conversion

- [ ] T019 Convert 82 `{% highlight lang %}...{% endhighlight %}` blocks to fenced code blocks (` ```lang `) across 20 posts
- [ ] T020 [P] Convert 16 `{% post_url YYYY-MM-DD-slug %}` links to `{{< ref "slug" >}}` across 11 posts
- [ ] T021 [P] Convert 5 `{% gist user/id %}` embeds to `{{< gist user id >}}` across 4 posts
- [ ] T022 [P] Convert 3 `<div class="center quote">` blocks to Markdown blockquotes (`> "Quote text"`) in 2 posts
- [ ] T022a [P] Convert 39 `<div class="center"><figure>` blocks to Hugo `{{< figure >}}` shortcode across 14 posts — use `src`, `link`, and `caption` params. Hugo's built-in `figure` produces semantic `<figure>` + `<figcaption>` natively.
- [ ] T022b [P] Replace 32 `{{ site.url }}/images/` Liquid template references with `/images/` (relative paths) across 9 posts — these are inside the figure blocks converted by T022a
- [ ] T022c [P] Convert 2 float-right `<div class="right"><figure>` blocks to Hugo `{{< figure >}}` shortcode with `class="right"` in `a-participants-conference-devopsdays-chicago.md`
- [ ] T023 [P] Convert 2 side-by-side image divs to `{{< sidebyside separator="+" >}}` shortcode in `spring-4-mybatis-java-config.md` and `testing-multiple-grails-versions-travis-ci.md`
- [ ] T024 [P] Convert 3 SpeakerDeck `<script>` embeds to `{{< speakerdeck id="..." ratio="..." >}}` shortcode in the 3 speaking posts
- [ ] T024a [P] Convert YouTube iframe embed to Hugo `{{< youtube ku3O4HnMXrM >}}` shortcode in `web-performance-monitoring-devopsdays-minneapolis.md`. If start time offset (t=400) is needed, may require raw HTML with responsive CSS instead.

### Special Pages

- [ ] T025 [P] Create `content/about.md` from existing `about.md` with Hugo-compatible front matter. Preserve disclaimer ("opinions expressed here are my own"). Preserve all social links (GitHub, Bitbucket, LinkedIn, Stack Overflow, SpeakerDeck, Medium, Flickr, Instagram, Strava) — replace Font Awesome `<i>` markup with Congo's icon system or labeled text links.
- [ ] T026 [P] Create `content/speaking/_index.md` from existing speaking content as section listing page
- [ ] T027 [P] Create `layouts/404.html` with friendly message, GitHub issue reporting link (pre-filled title "LanyonM Blog Broken Link", body placeholder, label "bug"), and homepage link

### Validation

- [ ] T028 Run `hugo serve` and verify zero errors, zero warnings
- [ ] T029 Spot-check all 32 posts: text, code highlighting, images, internal links render correctly
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
- [ ] T038 Grep for remaining Jekyll syntax (`{% highlight`, `{% post_url`, `{% gist`, `{% endhighlight`): must return zero matches
- [ ] T038a Verify homepage at `/` displays recent posts in reverse-chronological order (FR-022)

**Checkpoint**: All 32 posts render correctly. Old URLs redirect. About, Speaking, and 404 pages work. Zero Jekyll syntax remains.

---

## Phase 4: User Story 4 - Comments Work on Old and New Posts (Priority: P2)

**Goal**: Pre-2025 posts show Disqus in read-only mode. Post-2025 posts show Giscus with active commenting.

**Independent Test**: Load a pre-2025 post with `comments: true` — Disqus widget appears, no comment form. Load a post-2025 post — Giscus widget appears. Load a post without `comments` — no comment section.

### Implementation

- [ ] T039 Create `layouts/partials/comments.html` with date-based routing: Disqus (read-only) for posts before `giscusCutoffDate`, Giscus for posts on/after cutoff, nothing if `comments` is false/unset
- [ ] T040 Configure Disqus read-only mode in the comments partial using `this.page.disableNewComments = true` in the Disqus embed config
- [ ] T041 Set up Giscus: enable GitHub Discussions on `lanyonm/lanyonm.github.io`, create "Blog Comments" category (Announcements type), visit giscus.app to get repo ID and category ID
- [ ] T042 Update `hugo.toml` with Giscus `repoId` and `categoryId` values from giscus.app

### Validation

- [ ] T043 Verify pre-2025 post with `comments: true` shows Disqus with existing comments but no comment form
- [ ] T044 Verify post-2025 post with `comments: true` shows Giscus widget allowing new comments
- [ ] T045 Verify post without `comments` shows no comment section
- [ ] T046 Verify both comment widgets load async/deferred (no render blocking)

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

### Hamburger Navigation

- [ ] T051 Copy Congo's `layouts/partials/header.html` to project `layouts/partials/header.html` and replace inline nav links with hamburger button (three-line icon)
- [ ] T052 Implement slide-out menu panel in the header partial: nav links (Articles, Speaking, About, Tags) and social icons (LinkedIn, GitHub, Strava), overlay backdrop
- [ ] T053 Add hamburger CSS to `assets/css/custom.css`: icon animation (three lines → X), slide-out panel (fixed right, 300px, transform transition), overlay backdrop, transitions. Also add `figure.right` CSS (`float: right; max-width: 331px; margin: 0 0 1rem 1.5rem;`) for float-right figures from content migration.

### Hero Background with Scroll-Fade

- [ ] T054 Create `layouts/partials/hero-background.html` partial: renders when `backgroundImage` is set in front matter, outputs absolutely-positioned background with gradient overlay, supports `<picture>` with `backgroundImagePortrait` or CSS `object-position` fallback
- [ ] T055 Include hero-background partial in base layout (or homepage/article layout overrides) conditionally based on `backgroundImage` param

### Accessibility: Text Contrast Over Background Images

- [ ] T056 Add hero gradient overlay CSS to `assets/css/custom.css`: minimum `linear-gradient(to bottom, rgba(0,0,0,0.3), rgba(0,0,0,0.6))` in light mode, separate dark mode variant via Congo's theme class
- [ ] T057 Add nav backdrop-filter CSS to `assets/css/custom.css`: always-on `backdrop-filter: blur(12px)` when over hero, frosted-glass background (`rgba(250,250,250,0.88)` light / `rgba(24,24,27,0.88)` dark) engaging by 40px scroll
- [ ] T058 Add `prefers-reduced-motion` overrides to `assets/css/custom.css`: disable scroll-fade animation, show hero at static 0.6 opacity with full gradient overlay

### Custom JavaScript

- [ ] T059 Create `assets/js/custom.js` with: hamburger toggle (open/close menu, overlay, aria-expanded), Escape key handler, focus management (trap in open menu), scroll listener for nav transparent→solid transition + background image opacity fade, throttled via requestAnimationFrame

### Validation

- [ ] T060 Verify hamburger icon opens slide-out menu with nav links and social icons
- [ ] T061 Verify Escape key and overlay click close the menu; hamburger animates to X when open
- [ ] T062 Verify nav has backdrop blur from initial load; gains frosted-glass background after 40px scroll
- [ ] T063 Verify hero background image fades on scroll (test on homepage with `backgroundImage` set)
- [ ] T064 Contrast check (light mode): nav text ≥4.5:1 at 0px and 40px+ scroll; hero title ≥4.5:1 with overlay. Test with bright and dark hero images.
- [ ] T065 Contrast check (dark mode): same checks with dark mode active
- [ ] T066 Reduced motion check: `prefers-reduced-motion: reduce` shows static opacity, no animation, text still ≥4.5:1
- [ ] T067 Verify dark mode auto-detection and manual toggle work
- [ ] T068 Verify ToC displays on long posts with section navigation
- [ ] T069 Verify client-side search returns relevant results
- [ ] T070 Verify responsive layout on 320px, 768px, and 2560px viewports
- [ ] T071 Verify page without `backgroundImage` renders with solid nav (no transparent state)
- [ ] T072 Keyboard navigation: Tab through nav buttons, Enter opens menu, Escape closes, focus returns to hamburger

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

**Checkpoint**: Repository contains only Hugo files. No Jekyll artifacts remain.

---

## Phase 10: Final Validation & Lighthouse Audit

**Purpose**: Validate all success criteria with the site running locally

- [ ] T095 Visit all 32 posts and verify content fidelity (SC-001)
- [ ] T096 Request all 32 old-format URLs and verify redirects (SC-002)
- [ ] T097 Run Lighthouse CLI on homepage — all 4 scores ≥90 (SC-004)
- [ ] T098 Run Lighthouse CLI on a code-heavy article — all 4 scores ≥90 (SC-004)
- [ ] T099 Run Lighthouse CLI on about page — all 4 scores ≥90 (SC-004)
- [ ] T100 Verify Lighthouse Speed Index ≤3.0s on simulated mobile (SC-007)
- [ ] T101 Verify `/index.xml` validates and contains all posts (SC-005)
- [ ] T102 Verify zero Jekyll syntax remaining: `grep -r "{% " content/` (SC-006)
- [ ] T103 Check responsive rendering on 320px, 768px, 2560px viewports (SC-008)
- [ ] T103a Verify homepage displays recent posts in reverse-chronological order (FR-022)
- [ ] T104 WCAG AA spot-check: color contrast ≥4.5:1, keyboard navigation, semantic HTML, alt text on images
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
