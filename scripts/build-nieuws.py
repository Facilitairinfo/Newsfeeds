import os, time, hashlib
from urllib.parse import urljoin
from datetime import datetime, timezone
import requests, yaml
from bs4 import BeautifulSoup
from dateutil import parser as dateparser
from feedgen.feed import FeedGenerator

SELF_BASE_URL = os.environ.get("SELF_BASE_URL", "https://example.github.io/mijn-feeds")
USER_AGENT = "FeedBuilderBot/1.0 (+https://github.com)"

def get_html(url):
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
    resp.raise_for_status()
    return resp.text

def pick_text(el):
    return " ".join(el.get_text(" ", strip=True).split())

def parse_date(el, date_selector, date_attr):
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

def scrape_site(site, max_items_per_site=5):
    html = get_html(site["url"])
    soup = BeautifulSoup(html, "lxml")
    items = []
    for block in soup.select(site["item_selector"])[:max_items_per_site]:
        title_el = block.select_one(site["title_selector"]) if site.get("title_selector") else None
        link_el = block.select_one(site["link_selector"]) if site.get("link_selector") else None
        if not link_el:
            continue
        href = link_el.get("href") or ""
        link = urljoin(site.get("base_url") or site["url"], href)
        title = pick_text(title_el or link_el) or link
        dt = parse_date(block, site.get("date_selector"), site.get("date_attr"))
        items.append({
            "title": title,
            "link": link,
            "source": site["name"],
            "published": dt
        })
    return items

def build_feed(all_items, out_path, feed_title, feed_path):
    fg = FeedGenerator()
    fg.load_extension("podcast")  # harmless if not used
    fg.id(f"{SELF_BASE_URL}/{feed_path}")
    fg.title(feed_title)
    fg.link(href=f"{SELF_BASE_URL}/{feed_path}", rel="self")
    fg.link(href=SELF_BASE_URL, rel="alternate")
    fg.description(f"{feed_title} – automatisch bijgewerkt")
    fg.language("nl")

    # sorteer, vul datum in als ontbreekt, beperk tot 100
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
    fg.rss_str(pretty=True)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fg.rss_file(out_path)

def main():
    with open("sites-nieuws.yml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    all_items = []
    for site in cfg["sites"]:
        try:
            items = scrape_site(site)
            all_items.extend(items)
        except Exception as e:
            print(f"[WARN] Fout bij {site['name']}: {e}")
        time.sleep(1)  # beleefd crawlen
    build_feed(all_items, "public/nieuws.xml", "Nieuws feed", "nieuws.xml")

if __name__ == "__main__":
    main()
