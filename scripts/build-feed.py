#!/usr/bin/env python3
import sys
import os
import yaml
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

def load_config(yml_path):
    with open(yml_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def fetch_html(url):
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.text

def parse_items(html, config):
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    for elem in soup.select(config['item_selector']):
        item = {}
        # Titel
        if 'title_selector' in config:
            t = elem.select_one(config['title_selector'])
            item['title'] = t.get_text(strip=True) if t else ''
        # Link
        if 'link_selector' in config:
            l = elem.select_one(config['link_selector'])
            if l and l.has_attr('href'):
                item['link'] = l['href']
        # Summary (optioneel)
        if 'summary_selector' in config:
            s = elem.select_one(config['summary_selector'])
            item['summary'] = s.get_text(strip=True) if s else ''
        # Datum
        if 'date_selector' in config:
            d = elem.select_one(config['date_selector'])
            if d:
                date_text = d.get(config.get('date_attr')) if config.get('date_attr') else d.get_text(strip=True)
                item['date'] = parse_date(date_text, config.get('date_format'))
        items.append(item)
    return items

def parse_date(date_str, fmt=None):
    if not date_str:
        return None
    try:
        if fmt:
            return datetime.strptime(date_str.strip(), fmt).isoformat()
        return date_str.strip()
    except Exception:
        return date_str.strip()

def write_json(items, output_path):
    import json
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

def write_xml(items, output_path):
    import xml.etree.ElementTree as ET
    feed = ET.Element("feed")
    for item in items:
        el = ET.SubElement(feed, "item")
        ET.SubElement(el, "title").text = item.get("title", "")
        ET.SubElement(el, "link").text = item.get("link", "")
        ET.SubElement(el, "date").text = item.get("date", "")
        if "summary" in item:
            ET.SubElement(el, "summary").text = item.get("summary", "")
    tree = ET.ElementTree(feed)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)

def main():
    if len(sys.argv) != 3:
        print("Gebruik: build-feed.py <config.yml> <output.xml|.json>")
        sys.exit(1)

    config_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    cfg = load_config(config_path)
    html = fetch_html(cfg['url'])
    items = parse_items(html, cfg)

    ext = os.path.splitext(output_path)[1].lower()
    if ext == ".xml":
        write_xml(items, output_path)
    elif ext == ".json":
        write_json(items, output_path)
    else:
        raise ValueError("Ongeldig outputformaat. Gebruik .xml of .json")

if __name__ == '__main__':
    main()
