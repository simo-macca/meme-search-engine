import os
import sys
import time
import json
import logging
import requests
from datetime import datetime, timedelta
from run_spiders import run_spiders, remove_duplicates
from execute_solr_setup import execute_solr_setup

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# cache configuration
CACHE_FILE = "raw_data/scrape_metadata.json"
CACHE_EXPIRY_DAYS = 7


def wait_for_solr(solr_url="http://solr:8983", timeout=120):
    logger.info(f"Waiting for Solr to be ready at {solr_url}...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{solr_url}/solr/admin/info/system", timeout=5)
            if response.status_code == 200:
                logger.info("Solr is online and ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(3)
    logger.error("Timed out waiting for Solr.")
    return False


def should_run_scraper():
    # check if there are any data files
    has_data = False
    if os.path.exists("raw_data"):
        has_data = any(f.endswith('.json') and f != os.path.basename(CACHE_FILE) for f in os.listdir("raw_data"))

    if not has_data:
        logger.warning("No scraped data files found. Forcing scrape.")
        return True

    # check if the cache metadata file
    if not os.path.exists(CACHE_FILE):
        logger.info("No cache metadata found. Forcing scrape.")
        return True

    # check the timestamp
    try:
        with open(CACHE_FILE, "r") as f:
            data = json.load(f)
            last_run = datetime.fromisoformat(data["last_run"])

            if datetime.now() - last_run > timedelta(days=CACHE_EXPIRY_DAYS):
                logger.info(f"Cache expired (older than {CACHE_EXPIRY_DAYS} days). Forcing scrape.")
                return True
            else:
                logger.info(f"Cache valid! Last scraped on {last_run.strftime('%Y-%m-%d %H:%M')}.")
                return False
    except Exception as e:
        logger.warning(f"Error reading cache: {e}. Forcing scrape.")
        return True


def update_scrape_cache():
    os.makedirs("raw_data", exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump({"last_run": datetime.now().isoformat()}, f)


def main():
    logger.info("--- Starting Backend Automated Pipeline ---")

    solr_url = os.getenv('SOLR_BASE_PATH', 'http://solr:8983')

    # wait solr container
    if not wait_for_solr(solr_url):
        sys.exit(1)

    # scrape and deduplicate
    logger.info("--- Phase 1: Scraping and Deduplication ---")
    if should_run_scraper():
        logger.info("Starting the spiders... This might take a while.")
        run_spiders(output_dir="raw_data")
        remove_duplicates(output_dir="raw_data", unique_key="id")
        update_scrape_cache()
    else:
        logger.info("Skipping spiders. Utilizing local cached data from 'raw_data/'.")

    # solr setup and clustering injection
    logger.info("--- Phase 2: Solr Setup, Clustering, and Indexing ---")
    execute_solr_setup()

    logger.info("Pipeline completed successfully! The backend container will now exit.")


if __name__ == "__main__":
    main()
