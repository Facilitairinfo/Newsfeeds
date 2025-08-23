#!/usr/bin/env python3
import os
import glob
import yaml
from datetime import datetime
from feedgen.feed import FeedGenerator
from scraper import scrape_site  # jouw bestaande scraper-functie
import html

CONFIG_DIR = "configs"
OUTPUT_DIR = "docs"

def build_feed_from_config(cfg_path):
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    print(f"=== 🛠 Verwerk {os.path.basename(cfg_path)} ===")
    items = scrape_site(cfg['url'], cfg['scraper'])

    # 🔹 Sanity check + fallbacks
    clean_items = []
    for idx, entry in enumerate(items, start=1):
        title = (entry.get('title') or '').strip()
        link = (entry.get('link') or '').strip()
        description = (entry.get('description') or '').strip()
        pubDate = entry.get('pubDate')

        # Fallback voor lege description → titel
        if not description and title:
            description = title

        # Fallback voor lege datum → vandaag
        if not pubDate:
            pubDate = datetime.utcnow()

        if title and link and description and pubDate:
            clean_items.append({
                'title': html.unescape(title),
                'link': link,
                'description': html.unescape(description),
                'pubDate': pubDate,
                'category': entry.get('category')
            })
        else:
            print(f"⏭ Item {idx} overgeslagen (ontbrekende velden)")

    if not clean_items:
        print("⚠ Geen complete items, feed wordt niet aangemaakt.")
        return False

    # 🔹 Feed opbouwen
    fg = FeedGenerator()
    fg.title(cfg['feed']['title'])
    fg.link(href=cfg['feed']['link'], rel='alternate')
    fg.description(cfg['feed']['description'])
    fg.language(cfg['feed']['language'])

    for it in clean_items:
        fe = fg.add_entry()
        fe.title(it['title'])
        fe.link(href=it['link'])
        fe.description(it['description'])
        fe.pubDate(it['pubDate'])
        if it.get('category'):
            fe.category(term=it['category'])

    # 🔹 Outputpad
    name = os.path.splitext(os.path.basename(cfg_path))[0]
    out_path = os.path.join(OUTPUT_DIR, f"{name}.xml")
    fg.rss_file(out_path, pretty=True)
    print(f"📄 Feed weggeschreven naar {out_path} ({len(clean_items)} items)")
    return True

def main():
    cfg_files = sorted(glob.glob(os.path.join(CONFIG_DIR, "*.yml")))
    print("▶ Start feed generation")
    print("▶ Gevonden configs:", [os.path.basename(p) for p in cfg_files])
    for cfg_path in cfg_files:
        build_feed_from_config(cfg_path)

if __name__ == "__main__":
    main()
