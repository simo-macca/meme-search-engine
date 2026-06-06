BOT_NAME = "AlSiBot"

SPIDER_MODULES = ["meme_crawler.spiders"]
NEWSPIDER_MODULE = "meme_crawler.spiders"

ADDONS = {}

# Enable the Playwright downloader
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

# IMPORTANT: This fixes issues on Windows and ensures async works correctly
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Optional: Set to False if you want to see the browser pop up (good for debugging)
PLAYWRIGHT_LAUNCH_OPTIONS = {
    "headless": True,
    "timeout": 20 * 1000,  # 20 seconds
    "args": ["--start-maximized", "--disable-blink-features=AutomationControlled"]
}


# USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

DEFAULT_REQUEST_HEADERS = {
   "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
   "Accept-Language": "en-US,en;q=0.9",
}

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Concurrency and throttling settings
CONCURRENT_REQUESTS_PER_DOMAIN = 1
DOWNLOAD_DELAY = 2
FEED_EXPORT_ENCODING = "utf-8"
