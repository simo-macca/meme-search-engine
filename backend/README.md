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

If you are using macOS with Homebrew:

```bash
brew install solr
```

Start Solr:

```bash
solr start -p 8983
```

---

### 2. Create a Virtual Environment

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
playwright install
```

---

### 4. Run the Complete Pipeline

```bash
python3 main.py
```

The orchestrator will guide you through the entire process and handle setup checks automatically. The `main.py` script serves as the central orchestrator for the entire backend workflow.

### Pre-flight Checks

Before execution begins, it verifies:

- A Python virtual environment is active
- Apache Solr is reachable
- Required Python dependencies are installed

If packages are missing, the script can offer to install them automatically.

---

### Phase 1: Scraping

Launches all spiders to collect fresh meme data from:

- 9GAG
- iFunny
- Memedroid
- Memes.com

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

- Creates the Solr collection if necessary
- Defines the collection schema
- Uploads all deduplicated meme data

Configured fields include:

- `id`
- `title`
- `media_type`
- `media_src`
- `tags`

---

### Phase 4: Optional Topic Clustering

At the end of execution, the script can:

- Restart Solr with clustering enabled
- Locate Homebrew configuration paths automatically
- Apply required clustering settings
- Reload the Solr collection

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

Ensure your `.env` file exists:

```text
SOLR_BASE_PATH=http://localhost:8983
FILES_TO_INDEX_FOLDER=./raw_data
```

Then execute:

```bash
python3 execute_solr_setup.py
```

This script:

- Creates the Solr collection
- Defines the schema
- Uploads JSON documents
- Rebuilds the index

---

## Solr Configuration

### Starting Solr

```bash
solr start -p 8983
```

---

### Environment Variables

Create a `.env` file in the project root:

```text
SOLR_BASE_PATH=http://localhost:8983
FILES_TO_INDEX_FOLDER=./raw_data
```

---

### Running Index Setup

```bash
python3 execute_solr_setup.py
```

The script automatically:

- Checks collection existence
- Creates the collection when needed
- Configures schema fields
- Uploads indexed documents

---

### Stopping Solr

```bash
solr stop -p 8983
```

---

## Optional: Enable Topic Clustering (Advanced)

To power a "Topics Map" or grouped-search experience, Apache Solr can be configured to use the Lingo clustering algorithm.

### Step 1: Open the Default Configset

```bash
open $(brew --prefix solr)/server/solr/configsets/_default/conf
```

---

### Step 2: Update `managed-schema.xml`

Add the following fields inside the `<schema>` tag:

```xml
<field name="title" type="text_general" indexed="true" stored="true" multiValued="true"/>
<field name="tags" type="text_general" indexed="true" stored="true" multiValued="true"/>
<field name="media_type" type="string" indexed="true" stored="true" multiValued="true"/>
<field name="media_src" type="string" indexed="true" stored="true" multiValued="true"/>
```

---

### Step 3: Update `solrconfig.xml`

Add the clustering search component:

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

Replace or update the `/select` request handler:

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

You can perform these steps automatically through `main.py` or manually:

```bash
solr restart -p 8983 \
    -Dsolr.modules=clustering \
    -Dsolr.clustering.enabled=true

solr zk upconfig \
    -n memes_collection.AUTOCREATED \
    -d $(brew --prefix solr)/server/solr/configsets/_default/conf

curl "http://localhost:8983/solr/admin/collections?action=RELOAD&name=memes_collection"
```
