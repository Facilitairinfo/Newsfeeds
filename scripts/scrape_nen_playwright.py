import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urljoin
import xml.etree.ElementTree as ET
from dateutil import parser as dateparser
import os
import sys

BASE_URL = "https://www.nen.nl/nieuws-overzicht"
OUTPUT_PATH = "docs/sites-nen-nieuws.xml"

async def scrape_nen():
    print("🧭 Start Playwright scrape voor NEN...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(BASE_URL, wait_until="networkidle")

        items = await page.query_selector_all("div.news-item")
        print(f"🔎 Aantal nieuwsitems gevonden: {len(items)}")

        if not items:
            print("❌ Geen nieuwsitems gevonden – selectors of site controleren!")
            await browser.close()
            sys.exit(1)

        rss = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss, "channel")
        ET.SubElement(channel, "title").text = "NEN – Nieuws en ontwikkelingen"
        ET.SubElement(channel, "link").text = BASE_URL
        ET.SubElement(channel, "description").text = "Automatisch gegenereerde feed van NEN.nl"

        for el in items:
            title = await el.query_selector("h2.news-title")
            link = await el.query_selector("a")
            teaser = await el.query_selector("div.news-intro")
            date = await el.query_selector("span.news-date")

            title_text = await title.inner_text() if title else ""
            link_href = await link.get_attribute("href") if link else ""
            teaser_text = await teaser.inner_text() if teaser else ""
            date_text = await date.inner_text() if date else ""

            full_link = urljoin(BASE_URL, link_href)
            pub_date = dateparser.parse(date_text).strftime(
                "%a, %d %b %Y 00:00:00 +0100"
            ) if date_text else ""

            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = title_text
            ET.SubElement(item, "link").text = full_link
            ET.SubElement(item, "description").text = teaser_text
            ET.SubElement(item, "pubDate").text = pub_date

        await browser.close()

        os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
        tree = ET.ElementTree(rss)
        ET.indent(tree, space="  ", level=0)
        tree.write(OUTPUT_PATH, encoding="UTF-8", xml_declaration=True)

        print(f"📂 Bestand geschreven naar: {OUTPUT_PATH}")
        print("✅ Bestaat bestand na schrijven?", os.path.exists(OUTPUT_PATH))

if __name__ == "__main__":
    asyncio.run(scrape_nen())
