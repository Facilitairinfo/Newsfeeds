import os
import json
import feedparser
from datetime import datetime

FEEDS_DIR = "docs"
BASE_URL = "https://facilitairinfo.github.io/Newsfeeds"

status_list = []

for file_name in os.listdir(FEEDS_DIR):
    if file_name.lower().endswith(".xml"):
        feed_path = os.path.join(FEEDS_DIR, file_name)
        feed_url = f"{BASE_URL}/{file_name}"

        try:
            parsed = feedparser.parse(feed_path)
        except Exception:
            parsed = None

        if parsed and parsed.feed:
            website = parsed.feed.get("link", "Onbekend")
            status = bool(parsed.entries)
        else:
            website = "Onbekend"
            status = False

        status_list.append({
            "website": website,
            "feedbron": feed_url,
            "status": status,
            "last_checked": datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        })

# Schrijf feedstatus.json weg
with open(os.path.join(FEEDS_DIR, "feedstatus.json"), "w", encoding="utf-8") as f:
    json.dump(status_list, f, ensure_ascii=False, indent=2)

print(f"{len(status_list)} feeds verwerkt en feedstatus.json bijgewerkt.")
