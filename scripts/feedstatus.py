import json
import os
from datetime import datetime

STATUS_PATH = "docs/feedstatus.json"

def load_status():
    try:
        with open(STATUS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return {}
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_status(data):
    os.makedirs(os.path.dirname(STATUS_PATH), exist_ok=True)
    with open(STATUS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def update_status(config, items, status="success"):
    data = load_status()
    feed_name = config.get("output", "").split("/")[-1].replace(".xml", "") or "onbekende_feed"

    data[feed_name] = {
        "website": feed_name,
        "feedbron": f"https://facilitairinfo.github.io/Newsfeeds/{feed_name}.xml",
        "status": status,
        "item_count": len(items),
        "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    save_status(data)
