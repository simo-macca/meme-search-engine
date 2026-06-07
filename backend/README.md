# Memes Search Engine – Backend

This backend powers the complete data pipeline for a meme search engine, from scraping popular meme platforms to indexing content in Apache Solr with optional topic clustering capabilities.

## Overview

### Features

- Multi-source meme scraping
  - 9GAG
  - iFunny
  - Memedroid
  - Memes.com
- Automatic duplicate detection and removal
- Apache Solr collection creation and schema management
- Automated indexing pipeline
- Optional topic clustering using Solr's Lingo algorithm
- Interactive orchestration through a single entry point

---

## Architecture

```text
Meme Platforms
(9GAG, iFunny, Memedroid, Memes.com)
                │
                ▼
      Scrapy / Playwright Spiders
                │
                ▼
          raw_data/*.json
                │
                ▼
          Deduplication
                │
                ▼
      Apache Solr Collection
                │
                ▼
          Search Engine
                │
                ▼
 Optional Topic Clustering (Lingo)
```

---

## Backend Directory Structure

```text
backend/
├── meme_crawler/               # Scrapy project folder
│   ├── spiders/                # Target scrapers (9GAG, iFunny, Memedroid, Memes.com)
│   │   ├── ifunny_spider.py
│   │   ├── memedroid_spider.py
│   │   ├── memes_spider.py
│   │   ├── nine_gag_spider.py
│   │   └── nine_gag_wtf_spider.py
│   └── settings.py             # Scrapy settings and pipeline adjustments
├── execute_solr_setup.py       # Configures Solr schema fields and handles core setups
├── main.py                     # Main orchestrator pipeline script
├── requirements.txt            # Python dependencies list
├── run_spiders.py              # Sequence crawl executor and duplicate filter logic
└── scrapy.cfg                  # Scrapy deployment configuration configuration
```

---

## Quick Start (Recommended)

### 1. Install Apache Solr

Download the latest Solr binary release from the official website: **[https://solr.apache.org/downloads.html](https://solr.apache.org/downloads.html)**

Extract the downloaded archive (e.g., `solr-10.x.x`). To start Solr, navigate to the extracted folder in your terminal and run:

```bash
cd /path/to/solr-10.x.x
bin/solr start -p 8983
```

---

### 2. Configure Environment

Create a `.env` file in the project root:

```text
SOLR_BASE_PATH=http://localhost:8983
FILES_TO_INDEX_FOLDER=./raw_data
SOLR_INSTALL_DIR=/absolute/path/to/your/solr-10.x.x   # Replace with your actual extracted folder path
```

---

### 3. Create a Virtual Environment

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 4. Install Dependencies

```bash
pip install -r requirements.txt
playwright install
```

---

### 5. Run the Complete Pipeline

```bash
python3 main.py
```

The orchestrator will guide you through the entire process and handle setup checks automatically. The `main.py` script serves as the central orchestrator for the entire backend workflow.

### Pre-flight Checks

Before execution begins, it verifies:

* A Python virtual environment is active
* Apache Solr is reachable
* Required Python dependencies are installed

If packages are missing, the script can offer to install them automatically.

---

### Phase 1: Scraping

Launches all spiders to collect fresh meme data from:

* 9GAG
* iFunny
* Memedroid
* Memes.com

Scraped results are stored as JSON files inside:

```text
/raw_data
```

---

### Phase 2: Deduplication

Processes all collected datasets and removes duplicate meme entries to maintain data quality and indexing consistency.

---

### Phase 3: Solr Collection Setup & Indexing

The script:

* Creates the Solr collection if necessary
* Defines the collection schema
* Uploads all deduplicated meme data

Configured fields include:

* `id`
* `title`
* `media_type`
* `media_src`
* `tags`

---

### Phase 4: Optional Topic Clustering

At the end of execution, the script can:

* Restart Solr with clustering enabled
* Locate your Solr configuration paths automatically (via `.env`)
* Apply required clustering settings
* Reload the Solr collection

This step is optional and only needed for topic clustering functionality.

---

## Manual Workflow

If you prefer running each stage independently, use the following scripts.

## Scraping

Run all spiders:

```bash
python3 run_spiders.py
```

Output:

```text
/raw_data/*.json
```

---

## Solr Indexing

Ensure your `.env` file is properly configured. Then execute:

```bash
python3 execute_solr_setup.py
```

This script:

* Creates the Solr collection
* Defines the schema
* Uploads JSON documents
* Rebuilds the index

---

## Solr Configuration

### Starting Solr

Navigate to your Solr installation directory and run:

```bash
bin/solr start -p 8983
```

### Stopping Solr

```bash
bin/solr stop -p 8983
```

---

## Optional: Enable Topic Clustering (Advanced)

To power a "Topics Map" or grouped-search experience, Apache Solr can be configured to use the Lingo clustering algorithm.

### Step 1: Locate the Default Configset

Navigate to your extracted Solr directory. The configuration files are located at: `/path/to/solr-10.x.x/server/solr/configsets/_default/conf`

---

### Step 2: Update `managed-schema.xml`

Open the `managed-schema.xml` in that directory and add the following fields inside the `<schema>` tag:

```xml
<field name="title" type="text_general" indexed="true" stored="true" multiValued="true"/>
<field name="tags" type="text_general" indexed="true" stored="true" multiValued="true"/>
<field name="media_type" type="string" indexed="true" stored="true" multiValued="true"/>
<field name="media_src" type="string" indexed="true" stored="true" multiValued="true"/>
```

---

### Step 3: Update `solrconfig.xml`

Open the `solrconfig.xml` in the same directory and add the clustering search component:

```xml
<searchComponent class="org.apache.solr.handler.clustering.ClusteringComponent" name="clustering">
    <lst name="engine">
        <str name="name">lingo</str>
        <str name="clustering.fields">tags</str>
        <str name="clustering.algorithm">Lingo</str>
    </lst>
</searchComponent>
```

---

### Step 4: Enable Clustering in the Search Handler

Replace or update the `/select` request handler in `solrconfig.xml`:

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

---

### Step 5: Restart and Reload

You can perform these steps automatically through `main.py` or manually using the Solr `bin` script:

```bash
bin/solr restart -p 8983 \
    -Dsolr.modules=clustering \
    -Dsolr.clustering.enabled=true

bin/solr zk upconfig \
    -n memes_collection.AUTOCREATED \
    -d server/solr/configsets/_default/conf

curl "http://localhost:8983/solr/admin/collections?action=RELOAD&name=memes_collection"
```


[//]: # (  <filter>)
[//]: # (    <filter-name>CorsFilter</filter-name>)
[//]: # (    <filter-class>org.eclipse.jetty.servlets.CrossOriginFilter</filter-class>)
[//]: # (    <init-param>)
[//]: # (      <param-name>allowedOrigins</param-name>)
[//]: # (      <param-value>http://localhost:3000/</param-value>)
[//]: # (    </init-param>)
[//]: # (    <init-param>)
[//]: # (      <param-name>allowedMethods</param-name>)
[//]: # (      <param-value>GET,POST,PUT,DELETE,OPTIONS,HEAD</param-value>)
[//]: # (    </init-param>)
[//]: # (    <init-param>)
[//]: # (      <param-name>allowedHeaders</param-name>)
[//]: # (      <param-value>X-Requested-With,Content-Type,Accept,Origin</param-value>)
[//]: # (    </init-param>)
[//]: # (    <init-param>)
[//]: # (      <param-name>allowCredentials</param-name>)
[//]: # (      <param-value>true</param-value>)
[//]: # (    </init-param>)
[//]: # (  </filter>)
[//]: # ()
[//]: # (  <filter-mapping>)
[//]: # (    <filter-name>CorsFilter</filter-name>)
[//]: # (    <url-pattern>/*</url-pattern>)
[//]: # (  </filter-mapping>)
