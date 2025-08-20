import os
import sys
import yaml
import json
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timezone
from feedgen.feed import FeedGenerator
from utils import parse_event_date  # zelfde als in jouw repo

# Basisinstellingen
SELF_BASE_URL = "https://facilitairinfo.github.io/Newsfeeds"
REQUIRED_KEYS = ["name", "url", "selectors"]
SELECTOR_KEYS = ["item", "title", "link", "date", "summary"]

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def get_html(url):
    """Haalt HTML op met een User-Agent zodat 403's minder kans maken."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        )
    }
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    return r.text

def pick_text(el):
    return el.get_text(strip=True) if el else None

def load_sites(file_path):
    """Valideer en laad YAML-feedconfiguratie."""
    with open(file_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, list):
        raise ValueError(f"{file_path}: YAML root moet een lijst zijn (begin met '- name: ...').")

    for idx, site in enumerate(data, start=1):
        if not isinstance(site, dict):
            raise ValueError(f"{file_path}: item {idx} is geen dictionary.")

        for key in REQUIRED_KEYS:
            if key not in site:
                raise ValueError(f"{file_path}: item {idx} mist verplichte sleutel '{key}'.")

        selectors = site["selectors"]
        if not isinstance(selectors, dict):
            raise ValueError(f"{file_path}: item {idx} 'selectors' moet een dictionary zijn.")

        for sel_key in SELECTOR_KEYS:
            if sel_key not in selectors:
                raise ValueError(f"{file_path}: item {idx} mist selector '{sel_key}' in 'selectors'.")

    return data

def scrape_site(site):
    """Scrape één site en retourneer een lijst feeditems."""
    try:
        html = get_html(site["url"])
    except Exception as e:
        logging.error(f"❌ Ophalen mislukt voor {site['name']}: {e}")
        return []

    soup = BeautifulSoup(html, "lxml")
    sel = site["selectors"]
    max_items = site.get("max_items", 20)
    items = []

    for block in soup.select(sel["item"])[:max_items]:
        try:
            title_el = block.select_one(sel["title"])
            link_el = block.select_one(sel["link"])
            if not link_el:
                continue

            link = urljoin(site.get("base_url") or site["url"], link_el.get("href", ""))
            title = pick_text(title_el or link_el) or link
            date_el = block.select_one(sel["date"])
            date_text = pick_text(date_el)

            dt = parse_event_date(date_text) if date_text else None
            if dt and not dt.tzinfo:
                dt = dt.replace(tzinfo=timezone.utc)

            summary_el = block.select_one(sel["summary"])
            summary = pick_text(summary_el)

            items.append({
                "title": title,
                "link": link,
                "source": site["name"],
                "published": dt.isoformat() if dt else None,
                "summary": summary
            })
        except Exception as e:
            logging.warning(f"⚠️ Kon item niet verwerken: {e}")
            continue

    return items

def build_feed(all_items, out_path, feed_title, feed_path):
    """Bouwt een RSS-feedbestand op basis van gescrapete items."""
    fg = FeedGenerator()
    fg.id(f"{SELF_BASE_URL}/{feed_path}")
    fg.title(feed_title)
    fg.link(href=f"{SELF_BASE_URL}/{feed_path}", rel="self")
    fg.link(href=SELF_BASE_URL, rel="alternate")
    fg.description(f"{feed_title} – automatisch bijgewerkt")
    fg.language("nl")

    now = datetime.now(timezone.utc)
    sorted_items = sorted(
        (dict(i, published=(datetime.fromisoformat(i["published"]) if i["published"] else now)) for i in all_items),
        key=lambda x: x["published"],
        reverse=True
    )[:100]

    for it in sorted_items:
        fe = fg.add_entry()
        fe.id(it["link"])
        fe.title(f'{it["title"]} ({it["source"]})')
        fe.link(href=it["link"])
        fe.published(it["published"])
        if it.get("summary"):
            fe.description(it["summary"])

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fg.rss_file(out_path)
    logging.info(f"💾 Feed opgeslagen: {out_path}")

def save_json(all_items, out_path):
    """Slaat items ook op als JSON voor debugging/alternatief gebruik."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    logging.info(f"🗂️ JSON opgeslagen: {out_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Gebruik: python build-feed.py <sites-*.yml> [meer .yml bestanden...]")
        sys.exit(1)

    all_items = []
    for yaml_file in sys.argv[1:]:
        logging.info(f"📂 Verwerk bestand: {yaml_file}")
        try:
            sites = load_sites(yaml_file)
        except Exception as e:
            logging.error(f"❌ YAML-fout in {yaml_file}: {e}")
            continue

        for site in sites:
            scraped = scrape_site(site)
            logging.info(f"✅ {site['name']}: {len(scraped)} items gevonden")
            all_items.extend(scraped)

    feed_name = (
        os.path.splitext(os.path.basename(sys.argv[1]))[0].replace("sites-", "")
        if len(sys.argv) == 2 else "combined"
    )

    docs_dir = os.path.join(os.path.dirname(__file__), "../docs")
    build_feed(all_items, os.path.join(docs_dir, f"{feed_name}.xml"), feed_name.replace("-", " ").title(), f"{feed_name}.xml")
    save_json(all_items, os.path.join(docs_dir, f"{feed_name}.json"))
