#!/usr/bin/env python3
"""
One-shot migration script: rewrite front matter + Jekyll syntax across content/ files.

Designed to be re-run safely (idempotent where possible).
"""
import re
import sys
from pathlib import Path

# Map filename → original Jekyll date for posts (YYYY-MM-DD)
ORIGINAL_DATES = {
    "amqp-demo.md": "2012-10-27",
    "spring-grabbag.md": "2013-01-06",
    "mybatis-spring-java-config-contribution.md": "2013-01-19",
    "trying-go.md": "2013-05-30",
    "pi-dashboard-kiosk.md": "2013-05-31",
    "xbee-kill-a-watt.md": "2013-06-02",
    "front-end-engineer-all-in-one.md": "2013-07-01",
    "wp-shell-cookbook.md": "2013-07-28",
    "cams-summer-camp.md": "2013-08-03",
    "vagrant-graphite-statsd-chef.md": "2013-09-15",
    "xbee-kill-a-watt-transmitter.md": "2013-10-06",
    "testing-multiple-grails-versions-travis-ci.md": "2013-10-21",
    "yosemite-three-hike-days.md": "2013-11-10",
    "alphabetize-jekyll-page-tags-pure-liquid.md": "2013-11-21",
    "pushing-web-server-response-codes-graphite-logstash.md": "2013-11-27",
    "logstash-multiline-tomcat-log-parsing.md": "2014-01-12",
    "spring-4-mybatis-java-config.md": "2014-04-21",
    "markdown-to-confluence-uploader.md": "2014-08-16",
    "spring-4-sitemesh-java-config.md": "2014-11-23",
    "adopting-the-lanyon-theme.md": "2014-11-26",
    "raspberry-pi-init-script-python.md": "2015-01-11",
    "golang-http-stats-collector.md": "2015-03-29",
    "innovation-creative-company-devopsdays-newyork.md": "2015-04-30",
    "grafana-chef-cookbook-nginx-ssl.md": "2015-06-28",
    "web-performance-monitoring-devopsdays-minneapolis.md": "2015-07-08",
    "a-participants-conference-devopsdays-chicago.md": "2015-09-01",
    "chatops-hubot-grafana-images-hipchat.md": "2015-09-30",
    "pingdom-hipchat-integration-aws-lambda.md": "2015-11-25",
    "publish-maven-site-github-pages-travis-ci.md": "2015-12-19",
    "continuous-security-owasp-java-vulnerability-check.md": "2015-12-22",
    "log-aggregation-log4j-spring-logstash.md": "2015-12-29",
    "creative-and-technology-a-partnership-devopsdays-msn.md": "2016-11-02",
}

# Drafts: explicit dates per spec T015
DRAFT_DATES = {
    "not-invented-here-bias.md": "2013-06-05",
    "python-sphinx-build-watch-script.md": "2014-12-01",
}

DRAFTS = set(DRAFT_DATES)

ROOT = Path(__file__).resolve().parents[1]


def parse_front_matter(text: str):
    """Return (front_matter_lines: list[str], body: str). Front matter is preserved as raw lines."""
    if not text.startswith("---\n"):
        return [], text
    end = text.find("\n---\n", 4)
    if end == -1:
        return [], text
    fm_block = text[4:end]
    body = text[end + 5 :]
    return fm_block.split("\n"), body


def fm_to_dict(lines):
    """Lightweight YAML-ish parse: top-level scalars + lists. Tracks sub-blocks (e.g., og:)."""
    result = {}
    block_keys = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if m and not line.startswith(" "):
            key = m.group(1)
            val = m.group(2).strip()
            if val == "":
                # Begin a sub-block (mapping or list)
                sub = []
                j = i + 1
                while j < len(lines) and (lines[j].startswith(" ") or lines[j].startswith("-")):
                    sub.append(lines[j])
                    j += 1
                result[key] = ("block", sub)
                i = j
                continue
            result[key] = ("scalar", val)
            i += 1
        else:
            i += 1
    return result


def render_front_matter(fm: dict) -> str:
    """Render dict back to YAML lines (deterministic key order: title, description, date, draft, tags, categories, comments, images, aliases, then anything else)."""
    order = ["title", "description", "date", "draft", "tags", "categories", "comments", "images", "aliases", "showHero", "backgroundImage"]
    lines = []
    seen = set()
    for k in order:
        if k in fm:
            seen.add(k)
            kind, val = fm[k]
            if kind == "scalar":
                lines.append(f"{k}: {val}")
            else:
                lines.append(f"{k}:")
                lines.extend(val)
    for k, (kind, val) in fm.items():
        if k in seen:
            continue
        if kind == "scalar":
            lines.append(f"{k}: {val}")
        else:
            lines.append(f"{k}:")
            lines.extend(val)
    return "---\n" + "\n".join(lines) + "\n---\n"


def convert_og_to_images(fm: dict):
    """Convert legacy og: { image: 'foo.jpg' } block to images: ['/images/foo.jpg']"""
    if "og" not in fm:
        return
    kind, val = fm["og"]
    if kind != "block":
        return
    img_url = None
    for sub in val:
        m = re.match(r"\s+image:\s*['\"]?([^'\"\s]+)['\"]?\s*$", sub)
        if m:
            img_url = m.group(1)
            break
    del fm["og"]
    if img_url is None:
        return
    if img_url.startswith("http://") or img_url.startswith("https://"):
        path = img_url
    else:
        path = "/images/" + img_url
    fm["images"] = ("block", [f'  - "{path}"'])


# --- Body conversions ---

HIGHLIGHT_RE = re.compile(r"\{%\s*highlight\s+(\S+)\s*%\}(.*?)\{%\s*endhighlight\s*%\}", re.DOTALL)
POST_URL_RE = re.compile(r"\{%\s*post_url\s+(\d{4}-\d{2}-\d{2}-[A-Za-z0-9_\-]+)\s*%\}")
GIST_RE = re.compile(r"\{%\s*gist\s+([A-Za-z0-9_\-]+)/([0-9a-fA-F]+)\s*%\}")
SITE_URL_RE = re.compile(r"\{\{\s*site\.url\s*\}\}/images/")


def convert_highlight(body: str) -> str:
    def repl(m):
        lang = m.group(1)
        code = m.group(2)
        # Strip leading/trailing single newline
        if code.startswith("\n"):
            code = code[1:]
        if code.endswith("\n"):
            code = code[:-1]
        return f"```{lang}\n{code}\n```"
    return HIGHLIGHT_RE.sub(repl, body)


def convert_post_url(body: str) -> str:
    def repl(m):
        full = m.group(1)
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", full)
        return f'{{{{< ref "{slug}" >}}}}'
    return POST_URL_RE.sub(repl, body)


def convert_gist(body: str) -> str:
    return GIST_RE.sub(r'{{< gist \1 \2 >}}', body)


def convert_site_url_images(body: str) -> str:
    return SITE_URL_RE.sub("/images/", body)


def convert_blockquotes(body: str) -> str:
    """`<div class="center quote">...</div>` → `> "..."` blockquote."""
    pattern = re.compile(r'<div class="center quote">\s*(.*?)\s*</div>', re.DOTALL)

    def repl(m):
        inner = m.group(1).strip()
        # Strip leading/trailing whitespace and quote chars
        inner = re.sub(r"\s+", " ", inner)
        # Format as multi-line blockquote: prefix each non-empty line with >
        return "> " + inner
    return pattern.sub(repl, body)


def convert_figure_div(body: str) -> str:
    """
    Convert `<div class="center"><figure>...<img src="..." alt="..." />...<figcaption>caption</figcaption>...</figure></div>`
    or `<div class="center"><img src="..." alt="..." />...</div>` to {{< figure src="..." alt="..." caption="..." >}} shortcode.
    Also handles `class="right"` → adds class="right" to shortcode.
    """
    # Block 1: full figure with figcaption
    pattern_fig = re.compile(
        r'<div class="(center|right)">\s*<figure>\s*'
        r'<a href="([^"]*)">\s*<img src="([^"]*)"\s+alt="([^"]*)"\s*/?>\s*</a>\s*'
        r'<figcaption>(.*?)</figcaption>\s*'
        r'</figure>\s*</div>',
        re.DOTALL,
    )

    def repl_fig(m):
        cls, link, src, alt, caption = m.groups()
        caption = re.sub(r"\s+", " ", caption.strip())
        attrs = [f'src="{src}"', f'link="{link}"']
        if alt:
            attrs.append(f'alt="{alt}"')
        if caption:
            attrs.append(f'caption="{caption}"')
        if cls == "right":
            attrs.append('class="right"')
        return "{{< figure " + " ".join(attrs) + " >}}"

    body = pattern_fig.sub(repl_fig, body)

    # Block 2: figure without anchor link
    pattern_fig2 = re.compile(
        r'<div class="(center|right)">\s*<figure>\s*'
        r'<img src="([^"]*)"\s+alt="([^"]*)"\s*/?>\s*'
        r'<figcaption>(.*?)</figcaption>\s*'
        r'</figure>\s*</div>',
        re.DOTALL,
    )

    def repl_fig2(m):
        cls, src, alt, caption = m.groups()
        caption = re.sub(r"\s+", " ", caption.strip())
        attrs = [f'src="{src}"']
        if alt:
            attrs.append(f'alt="{alt}"')
        if caption:
            attrs.append(f'caption="{caption}"')
        if cls == "right":
            attrs.append('class="right"')
        return "{{< figure " + " ".join(attrs) + " >}}"

    body = pattern_fig2.sub(repl_fig2, body)

    # Block 3: simple <div class="center"><img.../></div> (no figure tag)
    pattern_img = re.compile(
        r'<div class="(center|right)">\s*'
        r'<img src="([^"]*)"\s+alt="([^"]*)"\s*/?>\s*'
        r'</div>',
        re.DOTALL,
    )

    def repl_img(m):
        cls, src, alt = m.groups()
        attrs = [f'src="{src}"']
        if alt:
            attrs.append(f'alt="{alt}"')
        if cls == "right":
            attrs.append('class="right"')
        return "{{< figure " + " ".join(attrs) + " >}}"

    body = pattern_img.sub(repl_img, body)
    return body


def convert_sidebyside(body: str) -> str:
    """`<div class="center spring-mybatis"|"center grails-travis">...<img>...<span>+</span>...<img>...</div>`"""
    pattern = re.compile(
        r'<div class="center (?:spring-mybatis|grails-travis)">\s*'
        r'<img src="([^"]*)"\s+alt="([^"]*)"\s*/?>\s*'
        r'<span>([^<]+)</span>\s*'
        r'<img src="([^"]*)"\s+alt="([^"]*)"\s*/?>\s*'
        r'</div>',
        re.DOTALL,
    )

    def repl(m):
        src1, alt1, sep, src2, alt2 = m.groups()
        return (
            f'{{{{< sidebyside separator="{sep.strip()}" >}}}}\n'
            f'![{alt1}]({src1})\n'
            f'![{alt2}]({src2})\n'
            f'{{{{< /sidebyside >}}}}'
        )

    return pattern.sub(repl, body)


def convert_speakerdeck(body: str) -> str:
    """Convert `<script async class="speakerdeck-embed" data-id="..." data-ratio="..." src="...speakerdeck...">` to `{{< speakerdeck id ratio >}}`."""
    pattern = re.compile(
        r'<script[^>]*class="speakerdeck-embed"[^>]*'
        r'data-id="([^"]+)"[^>]*'
        r'data-ratio="([^"]+)"[^>]*></script>',
        re.IGNORECASE,
    )

    def repl(m):
        sid, ratio = m.groups()
        return f'{{{{< speakerdeck id="{sid}" ratio="{ratio}" >}}}}'

    body = pattern.sub(repl, body)
    # Also handle ratio-first variants
    pattern2 = re.compile(
        r'<script[^>]*class="speakerdeck-embed"[^>]*'
        r'data-ratio="([^"]+)"[^>]*'
        r'data-id="([^"]+)"[^>]*></script>',
        re.IGNORECASE,
    )

    def repl2(m):
        ratio, sid = m.groups()
        return f'{{{{< speakerdeck id="{sid}" ratio="{ratio}" >}}}}'

    return pattern2.sub(repl2, body)


def convert_youtube(body: str) -> str:
    """Convert YouTube iframe to Hugo {{< youtube ID >}} shortcode."""
    pattern = re.compile(
        r'<iframe[^>]+src="https?://(?:www\.)?youtube\.com/embed/([A-Za-z0-9_\-]+)(?:\?[^"]*)?"[^>]*></iframe>',
        re.IGNORECASE,
    )

    def repl(m):
        return f'{{{{< youtube {m.group(1)} >}}}}'

    return pattern.sub(repl, body)


def demote_h1_in_body(body: str) -> str:
    """
    Congo renders title as h1. Demote any in-body `# heading` lines: # → ##, ## → ###, etc.
    Operates on lines starting with `#` followed by space.
    Preserves fenced code blocks and front-matter-leading-# (already stripped).
    """
    out = []
    in_fence = False
    fence_re = re.compile(r"^```")
    for line in body.split("\n"):
        if fence_re.match(line):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        m = re.match(r"^(#{1,5})\s", line)
        if m:
            new_level = "#" * (len(m.group(1)) + 1)
            line = new_level + line[len(m.group(1)) :]
        out.append(line)
    return "\n".join(out)


def remove_draft_date_header(body: str) -> str:
    """Drafts have a leading `# YYYY-MM-DD` line as their first body content. Remove it (the date is in front matter)."""
    pattern = re.compile(r"\A\s*# \d{4}-\d{2}-\d{2}\s*\n", re.MULTILINE)
    return pattern.sub("", body)


def jekyll_url_alias(slug: str, date: str, section: str) -> str:
    y, m, d = date.split("-")
    return f"/{section}/{y}/{m}/{d}/{slug}/"


def process_file(path: Path):
    text = path.read_text()
    fm_lines, body = parse_front_matter(text)
    if not fm_lines:
        print(f"WARN: No front matter in {path}", file=sys.stderr)
        return

    fm = fm_to_dict(fm_lines)
    fname = path.name
    section = path.parent.name  # 'articles' or 'speaking'

    # Determine date
    if fname in DRAFT_DATES:
        date = DRAFT_DATES[fname]
        fm["draft"] = ("scalar", "true")
    elif fname in ORIGINAL_DATES:
        date = ORIGINAL_DATES[fname]
    else:
        print(f"WARN: Unknown date for {fname}", file=sys.stderr)
        return

    # Always set ISO date (T-day per spec, Hugo derives chronological order from this)
    fm["date"] = ("scalar", date)

    # Remove layout, category fields
    fm.pop("layout", None)
    fm.pop("category", None)

    # Convert og: → images:
    convert_og_to_images(fm)

    # Add aliases (only for non-drafts; T018 says "all 32 published posts")
    if fname not in DRAFTS:
        slug = fname.replace(".md", "")
        alias = jekyll_url_alias(slug, date, section)
        # Preserve any existing aliases (unlikely)
        if "aliases" not in fm:
            fm["aliases"] = ("block", [f'  - "{alias}"'])

    # --- Body transforms ---
    if fname in DRAFTS:
        body = remove_draft_date_header(body)

    body = convert_highlight(body)
    body = convert_post_url(body)
    body = convert_gist(body)
    body = convert_site_url_images(body)
    body = convert_blockquotes(body)
    body = convert_figure_div(body)
    body = convert_sidebyside(body)
    body = convert_speakerdeck(body)
    body = convert_youtube(body)
    body = demote_h1_in_body(body)

    new_text = render_front_matter(fm) + body
    path.write_text(new_text)


def main():
    targets = sorted(list((ROOT / "content/articles").glob("*.md")) + list((ROOT / "content/speaking").glob("*.md")))
    for p in targets:
        process_file(p)
    print(f"Processed {len(targets)} files")


if __name__ == "__main__":
    main()
