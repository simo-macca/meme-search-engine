import os
import requests
from solr_setup import SolrSetup
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

SOLR_BASE_PATH = os.getenv('SOLR_BASE_PATH')
FILES_TO_INDEX_FOLDER = os.getenv('FILES_TO_INDEX_FOLDER')


def collection_exists(solr_base_url: str, collection_name: str) -> bool:
    url = f"{solr_base_url}/api/collections/{collection_name}"
    try:
        response = requests.get(url)
        return response.status_code == 200
    except Exception as e:
        print("Error checking collection existence:", e)
        return False


def execute_solr_setup():
    solr = SolrSetup(SOLR_BASE_PATH)
    collection_name = solr.collection_name

    if collection_exists(SOLR_BASE_PATH, collection_name):
        print(f"Collection '{collection_name}' exists. Deleting and recreating it...")
        solr.delete_collection()
    else:
        print(f"Collection '{collection_name}' does not exist.")

    print(f"Creating collection '{collection_name}'...")
    solr.setup_memes_collection()

    print("Indexing new memes...")
    solr.insert_files_into_collection(FILES_TO_INDEX_FOLDER)

if __name__ == "__main__":
    execute_solr_setup()
