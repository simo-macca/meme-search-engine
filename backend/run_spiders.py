import glob
import json
import os
import subprocess
import sys


def run_spiders(output_dir="raw_data"):
    os.makedirs(output_dir, exist_ok=True)
    print(f"📂 Output directory checked: {output_dir}")

    commands = [
        (
            "9GAG Spider (Standalone)",
            [sys.executable, "meme_crawler/spiders/nine_gag_spider.py"]
        ),
        (
            "9GAG Spider (WTF)",
            [sys.executable, "meme_crawler/spiders/nine_gag_wtf_spider.py"]
        ),
        (
            "Memedroid Spider",
            ["scrapy", "crawl", "memedroid_spider", "-O", f"{output_dir}/memedroid_spider.json", "--nolog"]
        ),
        (
            "iFunny Spider",
            ["scrapy", "crawl", "ifunny_spider", "-O", f"{output_dir}/ifunny_spider.json", "--nolog"]
        ),
        (
            "Memes.com Spider",
            ["scrapy", "crawl", "memes_spider", "-O", f"{output_dir}/memes_com.json", "--nolog"]
        ),
    ]

    for description, cmd in commands:
        print(f"\n🕷️  Running {description}...")
        try:
            subprocess.run(cmd, check=True)
            print(f"✅ {description} finished successfully.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running {description}: {e}")
        except FileNotFoundError:
            print(f"❌ Command not found: {cmd[0]}. Make sure Scrapy is installed and you are in the correct directory.")


def remove_duplicates(output_dir="raw_data", unique_key="id"):
    print("\n--- Starting Duplicate Removal Process ---")

    seen_identifiers = set()
    total_duplicates_removed = 0

    for filepath in glob.glob(os.path.join(output_dir, '*.json')):
        print(f"🔍 Processing file: {filepath}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print(f"⚠️ Could not decode JSON from {filepath}. Skipping.")
            continue
        except FileNotFoundError:
            print(f"⚠️ File not found: {filepath}. Skipping.")
            continue

        if not isinstance(data, list):
            print(f"⚠️ Data in {filepath} is not a list. Skipping deduplication.")
            continue

        unique_data = []
        duplicates_in_file = 0

        for item in data:
            identifier = item.get(unique_key) if isinstance(item, dict) else None

            if identifier and identifier not in seen_identifiers:
                seen_identifiers.add(identifier)
                unique_data.append(item)
            else:
                duplicates_in_file += 1

        total_duplicates_removed += duplicates_in_file

        if duplicates_in_file > 0:
            print(f"🧹 Removed {duplicates_in_file} duplicate(s) from {filepath}.")
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(unique_data, f, indent=4)
        else:
            print(f"✨ No duplicates found in {filepath}.")

    print(f"\n✅ Duplicate removal complete. Total duplicates removed across all files: {total_duplicates_removed}.")


if __name__ == "__main__":
    run_spiders()
    remove_duplicates(unique_key="id")
