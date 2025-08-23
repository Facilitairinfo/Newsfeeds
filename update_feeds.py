import os
import json
import feedparser
from datetime import datetime

FEEDS_DIR = "docs"
BASE_URL = "https://facilitairinfo.github.io/Newsfeeds"

# Optioneel: mapping xml-bestand → website
# Als je geen mapping hebt, blijft website leeg of vullen we 'Onbekend'
website_mapping = {
    "voorbeeld1.xml": "https://voorbeeld1.nl",
    "voorbeeld2.xml": "https://voorbeeld2.nl",
    # Voeg hier je eigen mappings toe als je wil dat de 'website'-kolom exact klopt
}

status_list = []

# Loop door alle .xml bestanden in docs/
for file_name in os.listdir(FEEDS_DIR):
    if file_name.lower().endswith(".xml"):
        feed_path = os.path.join(FEEDS_DIR, file_name)
        feed_url = f"{BASE_URL}/{file_name}"
        
        try:
            parsed = feedparser.parse(feed_path)
            status = bool(parsed.entries)
        except Exception:
            status = False
        
        website = website_mapping.get(file_name, "Onbekend")
        
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
