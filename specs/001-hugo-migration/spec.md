# Feature Specification: Migrate Blog from Jekyll to Hugo

**Feature Branch**: `001-hugo-migration`
**Created**: 2026-04-05
**Status**: Draft
**Input**: User description: "Migrate blog.lanyonm.org from Jekyll to Hugo, following the plan in MIGRATION_PLAN.md"

## Clarifications

### Session 2026-04-05

- Q: Should the RSS feed use Hugo's default `/index.xml` or keep Jekyll's `/feed.xml`? → A: Use Hugo's default `/index.xml` as the canonical feed URL and redirect `/feed.xml` to it for existing subscriber continuity.
- Q: What homepage layout should be used? → A: Recent posts listing in reverse-chronological order (matching current site behavior).
- Q: Should the 404 page preserve the GitHub issue reporting link? → A: Yes, preserve the link to create a GitHub issue pre-filled with "Broken Link" title, body placeholder, and "bug" label (matching current behavior).
- Q: Should Lighthouse ≥90 target apply to all four audit categories? → A: Yes, all four (Performance, Accessibility, Best Practices, SEO) must score ≥90.
- Q: What SEO markup elements should be required? → A: Canonical URLs, OpenGraph meta tags, and schema.org structured data on every post.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - All Existing Content Renders Correctly (Priority: P1)

A reader visits any of the 32 published blog posts and sees the complete content: prose, code blocks with syntax highlighting, embedded GitHub gists, and all images. The reading experience is equivalent to or better than the current Jekyll site.

**Why this priority**: Content is the core asset. If posts don't render correctly, the migration has failed regardless of any other improvements.

**Independent Test**: Can be fully tested by visiting each of the 32 posts locally and verifying text, code blocks, images, and gist embeds all render. Delivers the fundamental value of preserving the entire blog archive.

**Acceptance Scenarios**:

1. **Given** a published post with fenced code blocks, **When** a reader visits the post, **Then** code is displayed with language-appropriate syntax highlighting and correct formatting
2. **Given** a post containing an embedded GitHub gist, **When** a reader visits the post, **Then** the gist content loads and displays inline
3. **Given** a post with inline images, **When** a reader visits the post, **Then** all images load at their expected sizes without broken references
4. **Given** a post with internal links to other posts, **When** a reader clicks the link, **Then** they are navigated to the correct target post
5. **Given** a draft post, **When** the site is built for production, **Then** the draft is not visible to readers

---

### User Story 2 - Existing URLs Continue to Work (Priority: P1)

A reader (or search engine) accesses the blog using a previously-bookmarked or indexed URL in the old format (`/articles/YYYY/MM/DD/slug/`). They are seamlessly redirected to the content at the new simplified URL (`/articles/slug/`).

**Why this priority**: The site has been live since 2012 with inbound links from search engines, RSS readers, and external sites. Broken URLs mean lost traffic and degraded SEO.

**Independent Test**: Can be tested by requesting each of the 32 old-format URLs and verifying a redirect to the correct new URL. Delivers SEO continuity and avoids dead links.

**Acceptance Scenarios**:

1. **Given** a reader with a bookmarked old-format URL, **When** they visit it, **Then** they are redirected to the post at the new URL
2. **Given** a search engine crawling old URLs, **When** it follows the redirect, **Then** it receives an appropriate redirect status code
3. **Given** the new URL structure, **When** a reader visits `/articles/slug/`, **Then** the correct post is displayed
4. **Given** the static pages (About, Speaking), **When** a reader visits them, **Then** they render at their expected paths

---

### User Story 3 - Site Deploys Automatically (Priority: P2)

The blog author pushes changes to the main branch and the site is automatically built and deployed to the custom domain (blog.lanyonm.org) without manual intervention.

**Why this priority**: Automated deployment is essential for a maintainable blog. Without it, every content update requires manual steps that discourage publishing.

**Independent Test**: Can be tested by pushing a change to the main branch and verifying the live site updates within minutes. Delivers zero-friction publishing workflow.

**Acceptance Scenarios**:

1. **Given** a commit pushed to the main branch, **When** the automated build runs, **Then** the site is built and deployed to blog.lanyonm.org
2. **Given** a commit pushed to a non-main branch, **When** the build system checks, **Then** no deployment to the live site occurs
3. **Given** the custom domain blog.lanyonm.org, **When** a reader visits it after deployment, **Then** the site loads over HTTPS

---

### User Story 4 - Comments Work on Old and New Posts (Priority: P2)

Readers can see existing discussions on older blog posts but cannot add new comments via Disqus. New posts use a modern, GitHub-backed commenting system for active discussion.

**Why this priority**: Comments represent community engagement and historical discussion. Losing existing threads degrades the value of older posts, and new posts need a path for reader interaction.

**Independent Test**: Can be tested by loading an old post (pre-2025) and verifying the legacy comment system loads, and loading a new post and verifying the modern comment widget loads. Delivers reader engagement continuity.

**Acceptance Scenarios**:

1. **Given** a post published before 2025 with `comments: true`, **When** a reader views it, **Then** the existing Disqus comment thread is displayed in read-only mode (no new comments allowed)
2. **Given** a new post published after 2025 with `comments: true`, **When** a reader views it, **Then** a Giscus comment widget is displayed allowing new comments
3. **Given** a post with `comments` not set or set to false, **When** a reader views it, **Then** no comment section is displayed

---

### User Story 5 - Modern Reading Experience (Priority: P3)

Readers enjoy an improved browsing experience with dark mode support, a table of contents for long posts, client-side search, and responsive design across devices.

**Why this priority**: These are enhancements over the current site that improve reader experience but are not essential for content preservation or SEO continuity.

**Independent Test**: Can be tested by verifying dark mode toggles correctly, the table of contents navigates to headings, search returns relevant results, and the site is usable on mobile. Delivers a modernized reader experience.

**Acceptance Scenarios**:

1. **Given** a reader whose system prefers dark mode, **When** they load the site, **Then** the site renders in dark mode automatically
2. **Given** a reader on any page, **When** they use the appearance switcher, **Then** the site toggles between light and dark mode
3. **Given** a long post with multiple headings, **When** a reader views it, **Then** a table of contents is displayed that links to each section
4. **Given** a reader looking for a topic, **When** they use the search feature, **Then** relevant posts are returned based on their query
5. **Given** a reader on a mobile device, **When** they browse the site, **Then** the layout is responsive and readable

---

### User Story 6 - Tag and Feed Discovery (Priority: P3)

Readers can browse posts by tag and subscribe to the blog via RSS feed. The tag archive page lists all tags with post counts.

**Why this priority**: Tag browsing and RSS are existing features that regular readers rely on. They should carry over to the new site.

**Independent Test**: Can be tested by visiting the tags page and verifying tag listing, and by fetching the RSS feed URL and validating it contains all posts. Delivers content discoverability.

**Acceptance Scenarios**:

1. **Given** the tags page, **When** a reader visits `/tags/`, **Then** all tags are listed with the number of associated posts
2. **Given** a specific tag, **When** a reader clicks it, **Then** all posts with that tag are listed
3. **Given** an RSS reader, **When** it fetches `/index.xml`, **Then** valid RSS is returned containing recent posts
4. **Given** an RSS reader using the old feed URL, **When** it fetches `/feed.xml`, **Then** it is redirected to `/index.xml`

---

### Edge Cases

- What happens when a reader visits a URL that never existed (not an old-format redirect, just invalid)? A custom 404 page should be displayed.
- What happens when a gist embed fails to load (GitHub API unavailable)? The post should still render with the gist area showing graceful degradation.
- What happens when a post has no tags? The post should render without a tag section rather than showing an empty tag list.
- What happens when a reader disables JavaScript? Core content (text, images, code blocks) should still be readable. Interactive features (search, comments, gist embeds) may be unavailable.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Site MUST render all 32 existing published posts with complete content fidelity (text, code, images, links)
- **FR-002**: Site MUST convert all 82 Jekyll highlight blocks to standard fenced code blocks with syntax highlighting
- **FR-003**: Site MUST convert all 16 inter-post links to working references that resolve to the correct target posts
- **FR-004**: Site MUST convert all 5 GitHub gist embeds to working gist shortcodes
- **FR-005**: Site MUST serve 2 existing drafts as unpublished content not visible in production builds
- **FR-006**: Site MUST redirect all 32 old-format URLs (`/articles/YYYY/MM/DD/slug/`) to simplified URLs (`/articles/slug/`)
- **FR-007**: Site MUST preserve all 54 images (4.3 MB) with working references from posts
- **FR-008**: Site MUST serve the custom domain blog.lanyonm.org over HTTPS
- **FR-009**: Site MUST display existing Disqus comment threads in read-only mode (new comments disabled) on posts published before 2025 that have `comments: true`
- **FR-010**: Site MUST display Giscus comments on posts published from 2025 onward that have `comments: true`
- **FR-011**: Site MUST support automatic dark/light mode based on system preference, plus a manual toggle
- **FR-012**: Site MUST generate a valid RSS feed at `/index.xml` (Hugo's default location)
- **FR-012a**: Site MUST redirect requests to `/feed.xml` to `/index.xml` for existing subscriber continuity
- **FR-013**: Site MUST generate a tag taxonomy page at `/tags/` listing all tags with post counts
- **FR-014**: Site MUST include GA4 analytics tracking (measurement ID: G-NN7JP65RMS)
- **FR-015**: Site MUST deploy automatically via CI/CD when changes are pushed to the main branch
- **FR-016**: Site MUST display a custom 404 page for invalid URLs that includes a link to create a GitHub issue pre-filled with a broken link report title, body placeholder, and "bug" label, plus a link to the homepage
- **FR-017**: Site MUST provide client-side search across all published posts
- **FR-018**: Site MUST display a table of contents for posts with multiple headings
- **FR-019**: Site MUST preserve existing front matter fields (title, description, tags, comments, og) in migrated posts
- **FR-020**: Site MUST render About and Speaking pages at their expected paths
- **FR-021**: Site MUST remove all Jekyll-specific files (layouts, includes, Sass, Gemfile, _config.yml) from the repository after migration
- **FR-022**: Homepage MUST display a reverse-chronological listing of recent posts, matching the current site's homepage behavior
- **FR-023**: Every post MUST include a canonical URL, OpenGraph meta tags (title, description, image, type), and schema.org structured data (Article type with author, date, description)
- **FR-024**: Site MUST use a hamburger-style navigation with a slide-out menu panel containing nav links and social icons, replacing inline nav links
- **FR-025**: Site MUST support an optional per-page hero background image (via `backgroundImage` front matter field) that fades to invisible as the user scrolls down
- **FR-026**: Site MUST support an optional portrait crop of the hero image (via `backgroundImagePortrait` front matter field) served on portrait viewports; when no portrait crop is provided, CSS object-position MUST reframe the landscape image
- **FR-027**: Site MUST respect `prefers-reduced-motion` by disabling scroll-fade animation and displaying the hero image at a static opacity with full contrast overlay
- **FR-028**: Navigation bar MUST be transparent with backdrop blur over hero backgrounds and transition to a solid frosted-glass background on scroll
- **FR-029**: Site MUST convert all custom HTML content blocks (3 pull-quote divs, 2 side-by-side image divs, 3 SpeakerDeck script embeds) to Hugo-native equivalents (Markdown blockquotes and shortcodes)

### Key Entities

- **Post**: A blog article with title, date, description, body content, tags, comment preference, and optional OpenGraph metadata. Posts belong to sections (articles, speaking) that determine their URL structure.
- **Tag**: A taxonomy label applied to posts. Tags aggregate posts into browsable collections.
- **Comment Thread**: Reader discussions attached to a post. Legacy threads (pre-2025) are hosted on Disqus; new threads use Giscus backed by GitHub Discussions.
- **Static Page**: Non-post content (About, Speaking) with standalone URLs and no date-based organization.
- **Feed**: An RSS/XML representation of recent posts for syndication to feed readers.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of the 32 published posts render without content loss or broken elements (images, code blocks, links, gists)
- **SC-002**: 100% of old-format URLs redirect correctly to their new locations
- **SC-003**: Site builds and deploys to the live domain within 5 minutes of a push to the main branch
- **SC-004**: Site achieves a Lighthouse score of 90 or above in all four audit categories: Performance, Accessibility, Best Practices, and SEO
- **SC-005**: RSS feed validates against RSS 2.0 specification and contains all published posts
- **SC-006**: Zero Jekyll-specific syntax remains in any content file after migration
- **SC-007**: Site loads and is fully readable in under 3 seconds on a standard broadband connection
- **SC-008**: All pages render correctly on viewports from 320px (mobile) to 2560px (ultrawide)

## Assumptions

- The blog author is the sole contributor and can switch the GitHub Pages deployment source in repository settings
- Existing Disqus comment threads will continue to load via the Disqus embed as long as the Disqus account (shortname: lanyonm) remains active
- The Giscus commenting system requires enabling GitHub Discussions on the repository, which the author can configure
- The custom domain (blog.lanyonm.org) DNS is already configured to point to GitHub Pages and will not need DNS changes
- Hugo extended edition is available for local development and in the CI/CD environment
- The Congo theme is maintained and compatible with the current Hugo release
- Legacy Google Analytics (UA-42209870-1) is being dropped in favor of GA4 only
- No new content will be published on the Jekyll site during the migration period, avoiding merge conflicts
