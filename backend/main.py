import os
import sys
import time
import requests
from run_spiders import run_spiders, remove_duplicates
from execute_solr_setup import execute_solr_setup


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


def main():
    print("\n--- 🚀 Starting Backend Automated Pipeline ---")

    solr_url = os.getenv('SOLR_BASE_PATH', 'http://solr:8983')

    # 1. Wait for the Solr Container to fully boot
    if not wait_for_solr(solr_url):
        sys.exit(1)

    # 2. Scrape and Deduplicate
    print("\n--- 🕷️ Phase 1: Scraping and Deduplication ---")
    run_spiders(output_dir="raw_data")
    remove_duplicates(output_dir="raw_data", unique_key="id")

    # 3. Solr Setup & Clustering Injection
    print("\n--- 🔍 Phase 2: Solr Setup, Clustering, and Indexing ---")
    execute_solr_setup()

    print("\n🎉 Pipeline completed successfully! The backend container will now exit, and your data is ready in Solr.")


if __name__ == "__main__":
    main()
