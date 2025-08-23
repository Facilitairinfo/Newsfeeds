import pathlib
import subprocess
import sys

CONFIG_DIR = pathlib.Path("configs")
SCRIPT_DIR = pathlib.Path("scripts")

def main():
    configs = sorted(CONFIG_DIR.glob("*.yml"))
    if not configs:
        print("Geen config-bestanden gevonden in", CONFIG_DIR)
        sys.exit(0)

    print(f"🔍 {len(configs)} configs gevonden...")
    for config in configs:
        print(f"📡 Scrapen: {config.stem}")
        subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "scrape_site.py"), "--config", str(config)],
            check=True
        )

if __name__ == "__main__":
    main()
