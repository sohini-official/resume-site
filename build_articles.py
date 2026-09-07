import html
import os
import re
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
ART_DIR = os.path.join(ROOT, "article")

SITE = "Sohini Banerjee"


def human_title(stem):
    parts = re.sub(r"[-_]+", " ", stem).strip()
    return parts.title() or "Article"


def render_inline(s):
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*([^*]+?)\*", r"<em>\1</em>", s)
    return s


def parse_txt(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    stem = os.path.splitext(os.path.basename(path))[0]
    mtime = os.path.getmtime(path)
    date = time.strftime("%B %d, %Y", time.localtime(mtime))

    lines = [ln.strip() for ln in raw.splitlines()]
    title = None
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        lines = lines[1:]
    if not title:
        title = human_title(stem)

    tags, paras = [], []
    for ln in lines:
        if not ln:
            continue
        if all(w.startswith("#") for w in ln.split()):
            tags = [w.lstrip("#") for w in ln.split()]
            continue
        paras.append(render_inline(ln))
    return title, date, tags, paras, stem


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="description" content="{desc}" />
  <title>{title} · {site}</title>
  <link rel="stylesheet" href="{css}" />
</head>
<body>
  <header>
    <div class="container">
      <nav>
        <a class="logo" href="{home}">Sohini Banerjee</a>
        <div class="nav-links">
          <a href="{home}#about">About</a>
          <a href="{home}#experience">Experience</a>
          <a href="{home}#achievements">Achievements</a>
          <a href="{home}#education">Education</a>
          <a href="index.html">Blog</a>
          <a href="{home}#contact">Contact</a>
        </div>
      </nav>
    </div>
  </header>

  <main class="container">
    <article class="card article-card">
      <h1 class="article-title">{title}</h1>
      <p class="article-meta">
        By {site} · {date}{tags_byline}
      </p>
      <div class="article-body">
{body}
      </div>
      <div class="tag-list">{tags}
      </div>
    </article>
    <div class="article-nav">
      <a class="btn btn-outline" href="index.html">&larr; All articles</a>
      <a class="btn btn-outline" href="{home}">Back to homepage</a>
    </div>
  </main>

  <footer>
    <div class="container">
      &copy; <span id="year"></span> {site}. Built with plain HTML &amp; CSS.
    </div>
  </footer>

  <script>
    document.getElementById("year").textContent = new Date().getFullYear();
  </script>
</body>
</html>
"""


def build_article(title, date, tags, paras, stem):
    body = "\n".join(f"      <p>{p}</p>" for p in paras)
    tag_chips = "".join(f'<span class="tag">{html.escape(t)}</span>' for t in tags)
    tag_byline = " · " + " · ".join(html.escape(t) for t in tags) if tags else ""
    return PAGE.format(
        desc=html.escape(title),
        title=title,
        site=SITE,
        css="../css/style.css",
        home="../index.html",
        body=body,
        tags=tag_chips,
        tags_byline=tag_byline,
        date=date,
    )


def build_list(articles):
    cards = []
    for title, date, tags, paras, stem in articles:
        teaser = " ".join(re.sub(r"<[^>]+>", "", p) for p in paras)
        if len(teaser) > 200:
            teaser = teaser[:200].rsplit(" ", 1)[0] + "…"
        cards.append(
            f'      <div class="card">\n'
            f'        <h2><a href="{stem}.html">{title}</a></h2>\n'
            f'        <p class="date">{date}</p>\n'
            f'        <p>{html.escape(teaser)}</p>\n'
            f'        <a class="btn btn-outline" href="{stem}.html">Read article</a>\n'
            f'      </div>'
        )
    cards_html = "\n".join(cards)
    return PAGE.format(
        desc="Articles and blog posts",
        title="Articles",
        site=SITE,
        css="../css/style.css",
        home="../index.html",
        body=f"      <div class=\"grid blog-grid\">\n{cards_html}\n      </div>\n"
        + "      <p class=\"article-meta\">Thoughts on project management, communication, and connecting skills to daily life.</p>",
        tags="",
        tags_byline="",
        date="",
    )


def main():
    txts = sorted(f for f in os.listdir(ART_DIR) if f.endswith(".txt"))
    if not txts:
        print("No .txt files in article/")
        return
    articles = []
    for name in txts:
        path = os.path.join(ART_DIR, name)
        title, date, tags, paras, stem = parse_txt(path)
        out = os.path.join(ART_DIR, stem + ".html")
        with open(out, "w", encoding="utf-8") as f:
            f.write(build_article(title, date, tags, paras, stem))
        articles.append((title, date, tags, paras, stem))
        print(f"-> {stem}.html  ({title})")

    with open(os.path.join(ART_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(build_list(articles))
    print(f"-> index.html  ({len(articles)} article(s))")


if __name__ == "__main__":
    main()