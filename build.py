#!/usr/bin/env python3
"""Build the DioQuest site: src/ -> public/.

Usage:  python3 build.py

Each file in src/pages/ starts with a small header block:

    ---
    title: Page title
    description: One-sentence summary for search engines
    path: /about/
    nav: about
    ---

followed by the page's HTML. The build wraps it in src/layout.html and writes
it to public/<path>/index.html. Everything in src/assets/ is copied as-is.
Only the Python standard library is used.
"""
import datetime
import hashlib
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT = ROOT / "public"

# ---------------------------------------------------------------- settings --
SITE_URL = "https://www.dioquest.com"

# Shown on the contact page, in the footer and behind the store's request buttons.
CONTACT_EMAIL = "info@dioquest.com"

# Old Squarespace URLs that no longer exist -> where they should land.
REDIRECTS = {
    "/store/p/terra-cotta-dioquest-panel/": "/store/#terra-cotta",
    "/store/p/off-white-dioquest-panel/": "/store/#off-white",
    "/store/p/style-01-ej5na-2tt8t/": "/store/#bright-white",
    "/store/p/style-02-hxmaf-f3t6a/": "/store/#speckled",
    "/store/p/style-03-g2rtt-mef6l/": "/store/#foamed",
    "/cart/": "/store/",
}
# ---------------------------------------------------------------------------


def parse(page: Path):
    text = page.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise SystemExit(f"{page}: missing header block")
    _, head, body = text.split("---", 2)
    meta = {}
    for line in head.strip().splitlines():
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    for required in ("title", "description", "path"):
        if required not in meta:
            raise SystemExit(f"{page}: header is missing '{required}'")
    return meta, body.strip()


def out_file(path: str) -> Path:
    if path.endswith("/"):
        return OUT / path.strip("/") / "index.html"
    return OUT / path.lstrip("/")


def asset_version() -> str:
    digest = hashlib.sha1()
    for name in ("css/site.css", "js/site.js"):
        digest.update((SRC / "assets" / name).read_bytes())
    return digest.hexdigest()[:8]


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SRC / "assets", OUT / "assets")

    layout = (SRC / "layout.html").read_text(encoding="utf-8")
    version = asset_version()
    year = str(datetime.date.today().year)
    sitemap = []

    for page in sorted((SRC / "pages").rglob("*.html")):
        meta, body = parse(page)
        path = meta["path"]
        html = layout
        nav = meta.get("nav", "")
        if nav:
            html = html.replace(f'data-nav="{nav}"', f'data-nav="{nav}" aria-current="page"')
        values = {
            "title": meta["title"],
            "description": meta["description"],
            "canonical": SITE_URL + path,
            "og_image": SITE_URL + meta.get("image", "/assets/img/panel-prototype.webp"),
            "content": body,
            "contact_email": CONTACT_EMAIL,
            "year": year,
            "v": version,
        }
        for key, value in values.items():
            html = html.replace("{{" + key + "}}", value)
        target = out_file(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding="utf-8")
        if path.endswith("/"):
            sitemap.append(path)
        print(f"  {path}")

    for old, new in REDIRECTS.items():
        target = out_file(old)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            "<!doctype html>\n<meta charset=\"utf-8\">\n<title>DioQuest</title>\n"
            f"<link rel=\"canonical\" href=\"{SITE_URL}{new}\">\n"
            "<meta name=\"robots\" content=\"noindex\">\n"
            f"<meta http-equiv=\"refresh\" content=\"0; url={new}\">\n"
            f"<p>This page has moved to <a href=\"{new}\">{new}</a>.</p>\n",
            encoding="utf-8",
        )

    urls = "\n".join(f"  <url><loc>{SITE_URL}{p}</loc></url>" for p in sitemap)
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n</urlset>\n",
        encoding="utf-8",
    )
    (OUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8"
    )
    print(f"Built {len(sitemap)} pages + {len(REDIRECTS)} redirects into {OUT.name}/")


if __name__ == "__main__":
    main()
