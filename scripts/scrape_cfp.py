#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
from bs4 import BeautifulSoup
import yaml
from datetime import datetime
import dateparser

# Configuratie
CFP_URL = "https://cfp.nl/nieuws-en-cases/"
OUTPUT_FILE = os.path.join("configs", "sites-cfp-nieuws.yml")

def fetch_html(url: str) -> str:
    """Haalt HTML op van de opgegeven URL."""
    print(f"📡 Ophalen: {url}")
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.text

def parse_articles(html: str) -> list:
    """Parseert de HTML en geeft een lijst met artikel-data terug."""
    soup = BeautifulSoup(html, "html.parser")
    articles = []

    # Op CFP.nl staan de items in <article> met daarin <h3> en <time>
    for item in soup.select("article"):
        title_tag = item.select_one("h2, h3")
        link_tag = item.find("a", href=True)
        date_tag = item.find("time")

        if not title_tag or not link_tag:
            continue

        title = title_tag.get_text(strip=True)
        link = link_tag["href"]
        if link.startswith("/"):
            link = "https://cfp.nl" + link

        # Datum parsing (NL)
        if date_tag and date_tag.get_text(strip=True):
            parsed_date = dateparser.parse(
                date_tag.get_text(strip=True),
                languages=["nl"],
                settings={"TIMEZONE": "Europe/Amsterdam", "RETURN_AS_TIMEZONE_AWARE": True}
            )
        else:
            parsed_date = datetime.now()

        pub_date = parsed_date.strftime("%Y-%m-%dT%H:%M:%S%z")

        articles.append({
            "title": title,
            "link": link,
            "pubDate": pub_date
        })

    print(f"✅ {len(articles)} artikelen gevonden")
    return articles

def save_yaml(articles: list, file_path: str):
    """Slaat de lijst met artikelen op als YAML."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    data = {
        "site_name": "CFP Nieuws & Cases",
        "site_url": CFP_URL,
        "items": articles
    }
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)
    print(f"💾 YAML opgeslagen: {file_path}")

def scrape_cfp():
    """Main scraping proces."""
    try:
        html = fetch_html(CFP_URL)
        articles = parse_articles(html)
        if articles:
            save_yaml(articles, OUTPUT_FILE)
        else:
            print("⚠ Geen artikelen gevonden — YAML niet geüpdatet.")
    except Exception as e:
        print(f"❌ Fout tijdens scrapen: {e}")
        raise

if __name__ == "__main__":
    scrape_cfp()
