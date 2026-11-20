#!/usr/bin/env python3
"""Build the Marmotte-o-mètre.

    python3 build.py [french-site-url] [english-site-url]

One site per language, each on its own domain. Outputs, in dist/:
  fr/             French site (index.html, robots.txt, sitemap.xml, favicon.svg, og.png)
  en/             English site, same files; also the x-default for search engines
  artifact.html   single-file bilingual version for a claude.ai artifact
and public/, a copy of the site named by the MARMOT_SITE environment variable (fr or en), for the host to serve.

Text lives in src/i18n.json. Each static page is pre-rendered in its language so
crawlers read real text without running JavaScript.
"""
import html
import json
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).parent
SITE = {
    "fr": (sys.argv[1] if len(sys.argv) > 1 else "https://estcequelesmarmotteshibernent.fr").rstrip("/"),
    "en": (sys.argv[2] if len(sys.argv) > 2 else "https://aremarmotshibernating.com").rstrip("/"),
}
DIST = ROOT / "dist"

i18n = json.loads((ROOT / "src" / "i18n.json").read_text(encoding="utf-8"))
page = (ROOT / "src" / "page.html").read_text(encoding="utf-8")

marker = "/*i18n-start*/{}/*i18n-end*/"
assert page.count(marker) == 1, "i18n marker missing from src/page.html"
# "</" must not appear raw inside an inline script
page = page.replace(marker, json.dumps(i18n, ensure_ascii=False).replace("</", "<\\/"))


def lookup(tree, path):
    for key in path.split("."):
        tree = tree[int(key)] if isinstance(tree, list) else tree[key]
    return tree


def prerender(source, lang):
    """Write the language's text into every data-i18n element and aria-label."""
    words = i18n[lang]

    def text(m):
        return m.group(1) + html.escape(lookup(words, m.group(3)), quote=False) + m.group(5)

    def aria(m):
        return 'data-i18n-aria="%s" aria-label="%s"' % (m.group(1), html.escape(lookup(words, m.group(1))))

    source = re.sub(r'(<(\w+)[^>]*\sdata-i18n="([^"]+)"[^>]*>)([^<]*)(</\2>)', text, source)
    return re.sub(r'data-i18n-aria="([^"]+)" aria-label="[^"]*"', aria, source)


FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<circle cx="16" cy="14" r="8" fill="#6e4721"/><circle cx="48" cy="14" r="8" fill="#6e4721"/>
<circle cx="32" cy="34" r="26" fill="#a9743c"/><ellipse cx="32" cy="43" rx="14" ry="11" fill="#f1cf94"/>
<circle cx="22" cy="28" r="3.5" fill="#1a0d05"/><circle cx="42" cy="28" r="3.5" fill="#1a0d05"/>
<ellipse cx="32" cy="37" rx="4.5" ry="3" fill="#1a0d05"/>
<rect x="28" y="42" width="4" height="7" fill="#fff"/><rect x="32" y="42" width="4" height="7" fill="#fff"/>
</svg>
"""

# English site only: French-speaking visitors are sent to the French domain, unless they chose English.
# The French site never redirects, so crawlers (which browse in English) can index it.
REDIRECT = (
    "<script>(function(){try{if(location.hash==='#choisi'){localStorage.setItem('marmot-lang','en');return;}"
    "var s=localStorage.getItem('marmot-lang');"
    "var fr=s?s==='fr':(navigator.language||'').toLowerCase().indexOf('fr')===0;"
    "if(fr)location.replace('%s/');}catch(e){}})();</script>" % SITE["fr"]
)


def static_page(lang):
    words = i18n[lang]
    url = SITE[lang] + "/"
    other = "en" if lang == "fr" else "fr"
    head_part, body_part = page.split('<div class="app"', 1)
    head_part = re.sub(r"<title>.*?</title>\n?", "", head_part)
    head_part = re.sub(r'<meta name="claude:[^>]*>\n?', "", head_part)
    title = "%s | %s" % (words["seo"]["h2"], words["title"])
    desc = words["description"]
    ld = [
        {"@context": "https://schema.org", "@type": "WebSite", "name": words["title"], "url": url, "inLanguage": lang},
        {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "inLanguage": lang,
            "mainEntity": [
                {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
                for f in words["seo"]["faq"]
            ],
        },
    ]
    head = "\n".join(
        [
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
            "<title>%s</title>" % html.escape(title),
            '<meta name="description" content="%s">' % html.escape(desc),
            '<link rel="canonical" href="%s">' % url,
            '<link rel="alternate" hreflang="en" href="%s/">' % SITE["en"],
            '<link rel="alternate" hreflang="fr" href="%s/">' % SITE["fr"],
            '<link rel="alternate" hreflang="x-default" href="%s/">' % SITE["en"],
            '<link rel="icon" href="favicon.svg" type="image/svg+xml">',
            '<meta name="theme-color" content="#04050c">',
            '<meta property="og:type" content="website">',
            '<meta property="og:title" content="%s">' % html.escape(title),
            '<meta property="og:description" content="%s">' % html.escape(desc),
            '<meta property="og:url" content="%s">' % url,
            '<meta property="og:image" content="%s/og.png">' % SITE[lang],
            '<meta property="og:locale" content="%s">' % ("fr_FR" if lang == "fr" else "en_GB"),
            '<meta name="twitter:card" content="summary_large_image">',
            '<script type="application/ld+json">%s</script>'
            % json.dumps(ld, ensure_ascii=False).replace("</", "<\\/"),
            "<script>window.MARMOT_LANG='%s';window.MARMOT_ALT='%s';</script>"
            % (lang, SITE[other] + "/#choisi"),
            REDIRECT if lang == "en" else "",
            "<style>body{margin:0}</style>",
            head_part.strip(),
        ]
    )
    body = prerender('<div class="app"' + body_part, lang)
    return '<!doctype html>\n<html lang="%s">\n<head>\n%s\n</head>\n<body>\n%s\n</body>\n</html>\n' % (lang, head, body)


# dist/ is kept between builds: each site folder holds its hosting project link (.vercel)
DIST.mkdir(exist_ok=True)
(DIST / "artifact.html").write_text(page, encoding="utf-8")
for lang in ("fr", "en"):
    out = DIST / lang
    out.mkdir(exist_ok=True)
    (out / "index.html").write_text(static_page(lang), encoding="utf-8")
    (out / "favicon.svg").write_text(FAVICON, encoding="utf-8")
    shutil.copyfile(ROOT / "assets" / "og.png", out / "og.png")
    (out / "robots.txt").write_text("User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE[lang], encoding="utf-8")
    (out / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        "  <url><loc>%s/</loc>"
        '<xhtml:link rel="alternate" hreflang="en" href="%s/"/>'
        '<xhtml:link rel="alternate" hreflang="fr" href="%s/"/>'
        "<changefreq>daily</changefreq></url>\n</urlset>\n" % (SITE[lang], SITE["en"], SITE["fr"]),
        encoding="utf-8",
    )
print("Built dist/fr for", SITE["fr"], "and dist/en for", SITE["en"])

# On the host, each project publishes one language: MARMOT_SITE picks it (fr by default) and public/ is what gets served.
import os

site = os.environ.get("MARMOT_SITE", "fr")
if site not in SITE:
    sys.exit("MARMOT_SITE must be fr or en, got %r" % site)
PUBLIC = ROOT / "public"
if PUBLIC.exists():
    shutil.rmtree(PUBLIC)
shutil.copytree(DIST / site, PUBLIC)
print("Published the %s site to public/" % site)
