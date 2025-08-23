#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
from bs4 import BeautifulSoup
import yaml
from datetime import datetime
import dateparser

# Configuratie
BASE_URL = "https://cfp.nl"
START_URL = f"{BASE_URL}/nieuws-en-cases/"
OUTPUT_FILE = os.path.join("configs", "sites-cfp-nieuws.yml")

def fetch_html(url: str) -> str:
    print(f"📡 Ophalen: {url}")
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.text

def parse_articles_from_page(html: str) -> list:
    """Parseert 1 HTML-pagina en geeft lijst met artikel-data."""
    soup = BeautifulSoup(html, "html.parser")
    articles = []

    for item in soup.select("article"):
        title_tag = item.select_one("h2, h3")
        link_tag = item.find("a", href=True)
        date_tag = item.find("time")

        if not title_tag or not link_tag:
            continue

        title = title_tag.get_text(strip=True)
        link = link_tag["href"]
        if link.startswith("/"):
            link = BASE_URL + link

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

    return articles

def find_next_page(html: str) -> str | None:
    """Zoekt link naar de volgende pagina, of None."""
    soup = BeautifulSoup(html, "html.parser")
    next_link = soup.find("a", attrs={"aria-label": "Volgende"})
    if next_link and next_link.get("href"):
        href = next_link["href"]
        return href if href.startswith("http") else BASE_URL + href
    return None

def scrape_all_pages(start_url: str) -> list:
    """Loopt door alle pagina's en verzamelt artikelen."""
    all_articles = []
    url = start_url
    while url:
        html = fetch_html(url)
        page_articles = parse_articles_from_page(html)
        print(f"  ↳ {len(page_articles)} artikelen op deze pagina")
        all_articles.extend(page_articles)
        url = find_next_page(html)
    return all_articles

def save_yaml(articles: list, file_path: str):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    data = {
        "site_name": "CFP Nieuws & Cases",
        "site_url": START_URL,
        "items": articles
    }
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)
    print(f"💾 YAML opgeslagen: {file_path}")

def scrape_cfp():
    try:
        articles = scrape_all_pages(START_URL)
        if articles:
            save_yaml(articles, OUTPUT_FILE)
            print(f"🎉 Totaal {len(articles)} artikelen opgeslagen")
        else:
            print("⚠ Geen artikelen gevonden — YAML niet geüpdatet.")
    except Exception as e:
        print(f"❌ Fout tijdens scrapen: {e}")
        raise

if __name__ == "__main__":
    scrape_cfp()
