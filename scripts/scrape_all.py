import os
import glob
import datetime
import requests
from dateutil import parser as dateparser
import xml.etree.ElementTree as ET

# Pad naar je configs en scripts
CONFIG_DIR = "configs"
OUTPUT_DIR = "docs"

# -------------------------------
# Speciale scraper voor Werken voor Nederland
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
        jobs_sorted = sorted(jobs, key=parse_date, reverse=True)
        return jobs_sorted[:MAX_ITEMS]

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

    all_jobs = fetch_jobs()
    if not all_jobs:
        print("❌ Geen vacatures gevonden voor Werken voor Nederland")
        return

    jobs_final = sort_and_limit(all_jobs)
    rss_xml = jobs_to_rss(jobs_final)
    save_xml(rss_xml, os.path.join(OUTPUT_DIR, "sites-werkenvoornederland-vacatures.xml"))

# -------------------------------
# Bestaande scraping logica voor andere configs
# -------------------------------
def scrape_from_configs():
    import scrape_site  # jouw bestaande generieke scraper-module
    configs = glob.glob(os.path.join(CONFIG_DIR, "*.yml"))
    for config_file in configs:
        # Sla de WvN-config over; die doen we apart
        if "sites-werkenvoornederland-vacatures" in config_file:
            continue
        scrape_site.run(config_file)

# -------------------------------
# Main
# -------------------------------
if __name__ == "__main__":
    scrape_from_configs()
    scrape_wvn_vacatures()
