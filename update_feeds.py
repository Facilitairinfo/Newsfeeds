import os
import json
import feedparser
from datetime import datetime, timezone

# Map naar je feeds
FEEDS_DIR = "docs"

def process_feed(file_path):
    """Parse een feed-bestand en retourneer feed-informatie."""
    parsed = feedparser.parse(file_path)

    # Zoek de <link> naar de website in de feed
    website_url = ""
    if "link" in parsed.feed:
        website_url = parsed.feed.link

    # Feedbestand zelf op GitHub Pages
    feed_filename = os.path.basename(file_path)
    feed_url = f"https://facilitairinfo.github.io/Newsfeeds/{feed_filename}"

    status = bool(parsed.entries)  # True als er items in de feed staan

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
            feed_info = process_feed(file_path)
            feeds_status.append(feed_info)

    # Schrijf feedstatus.json weg
    output_path = os.path.join(FEEDS_DIR, "feedstatus.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(feeds_status, f, ensure_ascii=False, indent=2)

    print(f"{len(feeds_status)} feeds verwerkt en feedstatus.json bijgewerkt.")

if __name__ == "__main__":
    main()
