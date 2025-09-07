import os
import yaml

CONFIG_DIR = "configs"
LIMITS_BLOCK = {"limits": {"max_items": 5}}

def patch_file(path):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if "limits" not in data:
        data.update(LIMITS_BLOCK)
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, sort_keys=False)
        print(f"✅ Patched: {path}")
    else:
        print(f"⏩ Already has limits: {path}")

def main():
    for fname in os.listdir(CONFIG_DIR):
        if fname.endswith(".yml"):
            patch_file(os.path.join(CONFIG_DIR, fname))

if __name__ == "__main__":
    main()
