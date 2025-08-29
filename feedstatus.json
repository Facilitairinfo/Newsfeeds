import json
import os
from datetime import datetime

STATUS_FILE = "docs/feedstatus.json"

def load_status():
    """Laad bestaande status of retourneer lege dict als fallback."""
    try:
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                # Bestand is geen dict maar lijst of iets anders
                return {}
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_status(data):
    """Sla status op als JSON."""
    os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def update_status(config, items):
    """
    Update de feedstatus.json met de nieuwste items voor een feed.
    config: dict met minstens 'feed_name'
    items: lijst met item-data (mag leeg zijn)
    """
    feed_name = config.get("feed_name") or config.get("output") or "onbekende_feed"

    # Altijd een dict inladen
    data = load_status()

    # Feedstatus bijwerken
    data[feed_name] = {
        "laatste_update": datetime.utcnow().isoformat() + "Z",
        "aantal_items": len(items),
        "items": items
    }

    save_status(data)

if __name__ == "__main__":
    # Voor testdoeleinden
    cfg = {"feed_name": "test-feed"}
    update_status(cfg, [{"titel": "Voorbeeld", "link": "https://example.com"}])
    print("Status bijgewerkt:", load_status())
