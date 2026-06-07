# WDYMEME – Meme Search Engine

Welcome to **WDYMEME**, a full-stack Information Retrieval (IR) system designed to crawl, process, index, and explore memes from popular online platforms. 

The project leverages a robust backend pipeline to scrape and ingest raw data into an Apache Solr server, while offering a modern, responsive Vue 3 frontend that supports advanced metadata filtering and real-time automated topic clustering using the Lingo algorithm.

---

## Repository Structure

The workspace is split into two independent decoupled directories:

```text
meme-search-engine/
├── backend/            # Scrapy Spiders, Data Deduplication & Solr Indexing
│   ├── meme_crawler/   # Spiders for 9GAG, iFunny, Memedroid, and Memes.com
│   ├── main.py         # Full backend pipeline orchestrator
│   └── README.md       # Backend installation & Solr clustering guide
│
├── frontend/           # Vue 3 User Interface
│   ├── src/            # Components, Views, Pinia Stores, and Assets
│   └── README.md       # Frontend execution & environment guide
│
└── README.md           # Root documentation (this file)

```

---

## System Overview & Requirements

Before running the application, ensure you have the following global dependencies installed:

* **Python 3.10+** (for executing backend scripts and web scrapers)
* **Node.js (v20 or higher)** (for building and serving the web UI)
* **Apache Solr (installed via Homebrew)** (used as the indexing and text-search engine)

### Quick Architecture Flow

1. **Scrape & Deduplicate:** The Python backend runs custom spiders to extract images, videos, captions, and tags, compiling them into clean, deduplicated JSON datasets.
2. **Index & Cluster:** The data is pushed to a global Apache Solr cloud instance. A modified schema enables the **Lingo** clustering algorithm to dynamically group search results by context and topics.
3. **Query & Display:** The Vue 3 frontend queries Solr's REST API endpoint to retrieve matches, handle pagination, and render an interactive topics map sidebar.

---

## Setup & Execution

For detailed, step-by-step installation logs, environment configurations, and core setup instructions, please refer to the documentation inside the respective subdirectories:

* To set up the web scrapers, local environment variables, and configure your Homebrew Apache Solr core, follow the [Backend Setup Guide](./backend/README.md).
* To configure and launch the Vite development server and view the UI, follow the [Frontend Setup Guide](./frontend/README.md).

---

## Authors

This project was designed, implemented, and maintained by:

- [Alessandra Sasanelli](https://github.com/Alessandra-Sasanelli)
- [Simone Maccario](https://www.google.com/search?q=https://github.com/SimoneMaccario)
