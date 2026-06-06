import json
import os
import sys
import requests

class SolrSetup:

    collection_name: str = 'memes_collection'
    collection_fields: dict[str, list[dict[str, str|bool]]] = {
        "add-field": [
            {
                "name": "id",
                "type": "string",
                "multiValued": False,
                "stored": True
            },
            {
                "name": "media_type",
                "type": "string",
                "multiValued": False,
                "stored": True
            },
            {
                "name": "title",
                "type": "text_general",
                "multiValued": False,
                "stored": True
            },
            {
                "name": "media_src",
                "type": "string",
                "multiValued": False,
                "stored": True
            },
            {
                "name": "tags",
                "type": "string",
                "multiValued": True,
                "stored": True
            }
        ]
    }

    def __init__(self, solr_base_url: str) -> None:
        self.solr_base_url = solr_base_url

    def setup_memes_collection(self):
        url = f"{self.solr_base_url}/api/collections"
        payload = {
            "name": self.collection_name,
            "numShards": 1,
            "replicationFactor": 1
        }


        try:
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                print("Error creating collection:", response.text)
                return
            print(f"Collection '{self.collection_name}' created successfully")

            self.add_fields_to_collection()
        except Exception as e:
            print("Exception creating collection:", e)

    def add_fields_to_collection(self):
        response = requests.post(
            f"{self.solr_base_url}/api/collections/{self.collection_name}/schema",
            json=self.collection_fields,
        )

        if response.status_code != 200:
            print(response.json().get('message'))
            return

        sys.stdout.write("Added fields correctly to " + self.collection_name)

    def insert_files_into_collection(self, data_path: str):
        update_url = f"{self.solr_base_url}/api/collections/{self.collection_name}/update"

        for file in os.listdir(data_path):
            file_path = os.path.join(data_path, file)

            if not file.endswith(".json"):
                continue

            print(f"Indexing {file}...")

            try:
                with open(file_path, "r") as f:
                    data = json.load(f)

                docs = [data] if isinstance(data, dict) else data

                response = requests.post(update_url, json=docs)

                if response.status_code != 200:
                    print("Error indexing", file, "->", response.text)
                else:
                    refresh_response = requests.post(
                        f"{self.solr_base_url}/api/collections/{self.collection_name}/config",
                        json={
                            "set-property": {
                                "updateHandler.autoCommit.maxTime":15000
                            }
                        }
                    )
                    if refresh_response.status_code != 200:
                        print(f"{file} indexed successfully; could not refresh collection for search")
                        print(refresh_response.status_code, refresh_response.text)
                    else:
                        print(f"{file} indexed successfully")

            except Exception as e:
                print("Error processing", file, ":", e)

    def delete_collection(self):
        url = f"{self.solr_base_url}/api/collections/{self.collection_name}"
        response = requests.delete(url)

        if response.status_code == 200:
            print(f"Collection '{self.collection_name}' deleted successfully")
        else:
            print("Error deleting collection:", response.text)