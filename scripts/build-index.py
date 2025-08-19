import os
from datetime import datetime

# Pad naar de docs-map (waar je feeds staan)
DOCS_DIR = os.path.join(os.path.dirname(__file__), "../docs")
INDEX_PATH = os.path.join(DOCS_DIR, "index.html")

def get_feeds():
    """Vind alle XML-feeds in de docs-map (behalve die beginnen met 'rss')."""
    return sorted([
        f for f in os.listdir(DOCS_DIR)
        if f.endswith(".xml") and not f.startswith("rss")
    ])

def build_index(feeds):
    """Genereer een index.html met een lijst van alle feeds."""
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html><html lang='nl'><head><meta charset='UTF-8'>")
        f.write("<meta name='viewport' content='width=device-width, initial-scale=1'>")
        f.write("<title>Nieuwsfeeds overzicht</title>")
        f.write("<style>")
        f.write("body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; background: #f8f9fa; color: #333; }")
        f.write("h1 { color: #0078D4; } ul { list-style-type: none; padding: 0; }")
        f.write("li { margin: 8px 0; font-size: 1.1em; }")
        f.write("a { text-decoration: none; color: #0078D4; } a:hover { text-decoration: underline; }")
        f.write("footer { margin-top: 40px; font-size: 0.9em; color: #555; }")
        f.write("</style></head><body>")
        f.write("<h1>📡 Overzicht van feeds</h1>")
        f.write("<ul>")
        for feed in feeds:
            name = feed.replace(".xml", "").replace("-", " ").title()
            f.write(f"<li><a href='{feed}'>{name}</a></li>")
        f.write("</ul>")
        f.write(f"<footer><p>Automatisch gegenereerd op {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p></footer>")
        f.write("</body></html>")

if __name__ == "__main__":
    feeds = get_feeds()
    if feeds:
        build_index(feeds)
        print(f"[OK] index.html bijgewerkt met {len(feeds)} feeds.")
    else:
        print("[INFO] Geen feeds gevonden om te tonen.")
