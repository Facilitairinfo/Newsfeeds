import requests
from bs4 import BeautifulSoup
import yaml
from datetime import datetime, timezone, timedelta

CEST = timezone(timedelta(hours=2))
BASE_URL = "https://cfp.nl/nieuws-en-cases/"

def scrape_cfp():
    r = requests.get(BASE_URL)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    items = []
    for article in soup.select("div.blog_article"):
        a_tag = article.select_one("a.blog_article__content_holder")
        if not a_tag:
            continue

        title_tag = article.select_one("h6.blog_article__content_holder__title")
        desc_tag = article.select_one("div.blog_article__content_holder__content p")
        date_tag = article.select_one("div.blog_article__content_holder__meta_data__date")

        title = title_tag.get_text(strip=True) if title_tag else ""
        link = a_tag.get("href")
        description = desc_tag.get_text(strip=True) if desc_tag else ""
        date_str = date_tag.get_text(strip=True) if date_tag else ""

        # Parse datum "21-08-2025" naar datetime + CEST
        pub_date = None
        try:
            pub_date = datetime.strptime(date_str, "%d-%m-%Y").replace(tzinfo=CEST)
        except Exception as e:
            print(f"⚠ Kan datum niet parsen: {date_str} ({e})")

        items.append({
            "title": title,
            "link": link,
            "description": description,
            "pubDate": pub_date
        })

    feed_data = {
        "title": "CFP Nieuws",
        "link": BASE_URL,
        "description": "Laatste nieuws en cases van CFP Green Buildings",
        "items": items
    }

    with open(os.path.join("configs", "sites-cfp-nieuws.yml"), "w", encoding="utf-8") as f:
        yaml.dump(feed_data, f, allow_unicode=True)

    print(f"✅ {len(items)} items opgeslagen in sites-cfp-nieuws.yml")

if __name__ == "__main__":
    scrape_cfp()
