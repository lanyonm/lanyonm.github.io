# Static Disqus Comment Archive Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the live Disqus embed on pre-2025 posts with a static, privacy-safe HTML rendering of the archived comment threads.

**Architecture:** A throwaway, stdlib-only Python script converts a Disqus XML export into one sanitized JSON file per post under `data/disqus/<slug>.json`. Hugo renders those files with two small partials. The script, its tests, its fixture and the raw export all live in a working directory **outside the repo** (`$WORK`) and are never committed. Only the JSON output, partials, CSS and config changes land. CI keeps building with plain `hugo`.

**Working directory:** before starting, set `WORK` to a directory outside the repo (in Claude Code, use the session scratchpad) and `BLOG_REPO` to the repo root, then export both in every shell used below:

```bash
export WORK=/path/outside/repo/disqus-archive
export BLOG_REPO=/Users/michael.lanyon/projects/lanyonm/lanyonm.github.io
mkdir -p "$WORK/tests/fixtures"
```

**Tech Stack:** Python 3.11 stdlib (`xml.etree`, `html.parser`, `unittest`), Hugo 0.168 extended + Congo v2, existing `assets/css/custom.css`.

**Spec:** No separate spec. Requirements are the Global Constraints below; background is the privacy review that motivated this (Disqus is an ad-tech tracker that loads with no consent on every pre-2025 post).

## Background the implementer needs

- **Old Jekyll threads** were keyed by `page.url`. Jekyll's permalink ended in `.html`, so thread identifiers look like `/articles/2013/05/31/pi-dashboard-kiosk.html` and links look like `https://blog.lanyonm.org/articles/2013/05/31/pi-dashboard-kiosk.html`. These are exactly the `aliases:` values in each post's front matter.
- **Hugo-era threads:** the current `layouts/_partials/comments.html` passes `this.page.identifier = .File.UniqueID` (an MD5 hash) and `this.page.url = .Permalink` (`/articles/<slug>/`). Disqus has probably created a second, empty thread for every post visited since the migration. The export therefore can contain **two threads per post**; posts from both must be merged.
- **Disqus export format** (`xmlns="http://disqus.com"`, `xmlns:dsq="http://disqus.com/disqus-internals"`): `<thread dsq:id>` holds `<id>` (identifier), `<link>` and `<title>`. `<post dsq:id>` holds `<message>` (HTML in CDATA), `<createdAt>` (ISO-8601 UTC), `<isDeleted>`, `<isSpam>`, `<author><name/><email/><username/>…</author>`, `<thread dsq:id>`, and optionally `<parent dsq:id>`.
- **Disqus rewrites outbound links** to `https://disq.us/url?url=<urlencoded target>%3A<hash>&cuid=…`. Those redirects are themselves trackers.
- **Data access:** Hugo 0.158+ uses `hugo.Data` (see `layouts/_partials/sharing-links.html`). A file `data/disqus/pi-dashboard-kiosk.json` is reached with `index hugo.Data.disqus "pi-dashboard-kiosk"`. The slug equals `.File.ContentBaseName` (no page bundles exist in `content/`).
- **Comments partial location:** `layouts/_partials/comments.html` (Congo calls it when `params.article.showComments = true`). Existing styles: `.comments-section`, `.comments-label` and `.disqus-readonly-notice` in `assets/css/custom.css` (~line 1100).

## Global Constraints

- The raw Disqus export (`*.xml.gz`) contains commenter emails and IPs. Keep it outside the repo. The conversion script, tests and fixture also stay in `$WORK`; nothing from `$WORK` is committed.
- Published JSON/HTML may contain only: comment id, author display name, timestamp, sanitized message HTML. No email, username, IP, avatar or Disqus profile URL.
- No third-party requests from the archive: no avatars, no `disq.us` redirect links, no embedded media.
- Allowed message HTML: `p br a b strong i em code pre blockquote ul ol li`. Links only `http`/`https`, always with `rel="nofollow ugc noopener"`.
- Python stdlib only; tests run with `python3 -m unittest discover -s "$WORK/tests" -v`.
- Posts with `comments: false` render nothing, even if archive data exists.
- Giscus behaviour for posts dated after `params.giscusCutoffDate` is unchanged.
- Commit messages carry no `Co-Authored-By` trailer.

## Review Focus

1. Duplicate threads for one post (Jekyll `.html` thread + Hugo-era hash-identifier thread): posts from both are merged into one file, in date order. Covered in Task 3 `test_duplicate_threads_merge`.
2. A reply whose parent was deleted or marked spam: the reply is promoted to top level, not silently dropped. Covered in Task 3 `test_orphan_reply_promoted`.
3. Hostile or broken message HTML, such as a stray `</ol>` or an unclosed `<blockquote>`, that would otherwise break out of the comment list: the output is always balanced. Covered in Task 1 `test_unbalanced_tags_are_balanced`.
4. Re-running the script after a post is renamed or a comment is removed on request: stale JSON files don't linger. Covered in Task 3 `test_rerun_removes_stale_files`.
5. A commenter with a blank display name: rendered as "Guest", never as an empty `<span>`. Covered in Task 2 `test_blank_author_becomes_guest`.

---

## File Structure

| Path | Responsibility |
|---|---|
| `$WORK/disqus_archive.py` *(not committed)* | Export → JSON: sanitize, parse, map threads to slugs, build reply trees, write files |
| `$WORK/tests/test_disqus_archive.py` *(not committed)* | Unit tests for all of the above |
| `$WORK/tests/fixtures/disqus-export.xml` *(not committed)* | Small synthetic export covering every edge case |
| `data/disqus/<slug>.json` | Committed archive output (Task 5 only) |
| `layouts/_partials/comments.html` | Route pre-cutoff posts to the static archive instead of the Disqus embed |
| `layouts/_partials/disqus-archive.html` | Section wrapper: label, notice, top-level list |
| `layouts/_partials/disqus-comment.html` | One comment plus its replies (recursive) |
| `assets/css/custom.css` | Archive styles; replace `.disqus-readonly-notice` |
| `hugo.toml`, `.claude/CLAUDE.md` | Remove `[services.disqus]`; update docs |

---

### Task 1: Message sanitizer

**Files (all in `$WORK`, not committed):**
- Create: `$WORK/disqus_archive.py`
- Create: `$WORK/tests/test_disqus_archive.py`

**Interfaces:**
- Produces: `sanitize_message(html: str) -> str` and `unwrap_disqus_link(href: str) -> str`

- [ ] **Step 1: Write the failing tests** in `$WORK/tests/test_disqus_archive.py`:

```python
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import disqus_archive as da  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"
BLOG_REPO = Path(os.environ["BLOG_REPO"])


class SanitizeTests(unittest.TestCase):
    def test_allowed_markup_survives(self):
        html = "<p>Hi <b>there</b> <code>x</code></p><blockquote>q</blockquote>"
        self.assertEqual(da.sanitize_message(html), html)

    def test_script_and_content_removed(self):
        out = da.sanitize_message("<p>ok</p><script>alert(1)</script><iframe src=x></iframe>")
        self.assertEqual(out, "<p>ok</p>")

    def test_unknown_tags_dropped_text_kept(self):
        self.assertEqual(da.sanitize_message('<div class="x"><span>t</span></div>'), "t")

    def test_attributes_stripped(self):
        self.assertEqual(da.sanitize_message('<p onclick="x" style="y">t</p>'), "<p>t</p>")

    def test_link_gets_rel(self):
        out = da.sanitize_message('<a href="https://example.com/?a=1&b=2" target="_blank">e</a>')
        self.assertEqual(out, '<a href="https://example.com/?a=1&amp;b=2" rel="nofollow ugc noopener">e</a>')

    def test_non_http_link_unwrapped_to_text(self):
        self.assertEqual(da.sanitize_message('<a href="javascript:alert(1)">x</a>'), "x")

    def test_disqus_redirect_unwrapped(self):
        href = "https://disq.us/url?url=https%3A%2F%2Fgithub.com%2Flanyonm%3AAbCdEfGhIjKlMnOpQrStUvWxYz0&cuid=123"
        self.assertEqual(da.unwrap_disqus_link(href), "https://github.com/lanyonm")
        self.assertIn('href="https://github.com/lanyonm"', da.sanitize_message(f'<a href="{href}">g</a>'))

    def test_text_is_escaped(self):
        self.assertEqual(da.sanitize_message("<p>a &lt;b&gt; &amp; c</p>"), "<p>a &lt;b&gt; &amp; c</p>")

    def test_unbalanced_tags_are_balanced(self):
        self.assertEqual(da.sanitize_message("<blockquote><p>q</ol></p>"), "<blockquote><p>q</p></blockquote>")
        self.assertEqual(da.sanitize_message("</li></ol>tail"), "tail")

    def test_br_variants(self):
        self.assertEqual(da.sanitize_message("a<br>b<br/>c"), "a<br>b<br>c")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest discover -s "$WORK/tests" -v`
Expected: `ModuleNotFoundError: No module named 'disqus_archive'`

- [ ] **Step 3: Implement** `$WORK/disqus_archive.py`:

```python
#!/usr/bin/env python3
"""
Convert a Disqus XML export into static, sanitized per-post JSON under data/disqus/.

Throwaway tool kept outside the blog repo: run it, review the output, commit only
data/disqus/. The raw export contains commenter emails and IP addresses.
"""
import re
from html import escape
from html.parser import HTMLParser
from urllib.parse import parse_qs, urlparse

ALLOWED_TAGS = {"p", "br", "a", "b", "strong", "i", "em", "code", "pre", "blockquote", "ul", "ol", "li"}
VOID_TAGS = {"br"}
DROP_CONTENT_TAGS = {"script", "style", "iframe", "object", "embed", "svg", "math"}
DISQUS_HASH_SUFFIX = re.compile(r":[A-Za-z0-9_-]{20,}$")


def unwrap_disqus_link(href):
    """Return the real target of a disq.us redirect link, or href unchanged."""
    parsed = urlparse(href)
    if parsed.netloc.endswith("disq.us") and parsed.path.startswith("/url"):
        target = parse_qs(parsed.query).get("url", [""])[0]
        return DISQUS_HASH_SUFFIX.sub("", target)
    return href


class _Sanitizer(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.stack = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in DROP_CONTENT_TAGS:
            self.skip += 1
            return
        if self.skip or tag not in ALLOWED_TAGS:
            return
        if tag in VOID_TAGS:
            self.out.append(f"<{tag}>")
            return
        if tag == "a":
            href = unwrap_disqus_link(dict(attrs).get("href") or "")
            if urlparse(href).scheme not in ("http", "https"):
                return
            self.out.append(f'<a href="{escape(href)}" rel="nofollow ugc noopener">')
        else:
            self.out.append(f"<{tag}>")
        self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in DROP_CONTENT_TAGS:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip or tag not in self.stack:
            return
        while self.stack:
            open_tag = self.stack.pop()
            self.out.append(f"</{open_tag}>")
            if open_tag == tag:
                break

    def handle_data(self, data):
        if not self.skip:
            self.out.append(escape(data, quote=False))

    def result(self):
        self.close()
        while self.stack:
            self.out.append(f"</{self.stack.pop()}>")
        return "".join(self.out)


def sanitize_message(html):
    """Reduce Disqus message HTML to a small, balanced, tracker-free allowlist."""
    sanitizer = _Sanitizer()
    sanitizer.feed(html or "")
    return sanitizer.result().strip()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `BLOG_REPO="$BLOG_REPO" python3 -m unittest discover -s "$WORK/tests" -v`
Expected: all `SanitizeTests` pass. No commit; nothing in `$WORK` is committed.

---

### Task 2: Parse the Disqus export

**Files (all in `$WORK`, not committed):**
- Modify: `$WORK/disqus_archive.py`
- Modify: `$WORK/tests/test_disqus_archive.py`
- Create: `$WORK/tests/fixtures/disqus-export.xml`

**Interfaces:**
- Consumes: `sanitize_message`
- Produces: `Thread(id, identifier, link, title)`, `Post(id, thread_id, parent_id, author, created_at, message)` (frozen dataclasses, all `str` except `parent_id: str | None`), and `parse_export(path: str | Path) -> tuple[dict[str, Thread], list[Post]]`. `parse_export` excludes deleted and spam posts, sanitizes messages, and accepts `.xml` or `.xml.gz`.

- [ ] **Step 1: Create the fixture** `$WORK/tests/fixtures/disqus-export.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<disqus xmlns="http://disqus.com" xmlns:dsq="http://disqus.com/disqus-internals">
  <category dsq:id="1"><forum>lanyonm</forum><title>General</title><isDefault>true</isDefault></category>

  <!-- Jekyll-era thread: identifier/link match the post's alias -->
  <thread dsq:id="100">
    <id>/articles/2013/05/31/pi-dashboard-kiosk.html</id>
    <forum>lanyonm</forum><category dsq:id="1"/>
    <link>https://blog.lanyonm.org/articles/2013/05/31/pi-dashboard-kiosk.html</link>
    <title>Raspberry Pi Dashboard Kiosk</title>
  </thread>
  <!-- Hugo-era duplicate thread: hash identifier, new-style link -->
  <thread dsq:id="101">
    <id>0f1e2d3c4b5a69788796a5b4c3d2e1f0</id>
    <forum>lanyonm</forum><category dsq:id="1"/>
    <link>https://blog.lanyonm.org/articles/pi-dashboard-kiosk/</link>
    <title>Raspberry Pi Dashboard Kiosk · Michael Lanyon</title>
  </thread>
  <!-- Thread for a page that no longer exists -->
  <thread dsq:id="102">
    <id></id>
    <forum>lanyonm</forum><category dsq:id="1"/>
    <link>http://localhost:4000/drafts/never-published.html</link>
    <title>Draft</title>
  </thread>

  <post dsq:id="1000">
    <id/><message><![CDATA[<p>Great post!</p>]]></message>
    <createdAt>2013-06-01T10:00:00Z</createdAt>
    <isDeleted>false</isDeleted><isSpam>false</isSpam>
    <author><email>alice@example.com</email><name>Alice Example</name><isAnonymous>false</isAnonymous><username>alice</username></author>
    <ipAddress>203.0.113.7</ipAddress>
    <thread dsq:id="100"/>
  </post>
  <post dsq:id="1001">
    <id/><message><![CDATA[<p>Agreed &amp; thanks</p>]]></message>
    <createdAt>2013-06-02T09:00:00Z</createdAt>
    <isDeleted>false</isDeleted><isSpam>false</isSpam>
    <author><email>bob@example.com</email><name>Bob</name><isAnonymous>false</isAnonymous><username>bob</username></author>
    <thread dsq:id="100"/>
    <parent dsq:id="1000"/>
  </post>
  <post dsq:id="1002">
    <id/><message><![CDATA[<p>removed</p>]]></message>
    <createdAt>2013-06-02T12:00:00Z</createdAt>
    <isDeleted>true</isDeleted><isSpam>false</isSpam>
    <author><email>dan@example.com</email><name>Dan</name><isAnonymous>false</isAnonymous></author>
    <thread dsq:id="100"/>
  </post>
  <post dsq:id="1003">
    <id/><message><![CDATA[<p>Replying to a deleted comment</p>]]></message>
    <createdAt>2013-06-03T08:00:00Z</createdAt>
    <isDeleted>false</isDeleted><isSpam>false</isSpam>
    <author><email>carol@example.com</email><name>Carol</name><isAnonymous>false</isAnonymous></author>
    <thread dsq:id="100"/>
    <parent dsq:id="1002"/>
  </post>
  <post dsq:id="1004">
    <id/><message><![CDATA[<p>Buy pills</p>]]></message>
    <createdAt>2013-06-04T08:00:00Z</createdAt>
    <isDeleted>false</isDeleted><isSpam>true</isSpam>
    <author><email>spam@example.com</email><name>Spammer</name><isAnonymous>true</isAnonymous></author>
    <thread dsq:id="100"/>
  </post>
  <post dsq:id="1005">
    <id/><message><![CDATA[<p>See <a href="https://disq.us/url?url=https%3A%2F%2Fgithub.com%2Flanyonm%3AAbCdEfGhIjKlMnOpQrStUvWxYz0&amp;cuid=1">this</a></p><script>alert(1)</script>]]></message>
    <createdAt>2025-02-01T00:00:00Z</createdAt>
    <isDeleted>false</isDeleted><isSpam>false</isSpam>
    <author><email>anon@example.com</email><name>  </name><isAnonymous>true</isAnonymous></author>
    <thread dsq:id="101"/>
  </post>
  <post dsq:id="1006">
    <id/><message><![CDATA[<p>Draft comment</p>]]></message>
    <createdAt>2013-01-01T00:00:00Z</createdAt>
    <isDeleted>false</isDeleted><isSpam>false</isSpam>
    <author><email>erin@example.com</email><name>Erin</name><isAnonymous>false</isAnonymous></author>
    <thread dsq:id="102"/>
  </post>
</disqus>
```

- [ ] **Step 2: Write the failing tests.** Append to the test file, before the `if __name__` block:

```python
class ParseExportTests(unittest.TestCase):
    def setUp(self):
        self.threads, self.posts = da.parse_export(FIXTURES / "disqus-export.xml")
        self.by_id = {p.id: p for p in self.posts}

    def test_threads_parsed(self):
        self.assertEqual(set(self.threads), {"100", "101", "102"})
        t = self.threads["100"]
        self.assertEqual(t.identifier, "/articles/2013/05/31/pi-dashboard-kiosk.html")
        self.assertEqual(t.link, "https://blog.lanyonm.org/articles/2013/05/31/pi-dashboard-kiosk.html")

    def test_deleted_and_spam_excluded(self):
        self.assertEqual(set(self.by_id), {"1000", "1001", "1003", "1005", "1006"})

    def test_post_fields(self):
        p = self.by_id["1001"]
        self.assertEqual((p.thread_id, p.parent_id, p.author, p.created_at), ("100", "1000", "Bob", "2013-06-02T09:00:00Z"))
        self.assertEqual(p.message, "<p>Agreed &amp; thanks</p>")
        self.assertIsNone(self.by_id["1000"].parent_id)

    def test_message_sanitized(self):
        self.assertEqual(self.by_id["1005"].message, '<p>See <a href="https://github.com/lanyonm" rel="nofollow ugc noopener">this</a></p>')

    def test_blank_author_becomes_guest(self):
        self.assertEqual(self.by_id["1005"].author, "Guest")

    def test_gzip_export(self):
        import gzip, shutil, tempfile
        with tempfile.TemporaryDirectory() as tmp:
            gz = Path(tmp) / "export.xml.gz"
            with open(FIXTURES / "disqus-export.xml", "rb") as src, gzip.open(gz, "wb") as dst:
                shutil.copyfileobj(src, dst)
            _, posts = da.parse_export(gz)
        self.assertEqual(len(posts), 5)
```

- [ ] **Step 3: Run to verify failure**

Run: `python3 -m unittest discover -s "$WORK/tests" -v`
Expected: `AttributeError: module 'disqus_archive' has no attribute 'parse_export'`

- [ ] **Step 4: Implement.** Add these imports to the top of `$WORK/disqus_archive.py` (merge with existing, keeping them alphabetical):

```python
import gzip
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
```

Append:

```python
NS = {"d": "http://disqus.com", "dsq": "http://disqus.com/disqus-internals"}
DSQ_ID = "{http://disqus.com/disqus-internals}id"


@dataclass(frozen=True)
class Thread:
    id: str
    identifier: str
    link: str
    title: str


@dataclass(frozen=True)
class Post:
    id: str
    thread_id: str
    parent_id: "str | None"
    author: str
    created_at: str
    message: str


def _text(el, path):
    return (el.findtext(path, "", NS) or "").strip()


def parse_export(path):
    """Parse a Disqus export (.xml or .xml.gz) into threads and visible, sanitized posts."""
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rb") as fh:
        root = ET.parse(fh).getroot()

    threads = {}
    for t in root.findall("d:thread", NS):
        tid = t.get(DSQ_ID)
        threads[tid] = Thread(tid, _text(t, "d:id"), _text(t, "d:link"), _text(t, "d:title"))

    posts = []
    for p in root.findall("d:post", NS):
        if _text(p, "d:isDeleted") == "true" or _text(p, "d:isSpam") == "true":
            continue
        parent = p.find("d:parent", NS)
        posts.append(Post(
            id=p.get(DSQ_ID),
            thread_id=p.find("d:thread", NS).get(DSQ_ID),
            parent_id=parent.get(DSQ_ID) if parent is not None else None,
            author=_text(p, "d:author/d:name") or "Guest",
            created_at=_text(p, "d:createdAt"),
            message=sanitize_message(p.findtext("d:message", "", NS)),
        ))
    return threads, posts
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m unittest discover -s "$WORK/tests" -v`
Expected: all tests pass. No commit.

---

### Task 3: Map threads to posts, build reply trees, write JSON (CLI)

**Files (all in `$WORK`, not committed):**
- Modify: `$WORK/disqus_archive.py`
- Modify: `$WORK/tests/test_disqus_archive.py`

**Interfaces:**
- Consumes: `parse_export`, `Thread`, `Post`
- Produces:
  - `normalize_path(url: str) -> str`
  - `build_slug_index(content_dir: Path) -> dict[str, str]`
  - `resolve_slug(thread: Thread, index: dict[str, str]) -> str | None`
  - `build_tree(posts: list[Post]) -> list[dict]`
  - `main(argv: list[str] | None = None) -> int`
- JSON file shape, which Task 4 relies on: `{"count": int, "comments": [Comment]}`, where `Comment = {"id": str, "author": str, "date": "YYYY-MM-DDTHH:MM:SSZ", "message": str (sanitized HTML), "replies": [Comment]}`

- [ ] **Step 1: Write the failing tests.** Append before the `if __name__` block:

```python
import json
import tempfile


def _write_content(root):
    arts = root / "articles"
    arts.mkdir(parents=True)
    (arts / "pi-dashboard-kiosk.md").write_text(
        '---\ntitle: "Pi"\ndate: 2013-05-31\ncomments: true\naliases:\n'
        '  - "/articles/2013/05/31/pi-dashboard-kiosk.html"\n---\n\nBody\n', encoding="utf-8")
    (arts / "_index.md").write_text("---\ntitle: Articles\n---\n", encoding="utf-8")
    talks = root / "speaking"
    talks.mkdir()
    (talks / "a-talk.md").write_text('---\ntitle: "T"\n---\n', encoding="utf-8")


class MappingTests(unittest.TestCase):
    def test_normalize_path(self):
        for raw in ("https://blog.lanyonm.org/articles/2013/05/31/Pi.html",
                    "/articles/2013/05/31/pi/", "/articles/2013/05/31/pi/index.html",
                    "http://localhost:4000/articles/2013/05/31/pi.html?x=1#c"):
            self.assertEqual(da.normalize_path(raw), "/articles/2013/05/31/pi")

    def test_slug_index_from_aliases_and_permalinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            _write_content(Path(tmp))
            index = da.build_slug_index(Path(tmp))
        self.assertEqual(index["/articles/2013/05/31/pi-dashboard-kiosk"], "pi-dashboard-kiosk")
        self.assertEqual(index["/articles/pi-dashboard-kiosk"], "pi-dashboard-kiosk")
        self.assertEqual(index["/speaking/a-talk"], "a-talk")
        self.assertNotIn("_index", index.values())

    def test_real_content_has_legacy_alias(self):
        index = da.build_slug_index(BLOG_REPO / "content")
        self.assertEqual(index["/articles/2013/05/31/pi-dashboard-kiosk"], "pi-dashboard-kiosk")

    def test_resolve_prefers_identifier_then_link(self):
        index = {"/articles/x": "x"}
        self.assertEqual(da.resolve_slug(da.Thread("1", "/articles/x.html", "https://other/nope", ""), index), "x")
        self.assertEqual(da.resolve_slug(da.Thread("1", "deadbeef", "https://blog/articles/x/", ""), index), "x")
        self.assertIsNone(da.resolve_slug(da.Thread("1", "", "https://blog/gone/", ""), index))


def _post(pid, parent=None, when="2013-01-01T00:00:00Z"):
    return da.Post(pid, "t", parent, "A", when, "<p>m</p>")


class TreeTests(unittest.TestCase):
    def test_nesting_and_order(self):
        tree = da.build_tree([_post("2", "1", "2013-01-03T00:00:00Z"), _post("1", None, "2013-01-01T00:00:00Z"),
                              _post("3", "1", "2013-01-02T00:00:00Z"), _post("4", "3", "2013-01-04T00:00:00Z")])
        self.assertEqual([c["id"] for c in tree], ["1"])
        self.assertEqual([c["id"] for c in tree[0]["replies"]], ["3", "2"])
        self.assertEqual(tree[0]["replies"][0]["replies"][0]["id"], "4")
        self.assertEqual(set(tree[0]), {"id", "author", "date", "message", "replies"})

    def test_orphan_reply_promoted(self):
        tree = da.build_tree([_post("5", "missing")])
        self.assertEqual([c["id"] for c in tree], ["5"])


class CliTests(unittest.TestCase):
    def run_cli(self, *extra):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        _write_content(root / "content")
        self.out = root / "data" / "disqus"
        code = da.main([str(FIXTURES / "disqus-export.xml"), "--content", str(root / "content"),
                        "--out", str(self.out), *extra])
        return code

    def tearDown(self):
        self.tmp.cleanup()

    def test_duplicate_threads_merge(self):
        self.run_cli("--allow-unmatched")
        data = json.loads((self.out / "pi-dashboard-kiosk.json").read_text(encoding="utf-8"))
        self.assertEqual(data["count"], 4)
        self.assertEqual([c["id"] for c in data["comments"]], ["1000", "1003", "1005"])
        self.assertEqual([c["id"] for c in data["comments"][0]["replies"]], ["1001"])

    def test_no_private_fields_published(self):
        self.run_cli("--allow-unmatched")
        blob = "".join(p.read_text(encoding="utf-8") for p in self.out.glob("*.json"))
        for secret in ("@example.com", "203.0.113.7", "alice\"", "<script", "disq.us"):
            self.assertNotIn(secret, blob)

    def test_unmatched_fails_without_flag(self):
        self.assertEqual(self.run_cli(), 1)

    def test_unmatched_allowed_with_flag(self):
        self.assertEqual(self.run_cli("--allow-unmatched"), 0)
        self.assertEqual(sorted(p.name for p in self.out.glob("*.json")), ["pi-dashboard-kiosk.json"])

    def test_rerun_removes_stale_files(self):
        self.run_cli("--allow-unmatched")
        (self.out / "renamed-post.json").write_text("{}", encoding="utf-8")
        da.main([str(FIXTURES / "disqus-export.xml"), "--content", str(Path(self.tmp.name) / "content"),
                 "--out", str(self.out), "--allow-unmatched"])
        self.assertFalse((self.out / "renamed-post.json").exists())
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 -m unittest discover -s "$WORK/tests" -v`
Expected: `AttributeError: module 'disqus_archive' has no attribute 'normalize_path'` (and similar for the others)

- [ ] **Step 3: Implement.** Add these imports (merge alphabetically):

```python
import argparse
import json
import sys
from collections import Counter, defaultdict
```

Append:

```python
SECTIONS = ("articles", "speaking")
ALIAS_LINE = re.compile(r'^\s*-\s*["\']?([^"\'\s]+)["\']?\s*$')


def normalize_path(url):
    """Reduce any thread URL/identifier to a comparable path: no host, query, .html or trailing slash."""
    path = urlparse(url.strip()).path
    path = re.sub(r"(/index)?\.html?$", "", path).rstrip("/")
    return path.lower()


def _aliases(text):
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return []
    found, in_aliases = [], False
    for line in match.group(1).splitlines():
        if line.startswith("aliases:"):
            in_aliases = True
            continue
        if in_aliases:
            alias = ALIAS_LINE.match(line)
            if alias:
                found.append(alias.group(1))
                continue
            in_aliases = False
    return found


def build_slug_index(content_dir):
    """Map every current and legacy URL path of each post to its slug (content file basename)."""
    index = {}
    for section in SECTIONS:
        for md in sorted((Path(content_dir) / section).glob("*.md")):
            if md.name.startswith("_"):
                continue
            slug = md.stem
            index[normalize_path(f"/{section}/{slug}/")] = slug
            for alias in _aliases(md.read_text(encoding="utf-8")):
                index[normalize_path(alias)] = slug
    return index


def resolve_slug(thread, index):
    for candidate in (thread.identifier, thread.link):
        if candidate:
            slug = index.get(normalize_path(candidate))
            if slug:
                return slug
    return None


def build_tree(posts):
    """Nest replies under parents in chronological order; replies to missing parents become top-level."""
    nodes = {p.id: {"id": p.id, "author": p.author, "date": p.created_at, "message": p.message, "replies": []}
             for p in posts}
    roots = []
    for p in sorted(posts, key=lambda p: (p.created_at, p.id)):
        parent = nodes.get(p.parent_id) if p.parent_id else None
        (parent["replies"] if parent else roots).append(nodes[p.id])
    return roots


def main(argv=None):
    ap = argparse.ArgumentParser(description="Convert a Disqus export into data/disqus/<slug>.json")
    ap.add_argument("export", help="Disqus export .xml or .xml.gz (keep outside the repo)")
    ap.add_argument("--content", required=True, help="blog repo content/ dir")
    ap.add_argument("--out", required=True, help="output dir, normally <repo>/data/disqus")
    ap.add_argument("--allow-unmatched", action="store_true",
                    help="exit 0 even if some threads with comments map to no current post")
    args = ap.parse_args(argv)

    threads, posts = parse_export(args.export)
    index = build_slug_index(Path(args.content))

    by_slug, unmatched = defaultdict(list), Counter()
    for post in posts:
        thread = threads.get(post.thread_id)
        slug = resolve_slug(thread, index) if thread else None
        if slug:
            by_slug[slug].append(post)
        else:
            unmatched[thread.link if thread else f"thread {post.thread_id}"] += 1

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for stale in out.glob("*.json"):
        stale.unlink()
    for slug, slug_posts in sorted(by_slug.items()):
        payload = {"count": len(slug_posts), "comments": build_tree(slug_posts)}
        (out / f"{slug}.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{slug}: {len(slug_posts)}")
    for link, count in sorted(unmatched.items()):
        print(f"UNMATCHED {link}: {count}", file=sys.stderr)

    return 1 if unmatched and not args.allow_unmatched else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest discover -s "$WORK/tests" -v`
Expected: all tests pass. No commit.

---

### Task 4: Render the archive in Hugo

**Files:**
- Create: `layouts/_partials/disqus-archive.html`
- Create: `layouts/_partials/disqus-comment.html`
- Modify: `layouts/_partials/comments.html` (whole file)
- Modify: `assets/css/custom.css` (the `.disqus-readonly-notice` block at ~lines 1116–1128)

**Interfaces:**
- Consumes: `data/disqus/<slug>.json` in the shape defined in Task 3
- Produces: the rendered HTML: `section.comments-section.disqus-archive`, plus `li.archived-comment#comment-<id>` items nested in `ol.archived-comments`

- [ ] **Step 1: Generate throwaway fixture data and confirm the current behaviour (expected to fail)**

```bash
SCRATCH=$(mktemp -d)
python3 "$WORK/disqus_archive.py" "$WORK/tests/fixtures/disqus-export.xml" \
  --content "$BLOG_REPO/content" --out "$BLOG_REPO/data/disqus" --allow-unmatched
hugo --gc --minify -d "$SCRATCH/site" >/dev/null
grep -c 'archived-comment' "$SCRATCH/site/articles/pi-dashboard-kiosk/index.html"
```

Expected: `0`, because the archive isn't rendered yet.

- [ ] **Step 2: Create** `layouts/_partials/disqus-comment.html`:

```go-html-template
{{- /* One archived Disqus comment and its replies. Context: a Comment dict from data/disqus/<slug>.json.
       .message was sanitized to a small allowlist when exported (see specs/002), so safeHTML is intentional. */ -}}
<li class="archived-comment" id="comment-{{ .id }}">
  <div class="archived-comment-meta">
    <span class="archived-comment-author">{{ .author }}</span>
    <a class="archived-comment-date" href="#comment-{{ .id }}"><time datetime="{{ .date }}">{{ (time.AsTime .date).Format (site.Params.dateFormat | default "2006-01-02") }}</time></a>
  </div>
  <div class="archived-comment-body">{{ .message | safeHTML }}</div>
  {{- with .replies }}
  <ol class="archived-comments archived-replies">
    {{- range . }}{{ partial "disqus-comment.html" . }}{{ end }}
  </ol>
  {{- end }}
</li>
```

- [ ] **Step 3: Create** `layouts/_partials/disqus-archive.html`:

```go-html-template
{{- /* Static archive of a post's Disqus thread. Context: the dict from data/disqus/<slug>.json. */ -}}
<section class="comments-section disqus-archive" aria-labelledby="archived-comments-label">
  <div class="comments-label" id="archived-comments-label">Comments ({{ .count }})</div>
  <p class="disqus-archive-notice">
    Archived from Disqus &mdash; comments are closed.
    Want your comment removed? <a href="https://github.com/lanyonm/lanyonm.github.io/issues/new?title=Remove%20archived%20comment">Open an issue</a>.
  </p>
  <ol class="archived-comments">
    {{- range .comments }}{{ partial "disqus-comment.html" . }}{{ end }}
  </ol>
</section>
```

- [ ] **Step 4: Replace** `layouts/_partials/comments.html` entirely:

```go-html-template
{{- /* Comments: Giscus for posts after params.giscusCutoffDate; a static Disqus archive (data/disqus/<slug>.json)
       for earlier posts that had comments. Honors per-post `comments: false`. */ -}}
{{- if ne .Params.comments false -}}
  {{- $cutoff := time.AsTime (.Site.Params.giscusCutoffDate | default "2025-01-01") -}}
  {{- if (time.AsTime .Date).After $cutoff -}}
    <div class="comments-section">
      <div class="comments-label">Comments</div>
      {{- $g := .Site.Params.giscus -}}
      {{- if and $g $g.repoId $g.categoryId -}}
        <script
          src="https://giscus.app/client.js"
          data-repo="{{ $g.repo }}"
          data-repo-id="{{ $g.repoId }}"
          data-category="{{ $g.category | default "Blog Comments" }}"
          data-category-id="{{ $g.categoryId }}"
          data-mapping="{{ $g.mapping | default "pathname" }}"
          data-strict="{{ $g.strict | default "0" }}"
          data-reactions-enabled="{{ $g.reactionsEnabled | default "1" }}"
          data-emit-metadata="{{ $g.emitMetadata | default "0" }}"
          data-input-position="{{ $g.inputPosition | default "bottom" }}"
          data-theme="{{ $g.lightTheme | default "light" }}"
          data-lang="{{ $g.lang | default "en" }}"
          data-loading="{{ $g.loading | default "lazy" }}"
          crossorigin="anonymous"
          async
        ></script>
        <noscript>Comments require JavaScript.</noscript>
      {{- else -}}
        <p class="comments-disabled-notice text-sm text-neutral-500 dark:text-neutral-400">Comments are temporarily unavailable.</p>
        {{- warnf "[COMMENTS] Giscus repoId/categoryId not configured for post %s" .RelPermalink -}}
      {{- end -}}
    </div>
  {{- else -}}
    {{- with index (hugo.Data.disqus | default dict) .File.ContentBaseName -}}
      {{- partial "disqus-archive.html" . -}}
    {{- end -}}
  {{- end -}}
{{- end -}}
```

Before replacing the file, diff its Giscus block against the current one; it must be carried over unchanged.

- [ ] **Step 5: Styles.** In `assets/css/custom.css`, replace the `.disqus-readonly-notice` and `.dark .disqus-readonly-notice` blocks with:

```css
.disqus-archive-notice {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 99px;
  background: var(--brand-neutral-100);
  color: var(--brand-neutral-500);
  font-size: 0.8rem;
  margin-bottom: 1.5rem;
}
.dark .disqus-archive-notice {
  background: var(--brand-neutral-700);
  color: var(--brand-neutral-300);
}
.disqus-archive-notice a { text-decoration: underline; }

.archived-comments { list-style: none; margin: 0; padding: 0; }
.archived-comment { margin: 0 0 1.5rem; }
.archived-replies {
  margin-top: 1rem;
  padding-left: 1.25rem;
  border-left: 2px solid var(--brand-neutral-200);
}
.dark .archived-replies { border-left-color: var(--brand-neutral-600); }
.archived-replies .archived-replies .archived-replies .archived-replies { padding-left: 0; border-left: 0; }
.archived-comment-meta {
  font-family: var(--font-display);
  font-size: 0.85rem;
  margin-bottom: 0.35rem;
}
.archived-comment-author { font-weight: 600; }
.archived-comment-date { color: var(--brand-neutral-400); margin-left: 0.5rem; text-decoration: none; }
.archived-comment-body { font-size: 0.95rem; overflow-wrap: anywhere; }
.archived-comment-body p { margin: 0 0 0.5rem; }
.archived-comment-body pre { overflow-x: auto; }
```

- [ ] **Step 6: Build and verify**

```bash
hugo --gc --minify -d "$SCRATCH/site" 2>&1 | grep -iE 'error|warn' ; \
P="$SCRATCH/site/articles/pi-dashboard-kiosk/index.html"; \
grep -c 'disqus.com/embed.js' "$P"; \
grep -oE 'Comments \(4\)' "$P"; \
grep -oE 'archived-replies.{0,60}comment-1001' "$P" | head -1; \
grep -c '<script>alert' "$P"; \
grep -c 'comments-section' "$SCRATCH/site/articles/trying-go/index.html"; \
grep -c 'comments-section' "$SCRATCH/site/articles/amqp-demo/index.html"
```

Expected, in order: no Hugo errors or warnings, `0`, `Comments (4)`, one match showing comment 1001 nested inside `archived-replies`, `0`, `0` (a post without archive data shows no comments section), `0` (`comments: false`).

- [ ] **Step 7: Visual check.** Run `hugo serve --port 1313 --baseURL http://localhost:1313/ --appendPort=false` and open `/articles/pi-dashboard-kiosk/` in light and dark mode and at 375px width. The nested reply should be indented, the link should point to `https://github.com/lanyonm`, and DevTools → Network should show no requests to `disqus.com`, `disq.us` or `disquscdn.com`.

- [ ] **Step 8: Remove the fixture data and commit** (the real data comes in Task 5):

```bash
rm -rf data/disqus
git add layouts/_partials/comments.html layouts/_partials/disqus-archive.html layouts/_partials/disqus-comment.html assets/css/custom.css
git commit -m "Render archived Disqus comments statically instead of embedding Disqus"
```

---

### Task 5: Import the real export and cut over

**Files:**
- Create: `data/disqus/*.json`
- Modify: `hugo.toml` (remove `[services.disqus]`, lines ~59–60)
- Modify: `.claude/CLAUDE.md`

- [ ] **Step 1: Export (manual, done by Mike).** Go to `https://lanyonm.disqus.com/admin/discussions/export/` (or Disqus Admin → Moderation → Export) and request the export. Disqus emails a link to a `.xml.gz`; save it **outside the repo**, e.g. `~/Downloads/lanyonm-disqus.xml.gz`.

- [ ] **Step 2: Dry run into scratch and review the report**

```bash
OUT="$(mktemp -d)/disqus"
python3 "$WORK/disqus_archive.py" ~/Downloads/lanyonm-disqus.xml.gz --content "$BLOG_REPO/content" --out "$OUT"
```

Expected: one `slug: N` line per post with comments. For each `UNMATCHED <link>: N` line, decide whether to add the missing alias to that post's front matter (preferred, if the comment belongs to a live post) or accept the loss (drafts, localhost, deleted pages). Re-run until every remaining unmatched line is one you're consciously dropping.

- [ ] **Step 3: Spot-check against live Disqus.** List the three busiest posts:

```bash
python3 -c 'import json,pathlib,sys; d=pathlib.Path(sys.argv[1]); print(*sorted(((json.loads(f.read_text())["count"], f.stem) for f in d.glob("*.json")), reverse=True)[:3], sep="\n")' "$OUT"
```

(`$OUT` is the scratch directory from Step 2.) For each one, compare the count, the authors and the reply nesting with the Disqus thread on the live site.

- [ ] **Step 4: Write the real data**

```bash
python3 "$WORK/disqus_archive.py" ~/Downloads/lanyonm-disqus.xml.gz --content "$BLOG_REPO/content" --out "$BLOG_REPO/data/disqus" --allow-unmatched
git status --short data/disqus
grep -rlE '@[a-z0-9-]+\.[a-z]{2,}|disq\.us|disquscdn' data/disqus || echo "clean"
```

Expected: JSON files only, and `clean` (any `@` match must be a commenter typing an address in their message body; review each one by hand).

- [ ] **Step 5: Remove the Disqus config.** Delete from `hugo.toml`:

```toml
  [services.disqus]
    shortname = "lanyonm"
```

- [ ] **Step 6: Verify the full build has no Disqus at all**

```bash
SCRATCH=$(mktemp -d); hugo --gc --minify -d "$SCRATCH/site" 2>&1 | grep -iE 'error|warn'; \
grep -rlE 'disqus\.com|disq\.us|disquscdn' "$SCRATCH/site" || echo "no disqus"
```

Expected: no errors or warnings, and `no disqus`.

- [ ] **Step 7: Update `.claude/CLAUDE.md`:**
  - Layouts: change the `comments.html` line to `` `layouts/_partials/comments.html` — Giscus post-cutoff; pre-cutoff posts render the static Disqus archive from `data/disqus/<slug>.json` via `disqus-archive.html` / `disqus-comment.html` ``.
  - Configuration: remove the `services.disqus.shortname` bullet.
  - Key Integrations: replace the Disqus bullet with `` **Disqus archive** (static): pre-2025 comments were exported once from Disqus and converted (by a one-off script, not kept) to sanitized `data/disqus/<slug>.json`. Disqus itself is no longer loaded. To honor a removal request, delete that comment object (and adjust `count`) in the post's JSON. ``

- [ ] **Step 8: Commit**

```bash
git add data/disqus hugo.toml .claude/CLAUDE.md
git commit -m "Import archived Disqus comments and stop loading Disqus"
```

- [ ] **Step 9: Afterwards (optional, manual).** Once the deploy is live and checked, delete the raw export from `~/Downloads` and `$WORK`. Consider also deleting the Disqus site (Disqus Admin → Settings → General → Delete) so the comment data no longer sits with Disqus.
