import os

DOCS_DIR = os.path.join(os.path.dirname(__file__), "../docs")
index_path = os.path.join(DOCS_DIR, "index.html")

def get_feeds():
    return sorted([
        f for f in os.listdir(DOCS_DIR)
        if f.endswith(".xml") and not f.startswith("rss")
    ])

def build_index(feeds):
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html><html lang='nl'><head><meta charset='UTF-8'>")
        f.write("<title>Nieuwsfeeds overzicht</title></head><body>")
        f.write("<h1>📡 Overzicht van feeds</h1><ul>")
        for feed in feeds:
            name = feed.replace(".xml", "").replace("-", " ").title()
            f.write(f"<li><a href='{feed}'>{name}</a></li>")
        f.write("</ul><p><em>Automatisch gegenereerd</em></p></body></html>")

if __name__ == "__main__":
    feeds = get_feeds()
    build_index(feeds)
