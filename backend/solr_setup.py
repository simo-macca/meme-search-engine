import json
import os
import sys
import logging
import requests

logger = logging.getLogger(__name__)

class SolrSetup:
    collection_name: str = 'memes_collection'
    collection_fields: dict[str, list[dict[str, str | bool]]] = {
        "add-field": [
            {"name": "id", "type": "string", "multiValued": False, "stored": True},
            {"name": "media_type", "type": "string", "multiValued": False, "stored": True},
            {"name": "title", "type": "text_general", "multiValued": False, "stored": True},
            {"name": "media_src", "type": "string", "multiValued": False, "stored": True},
            {"name": "tags", "type": "string", "multiValued": True, "stored": True}
        ]
    }

    def __init__(self, solr_base_url: str) -> None:
        self.solr_base_url = solr_base_url

    def setup_memes_collection(self):
        url = f"{self.solr_base_url}/api/collections"
        payload = {"name": self.collection_name, "numShards": 1, "replicationFactor": 1}

        try:
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                logger.error(f"Error creating collection: {response.text}")
                return
            logger.info(f"Collection '{self.collection_name}' created successfully")

            self.add_fields_to_collection()
            self.configure_clustering()
        except Exception as e:
            logger.error(f"Exception creating collection: {e}")

    def add_fields_to_collection(self):
        response = requests.post(
            f"{self.solr_base_url}/api/collections/{self.collection_name}/schema",
            json=self.collection_fields,
        )
        if response.status_code != 200:
            logger.error(response.json().get('message'))
            return
        logger.info(f"Added fields correctly to {self.collection_name}")

    def configure_clustering(self):
        logger.info("Configuring Lingo Clustering via Solr Config API...")
        config_url = f"{self.solr_base_url}/api/collections/{self.collection_name}/config"

        # add clustering component
        component_payload = {
            "add-searchcomponent": {
                "name": "clustering",
                "class": "org.apache.solr.handler.clustering.ClusteringComponent",
                "engine": [
                    {
                        "name": "lingo",
                        "clustering.fields": "tags",
                        "clustering.algorithm": "Lingo"
                    }
                ]
            }
        }
        requests.post(config_url, json=component_payload)

        # update requestHandler to use clustering
        handler_payload = {
            "update-requesthandler": {
                "name": "/select",
                "class": "solr.SearchHandler",
                "defaults": {
                    "echoParams": "explicit",
                    "rows": 10,
                    "clustering": True,
                    "clustering.engine": "lingo"
                },
                "last-components": ["clustering"]
            }
        }
        resp = requests.post(config_url, json=handler_payload)
        if resp.status_code == 200:
            logger.info("Clustering configured successfully.")
        else:
            logger.error(f"Failed to configure clustering: {resp.text}")

    def insert_files_into_collection(self, data_path: str):
        update_url = f"{self.solr_base_url}/api/collections/{self.collection_name}/update"
        if not os.path.exists(data_path):
            logger.error(f"Directory {data_path} not found.")
            return

        for file in os.listdir(data_path):
            file_path = os.path.join(data_path, file)
            if not file.endswith(".json"): continue

            logger.info(f"Indexing {file}...")
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                docs = [data] if isinstance(data, dict) else data
                response = requests.post(update_url, json=docs)

                if response.status_code == 200:
                    requests.post(
                        f"{self.solr_base_url}/api/collections/{self.collection_name}/config",
                        json={"set-property": {"updateHandler.autoCommit.maxTime": 15000}}
                    )
                    logger.info(f"File {file} indexed successfully")
                else:
                    logger.error(f"Error indexing {file} -> {response.text}")
            except Exception as e:
                logger.error(f"Error processing {file}: {e}")

    def delete_collection(self):
        url = f"{self.solr_base_url}/api/collections/{self.collection_name}"
        response = requests.delete(url)
        if response.status_code == 200:
            logger.info(f"Collection '{self.collection_name}' deleted successfully")
