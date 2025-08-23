import os
import yaml
from datetime import datetime, timezone, timedelta
from feedgen.feed import FeedGenerator

CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'configs')
DOCS_DIR = os.path.join(os.path.dirname(__file__), '..', 'docs')

# In Nederland: augustus = CEST (UTC+2)
CEST = timezone(timedelta(hours=2))

def build_feed_from_config(cfg_path):
    with open(cfg_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    fg = FeedGenerator()
    fg.title(config.get('title', 'Onbekende titel'))

    feed_link = config.get('link') or "https://cfp.nl/nieuws-en-cases/"
    feed_desc = config.get('description') or "Laatste nieuws en cases van CFP Green Buildings"
    fg.link(href=feed_link, rel='alternate')
    fg.description(feed_desc)

    # Pak maximaal de laatste 6 items
    items = config.get('items', [])[:6]

    for it in items:
        fe = fg.add_entry()
        fe.title(it.get('title', ''))
        fe.link(href=it.get('link', ''))
        fe.description(it.get('description', ''))

        pub_date = it.get('pubDate')

        # Strings zoals "21-08-2025" of ISO-format naar datetime
        if isinstance(pub_date, str):
            try:
                pub_date = datetime.strptime(pub_date, "%d-%m-%Y")
            except ValueError:
                try:
                    pub_date = datetime.fromisoformat(pub_date)
                except ValueError:
                    pub_date = None

        # Voeg tijdzone toe indien nodig
        if hasattr(pub_date, 'tzinfo') and pub_date and pub_date.tzinfo is None:
            pub_date = pub_date.replace(tzinfo=CEST)

        if pub_date:
            fe.pubDate(pub_date)

    feed_filename = os.path.splitext(os.path.basename(cfg_path))[0] + '.xml'
    fg.rss_file(os.path.join(DOCS_DIR, feed_filename), pretty=True)
    print(f"✅ Feed gebouwd voor: {cfg_path}")

def main():
    cfg_files = [os.path.join(CONFIG_DIR, "sites-cfp-nieuws.yml")]
    print(f"▶ Gevonden configs: {[os.path.basename(c) for c in cfg_files]}")
    for cfg_path in cfg_files:
        if os.path.exists(cfg_path):
            print(f"=== 🛠 Verwerk {os.path.basename(cfg_path)} ===")
            build_feed_from_config(cfg_path)
        else:
            print(f"⚠ Configbestand niet gevonden: {cfg_path}")

if __name__ == "__main__":
    os.makedirs(DOCS_DIR, exist_ok=True)
    main()
