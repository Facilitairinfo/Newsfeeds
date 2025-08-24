# Newsfeeds

[![Build & Scrape Feeds](https://github.com/facilitairinfo/Newsfeeds/actions/workflows/build-feeds.yml/badge.svg)](https://github.com/facilitairinfo/Newsfeeds/actions/workflows/build-feeds.yml)
![Last updated](https://img.shields.io/endpoint?url=https%3A%2F%2Fshields-io-visitor-counter.vercel.app%2Fapi%2Fgithub_last_commit_time%3Fuser%3Dfacilitairinfo%26repo%3DNewsfeeds&label=Updated)

Automatisch genereren en bijhouden van XML‑feeds en feedstatus voor diverse bronnen.  
Deze repository bevat de scraping‑scripts en workflow‑automatisering om feeds up‑to‑date te houden.

---

## 📋 Over dit project
Dit project:
- Scraped nieuws- of contentfeeds op basis van YAML‑configuraties in de `configs/` map
- Genereert XML‑bestanden in `docs/` die direct kunnen worden gepubliceerd via GitHub Pages
- Maakt een `feedstatus.json` om de beschikbaarheid van feeds te monitoren
- Draait volledig automatisch via GitHub Actions, twee keer per uur (om :15 en :45)

---

## ⚙️ Hoe het werkt
1. **Scraper** (`scripts/scrape_all.py`):
   - Zoekt alle `.yml`-configbestanden in `configs/`
   - Roept per config het juiste scraping‑script aan
2. **Feedstatus** (`scripts/gen_feedstatus.py`):
   - Controleert of de feeds nog geldig en bereikbaar zijn
   - Schrijft de resultaten weg naar `feedstatus.json`
3. **Workflow** (`.github/workflows/build-feeds.yml`):
   - Installeert dependencies uit `requirements.txt`
   - Voert de scraper en feedstatus‑generator uit
   - Commit automatisch gewijzigde bestanden

---

## 🚀 Zelf draaien
Wil je lokaal testen?

```bash
# 1. Clone de repository
git clone https://github.com/facilitairinfo/Newsfeeds.git
cd Newsfeeds

# 2. Installeer dependencies
pip install -r requirements.txt

# 3. Scrape feeds
python scripts/scrape_all.py

# 4. Genereer feedstatus.json
python scripts/gen_feedstatus.py
