#!/usr/bin/env python3
import os
import sys
import glob
import subprocess

CONFIG_DIR = "configs"    # map met je .yml-configs
OUTPUT_DIR = "docs"       # map voor de gegenereerde XML-feeds

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    configs = sorted(glob.glob(os.path.join(CONFIG_DIR, "*.yml")))
    if not configs:
        print(f"⚠ Geen configbestanden gevonden in {CONFIG_DIR}/")
        sys.exit(1)
    
    print(f"▶ Gevonden configs: {[os.path.basename(c) for c in configs]}")
    
    success = []
    failed = []
    
    for cfg in configs:
        feed_name = os.path.splitext(os.path.basename(cfg))[0]
        print(f"\n=== 🛠 Verwerk {feed_name} ===")
        
        try:
            # Voorbeeld: aanroep je bestaande feedgenerator CLI
            subprocess.run(
                ["python", "scripts/single-feed-gen.py", cfg, OUTPUT_DIR],
                check=True
            )
            success.append(feed_name)
        except subprocess.CalledProcessError as e:
            print(f"⚠ Fout bij {feed_name}: {e}")
            failed.append(feed_name)
    
    print("\n✅ Geslaagde feeds:", success)
    if failed:
        print("❌ Mislukte feeds:", failed)
        sys.exit(1)

if __name__ == "__main__":
    main()
