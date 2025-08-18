import os
from urllib.parse import urljoin
from datetime import datetime, timezone
from bs4 import BeautifulSoup
import dateparser
import requests
from feedgen.feed import FeedGenerator

SELF_BASE_URL = "https://facilitairinfo.github.io/Newsfeeds"

def get_html(url):
    """Haalt HTML op van een URL."""
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.text

def pick_text(el):
    """Pakt de tekst uit een BeautifulSoup-element als die er is."""
    return el.get_text(strip=True) if el else None

def parse_date(block, date_selector=None, date_attr=None, date_format=None, date_format_out=None):
    """Haalt datum uit HTML-block en zet om naar datetime (UTC)."""
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
            dt = dateparser.parse(raw)
        if date_format_out:
            # voor consistentie in de feed
            raw_iso = dt.strftime(date_format_out)
            dt = datetime.strptime(raw_iso, "%Y-%m-%d")
        if not dt.tzinfo:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception as e:
        print(f"[WARN] Kon datum niet parsen: {raw} ({e})")
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
    fg.rss_file(out_path)

if __name__ == "__main__":
    import yaml
    config_path = os.path.join(os.path.dirname(__file__), "../sites-nieuws.yml")
    with open(config_path, "r", encoding="utf-8") as f:
        sites = yaml.safe_load(f)
    all_items = []
    for site in sites:
        all_items.extend(scrape_site(site))
    out_path = os.path.join(os.path.dirname(__file__), "../docs/nieuws.xml")
    build_feed(all_items, out_path, "Facilitair Nieuws", "nieuws.xml")
