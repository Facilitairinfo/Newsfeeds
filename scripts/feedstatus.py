import json
import os
from datetime import datetime
from jinja2 import Template

STATUS_PATH = "docs/feedstatus.json"
HTML_PATH = "docs/feedonderhoud.html"

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
      <tr><th>Website</th><th>Feedbron</th><th>Laatste update</th><th>Aantal items</th><th>Status</th></tr>
      {% for feed, info in data.items() %}
      <tr>
        <td>{{ info.website }}</td>
        <td><a href="{{ info.feedbron }}">{{ info.feedbron }}</a></td>
        <td>{{ info.last_checked }}</td>
        <td>{{ info.item_count }}</td>
        <td>{{ info.status }}</td>
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

    website = config.get("website", feed_name)
    feedbron = config.get("feedbron") or f"https://facilitairinfo.github.io/Newsfeeds/{feed_name}.xml"

    data[feed_name] = {
        "website": website,
        "feedbron": feedbron,
        "status": status,
        "item_count": len(items),
        "last_checked": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    save_status(data)
    save_html(data)
