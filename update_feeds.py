import os
import json
import feedparser
from datetime import datetime

# Map naar de 'docs' map waar feedstatus.json en je XML-bestanden staan
FEEDS_DIR = "docs"

# Vul hieronder je volledige feedlijst in.
# Elke entry bevat: website, feed_url en de bijbehorende xml-bestandsnaam in /docs
feeds = [
    {
        "website": "https://voorbeeld1.nl",
        "feed_url": "https://voorbeeld1.nl/rss.xml",
        "xml_file": "voorbeeld1.xml"
    },
    {
        "website": "https://voorbeeld2.nl",
        "feed_url": "https://voorbeeld2.nl/feed",
        "xml_file": "voorbeeld2.xml"
    },
    # Voeg hier AL je feeds toe met de juiste xml-bestandsnaam
]

status_list = []

for feed in feeds:
    try:
        parsed = feedparser.parse(feed["feed_url"])
        status = bool(parsed.entries)
    except Exception:
        status = False

    # Bouw de feedbron-link op basis van de xml-bestandsnaam
    feedbron_url = f"https://facilitairinfo.github.io/{feed['xml_file']}"

    status_list.append({
        "website": feed["website"],
        "feedbron": feedbron_url,
        "status": status,
        "last_checked": datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    })

# Zorg dat de docs-map bestaat
os.makedirs(FEEDS_DIR, exist_ok=True)

# Schrijf feedstatus.json weg met nette indeling
with open(os.path.join(FEEDS_DIR, "feedstatus.json"), "w", encoding="utf-8") as f:
    json.dump(status_list, f, ensure_ascii=False, indent=2)

print("feedstatus.json bijgewerkt met feedbron-links via mapping.")
