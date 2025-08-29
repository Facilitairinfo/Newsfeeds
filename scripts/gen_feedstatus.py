import json
from datetime import datetime

STATUS_PATH = "docs/feedstatus.json"
HTML_PATH = "docs/feedonderhoud.html"

def load_status():
    with open(STATUS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_html(data):
    rows = []
    for feed in sorted(data.values(), key=lambda x: x["website"]):
        status_color = "✅" if feed["status"] == "success" else "❌"
        rows.append(f"""
        <tr>
            <td>{feed['website']}</td>
            <td><a href="{feed['feedbron']}">XML</a></td>
            <td>{status_color}</td>
            <td>{feed['last_checked']}</td>
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
