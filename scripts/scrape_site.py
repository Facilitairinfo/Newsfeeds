import argparse
import pathlib
import sys

def scrape(config_path: pathlib.Path):
    # TODO: Hier komt je huidige scraping logica — dit kan exact uit scrape_cfp.py worden overgenomen
    # Bijvoorbeeld:
    # 1. Config inlezen (YAML)
    # 2. Data ophalen / scrapen
    # 3. RSS-feed genereren in docs/sites-<confignaam>.xml
    print(f"Scraping met config: {config_path}")
    # ... implementatie ...

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape één site config")
    parser.add_argument("--config", required=True, help="Pad naar .yml-config")
    args = parser.parse_args()

    config_file = pathlib.Path(args.config)
    if not config_file.exists():
        print(f"Config niet gevonden: {config_file}")
        sys.exit(1)

    scrape(config_file)
