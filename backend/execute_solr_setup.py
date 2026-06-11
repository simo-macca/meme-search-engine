import logging
import os

import requests
from dotenv import find_dotenv, load_dotenv
from solr_setup import SolrSetup

logger = logging.getLogger(__name__)

load_dotenv(find_dotenv())

SOLR_BASE_PATH = os.getenv("SOLR_BASE_PATH")
FILES_TO_INDEX_FOLDER = os.getenv("FILES_TO_INDEX_FOLDER")


def collection_exists(solr_base_url: str, collection_name: str) -> bool:
    url = f"{solr_base_url}/api/collections/{collection_name}"
    try:
        response = requests.get(url)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"Error checking collection existence: {e}")
        return False


def execute_solr_setup():
    solr = SolrSetup(SOLR_BASE_PATH)
    collection_name = solr.collection_name

    if collection_exists(SOLR_BASE_PATH, collection_name):
        logger.info(f"Collection '{collection_name}' exists. Deleting and recreating it...")
        solr.delete_collection()
    else:
        logger.info(f"Collection '{collection_name}' does not exist.")

    logger.info(f"Creating collection '{collection_name}'...")
    solr.setup_memes_collection()

    logger.info("Indexing new memes...")
    solr.insert_files_into_collection(FILES_TO_INDEX_FOLDER)


if __name__ == "__main__":
    logging.basicConfig()
    execute_solr_setup()
