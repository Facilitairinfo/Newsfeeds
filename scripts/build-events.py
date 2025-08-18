import os, time
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

def parse_date(el, sel, attr):
    if not sel:
        return None
    n = el.select_one(sel)
    if not n:
        return None
    raw = n.get(attr) if attr else pick_text(n)
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
        title_el = block.select_one(site.get("title_selector", ""))
        link_el = block.select_one(site.get("link_selector", "a"))
        if not link_el:
            continue
        link = urljoin(site.get("base_url") or site["url"], link_el.get("href") or "")
        title = pick_text(title_el or link_el) or link
        start_dt = parse_date(block, site.get("date_selector"), site.get("date_attr"))
        items.append({
            "title": title,
            "link": link,
            "published": start_dt or datetime.now(timezone.utc),
        })
    return items

def build_feed(items, out_path, feed_title, feed_path):
    fg = FeedGenerator()
    fg.id(f"{SELF_BASE_URL}/{feed_path}")
    fg.title(feed_title)
    fg.link(href=f"{SELF_BASE_URL}/{feed_path}", rel="self")
    fg.link(href=SELF_BASE_URL, rel="alternate")
    fg.description(f"{feed_title} – events")
    fg.language("nl")

    items_sorted = sorted(items, key=lambda x: x["published"] or datetime.now(timezone.utc), reverse=True)[:100]
    for it in items_sorted:
        fe = fg.add_entry()
        fe.id(it["link"])
        fe.title(it["title"])
        fe.link(href=it["link"])
        fe.published(it["published"])
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fg.rss_file(out_path)

def main():
    with open("sites-events.yml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    all_items = []
    for site in cfg["sites"]:
        try:
            all_items.extend(scrape_site(site))
        except Exception as e:
            print(f"[WARN] Fout bij {site['name']}: {e}")
        time.sleep(1)
    build_feed(all_items, "public/events.xml", "Events feed", "events.xml")

if __name__ == "__main__":
    main()
