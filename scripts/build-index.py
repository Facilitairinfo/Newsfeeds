import os
import yaml
from datetime import datetime

# Map waar de XML-feeds en YAML-configuraties staan
DOCS_DIR = os.path.join(os.path.dirname(__file__), "../docs")
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
INDEX_PATH = os.path.join(DOCS_DIR, "index.html")
FAVICON_URL = "https://upload.wikimedia.org/wikipedia/commons/4/4a/Feed-icon.svg"

def get_feeds():
    """Vind alle XML-feeds in docs-map (behalve die beginnen met 'rss')."""
    return sorted([
        f for f in os.listdir(DOCS_DIR)
        if f.endswith(".xml") and not f.startswith("rss")
    ])

def get_feed_description(feed_name):
    """
    Zoek in het corresponderende sites-*.yml bestand of er een beschrijving is.
    Gebruikt de 'name' uit de YAML of maakt een generieke tekst.
    """
    yaml_name = f"sites-{feed_name}.yml"
    yaml_path = os.path.join(ROOT_DIR, yaml_name)
    if os.path.exists(yaml_path):
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                sites = yaml.safe_load(f)
            if sites and isinstance(sites, list):
                bronnen = [site.get("name") for site in sites if "name" in site]
                bronnen_lijst = ", ".join(bronnen)
                return f"Bronnen: {bronnen_lijst}"
        except Exception as e:
            return f"Beschrijving kon niet geladen worden ({e})"
    return "Automatisch gegenereerde feed."

def build_index(feeds):
    """Genereer index.html met favicon, intro en beschrijvingen."""
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        # Head
        f.write("<!DOCTYPE html><html lang='nl'><head><meta charset='UTF-8'>")
        f.write("<meta name='viewport' content='width=device-width, initial-scale=1'>")
        f.write("<title>Nieuwsfeeds overzicht</title>")
        f.write(f"<link rel='icon' type='image/svg+xml' href='{FAVICON_URL}'>")
        f.write("<style>")
        f.write("body { font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; background: #f8f9fa; color: #333; }")
        f.write("h1 { color: #0078D4; display: flex; align-items: center; gap: 8px; }")
        f.write("ul { list-style-type: none; padding: 0; }")
        f.write("li { margin: 12px 0; font-size: 1.05em; background: #fff; padding: 10px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }")
        f.write("a { font-weight: bold; text-decoration: none; color: #0078D4; } a:hover { text-decoration: underline; }")
        f.write("p.desc { margin: 4px 0 0; font-size: 0.9em; color: #555; }")
        f.write("footer { margin-top: 40px; font-size: 0.85em; color: #555; }")
        f.write("</style></head><body>")
        
        # Body
        f.write("<h1>📡 Overzicht van feeds</h1>")
        f.write("<p>Welkom bij het <strong>Facilitair Netwerk</strong> nieuwsfeed‑overzicht. "
                "Hier vind je de meest recente nieuws‑, event‑ en podcastfeeds, automatisch bijgewerkt.</p>")
        f.write("<ul>")
        for feed in feeds:
            name_clean = feed.replace(".xml", "").replace("-", " ").title()
            desc = get_feed_description(feed.replace(".xml", ""))
            f.write(f"<li><a href='{feed}'>{name_clean}</a>")
            if desc:
                f.write(f"<p class='desc'>{desc}</p>")
            f.write("</li>")
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
