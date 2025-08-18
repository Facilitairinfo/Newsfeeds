import os, requests

SELF_BASE_URL = os.environ.get("SELF_BASE_URL", "https://example.github.io/mijn-feeds")
SOURCE = os.environ.get("PODCAST_SOURCE_FEED", "https://example.com/podcast.xml")
USER_AGENT = "FeedBuilderBot/1.0 (+https://github.com)"

def main():
    resp = requests.get(SOURCE, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    xml = resp.content
    os.makedirs("public", exist_ok=True)
    with open("public/podcast.xml", "wb") as f:
        f.write(xml)
    print(f"Podcast doorgezet vanaf: {SOURCE}")

if __name__ == "__main__":
    main()
