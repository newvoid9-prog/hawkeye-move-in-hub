"""Builds the site's HTML pages from _src/ content files and one shared layout.

Run from the repo root:  python3 _build.py
Files and folders starting with "_" are skipped by GitHub Pages (Jekyll), so
the sources and this script are never published as pages.
"""
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).parent
BASE_URL = "https://newvoid9-prog.github.io/hawkeye-move-in-hub/"
UPDATED = "2026-10-27"
NOTICE = ("This is a fictional website created for educational purposes as part of "
          "MKTG:4400 at the University of Iowa. It is not a real business.")

NAV = [
    ("index.html", "Home"),
    ("roommate-finder.html", "Roommate Finder"),
    ("dorms-ranked.html", "Dorms Ranked"),
    ("dorm-costs.html", "Dorm Costs"),
    ("make-friends-before-college.html", "Make Friends"),
]

PAGES = [
    {
        "file": "index.html",
        "title": "University of Iowa Incoming Freshman Guide | Hawkeye Move-In Hub",
        "description": "Admitted to the University of Iowa? Find a roommate, compare all ten first-year residence halls, see real 2026-27 dorm costs, and meet your class before move-in.",
    },
    {
        "file": "roommate-finder.html",
        "crumb": "Roommate Finder",
        "title": "University of Iowa Roommate Finder: How to Find a Good Match | Hawkeye Move-In Hub",
        "description": "How the University of Iowa roommate search works, where admitted Hawkeyes actually find roommates, the 12 questions to ask, and when going random is the smarter call.",
    },
    {
        "file": "dorms-ranked.html",
        "crumb": "Dorms Ranked",
        "title": "University of Iowa Dorms Ranked, Worst to Best (2026) | Hawkeye Move-In Hub",
        "description": "All ten University of Iowa first-year residence halls ranked worst to best, with side of campus, dining, room types, and 2026-27 starting prices for each hall.",
    },
    {
        "file": "dorm-costs.html",
        "crumb": "Dorm Costs",
        "title": "University of Iowa Dorm Costs 2026-27: Room and Meal Plan Prices | Hawkeye Move-In Hub",
        "description": "What University of Iowa dorms cost in 2026-27: room rates by hall and room type, every meal plan price, a yearly cost calculator, and the fees people forget.",
    },
    {
        "file": "make-friends-before-college.html",
        "crumb": "Make Friends",
        "title": "How to Make Friends Before College Starts: 6 Things That Work | Hawkeye Move-In Hub",
        "description": "How to make friends before college starts: six practical steps for incoming freshmen, from class Instagram pages to your future floor, so move-in day is not day one.",
    },
]


def asset_version(path):
    """Short content hash so browsers fetch a changed file instead of a cached copy."""
    return hashlib.sha1((ROOT / path).read_bytes()).hexdigest()[:8]


def page_url(file):
    return BASE_URL if file == "index.html" else BASE_URL + file


def nav_items(current):
    items = []
    for file, label in NAV:
        href = "./" if file == "index.html" else file
        current_attr = ' aria-current="page"' if file == current else ""
        items.append(f'<li><a href="{href}"{current_attr}>{label}</a></li>')
    return "\n          ".join(items)


def faq_html(faqs):
    if not faqs:
        return ""
    rows = "\n".join(
        f"<details><summary>{html.escape(q)}</summary><p>{a}</p></details>" for q, a in faqs
    )
    return f'<section class="faq" aria-labelledby="faq-heading">\n<h2 id="faq-heading">Frequently asked questions</h2>\n{rows}\n</section>'


def structured_data(page, faqs):
    blocks = []
    if page["file"] == "index.html":
        blocks.append({
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "Hawkeye Move-In Hub",
            "url": BASE_URL,
            "description": page["description"],
        })
    else:
        blocks.append({
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": BASE_URL},
                {"@type": "ListItem", "position": 2, "name": page["crumb"], "item": page_url(page["file"])},
            ],
        })
    if faqs:
        blocks.append({
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer", "text": html.unescape(_strip_tags(a))}}
                for q, a in faqs
            ],
        })
    return "\n  ".join(
        f'<script type="application/ld+json">{json.dumps(b, ensure_ascii=False)}</script>' for b in blocks
    )


def _strip_tags(text):
    out, inside = [], False
    for ch in text:
        if ch == "<":
            inside = True
        elif ch == ">":
            inside = False
        elif not inside:
            out.append(ch)
    return "".join(out)


def load_source(file):
    """Each _src file holds the page body, optionally followed by an FAQ block.

    FAQ block format, after a line containing only '<!-- FAQ -->':
        Q: question text
        A: answer html
    """
    raw = (ROOT / "_src" / file).read_text()
    body, _, faq_raw = raw.partition("<!-- FAQ -->")
    faqs, question = [], None
    for line in faq_raw.splitlines():
        line = line.strip()
        if line.startswith("Q: "):
            question = line[3:]
        elif line.startswith("A: ") and question:
            faqs.append((question, line[3:]))
            question = None
    return body.strip(), faqs


def render(page):
    body, faqs = load_source(page["file"])
    body = body.replace("{{FAQ}}", faq_html(faqs))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(page["title"])}</title>
  <meta name="description" content="{html.escape(page["description"])}">
  <link rel="canonical" href="{page_url(page["file"])}">
  <meta property="og:title" content="{html.escape(page["title"])}">
  <meta property="og:description" content="{html.escape(page["description"])}">
  <meta property="og:url" content="{page_url(page["file"])}">
  <meta property="og:type" content="website">
  <meta name="theme-color" content="#16130f">
  <link rel="icon" href="img/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@100..125,500..800&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="css/style.css?v={asset_version("css/style.css")}">
  {structured_data(page, faqs)}
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <p class="notice" role="note">{NOTICE}</p>

  <header class="site-header">
    <div class="wrap">
      <a class="brand" href="./"><span class="brand-mark" aria-hidden="true">HM</span>Hawkeye Move-In Hub</a>
      <nav class="site-nav" aria-label="Main navigation">
        <ul>
          {nav_items(page["file"])}
        </ul>
      </nav>
    </div>
  </header>

  <main id="main">
{body}
  </main>

  <footer class="site-footer">
    <div class="wrap">
      <div>
        <p class="footer-brand">Hawkeye Move-In Hub</p>
        <p>A student-written guide for admitted University of Iowa students, from acceptance to move-in day. Hawkeye Move-In Hub is not affiliated with the University of Iowa. Always confirm deadlines and rates with University Housing and Dining. Last updated October 27, 2026.</p>
      </div>
      <nav aria-label="Footer navigation">
        <ul>
          {nav_items(None)}
        </ul>
      </nav>
    </div>
    <p class="notice" role="note">{NOTICE}</p>
  </footer>
</body>
</html>
"""


def write_sitemap():
    urls = "\n".join(
        f"  <url><loc>{page_url(p['file'])}</loc><lastmod>{UPDATED}</lastmod></url>" for p in PAGES
    )
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n</urlset>\n"
    )


if __name__ == "__main__":
    for page in PAGES:
        (ROOT / page["file"]).write_text(render(page))
    write_sitemap()
    print(f"Built {len(PAGES)} pages and sitemap.xml")
