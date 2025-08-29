import argparse
import pathlib
import sys
import os
import yaml
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import xml.etree.ElementTree as ET
from dateutil import parser as dateparser

def run(config_path: pathlib.Path):
    """Draait de generieke HTML-config scraper voor één .yml-configbestand."""
    if not config_path.exists():
        print(f"❌ Config niet gevonden: {config_path}")
        return None, []

    # Config laden
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    site_cfg = cfg.get("site", {})
    base_url = site_cfg.get("bron", {}).get("url", "").strip()
    selectors = site_cfg.get("selectors", {})
    mapping = site_cfg.get("mapping", {})
    opties = site_cfg.get("opties", {})

    print(f"🔍 Start scrape: {site_cfg.get('titel', site_cfg.get('naam', 'Onbekende site'))}")

    # HTML ophalen
    try:
        resp = requests.get(base_url, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print(f"⚠ Fout bij ophalen {base_url}: {e}")
        return None, []

    soup = BeautifulSoup(resp.text, "html.parser")
    items_sel = selectors.get("items")
    if not items_sel:
        print(f"❌ Geen 'items' selector in config {config_path}")
        return None, []

    elements = soup.select(items_sel)
    feed_items = []

    for el in elements:
        item_data = {}
        for field, selector in selectors.items():
            if field == "items":
                continue
            if "::attr(" in selector:
                sel_el = el.select_one(selector.split("::attr")[0])
                if sel_el:
                    attr_name = selector.split("::attr(")[1].rstrip(")")
                    item_data[field] = sel_el.get(attr_name, "").strip()
                else:
                    item_data[field] = ""
            else:
                sel_el = el.select_one(selector)
                item_data[field] = sel_el.get_text(strip=True) if sel_el else ""

        # Mapping toepassen
        mapped = {}
        for dest, src in mapping.items():
            mapped[dest] = item_data.get(src, "")

        # Absolute links
        if opties.get("absolute_links") and mapped.get("link", "").startswith("/"):
            mapped["link"] = urljoin(base_url, mapped["link"])

        feed_items.append(mapped)

    # RSS bouwen
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = site_cfg.get("titel", site_cfg.get("naam", ""))
    ET.SubElement(channel, "link").text = base_url
    ET.SubElement(channel, "description").text = f"Feed voor {site_cfg.get('titel', '')}"

    for it in feed_items:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = it.get("titel", "")
        ET.SubElement(item, "link").text = it.get("link", "")
        if it.get("beschrijving"):
            ET.SubElement(item, "description").text = it["beschrijving"]
        if it.get("publicatie_datum"):
            try:
                dt_parsed = dateparser.parse(it["publicatie_datum"])
                ET.SubElement(item, "pubDate").text = dt_parsed.strftime(
                    "%a, %d %b %Y %H:%M:%S %z"
                )
            except Exception:
                ET.SubElement(item, "pubDate").text = it["publicatie_datum"]

    # Outputpad bepalen
    output_path = opties.get("output") or os.path.join(
        "docs", f"{site_cfg.get('naam','output')}.xml"
    )
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    tree = ET.ElementTree(rss)
    ET.indent(tree, space=" ", level=0)
    tree.write(output_path, encoding=opties.get("encoding", "UTF-8"), xml_declaration=True)
    print(f"✅ Feed opgeslagen: {output_path}")

    # Config dict voor update_status
    config_for_status = {
        "website": site_cfg.get("titel", site_cfg.get("naam", "")),
        "feedbron": os.path.basename(output_path)
    }

    return config_for_status, feed_items

def scrape(config_path: pathlib.Path):
    """Alias naar run(), zodat oude aanroepen blijven werken."""
    return run(config_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape één site config")
    parser.add_argument("--config", required=True, help="Pad naar .yml-config")
    args = parser.parse_args()
    config_file = pathlib.Path(args.config)
    run(config_file)
