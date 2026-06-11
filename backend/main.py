import os
import sys
import time
import json
import requests
from datetime import datetime, timedelta
from run_spiders import run_spiders, remove_duplicates
from execute_solr_setup import execute_solr_setup

# Cache configuration
CACHE_FILE = "raw_data/scrape_metadata.json"
CACHE_EXPIRY_DAYS = 7


def wait_for_solr(solr_url="http://solr:8983", timeout=120):
    print(f"⏳ Waiting for Solr to be ready at {solr_url}...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{solr_url}/solr/admin/info/system", timeout=5)
            if response.status_code == 200:
                print("✅ Solr is online and ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(3)
    print("❌ Timed out waiting for Solr.")
    return False


def should_run_scraper():
    # Fail-safe 1: Check if there are actually any data files to index
    has_data = False
    if os.path.exists("raw_data"):
        has_data = any(f.endswith('.json') and f != os.path.basename(CACHE_FILE) for f in os.listdir("raw_data"))

    if not has_data:
        print("⚠️ No scraped data files found. Forcing scrape.")
        return True

    # Fail-safe 2: Check if the cache metadata file exists
    if not os.path.exists(CACHE_FILE):
        print("ℹ️ No cache metadata found. Forcing scrape.")
        return True

    # Main logic: Check the timestamp
    try:
        with open(CACHE_FILE, "r") as f:
            data = json.load(f)
            last_run = datetime.fromisoformat(data["last_run"])

            if datetime.now() - last_run > timedelta(days=CACHE_EXPIRY_DAYS):
                print(f"⏳ Cache expired (older than {CACHE_EXPIRY_DAYS} days). Forcing scrape.")
                return True
            else:
                print(f"⏭️ Cache valid! Last scraped on {last_run.strftime('%Y-%m-%d %H:%M')}.")
                return False
    except Exception as e:
        print(f"⚠️ Error reading cache: {e}. Forcing scrape.")
        return True


def update_scrape_cache():
    os.makedirs("raw_data", exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump({"last_run": datetime.now().isoformat()}, f)


def main():
    print("\n--- 🚀 Starting Backend Automated Pipeline ---")

    solr_url = os.getenv('SOLR_BASE_PATH', 'http://solr:8983')

    # 1. Wait for the Solr Container to fully boot
    if not wait_for_solr(solr_url):
        sys.exit(1)

    # 2. Scrape and Deduplicate (with Caching)
    print("\n--- 🕷️ Phase 1: Scraping and Deduplication ---")
    if should_run_scraper():
        print("🏃‍♂️ Starting the spiders... This might take a while.")
        run_spiders(output_dir="raw_data")
        remove_duplicates(output_dir="raw_data", unique_key="id")
        update_scrape_cache()
    else:
        print("⚡ Skipping spiders. Utilizing local cached data from 'raw_data/'.")

    # 3. Solr Setup & Clustering Injection
    print("\n--- 🔍 Phase 2: Solr Setup, Clustering, and Indexing ---")
    execute_solr_setup()

    print("\n🎉 Pipeline completed successfully! The backend container will now exit.")


if __name__ == "__main__":
    main()
