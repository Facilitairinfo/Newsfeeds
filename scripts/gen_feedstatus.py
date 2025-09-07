import json
from datetime import datetime

STATUS_PATH = "docs/feedstatus.json"
HTML_PATH = "docs/feedonderhoud.html"

def load_status():
    with open(STATUS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_html(data):
    rows = []

    # Log ontbrekende velden
    for feed_id, feed in data.items():
        missing = [k for k in ["website", "feedbron", "status", "last_checked"] if k not in feed]
        if missing:
            print(f"⚠️ Feed '{feed_id}' mist velden: {', '.join(missing)}")

    # Sorteer op website_name > website > fallback
    for feed in sorted(data.values(), key=lambda x: x.get("website_name") or x.get("website") or ""):
        status = feed.get("status", "unknown")
        status_color = "✅" if status == "success" else "❌"
        website = feed.get("website", "onbekend")
        feedbron = feed.get("feedbron", "#")
        last_checked = feed.get("last_checked", "–")
        bg = "lightgreen" if status == "success" else "#ffe6e6"

        rows.append(f"""
        <tr style="background-color:{bg}">
          <td>{website}</td>
          <td><a href="{feedbron}">XML</a></td>
          <td>{status_color}</td>
          <td>{last_checked}</td>
        </tr>
        """)

    html = f"""<!DOCTYPE html>
    <html lang="nl">
    <head>
      <meta charset="UTF-8">
      <title>Feedonderhoud</title>
      <style>
        body {{ font-family: Arial; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
      </style>
    </head>
    <body>
      <h1>Feedonderhoud</h1>
      <table>
        <tr>
          <th>Website</th>
          <th>Feed‑bron</th>
          <th>Status</th>
          <th>Laatst gecheckt</th>
        </tr>
        {''.join(rows)}
      </table>
    </body>
    </html>
    """

    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    data = load_status()
    generate_html(data)
