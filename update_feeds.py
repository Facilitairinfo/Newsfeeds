import os
import json
import feedparser
from datetime import datetime
import pytz

# Map waarin de feedbestanden staan
FEEDS_DIR = "docs"

# Koppeling feedbestand → nieuwsbron-URL
# Voeg hier nieuwe feeds toe zodra je ze hebt
NEWS_SOURCE_URLS = {
    "sites-iss-nederland-nieuws.xml": "https://www.issworld.com/nl-nl/insights/insights/nl/nieuws-en-pers",
    "sites-nen-nieuws.xml": "https://www.nen.nl/nieuws",
    "sites-werkenvoornederland-nieuws.xml": "https://www.werkenvoornederland.nl/actueel",
    "sites-envalue-nieuws.xml": "https://www.envalue.nl/nieuws",
    "sites-cfp-nieuws.xml": "https://cfp.nl/nieuws",
    "sites-fmn-nieuws.xml": "https://fmn.nl/nieuws"
}

def process_feed(file_path):
    """Parset een feed-bestand en retourneert de relevante info."""
    parsed = feedparser.parse(file_path)

    # Website-naam uit de feed
    website_name = parsed.feed.get("title", os.path.splitext(os.path.basename(file_path))[0])

    # Publieke URL van de feed op GitHub Pages
    feed_filename = os.path.basename(file_path)
    feed_url = f"https://facilitairinfo.github.io/Newsfeeds/{feed_filename}"

    # Nieuwsbron-URL uit mapping (indien bekend)
    website_url = NEWS_SOURCE_URLS.get(feed_filename, "")

    # Status: True als er items zijn
    status = bool(parsed.entries)

    # Nederlandse tijdzone instellen
    tz_nl = pytz.timezone("Europe/Amsterdam")
    last_checked_nl = datetime.now(tz_nl).strftime("%Y-%m-%d %H:%M")

    return {
        "website_name": website_name,
        "website_url": website_url,
        "feedbron": feed_url,
        "status": status,
        "last_checked": last_checked_nl
    }

def main():
    feeds_status = []

    for filename in os.listdir(FEEDS_DIR):
        if filename.endswith(".xml"):
            file_path = os.path.join(FEEDS_DIR, filename)
            feeds_status.append(process_feed(file_path))

    # Wegschrijven naar feedstatus.json
    output_path = os.path.join(FEEDS_DIR, "feedstatus.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(feeds_status, f, ensure_ascii=False, indent=2)

    # HTML genereren
    html_path = os.path.join(FEEDS_DIR, "feedonderhoud.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write("<html><head><meta charset='UTF-8'><title>Feedonderhoud</title></head><body>\n")
        f.write("<h1>Feedonderhoud</h1>\n")
        f.write("<table border='1' cellspacing='0' cellpadding='5'>\n")
        f.write("<tr><th>Website</th><th>Feed‑bron</th><th>Status</th><th>Laatst gecheckt (Nederlandse tijd)</th></tr>\n")

        for feed in feeds_status:
            # Website als klikbare link
            if feed["website_url"]:
                website_html = f'<a href="{feed["website_url"]}" target="_blank" rel="noopener noreferrer">{feed["website_name"]}</a>'
            else:
                website_html = feed["website_name"]

            # Feedbron als klikbare link
            feed_html = f'<a href="{feed["feedbron"]}" target="_blank" rel="noopener noreferrer">XML</a>'

            status_html = "✅" if feed["status"] else "❌"

            f.write(f"<tr><td>{website_html}</td><td>{feed_html}</td><td>{status_html}</td><td>{feed['last_checked']}</td></tr>\n")

        f.write("</table>\n</body></html>")

    # Samenvatting in de logs
    totaal = len(feeds_status)
    werkend = sum(1 for f in feeds_status if f["status"])
    kapot = totaal - werkend

    print(f"{totaal} feeds verwerkt en feedstatus.json + feedonderhoud.html bijgewerkt.")
    print(f" ✔ {werkend} werkend")
    print(f" ✖ {kapot} niet‑werkend")

if __name__ == "__main__":
    main()
