import os, requests, yaml

USER_AGENT = "FeedBuilderBot/1.0 (+https://github.com)"

def main():
    with open("sites-podcast.yml", "r") as f:
        config = yaml.safe_load(f)

    site = config["sites"][0]  # Neem de eerste podcastfeed
    url = site["url"]

    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    xml = resp.content

    os.makedirs("public", exist_ok=True)
    with open("public/podcast.xml", "wb") as f:
        f.write(xml)

    print(f"Podcast doorgezet vanaf: {url}")

if __name__ == "__main__":
    main()
