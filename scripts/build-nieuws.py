import os
import sys
from urllib.parse import urljoin
from datetime import datetime, timezone
from pathlib import Path
from bs4 import BeautifulSoup
import dateparser
import requests
from feedgen.feed import FeedGenerator
import yaml

# Basis-URL voor publicatie
SELF_BASE_URL = "https://facilitairinfo.github.io/Newsfeeds"

# -------------------------------------------------
# Helper functies
# -------------------------------------------------

def get_html(url):
    """Haalt HTML op van een URL."""
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.text

def pick_text(el):
    return el.get_text(strip=True) if el else None

def parse_date(block, date_selector=None, date_attr=None, date_format=None, date_format_out=None):
    """Parseert een datum uit een HTML-blok."""
    if not date_selector:
        return None
    date_el = block.select_one(date_selector)
    if not date_el:
        return None
    raw = date_el.get(date_attr) if date_attr else date_el.get_text(strip=True)
    if not raw:
        return None
    try:
        if date_format:
            dt = datetime.strptime(raw.strip(), date_format)
        else:
            dt = dateparser.parse(raw, languages=["nl", "en"])
        if date_format_out:
            raw_iso = dt.strftime(date_format_out)
            dt = datetime.strptime(raw_iso, "%Y-%m-%d")
        if not dt.tzinfo:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception as e:
        print(f"[WARN] Kon datum niet parsen: {raw} ({e})")
        return None

# -------------------------------------------------
# Validatie functies
# -------------------------------------------------

REQUIRED_KEYS = [
    "name",
    "url",
    "item_selector",
    "title_selector",
    "link_selector",
    "date_selector",
    "date_format"
]

def load_sites(file_path):
    """Laadt en valideert een sites-*.yml bestand."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, list):
        raise ValueError(f"{file_path}: YAML root moet een lijst zijn (begin elke site met '- name: ...').")

    for idx, site in enumerate(data, start=1):
        if not isinstance(site, dict):
            raise ValueError(f"{file_path}: item {idx} is geen dictionary.")
        for key in REQUIRED_KEYS:
            if key not in site:
                raise ValueError(f"{file_path}: item {idx} mist verplichte sleutel '{key}'.")

    return data

# -------------------------------------------------
# Scraper
# -------------------------------------------------

def scrape_site(site):
    html = get_html(site["url"])
    soup = BeautifulSoup(html, "lxml")
    max_items = site.get("max_items", 5)
    items = []

    for block in soup.select(site["item_selector"])[:max_items]:
        title_el = block.select_one(site["title_selector"])
        link_el = block.select_one(site["link_selector"])
        if not link_el:
            print(f"[WARN] Geen link gevonden voor {site['name']}")
            continue
        href = link_el.get("href") or ""
        link = urljoin(site.get("base_url") or site["url"], href)
        title = pick_text(title_el or link_el) or link
        dt = parse_date(
            block,
            site.get("date_selector"),
            site.get("date_attr"),
            site.get("date_format"),
            site.get("date_format_out")
        )
        if not dt:
            print(f"[INFO] Geen datum gevonden voor: {title}")
        items.append({
            "title": title,
            "link": link,
            "source": site["name"],
            "published": dt
        })
    return items

# -------------------------------------------------
# Feed builder
# -------------------------------------------------

def build_feed(all_items, out_path, feed_title, feed_path):
    fg = FeedGenerator()
    fg.load_extension("podcast")
    fg.id(f"{SELF_BASE_URL}/{feed_path}")
    fg.title(feed_title)
    fg.link(href=f"{SELF_BASE_URL}/{feed_path}", rel="self")
    fg.link(href=SELF_BASE_URL, rel="alternate")
    fg.description(f"{feed_title} – automatisch bijgewerkt")
    fg.language("nl")

    now = datetime.now(timezone.utc)
    items_sorted = sorted(
        (dict(i, published=(i["published"] or now)) for i in all_items),
        key=lambda x: x["published"],
        reverse=True
    )[:100]

    for it in items_sorted:
        fe = fg.add_entry()
        fe.id(it["link"])
        fe.title(f'{it["title"]} ({it["source"]})')
        fe.link(href=it["link"])
        fe.published(it["published"])

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fg.rss_file(out_path)

# -------------------------------------------------
# Main
# -------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Gebruik: python build-nieuws.py <yaml-bestand>")
        sys.exit(1)

    yaml_file = sys.argv[1]
    feed_name = os.path.splitext(os.path.basename(yaml_file))[0].replace("sites-", "")
    output_file = f"{feed_name}.xml"
    output_path = os.path.join(os.path.dirname(__file__), f"../docs/{output_file}")

    # ✅ Nu inclusief validatie
    all_sites = []
    all_sites.extend(load_sites(yaml_file))

    all_items = []
    for site in all_sites:
        all_items.extend(scrape_site(site))

    build_feed(all_items, output_path, feed_name.replace("-", " ").title(), output_file)
