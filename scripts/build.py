#!/usr/bin/env python3
"""Build the blog, sitemap, feed and llms.txt for efazati.org.

The site is static and Netlify serves the repo as it is, so the generated files
are committed. Run this after adding or editing anything under content/posts:

    python3 scripts/build.py

Posts are content/posts/<slug>.html: a few `key: value` header lines, a `---`
line, then the HTML body. The order on the page is ORDER below, not the date:
most posts share a publish date, and a sort on it would shuffle them.

Everything that lists posts (home page, blog index, sitemap, feed, llms.txt)
is written from the same list here. Keeping them by hand drifted the moment
there were two of them; the old sitemap still said May.
"""
import datetime as dt
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://efazati.org"
AUTHOR = "Mohammad Efazati"

# Newest-first reading order. A post missing from this list fails the build
# rather than quietly not appearing.
ORDER = [
    "hiring-engineers-when-ai-is-in-the-room",
    "engineering-with-claude-code",
    "first-30-days-with-an-unfamiliar-infrastructure",
    "broken-on-purpose",
    "kubernetes-at-the-edge-on-x86-and-arm",
    "opentelemetry-before-the-vendor",
    "one-ci-cd-for-200-projects",
]


def load_posts():
    files = {p.stem: p for p in (ROOT / "content/posts").glob("*.html")}
    missing = set(files) ^ set(ORDER)
    if missing:
        raise SystemExit(f"ORDER and content/posts disagree: {sorted(missing)}")
    posts = []
    for slug in ORDER:
        head, body = files[slug].read_text().split("\n---\n", 1)
        meta = dict(line.split(": ", 1) for line in head.strip().splitlines())
        meta["slug"] = slug
        meta["body"] = body.strip()
        meta["url"] = f"{SITE}/blog/{slug}/"
        meta["path"] = f"/blog/{slug}/"
        words = len(re.sub(r"<[^>]+>", " ", body).split())
        meta["minutes"] = max(1, round(words / 220))
        if "—" in body or "—" in meta["title"] or "—" in meta["description"]:
            raise SystemExit(f"{slug}: em dash in the text; use a comma, colon or brackets")
        posts.append(meta)
    return posts


def nice_date(iso):
    return dt.date.fromisoformat(iso).strftime("%-d %b %Y")


E = html.escape

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="author" content="Mohammad Efazati">
<link rel="canonical" href="{url}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta name="theme-color" content="#0b0b0c">
<meta property="og:type" content="{ogtype}">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{ogtitle}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="https://efazati.org/assets/images/me.jpg">
<meta property="og:site_name" content="Mohammad Efazati">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{ogtitle}">
<meta name="twitter:description" content="{desc}">
<link rel="icon" type="image/jpeg" href="/assets/images/me.jpg">
<link rel="alternate" type="application/rss+xml" title="Mohammad Efazati: writing" href="/feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&amp;display=swap">
<link rel="stylesheet" href="/assets/css/site.css">
{ld}
</head>
<body>
<div class="w">
"""

# Kept identical to the header in index.html, which is hand-written (there it
# sits inside the hero, next to the photo).
TOP = """<header class="top">
    <a class="name" href="/">Efazati</a>
    <nav aria-label="Primary">
        <a href="/#about">About</a>
        <a href="/#projects">Projects</a>
        <a href="/blog/"{blog_current}>Writing</a>
        <a href="/#contact">Contact</a>
    </nav>
</header>
"""

FOOT = """<footer>
    <span>&copy; {year} Mohammad Efazati</span>
    <nav aria-label="Footer">
        <a href="/feed.xml">RSS</a>
        <a href="/llms.txt">llms.txt</a>
        <a href="https://github.com/efazati" rel="me">GitHub</a>
        <a href="https://www.linkedin.com/in/efazati" rel="me">LinkedIn</a>
    </nav>
</footer>
</div>
</body>
</html>
"""


def page(title, ogtitle, desc, url, body, ogtype="website", ld="", blog_current=False):
    return (
        HEAD.format(title=E(title), ogtitle=E(ogtitle), desc=E(desc), url=url, ogtype=ogtype, ld=ld)
        + TOP.format(blog_current=' aria-current="page"' if blog_current else "")
        + body
        + FOOT.format(year=dt.date.today().year)
    )


def item(p):
    return f"""    <li><a href="{p['path']}"><div class="meta"><b>{E(p['tag'])}</b>{nice_date(p['date'])} &middot; {p['minutes']} min</div><div><h2>{E(p['title'])}</h2><p>{E(p['description'])}</p></div></a></li>
"""


def short(p):
    return f"""    <li><a href="{p['path']}"><b>{E(p['title'])}</b><span>{E(p['tag'])}</span></a></li>
"""


def card(p, n):
    # The home page leads with three posts as coloured cards. The description
    # is written for search results and is too long for a card, so each post
    # carries a one-line teaser of its own.
    lead = p.get("teaser") or p["description"]
    return f"""<a class="card c{n}" href="{p['path']}"><span class="t">{E(p['tag'])}</span><div><h3>{E(p['title'])}</h3><p>{E(lead)}</p></div></a>"""


def build_blog_index(posts):
    body = f"""<main>
<div class="page-head">
<h1>Writing</h1>
<p>Notes on platforms, Kubernetes, observability, CI/CD, and hiring engineers now that AI is part of the job. Written from work I have done.</p>
</div>
<ul class="posts">
{''.join(item(p) for p in posts)}</ul>
</main>
"""
    ld = """<script type="application/ld+json">
{"@context":"https://schema.org","@type":"Blog","name":"Mohammad Efazati: writing","url":"https://efazati.org/blog/","author":{"@type":"Person","name":"Mohammad Efazati","url":"https://efazati.org/"}}
</script>"""
    out = page(
        "Writing | Mohammad Efazati",
        "Writing by Mohammad Efazati",
        "Notes on platform engineering, Kubernetes, observability, CI/CD and technical hiring with AI, from 20+ years of infrastructure work.",
        f"{SITE}/blog/",
        body,
        ld=ld,
        blog_current=True,
    )
    write("blog/index.html", out)


def build_post(p, posts):
    others = [o for o in posts if o["slug"] != p["slug"]][:3]
    ld = (
        '<script type="application/ld+json">\n'
        + '{"@context":"https://schema.org","@type":"BlogPosting",'
        + f'"headline":{json_str(p["title"])},"description":{json_str(p["description"])},'
        + f'"datePublished":"{p["date"]}","dateModified":"{p.get("updated", p["date"])}",'
        + f'"url":"{p["url"]}","mainEntityOfPage":"{p["url"]}","image":"https://efazati.org/assets/images/me.jpg",'
        + '"author":{"@type":"Person","name":"Mohammad Efazati","url":"https://efazati.org/"},'
        + '"publisher":{"@type":"Person","name":"Mohammad Efazati","url":"https://efazati.org/"}}\n'
        + "</script>"
    )
    body = f"""<main>
<article class="article">
    <p class="eyebrow kicker">{E(p['tag'])}</p>
    <h1>{E(p['title'])}</h1>
    <p class="meta">Mohammad Efazati &middot; <time datetime="{p['date']}">{nice_date(p['date'])}</time> &middot; {p['minutes']} min read</p>
    <div class="prose">
{p['body']}
    </div>
</article>
<div class="after">
    <p>Thoughts on this? I am happy to compare notes: <a href="mailto:mohammad@efazati.org">mohammad@efazati.org</a>.</p>
    <p class="eyebrow">More writing</p>
    <ul class="list">
{''.join(short(o) for o in others)}    </ul>
</div>
</main>
"""
    out = page(
        f"{p['title']} | Mohammad Efazati",
        p["title"],
        p["description"],
        p["url"],
        body,
        ogtype="article",
        ld=ld,
        blog_current=True,
    )
    write(f"blog/{p['slug']}/index.html", out)


def json_str(s):
    import json
    return json.dumps(s, ensure_ascii=False)


def build_home_cards(posts):
    """Fill the Writing list of index.html between its markers."""
    cards = "".join(card(p, n) for n, p in enumerate(posts[:3], 1))
    rest = "".join("            " + short(p).strip() + "\n" for p in posts[3:])
    rows = f"""        <div class="cards">{cards}</div>
        <ul class="list">
{rest}        </ul>
"""
    idx = ROOT / "index.html"
    text = idx.read_text()
    new, n = re.subn(
        r"(<!-- posts:start -->\n).*?(\s*<!-- posts:end -->)",
        lambda m: m.group(1) + rows + "        <!-- posts:end -->",
        text,
        flags=re.S,
    )
    if n != 1:
        raise SystemExit("index.html: posts:start/posts:end markers not found")
    idx.write_text(new)


def build_sitemap(posts):
    today = dt.date.today().isoformat()
    urls = [(f"{SITE}/", today, "1.0"), (f"{SITE}/blog/", today, "0.8")]
    urls += [(p["url"], p.get("updated", p["date"]), "0.7") for p in posts]
    body = "".join(
        f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{d}</lastmod>\n    <priority>{pr}</priority>\n  </url>\n"
        for u, d, pr in urls
    )
    write(
        "sitemap.xml",
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "</urlset>\n",
    )


def build_feed(posts):
    def rfc822(iso):
        return dt.datetime.fromisoformat(iso + "T09:00:00+00:00").strftime("%a, %d %b %Y %H:%M:%S +0000")

    items = "".join(
        f"""  <item>
    <title>{E(p['title'])}</title>
    <link>{p['url']}</link>
    <guid isPermaLink="true">{p['url']}</guid>
    <pubDate>{rfc822(p['date'])}</pubDate>
    <category>{E(p['tag'])}</category>
    <description>{E(p['description'])}</description>
  </item>
"""
        for p in posts
    )
    write(
        "feed.xml",
        f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
<channel>
  <title>Mohammad Efazati: writing</title>
  <link>{SITE}/blog/</link>
  <atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>
  <description>Platform engineering, Kubernetes, observability, CI/CD and technical hiring with AI.</description>
  <language>en</language>
{items}</channel>
</rss>
""",
    )


def to_markdown(fragment):
    """Just enough HTML to Markdown for llms-full.txt; the posts use a small set of tags."""
    s = fragment
    s = re.sub(r"<pre><code>(.*?)</code></pre>", lambda m: "```\n" + m.group(1) + "\n```", s, flags=re.S)
    s = re.sub(r"<h2>(.*?)</h2>", r"\n## \1\n", s)
    s = re.sub(r"<h3>(.*?)</h3>", r"\n### \1\n", s)
    s = re.sub(r"<blockquote>(.*?)</blockquote>", r"> \1", s, flags=re.S)
    s = re.sub(r"<li>(.*?)</li>", r"- \1", s, flags=re.S)
    s = re.sub(r'<a href="(/[^"]*)">(.*?)</a>', lambda m: f"[{m.group(2)}]({SITE}{m.group(1)})", s)
    s = re.sub(r'<a href="([^"]*)">(.*?)</a>', r"[\2](\1)", s)
    s = re.sub(r"</?(strong|b)>", "**", s)
    s = re.sub(r"</?em>", "_", s)
    s = re.sub(r"</?code>", "`", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    return re.sub(r"\n{3,}", "\n\n", s).strip()


def build_llms(posts):
    intro = (ROOT / "content/llms-intro.md").read_text().strip()
    lst = "\n".join(f"- [{p['title']}]({p['url']}): {p['description']}" for p in posts)
    short = f"""{intro}

## Writing

{lst}

## Optional

- [Full text of every post]({SITE}/llms-full.txt): this file plus each article in Markdown
- [RSS feed]({SITE}/feed.xml)
"""
    write("llms.txt", short)
    full = [intro, "", "# Writing", ""]
    for p in posts:
        full += [
            f"## {p['title']}",
            "",
            f"URL: {p['url']}  ",
            f"Published: {p['date']} · Topic: {p['tag']}",
            "",
            f"_{p['description']}_",
            "",
            to_markdown(p["body"]).replace("\n## ", "\n### "),
            "",
            "---",
            "",
        ]
    write("llms-full.txt", "\n".join(full))


def write(rel, text):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def main():
    posts = load_posts()
    build_blog_index(posts)
    for p in posts:
        build_post(p, posts)
    build_home_cards(posts)
    build_sitemap(posts)
    build_feed(posts)
    build_llms(posts)
    print(f"built {len(posts)} posts, blog index, home cards, sitemap, feed, llms.txt, llms-full.txt")


if __name__ == "__main__":
    main()
