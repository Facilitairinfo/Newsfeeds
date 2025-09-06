import os
import json
from datetime import datetime
import pytz
from jinja2 import Template

STATUS_PATH = "docs/feedstatus.json"
HTML_PATH = "docs/feedonderhoud.html"
MIN_ITEMS_REQUIRED = 3

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

def save_html(data):
    os.makedirs(os.path.dirname(HTML_PATH), exist_ok=True)
    html_template = """
    <html><head><meta charset="utf-8"><title>Feedstatus</title></head>
    <body>
    <h1>Feedstatus overzicht</h1>
    <table border="1" cellspacing="0" cellpadding="4">
    <tr><th>Website</th><th>Feedbron</th><th>Laatst gecheckt (NL-tijd)</th><th>Aantal items</th><th>Status</th></tr>
    {% for feed, info in data.items() %}
    <tr>
      <td><a href="{{ info.website_url }}" target="_blank" rel="noopener noreferrer">{{ info.website_name }}</a></td>
      <td><a href="{{ info.feedbron }}" target="_blank" rel="noopener noreferrer">{{ info.feedbron }}</a></td>
      <td>{{ info.last_checked }}</td>
      <td>{{ info.item_count }}</td>
      <td>{{ '✅' if info.status else '❌' }}</td>
    </tr>
    {% endfor %}
    </table>
    </body></html>
    """
    tmpl = Template(html_template)
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(tmpl.render(data=data))

def update_status(config, items, status="success"):
    data = load_status()

    feed_name = os.path.basename(config.get("output", "")) \
        .replace(".xml", "") or "onbekende_feed"

    website_name = config.get("website", feed_name)
    website_url = config.get("site_url", config.get("website_url", ""))
    feedbron = config.get("feedbron") or f"https://facilitairinfo.github.io/Newsfeeds/{feed_name}.xml"

    tz_nl = pytz.timezone("Europe/Amsterdam")
    last_checked = datetime.now(tz_nl).strftime("%Y-%m-%d %H:%M")

    item_count = len(items)
    is_success = status == "success" and item_count >= MIN_ITEMS_REQUIRED

    data[feed_name] = {
        "website_name": website_name,
        "website_url": website_url,
        "feedbron": feedbron,
        "item_count": item_count,
        "last_checked": last_checked,
        "status": is_success
    }

    save_status(data)
    save_html(data)
    print(f"📊 Status bijgewerkt voor {website_name}: {item_count} items, status = {'✅' if is_success else '❌'}")
