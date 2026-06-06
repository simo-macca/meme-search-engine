# Memes Search Engine – Backend

This backend project handles the end-to-end pipeline for a meme search engine: from scraping top meme platforms to indexing the data into an Apache Solr server with advanced clustering capabilities.

## 🚀 Getting Started

### 1\. Environment Setup

Create a virtual environment in the root folder, activate it, and install the necessary dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install
```

### 2\. Full Pipeline Execution (Recommended)

The easiest way to run the entire backend is through the `main.py` script. This script acts as an orchestrator for the entire process.

To run the full pipeline:

```bash
python3 main.py
```

**What `main.py` does:**

  * **Pre-flight Checks**: Verifies that your virtual environment is active and that the Solr server is running and reachable.
  * **Dependency Management**: Checks if all packages in `requirements.txt` are installed and offers to install missing ones automatically.
  * **Phase 1: Scraping**: Triggers all spiders (9GAG, iFunny, Memedroid, Memes.com) to collect fresh data.
  * **Phase 2: deduplication**: Automatically removes duplicate meme entries across all scraped JSON files to ensure data integrity.
  * **Phase 3: Solr Indexing**: Communicates with your Solr instance to create the collection, define the schema, and index the deduplicated data.
  * **Phase 4: Optional Clustering**: Provides an interactive prompt to restart Solr with the clustering module enabled and apply the necessary Lingo algorithm configurations.

-----

### 3\. Manual Steps (Alternative)

If you prefer to run parts of the pipeline manually, you can use the individual scripts:

#### Scraping and Data Preparation

Run the master scraping script to crawl platforms and save data to the `/raw_data` directory:

```bash
python3 ./run_spiders.py
```

*This script crawls 9GAG, iFunny, Memedroid, and Memes.com, saving the output as `.json` files.*

#### Solr Indexing

**Note:** If you haven't already, please review the **Solr Configuration** section below to ensure your server is running and your schema is correctly defined.

Once confirmed, ensure your `.env` file is configured with `SOLR_BASE_PATH` and `FILES_TO_INDEX_FOLDER`, then run:

```bash
python3 ./execute_solr_setup.py
```

*This script deletes the existing collection (if any), recreates it with the proper schema, and indexes your JSON files.*

-----

## 🔍 Solr Configuration

### 1\. Starting the Server

Navigate to your Solr directory and start the server in cloud mode:

```bash
cd solr-9.10.0
bin/solr start -cloud -p 8983
```

### 2\. Basic Indexing

Add a `.env` file in the root folder with the following configuration:

```text
SOLR_BASE_PATH=http://localhost:8983
FILES_TO_INDEX_FOLDER=./raw_data
```

Execute the setup script. This script checks if the collection exists, creates it if necessary, defines the schema fields (`id`, `title`, `media_type`, `media_src`, `tags`), and indexes your JSON files:

```bash
python3 ./execute_solr_setup.py
```

### 3\. Stopping the Server

Navigate to your Solr directory and start the server in cloud mode:

```bash
cd solr-9.10.0
bin/solr stop -p 8983
```

-----

## 🧩 Advanced: Topic Clustering

To enable the **Lingo** clustering algorithm for a "Topics Map" view, follow these steps:

1.  **Modify `managed-schema.xml`**: Usually located at `server/solr/configsets/_default/conf`. Add these tags inside the `<schema>` tag:

    ```xml
    <field name="title" type="text_general" indexed="true" stored="true" multiValued="true"/>
    <field name="tags" type="text_general" indexed="true" stored="true" multiValued="true"/>
    <field name="media_type" type="string" indexed="true" stored="true" multiValued="true"/>
    <field name="media_src" type="string" indexed="true" stored="true" multiValued="true"/>
    ```

2.  **Modify `solrconfig.xml`**: Add the clustering search component:

    ```xml
    <searchComponent class="org.apache.solr.handler.clustering.ClusteringComponent" name="clustering">
        <lst name="engine">
        <str name="name">lingo</str>
        <str name="clustering.fields">tags</str>
        <str name="clustering.algorithm">Lingo</str>
        </lst>
    </searchComponent>
    ```

3.  **Update Request Handler**: Substitute the `/select` request handler in `solrconfig.xml` to enable clustering:

    ```xml
    <requestHandler name="/select" class="solr.SearchHandler">
        <lst name="defaults">
          <str name="echoParams">explicit</str>
          <int name="rows">10</int>
          <bool name="clustering">true</bool>
          <str name="clustering.engine">lingo</str>
        </lst>
        <arr name="last-components">
          <str>clustering</str>
        </arr>
    </requestHandler>
    ```

4.  **Restart and Update**: Restart Solr with the clustering module enabled and upload the new configurations:

    ```bash
    bin/solr restart -cloud -p 8983 -Dsolr.modules=clustering -Dsolr.clustering.enabled=true
    bin/solr zk upconfig -n memes_collection.AUTOCREATED -d server/solr/configsets/_default/conf
    curl "http://localhost:8983/solr/admin/collections?action=RELOAD&name=memes_collection"
    ```