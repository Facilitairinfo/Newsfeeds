import os
import time
from urllib.parse import urljoin
from datetime import datetime, timezone

import requests
import yaml
from bs4 import BeautifulSoup
from dateutil import parser as dateparser
from feedgen.feed import FeedGenerator

# Basisinstellingen
SELF_BASE_URL = os.environ.get(
    "SELF_BASE_URL",
    "https://example.github.io/mijn-feeds"
)
USER_AGENT = "FeedBuilderBot/1.0 (+https://github.com)"


def get_html(url):
    """Haalt HTML op van een URL."""
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
    resp.raise_for_status()
    return resp.text


def pick_text(el):
    """Geeft nette, opgeschoonde tekst uit een BeautifulSoup-element."""
    return " ".join(el.get_text(" ", strip=True).split())


def parse_date(el, date_selector, date_attr):
    """Probeert een datum uit een element te parsen."""
    if not date_selector:
        return None
    node = el.select_one(date_selector)
    if not node:
        return None
    raw = node.get(date_attr) if date_attr else pick_text(node)
    if not raw:
        return None
    try:
        dt = dateparser.parse(raw)
        if not dt.tzinfo:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def scrape_site(site):
    """Scrapet één site en geeft een lijst feed-items terug."""
    html = get_html(site["url"])
    soup = BeautifulSoup(html, "lxml")

    max_items = site.get("max_items", 5)  # optioneel instelbaar in YAML
    items = []

    for block in soup.select(site["item_selector"])[:max_items]:
        title_el = block.select_one(site.get("title_selector") or "") if site.get("title_selector") else None
        link_el = block.select_one(site.get("link_selector") or "") if site.get("link_selector") else None

        if not link_el:
            print(f"[WARN] Geen link gevonden voor {site['name']}")
            continue

        href = link_el.get("href") or ""
        link = urljoin(site.get("base_url") or site["url"], href)
        title = pick_text(title_el or link_el) or link

        dt = parse_date(block, site.get("date_selector"), site.get("date_attr"))
        if not dt:
            print(f"[INFO] Geen datum gevonden voor: {title}")

        items.append({
            "title": title,
            "link": link,
            "source": site["name"],
            "published": dt
        })

    return items


def build_feed(all_items, out_path, feed_title, feed_path):
    """Bouwt de RSS-feed en schrijft deze naar bestand."""
    fg = FeedGenerator()
    fg.load_extension("podcast")  # heeft geen effect tenzij je podcast velden toevoegt
    fg.id(f"{SELF_BASE_URL}/{feed_path}")
    fg.title(feed_title)
    fg.link(href=f"{SELF_BASE_URL}/{feed_path}", rel="self")
    fg.link(href=SELF_BASE_URL, rel="alternate")
    fg.description(f"{feed_title} – automatisch bijgewerkt")
    fg.language("nl")

    now = datetime.now(timezone.utc)

    # Sorteer op datum, vul ontbrekende datums met nu, en beperk tot max. 100 items
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
    fg.rss_file(out_path, pretty=True)


def main():
    """Laadt sites-config en genereert nieuwsfeed."""
    with open("sites-nieuws.yml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    all_items = []
    for site in cfg.get("sites", []):
        try:
            items = scrape_site(site)
            all_items.extend(items)
        except Exception as e:
            print(f"[WARN] Fout bij {site['name']}: {e}")
        time.sleep(1)  # beleefd crawlen

    build_feed(all_items, "public/nieuws.xml", "Nieuws feed", "nieuws.xml")


if __name__ == "__main__":
    main()
