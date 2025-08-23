#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

def scrape_site(url, scraper_cfg):
    """
    Haalt de HTML op van `url`, selecteert de items met `item_selector`
    en geeft een lijst dicts terug met title, link, description, pubDate, category.
    """
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    items_data = []

    for item in soup.select(scraper_cfg['item_selector']):
        data = {}

        # Titel
        if 'title_selector' in scraper_cfg:
            title_el = item.select_one(scraper_cfg['title_selector'])
            if title_el:
                data['title'] = title_el.get_text(strip=True)

        # Link
        if 'link_selector' in scraper_cfg:
            link_selector = scraper_cfg['link_selector']
            if '@' in link_selector:
                css_sel, attr = link_selector.split('@', 1)
                link_el = item.select_one(css_sel)
                if link_el and link_el.has_attr(attr):
                    data['link'] = urljoin(url, link_el[attr])
            else:
                link_el = item.select_one(link_selector)
                if link_el:
                    data['link'] = urljoin(url, link_el.get('href', ''))

        # Datum
        if 'date_selector' in scraper_cfg:
            date_el = item.select_one(scraper_cfg['date_selector'])
            if date_el:
                raw_date = date_el.get_text(strip=True)
                fmt = scraper_cfg.get('date_format')
                try:
                    data['pubDate'] = datetime.strptime(raw_date, fmt)
                except Exception:
                    data['pubDate'] = None

        # Omschrijving
        if 'description_selector' in scraper_cfg:
            desc_el = item.select_one(scraper_cfg['description_selector'])
            if desc_el:
                data['description'] = desc_el.get_text(strip=True)

        # Categorie (optioneel)
        if 'category_selector' in scraper_cfg:
            cat_el = item.select_one(scraper_cfg['category_selector'])
            if cat_el:
                data['category'] = cat_el.get_text(strip=True)

        items_data.append(data)

    return items_data
