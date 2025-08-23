import os
import json
import feedparser
from datetime import datetime, timezone

# Map waar je feedbestanden staan
FEEDS_DIR = "docs"

def process_feed(file_path):
    """Parse een feed-bestand en retourneer feed-informatie."""
    parsed = feedparser.parse(file_path)

    # Zoek de <link> naar de website
    website_url = parsed.feed.get("link", "")

    # URL naar de feed zelf op GitHub Pages
    feed_filename = os.path.basename(file_path)
    feed_url = f"https://facilitairinfo.github.io/Newsfeeds/{feed_filename}"

    # True als er entries in staan, anders False
    status = bool(parsed.entries)

    return {
        "website": website_url,
        "feedbron": feed_url,
        "status": status,
        "last_checked": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    }

def main():
    feeds_status = []

    for filename in os.listdir(FEEDS_DIR):
        if filename.endswith(".xml"):
            file_path = os.path.join(FEEDS_DIR, filename)
            feeds_status.append(process_feed(file_path))

    # Wegschrijven naar feedstatus.json
    output_path = os.path.join(FEEDS_DIR, "feedstatus.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(feeds_status, f, ensure_ascii=False, indent=2)

    # Samenvatting in logs
    totaal = len(feeds_status)
    werkend = sum(1 for f in feeds_status if f["status"])
    kapot = totaal - werkend

    print(f"{totaal} feeds verwerkt en feedstatus.json bijgewerkt.")
    print(f"  ✔ {werkend} werkend")
    print(f"  ✖ {kapot} niet‑werkend")

if __name__ == "__main__":
    main()
