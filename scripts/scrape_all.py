import os
import glob
import datetime
import requests
from dateutil import parser as dateparser
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import scrape_site  # nieuwe versie met run()

CONFIG_DIR = "configs"
OUTPUT_DIR = "docs"

# -------------------------------
# Werken voor Nederland scraper
# -------------------------------
def scrape_wvn_vacatures():
    API_URL = "https://api.cso20.net/v1/JobAPI/GetJobs"
    PARAMS_BASE = {
        "Type": "vacature",
        "Vakgebied": "CVG.09",
        "WerkDenkniveau": "CWD.08,CWD.04",
        "PageSize": 20,
        "Sortering": "PublicatieDatum_desc",
        "PublicatieDatumVanaf": (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    }
    MAX_ITEMS = 6
    MAX_PAGES = 3

    def fetch_jobs():
        jobs = []
        for page in range(1, MAX_PAGES + 1):
            params = PARAMS_BASE.copy()
            params["PageNumber"] = page
            try:
                resp = requests.get(API_URL, params=params, timeout=20)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                print(f"⚠ Fout bij ophalen pagina {page}: {e}")
                break
            if not data:
                break
            jobs.extend(data)
            if len(jobs) >= MAX_ITEMS:
                break
        return jobs

    def sort_and_limit(jobs):
        def parse_date(job):
            try:
                return dateparser.parse(job.get("PublicatieDatum"))
            except Exception:
                return datetime.datetime.min
        return sorted(jobs, key=parse_date, reverse=True)[:MAX_ITEMS]

    def jobs_to_rss(jobs):
        rss = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss, "channel")
        ET.SubElement(channel, "title").text = "Werken voor Nederland – Vacatures"
        ET.SubElement(channel, "link").text = "https://www.werkenvoornederland.nl/"
        ET.SubElement(channel, "description").text = "Vacatureoverzicht – Werken voor Nederland"
        for job in jobs:
            item = ET.SubElement(channel, "item")
            ET.SubElement(item, "title").text = job.get("Titel", "").strip()
            ET.SubElement(item, "link").text = job.get("Url", "").strip()
            ET.SubElement(item, "description").text = job.get("Organisatie", "").strip()
            ET.SubElement(item, "pubDate").text = job.get("PublicatieDatum", "").strip()
            ET.SubElement(item, "category").text = job.get("Standplaats", "").strip()
        return rss

    def save_xml(element, filename):
        tree = ET.ElementTree(element)
        ET.indent(tree, space="  ", level=0)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        tree.write(filename, encoding="UTF-8", xml_declaration=True)
        print(f"✅ WVN-feed opgeslagen in {filename}")

    jobs = fetch_jobs()
    if not jobs:
        print("❌ Geen vacatures gevonden voor WVN")
        return
    rss_xml = jobs_to_rss(sort_and_limit(jobs))
    save_xml(rss_xml, os.path.join(OUTPUT_DIR, "sites-werkenvoornederland-vacatures.xml"))

# -------------------------------
# ISS Nederland – Nieuws
# -------------------------------
def scrape_iss_nieuws():
    BASE_URL = "https://www.issworld.com"
    LIST_URL = "https://www.issworld.com/nl-nl/insights/insights/nl/nieuws-en-pers"
    MAX_ITEMS = 10

    def fetch_articles():
        try:
            resp = requests.get(LIST_URL, timeout=20)
            resp.raise_for_status()
        except Exception as e:
            print(f"⚠ Fout bij ophalen ISS nieuws: {e}")
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        arts = []
        for li in soup.select("ul.newsList_list__h45E5 > li"):
            title_el = li.select_one(".NewsItem_heading__O_Q6b")
            link_el = li.select_one(".NewsItem_link__orVEi a")
            teaser_el = li.select_one(".NewsItem_teaser__EuQDB")
            date_el = li.select_one("time")
            img_el = li.select_one(".NewsItem_image__oXWI1 img")
            title = title_el.get_text(strip=True) if title_el else None
            link = urljoin(BASE_URL, link_el["href"]) if link_el and link_el.has_attr("href") else None
            teaser = teaser_el.get_text(strip=True) if teaser_el else ""
            pub_date = date_el["datetime"] if date_el and date_el.has_attr("datetime") else None
            img_url = urljoin(BASE_URL, img_el["src"]) if img_el and img_el.has_attr("src") else None
            if title and link:
                arts.append({
                    "title": title, "link": link,
                    "description": teaser, "pubDate": pub_date,
                    "image": img_url
                })
        return arts

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
        print(f"✅ ISS-feed opgeslagen in {filename}")

    arts = fetch_articles()
    if not arts:
        print("❌ Geen nieuwsartikelen gevonden voor ISS")
        return
    rss_xml = build_rss(arts[:MAX_ITEMS])
    save_xml(rss_xml, os.path.join(OUTPUT_DIR, "sites-iss-nederland-nieuws.xml"))

# -------------------------------
# Generieke configs
# -------------------------------
def scrape_from_configs():
    configs = glob.glob(os.path.join(CONFIG_DIR, "*.yml"))
    for config_file in configs:
        if "sites-werkenvoornederland-vacatures" in config_file:
            continue
        if "sites-iss-nederland-nieuws" in config_file:
            continue
        scrape_site.run(pathlib.Path(config_file))

# -------------------------------
# Main
# -------------------------------
if __name__ == "__main__":
    scrape_from_configs()
    scrape_wvn_vacatures()
    scrape_iss_nieuws()
