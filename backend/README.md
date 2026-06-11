# Backend Data Pipeline & Solr Orchestrator

This directory contains the automated Python pipeline responsible for data acquisition, cleaning, and search engine configuration.

It is designed to run as an ephemeral Docker container: it boots up, does its job, and cleanly exits once the data is safely stored inside Solr.

## Core Features

- **Headless Scraping:** Utilizes `Scrapy` and `Playwright` to navigate and extract data from Javascript-heavy meme websites (9GAG, iFunny, Memedroid, etc.).
- **Smart Data Caching:** Scraped data is stored locally in `raw_data/` and mapped to a Docker volume. To prevent massive unnecessary web scraping, a 7-day cache is implemented.
- **Automated Solr Configuration:** Replaces manual XML editing. It uses the Solr Config API to automatically create collections, define schemas, and inject the **Lingo Clustering Engine**.

## How the Caching Works

The `main.py` orchestrator includes a smart caching system to save time and bandwidth.

When you run Docker, the script checks `raw_data/scrape_metadata.json`. If the last scrape was less than 7 days ago, it **skips the spiders entirely** and proceeds directly to indexing the existing JSON files into Solr.

### Forcing a Re-Scrape

If you want to force the spiders to run immediately and fetch new memes:
1. Navigate to `backend/raw_data/`.
2. Delete the `scrape_metadata.json` file.
3. Restart the Docker container (`docker compose up`). The system will detect the missing metadata and trigger a fresh scrape.

## Local Development (Without Docker)

If you wish to test or modify the Python scripts locally on your machine:

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies and Playwright browsers:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. Run the pipeline (ensure Solr is running locally on port 8983):
   ```bash
   python main.py
   ```
