import sys
from scraper import scrape, write_feed
import yaml

def main():
    if len(sys.argv) != 3 or sys.argv[1] != "--config":
        print("Gebruik: python run_scraper.py --config <pad-naar-config>")
        sys.exit(1)

    config_path = sys.argv[2]
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    print(f"🔍 Scraping: {config.get('id', 'onbekend')}")
    items = scrape(config)

    if not items:
        print("⚠️ Geen items gevonden, schrijf lege XML")
        write_feed([], config)
        return

    print(f"✅ {len(items)} items gevonden")
    write_feed(items, config)

if __name__ == "__main__":
    main()
