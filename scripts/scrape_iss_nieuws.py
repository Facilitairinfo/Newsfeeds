import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

BASE_URL = "https://www.issworld.com"
LIST_URL = "https://www.issworld.com/nl-nl/insights/insights/nl/nieuws-en-pers"
OUTPUT_FILE = "docs/sites-iss-nederland-nieuws.xml"
MAX_ITEMS = 10

def fetch_articles():
    resp = requests.get(LIST_URL, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    articles = []
    for li in soup.select("ul.newsList_list__h45E5 > li"):
        title_el = li.select_one(".NewsItem_heading__O_Q6b")
        link_el = li.select_one(".NewsItem_link__orVEi a")
        teaser_el = li.select_one(".NewsItem_teaser__EuQDB")
        date_attr = li.select_one("time")
        img_el = li.select_one(".NewsItem_image__oXWI1 img")

        title = title_el.get_text(strip=True) if title_el else None
        link = urljoin(BASE_URL, link_el["href"]) if link_el else None
        teaser = teaser_el.get_text(strip=True) if teaser_el else ""
        pub_date = date_attr["datetime"] if date_attr and date_attr.has_attr("datetime") else None
        img_url = urljoin(BASE_URL, img_el["src"]) if img_el and img_el.has_attr("src") else None

        if title and link:
            articles.append({
                "title": title,
                "link": link,
                "description": teaser,
                "pubDate": pub_date,
                "image": img_url
            })
    return articles

def build_rss(items):
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "ISS Nederland – Nieuws en pers"
    ET.SubElement(channel, "link").text = LIST_URL
    ET.SubElement(channel, "description").text = "Laatste nieuws van ISS Nederland"

    for art in items:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = art["title"]
        ET.SubElement(item, "link").text = art["link"]
        ET.SubElement(item, "description").text = art["description"]
        if art["pubDate"]:
            ET.SubElement(item, "pubDate").text = art["pubDate"]
        if art["image"]:
            ET.SubElement(item, "enclosure", url=art["image"], type="image/jpeg")
    return rss

def save_xml(element, filename):
    tree = ET.ElementTree(element)
    ET.indent(tree, space="  ", level=0)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    tree.write(filename, encoding="UTF-8", xml_declaration=True)

if __name__ == "__main__":
    feed_items = fetch_articles()[:MAX_ITEMS]
    rss_xml = build_rss(feed_items)
    save_xml(rss_xml, OUTPUT_FILE)
    print(f"✅ Feed opgeslagen: {OUTPUT_FILE}")
