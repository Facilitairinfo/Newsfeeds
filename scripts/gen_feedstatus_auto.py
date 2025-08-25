import json
from pathlib import Path
from datetime import datetime
import requests

DOCS_DIR = Path(__file__).parent / "docs"
BASE_URL = "https://facilitairinfo.github.io/Newsfeeds/"

def check_feed(url):
    try:
        resp = requests.head(url, timeout=10)
        return resp.status_code == 200
    except Exception:
        return False

feeds_status = []

for xml_file in sorted(DOCS_DIR.glob("sites-*-nieuws.xml")):
    feed_url = f"{BASE_URL}{xml_file.name}"
    # Eventueel mapping van website-URL's via apart configbestand
    website_url = None  # ← hier kun je optioneel koppelen aan 'echte' website
    status = check_feed(feed_url)
    feeds_status.append({
        "website": website_url or "-",
        "feedbron": feed_url,
        "status": status,
        "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

with open(DOCS_DIR / "feedstatus.json", "w", encoding="utf-8") as f:
    json.dump(feeds_status, f, ensure_ascii=False, indent=2)

print(f"{len(feeds_status)} feeds gecontroleerd en feedstatus.json bijgewerkt.")
