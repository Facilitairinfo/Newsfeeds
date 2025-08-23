import feedparser
import json
from datetime import datetime
from pathlib import Path
import os

# Pad naar de docs-map (waar je .xml feeds staan)
docs_path = Path("docs")
resultaten = []

for xml_file in docs_path.glob("*.xml"):
    aangemaakt_op = datetime.fromtimestamp(
        os.path.getctime(xml_file)
    ).strftime("%Y-%m-%d")
    status = "nee"
    laatst_bijgewerkt = "onbekend"
    laatst_succesvol = "nooit"
    naam = xml_file.stem
    bron_url = ""

    try:
        parsed = feedparser.parse(xml_file.open("rb").read())

        # Titel uit de feed zelf
        if parsed.feed.get("title"):
            naam = parsed.feed.title

        # Originele bronlink uit de feed
        if parsed.feed.get("link"):
            bron_url = parsed.feed.link

        # Controleren of er items in de feed zitten
        if parsed.entries:
            status = "ja"
            entry_date = parsed.entries[0].get("published") or parsed.entries[0].get("updated")
            if entry_date:
                laatst_bijgewerkt = entry_date
            laatst_succesvol = datetime.now().strftime("%Y-%m-%d %H:%M")

    except Exception as e:
        print(f"Fout bij {xml_file.name}: {e}")

    resultaten.append({
        "naam": naam,
        "status": status,
        "laatst_bijgewerkt": laatst_bijgewerkt,
        "aangemaakt_op": aangemaakt_op,
        "laatst_succesvol": laatst_succesvol,
        "bron": bron_url
    })

# Wegschrijven naar feedstatus.json
with open(docs_path / "feedstatus.json", "w", encoding="utf-8") as f:
    json.dump(resultaten, f, ensure_ascii=False, indent=2)

print("feedstatus.json bijgewerkt met alle gevonden feeds.")
