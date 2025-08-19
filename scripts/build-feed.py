import os, sys
from pathlib import Path
from urllib.parse import urljoin
from datetime import datetime, timezone
from bs4 import BeautifulSoup
import yaml, requests, dateparser
from feedgen.feed import FeedGenerator
from utils import parse_event_date  # onze datumparser met fallback & kleuren

SELF_BASE_URL = "https://facilitairinfo.github.io/Newsfeeds"

REQUIRED_KEYS = [
    "name", "url", "item_selector",
    "title_selector", "link_selector",
    "date_selector", "date_format"
]

def get_html(url):
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.text

def pick_text(el):
    return el.get_text(strip=True) if el else None

def load_sites(file_path):
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
    return data

def scrape_site(site):
    html = get_html(site["url"])
    soup = BeautifulSoup(html, "lxml")
    items = []
    max_items = site.get("max_items", 20)

    for block in soup.select(site["item_selector"])[:max_items]:
        title_el = block.select_one(site["title_selector"])
        link_el = block.select_one(site["link_selector"])
        if not link_el:
            continue

        link = urljoin(site.get("base_url") or site["url"], link_el.get("href", ""))
        title = pick_text(title_el or link_el) or link

        # Generieke datumparser (werkt voor nieuws, events, podcasts)
        dt = parse_event_date(
            block,
            date_selector=site.get("date_selector"),
            date_format=site.get("date_format"),
            fallback_day_selector=site.get("fallback_day_selector"),
            fallback_month_selector=site.get("fallback_month_selector"),
            fallback_year_selector=site.get("fallback_year_selector")
        )

        if dt and not dt.tzinfo:
            dt = dt.replace(tzinfo=timezone.utc)

        items.append({
            "title": title,
            "link": link,
            "source": site["name"],
            "published": dt
        })

    return items

def build_feed(all_items, out_path, feed_title, feed_path):
    fg = FeedGenerator()
    fg.id(f"{SELF_BASE_URL}/{feed_path}")
    fg.title(feed_title)
    fg.link(href=f"{SELF_BASE_URL}/{feed_path}", rel="self")
    fg.link(href=SELF_BASE_URL, rel="alternate")
    fg.description(f"{feed_title} – automatisch bijgewerkt")
    fg.language("nl")
    now = datetime.now(timezone.utc)
    sorted_items = sorted(
        (dict(i, published=(i["published"] or now)) for i in all_items),
        key=lambda x: x["published"], reverse=True
    )[:100]
    for it in sorted_items:
        fe = fg.add_entry()
        fe.id(it["link"])
        fe.title(f'{it["title"]} ({it["source"]})')
        fe.link(href=it["link"])
        fe.published(it["published"])
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fg.rss_file(out_path)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Gebruik: python build-feed.py <sites-*.yml> [<sites-*.yml> ...]")
        sys.exit(1)
    all_sites, all_items = [], []
    for yaml_file in sys.argv[1:]:
        sites = load_sites(yaml_file)
        all_sites.extend(sites)
        for site in sites:
            all_items.extend(scrape_site(site))
    # naam van eerste bestand bepaalt feednaam bij 1 input, anders 'combined'
    if len(sys.argv) == 2:
        feed_name = os.path.splitext(os.path.basename(sys.argv[1]))[0].replace("sites-", "")
    else:
        feed_name = "combined"
    output_file = f"{feed_name}.xml"
    output_path = os.path.join(os.path.dirname(__file__), f"../docs/{output_file}")
    build_feed(all_items, output_path, feed_name.replace("-", " ").title(), output_file)
