import os
import json
import feedparser
from datetime import datetime
import pytz

FEEDS_DIR = "docs"
MIN_ITEMS_REQUIRED = 3

# Alleen uitzonderingen of correcties hier opnemen
NEWS_SOURCE_URLS = {
    "sites-iss-nederland-nieuws.xml": "https://www.issworld.com/nl-nl/insights/insights/nl/nieuws-en-pers",
    # voorbeeld: "bestandsnaam.xml": "https://andere-url.nl"
}

def process_feed(file_path):
    parsed = feedparser.parse(file_path)
    feed_filename = os.path.basename(file_path)

    website_name = parsed.feed.get("title", os.path.splitext(feed_filename)[0])
    website_url = parsed.feed.get("link", "").strip()
    if not website_url:
        website_url = NEWS_SOURCE_URLS.get(feed_filename, "")

    feed_url = f"https://facilitairinfo.github.io/Newsfeeds/{feed_filename}"
    item_count = len(parsed.entries)
    status = item_count >= MIN_ITEMS_REQUIRED

    tz_nl = pytz.timezone("Europe/Amsterdam")
    last_checked_nl = datetime.now(tz_nl).strftime("%Y-%m-%d %H:%M")

    return {
        "website_name": website_name,
        "website_url": website_url,
        "feedbron": feed_url,
        "status": status,
        "last_checked": last_checked_nl,
        "item_count": item_count
    }

def main():
    feeds_status = []

    for filename in os.listdir(FEEDS_DIR):
        if filename.endswith(".xml"):
            file_path = os.path.join(FEEDS_DIR, filename)
            feeds_status.append(process_feed(file_path))

    # feedstatus.json
    with open(os.path.join(FEEDS_DIR, "feedstatus.json"), "w", encoding="utf-8") as f:
        json.dump(feeds_status, f, ensure_ascii=False, indent=2)

    # feedonderhoud.html
    html_path = os.path.join(FEEDS_DIR, "feedonderhoud.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write("<html><head><meta charset='UTF-8'><title>Feedstatus</title></head><body>\n")
        f.write("<h1>Feedstatus overzicht</h1>\n")
        f.write("<table border='1' cellspacing='0' cellpadding='5'>\n")
        f.write("<tr><th>Website</th><th>Feedbron</th><th>Laatst gecheckt (NL-tijd)</th><th>Aantal items</th><th>Status</th></tr>\n")

        for feed in feeds_status:
            website_html = f'<a href="{feed["website_url"]}" target="_blank" rel="noopener noreferrer">{feed["website_name"]}</a>' if feed["website_url"] else feed["website_name"]
            feed_html = f'<a href="{feed["feedbron"]}" target="_blank" rel="noopener noreferrer">{os.path.basename(feed["feedbron"])}</a>'
            status_html = "✅" if feed["status"] else "❌"

            f.write(f"<tr><td>{website_html}</td><td>{feed_html}</td><td>{feed[\"last_checked\"]}</td><td>{feed[\"item_count\"]}</td><td>{status_html}</td></tr>\n")

        f.write("</table>\n</body></html>")

    print(f"{len(feeds_status)} feeds verwerkt en feedstatus.json + feedonderhoud.html bijgewerkt.")

if __name__ == "__main__":
    main()
