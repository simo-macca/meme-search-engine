# Meme Search Engine

![Vue.js](https://img.shields.io/badge/Vue.js-35495E?style=for-the-badge&logo=vue.js&logoColor=4FC08D)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Apache Solr](https://img.shields.io/badge/Apache_Solr-D9411E?style=for-the-badge&logo=apache&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)

A full-stack Information Retrieval system dedicated to scraping, clustering, and searching memes. Built by Alessandra Sasanelli and Simone Maccario, this project uses a Python-based data pipeline to scrape meme platforms, Apache Solr for advanced full-text indexing and Lingo clustering, and a modern Vue.js frontend for a seamless user experience.

## Architecture Overview

The system is fully containerized and consists of three main microservices:

1. **Apache Solr (Backend Search Engine):** Runs in cloud mode with the Lingo clustering algorithm enabled natively.
2. **Python Data Pipeline (Backend Automator):** A headless orchestrator that scrapes data using Playwright/Scrapy, deduplicates it, configures the Solr schema via API, and indexes the documents.
3. **Vue.js + Nginx (Frontend):** A reactive user interface served by Nginx. Nginx also acts as a reverse proxy to Solr, eliminating CORS policies by keeping the UI and API on the same domain.

## Quickstart (Docker)

You do not need to install Python, Node.js, or Solr on your local machine. Docker handles everything.

1. Clone the repository:
   ```bash
   git clone git@github.com:simo-macca/meme-search-engine.git
   cd meme-search-engine
    ```

2. Start the entire ecosystem:
    ```bash
    docker compose up --build
    ```

3. Access the application:
   * **Frontend:** [http://localhost:8080](https://www.google.com/search?q=http://localhost:8080)
   * **Solr Admin UI:** [http://localhost:8983](https://www.google.com/search?q=http://localhost:8983)

*Note: On the very first run, the Python backend will launch headless spiders to scrape data. This will take some time. Subsequent runs will use local caching and boot instantly.*

## Project Structure

```text
meme-search-engine/
├── backend/            # Python scraping pipeline, schemas, and Solr setup scripts
├── frontend/           # Vue.js user interface and Nginx proxy configuration
├── docker-compose.yml
└── README.md
```
