# 📰 Newsfeeds

Automatisch genereren en bijhouden van XML‑feeds, statusoverzichten en onderhoudspagina’s voor diverse nieuwsbronnen.

## 📋 Over dit project
Dit project:
- Scrapet nieuws- of contentfeeds op basis van `.yml`‑configuraties in de map [`configs/`](configs/)
- Genereert `.xml`‑bestanden in [`docs/`](docs/) die direct via **GitHub Pages** gepubliceerd worden
- Maakt een `feedstatus.json` en `feedonderhoud.html` om beschikbaarheid en onderhoud bij te houden
- Draait **volledig automatisch** via GitHub Actions op vaste tijden (zie schema hieronder)

## 📡 Live feeds
Klik op een feednaam om het actuele XML‑bestand te bekijken:

- *[Voorbeeldfeed 1](docs/voorbeeldfeed1.xml)*
- *[Voorbeeldfeed 2](docs/voorbeeldfeed2.xml)*

📂 [Feedstatus (JSON)](docs/feedstatus.json)  
📄 [Feedonderhoud](docs/feedonderhoud.html)

> 🔹 **Tip:** vervang de voorbeeldlinks hierboven door de daadwerkelijke bestandsnamen uit je `docs/`‑map.  
> GitHub Pages publiceert die automatisch op:  
> `https://facilitairinfo.github.io/Newsfeeds/<bestandsnaam>.xml`

## ⚙️ Hoe het werkt

### 1️⃣ Scraper
`scripts/scrape_all.py`:
- Zoekt alle `.yml`‑configbestanden in `configs/`
- Roept per config het juiste scraping‑script aan
- Schrijft de `.xml`‑feeds naar `docs/`

### 2️⃣ Feedstatus
`scripts/gen_feedstatus.py`:
- Controleert of de feeds geldig en bereikbaar zijn
- Schrijft resultaten naar `feedstatus.json`
- Past ook `feedonderhoud.html` aan

### 3️⃣ Workflows
- **`update_feeds.yml`** – draait 8× per dag op vaste tijden  
- **`build-feeds.yml`** – zelfde logica en tijden, plus handmatige optie  
Beide workflows:
- Installeren dependencies
- Draaien de scraper met retry‑logica
- Committen alleen als er wijzigingen zijn

## 🕒 Draaischema (NL‑tijd)

| Tijd  | Omschrijving                            |
|-------|-----------------------------------------|
| 04:00 | Vroege ochtendscan                      |
| 07:00 | Ochtendnieuws                           |
| 08:00 | Persberichten / updates                 |
| 09:00 | Laatste ochtendgolf                     |
| 10:00 | Late ochtendcontent                     |
| 13:00 | Lunchupdate                             |
| 16:00 | Middagronde                             |
| 19:00 | Avondcheck                              |

*(Draaitijden komen overeen voor beide workflows.)*

## 🚀 Zelf draaien (lokaal testen)
```bash
# 1. Clone de repository
git clone https://github.com/facilitairinfo/Newsfeeds.git
cd Newsfeeds

# 2. Installeer dependencies
pip install -r requirements.txt

# 3. Scrape feeds
python scripts/scrape_all.py

# 4. Genereer feedstatus
python scripts/gen_feedstatus.py
