#!/usr/bin/env python3
import os
import sys
import glob
import yaml
import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime
import dateparser

CONFIG_DIR = "configs"
OUTPUT_DIR = "docs"

def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def fetch_and_parse(url):
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")

def build_feed_from_config(cfg_path):
    cfg = load_config(cfg_path)
    feed_name = os.path.splitext(os.path.basename(cfg_path))[0]
    print(f"=== 🛠 Verwerk {feed_name} ===")

    fg = FeedGenerator()
    fg.title(cfg.get("title", feed_name))
    fg.link(href=cfg.get("link", ""), rel="alternate")
    fg.description(cfg.get("description", f"Feed voor {feed_name}"))
    fg.language(cfg.get("language", "nl"))

    items = 0
    for source in cfg.get("sources", []):
        try:
            soup = fetch_and_parse(source["url"])
            elements = soup.select(source["item_selector"])
            for el in elements[: cfg.get("max_items", 10)]:
                fe = fg.add_entry()
                fe.title(el.select_one(source["title_selector"]).get_text(strip=True))
                link_el = el.select_one(source["link_selector"])
                if link_el and link_el.get("href"):
                    fe.link(href=requests.compat.urljoin(source["url"], link_el["href"]))
                if source.get("date_selector"):
                    date_text = el.select_one(source["date_selector"]).get_text(strip=True)
                    parsed_date = dateparser.parse(date_text)
                    if parsed_date:
                        fe.pubDate(parsed_date)
                if source.get("summary_selector"):
                    fe.description(el.select_one(source["summary_selector"]).get_text(strip=True))
                items += 1
        except Exception as e:
            print(f"⚠ Fout bij bron {source.get('url')}: {e}")

    if items == 0:
        print(f"⚠ Geen items gevonden voor {feed_name}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{feed_name}.xml")
    fg.rss_file(out_path, pretty=True)
    print(f"📄 Feed weggeschreven naar {out_path} ({items} items)")
    return items > 0

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    configs = sorted(glob.glob(os.path.join(CONFIG_DIR, "*.yml")))
    if not configs:
        print(f"⚠ Geen configbestanden gevonden in {CONFIG_DIR}/")
        sys.exit(1)

    print(f"▶ Gevonden configs: {[os.path.basename(c) for c in configs]}")

    success, failed = [], []
    for cfg_path in configs:
        ok = build_feed_from_config(cfg_path)
        (success if ok else failed).append(os.path.splitext(os.path.basename(cfg_path))[0])

    print("\n=== 📊 Samenvatting ===")
    print(f"✅ Geslaagd: {len(success)} → {success}")
    print(f"❌ Mislukt: {len(failed)} → {failed}")

    if failed:
        sys.exit(1)

if __name__ == "__main__":
    main()
