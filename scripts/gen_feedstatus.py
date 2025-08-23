#!/usr/bin/env python3
import json
import yaml
import requests
import datetime
from pathlib import Path

CONFIG_DIR = Path("configs")
OUTFILE = Path("feedstatus.json")
TIMEOUT = 8  # seconden

def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def guess_feed_url(cfg_path: Path, cfg: dict) -> str:
    site = cfg.get("site", {})
    opties = site.get("opties", {})
    feed_section = cfg.get("feed", {})

    if opties.get("output"):
        rel = Path(opties["output"])
        return f"https://facilitairinfo.github.io/Newsfeeds/{rel.name}"

    if isinstance(feed_section, dict):
        for key in ("id", "link"):
            if isinstance(feed_section.get(key), str):
                return feed_section[key]

    return f"https://facilitairinfo.github.io/Newsfeeds/{cfg_path.stem}.xml"

def check_json_feed(bron: dict) -> bool:
    try:
        resp = requests.get(bron["url"], params=bron.get("params", {}), timeout=TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        items = data if isinstance(data, list) else data.get("Items") or data.get("items") or []
        return isinstance(items, list) and len(items) > 0
    except Exception as e:
        print(f"[FOUT] JSON-feed {bron.get('url')}: {e}")
        return False

def check_xml_feed(url: str) -> bool:
    try:
        resp = requests.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        txt = resp.text.lower()
        return ("<item" in txt) or ("<entry" in txt)
    except Exception as e:
        print(f"[FOUT] XML/HTML-feed {url}: {e}")
        return False

def main():
    statuslist = []
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    for cfg_path in sorted(CONFIG_DIR.glob("*.yml")):
        cfg = load_yaml(cfg_path)
        site = cfg.get("site", {})
        titel = site.get("titel") or site.get("naam") or cfg_path.stem
        feed_type = site.get("type", "html").lower()
        feed_url = guess_feed_url(cfg_path, cfg)

        if feed_type == "json":
            ok = check_json_feed(site.get("bron", {}))
        else:
            ok = check_xml_feed(feed_url)

        statuslist.append({
            "website": titel,
            "feedbron": feed_url,
            "status": ok,
            "last_checked": now_str
        })

    with OUTFILE.open("w", encoding="utf-8") as f:
        json.dump(statuslist, f, ensure_ascii=False, indent=2)

    print(f"[OK] {len(statuslist)} feeds verwerkt → {OUTFILE}")

if __name__ == "__main__":
    main()
