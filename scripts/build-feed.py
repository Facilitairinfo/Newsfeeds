#!/usr/bin/env python3
import os
import sys
import glob
import yaml
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import dateparser

CONFIG_DIR = "configs"
OUTPUT_DIR = "docs"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"

def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def get(session, url, timeout=20):
    r = session.get(url, timeout=timeout, headers={"User-Agent": USER_AGENT})
    r.raise_for_status()
    return r.text

def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]

def select_first_text(el, selectors):
    for sel in as_list(selectors):
        node = el.select_one(sel)
        if node:
            text = node.get_text(strip=True)
            if text:
                return text
    return None

def select_first_link(el, selectors, base_url):
    # Try selectors first
    for sel in as_list(selectors):
        node = el.select_one(sel)
        if node and node.get("href"):
            return urljoin(base_url, node["href"])
    # Fallback: any <a> inside the item
    node = el.select_one("a[href]")
    if node and node.get("href"):
        return urljoin(base_url, node["href"])
    return None

def select_first_date(el, selectors, date_attr=None, date_format=None):
    # Try attribute first (e.g., datetime)
    for sel in as_list(selectors):
        node = el.select_one(sel)
        if not node:
            continue
        if date_attr and node.has_attr(date_attr):
            raw = node.get(date_attr)
            if raw:
                # If a strict format is provided, try it; otherwise parse freely.
                if date_format:
                    try:
                        return datetime.strptime(raw, date_format)
                    except Exception:
                        pass
                parsed = dateparser.parse(raw)
                if parsed:
                    return parsed
        # Or parse visible text
        raw_text = node.get_text(strip=True)
        if raw_text:
            parsed = dateparser.parse(raw_text)
            if parsed:
                return parsed
    return None

def add_entry(fg, title, link, summary, pubdate):
    fe = fg.add_entry()
    if title:
        fe.title(title)
    if link:
        fe.link(href=link)
        fe.guid(link, permalink=True)
    if summary:
        fe.description(summary)
    if pubdate:
        fe.pubDate(pubdate)

def build_feed_from_config(cfg_path, session):
    cfg = load_config(cfg_path)
    feed_name = os.path.splitext(os.path.basename(cfg_path))[0]
    print(f"=== 🛠 Verwerk {feed_name} ===")

    # Channel metadata (link is verplicht in feedgen → maak een verstandige fallback)
    main_link = cfg.get("link") or cfg.get("url") or ""
    fg = FeedGenerator()
    fg.title(cfg.get("title", feed_name))
    fg.link(href=main_link, rel="alternate")
    fg.description(cfg.get("description", f"Feed voor {feed_name}"))
    fg.language(cfg.get("language", "nl"))
    fg.lastBuildDate(datetime.utcnow())

    max_items = int(cfg.get("max_items", 12))
    total_items = 0

    sources = cfg.get("sources")
    # Backward-compatible: als er geen 'sources' is, neem top-level velden als één source
    if not sources:
        sources = [{
            "url": cfg.get("url"),
            "item_selector": cfg.get("item_selector"),
            "title_selector": cfg.get("title_selector"),
            "link_selector": cfg.get("link_selector"),
            "summary_selector": cfg.get("summary_selector"),
            "date_selector": cfg.get("date_selector"),
            "date_attr": cfg.get("date_attr"),
            "date_format": cfg.get("date_format"),
        }]

    for source in sources:
        src_url = source.get("url")
        if not src_url:
            print("⚠ Bron overgeslagen: geen url")
            continue

        try:
            html = get(session, src_url)
        except Exception as e:
            print(f"⚠ Fout bij ophalen {src_url}: {e}")
            continue

        soup = BeautifulSoup(html, "html.parser")
        items = soup.select(source.get("item_selector") or "article, li, div")

        if not items:
            print(f"⚠ Geen items gevonden met selector '{source.get('item_selector')}' op {src_url}")
            continue

        count = 0
        for el in items:
            if count >= max_items:
                break

            title = select_first_text(el, source.get("title_selector") or ["h2 a", "h3 a", "a"])
            link = select_first_link(el, source.get("link_selector") or ["h2 a", "h3 a", "a"], base_url=src_url)
            summary = select_first_text(el, source.get("summary_selector") or [".intro", ".excerpt", "p"])
            pubdate = select_first_date(
                el,
                source.get("date_selector") or ["time", ".date", ".published", "span"],
                date_attr=source.get("date_attr"),
                date_format=source.get("date_format")
            )

            # Sla items zonder link of titel over (RSS readers hebben daar weinig aan)
            if not link and not title:
                continue

            add_entry(fg, title, link, summary, pubdate)
            count += 1
            total_items += 1

        print(f"• {src_url} → {count} items")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{feed_name}.xml")
    fg.rss_file(out_path, pretty=True)
    print(f"📄 Feed weggeschreven naar {out_path} ({total_items} items)")

    return total_items > 0

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    configs = sorted(glob.glob(os.path.join(CONFIG_DIR, "*.yml")))
    if not configs:
        print(f"⚠ Geen configbestanden gevonden in {CONFIG_DIR}/")
        sys.exit(1)

    print(f"▶ Gevonden configs: {[os.path.basename(c) for c in configs]}")
    session = requests.Session()

    success, failed = [], []
    for cfg_path in configs:
        ok = build_feed_from_config(cfg_path, session)
        (success if ok else failed).append(os.path.splitext(os.path.basename(cfg_path))[0])

    print("\n=== 📊 Samenvatting ===")
    print(f"✅ Geslaagd: {len(success)} → {success}")
    print(f"❌ Mislukt: {len(failed)} → {failed}")
    if failed:
        # Exit 0 zodat de workflow blijft committen; wil je falen bij lege feeds, zet naar 1.
        sys.exit(0)

if __name__ == "__main__":
    main()
