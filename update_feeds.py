import os
import json
import feedparser
from datetime import datetime

# Pad naar je feeds
FEEDS_DIR = "docs"

# Hier vul je jouw feedlijst in (website & feed_url)
feeds = [
    {"website": "https://voorbeeld.nl", "feed_url": "https://voorbeeld.nl/rss.xml"},
    # meer feeds...
]

status_list = []

for feed in feeds:
    try:
        d = feedparser.parse(feed["feed_url"])
        status = bool(d.entries)  # True als er items zijn
    except Exception:
        status = False

    # Afleiden bestandsnaam (optioneel: robuuster maken via mapping)
    xml_filename = os.path.basename(feed["feed_url"])  # bv. 'rss.xml'
    feedbron_url = f"https://facilitairinfo.github.io/{xml_filename}"

    status_list.append({
        "website": feed["website"],
        "feedbron": feedbron_url,
        "status": status,
        "last_checked": datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
    })

# Opslaan naar JSON
with open(os.path.join(FEEDS_DIR, "feedstatus.json"), "w", encoding="utf-8") as f:
    json.dump(status_list, f, ensure_ascii=False, indent=2)

print("feedstatus.json bijgewerkt met feedbron-links.")
