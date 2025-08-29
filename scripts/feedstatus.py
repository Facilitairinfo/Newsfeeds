import json, os
from datetime import datetime

STATUS_PATH = "docs/feedstatus.json"

def load_status():
    if os.path.exists(STATUS_PATH):
        with open(STATUS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_status(data):
    with open(STATUS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def update_status(config, items, status="success"):
    data = load_status()
    feed_name = config['output'].split("/")[-1].replace(".xml", "")
    data[feed_name] = {
        "website": feed_name,
        "feedbron": f"https://facilitairinfo.github.io/Newsfeeds/{feed_name}.xml",
        "status": status,
        "item_count": len(items),
        "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    save_status(data)
