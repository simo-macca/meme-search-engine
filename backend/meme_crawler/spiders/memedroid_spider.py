import uuid
import scrapy
from scrapy_playwright.page import PageMethod

class MemedroidSpider(scrapy.Spider):
    name = "memedroid_spider"

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'ROBOTSTXT_OBEY': False,
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            'headless': True,
            'args': ['--disable-blink-features=AutomationControlled'],
        },
        'PLAYWRIGHT_ABORT_REQUEST': lambda req: any(x in req.url for x in [
            "google-analytics", "doubleclick", "gumgum", "criteo", "pubmatic",
            "amazon-adsystem", "smilewanted", "adnxs", "rubiconproject"
        ]),
        'DOWNLOAD_DELAY': 2,
        'LOG_LEVEL': 'INFO',
    }

    def start_requests(self):
        start_page = 1
        end_page = 200

        for i in range(start_page, end_page + 1):
            url = f"https://www.memedroid.com/memes/trending?page={i}"

            self.logger.info(f"MemedroidSpider: Requesting page {i}...")

            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_selector", "div.gallery-memes-container article", timeout=15000),
                    ],
                },
                callback=self.parse
            )

    def parse(self, response):
        content_nodes = response.xpath(
            '//a[contains(@class, "gallery-image-link")]//img | //div[contains(@class, "gallery-video-container")]//video'
        )

        self.logger.info(f"MemedroidSpider page {response.url.split('=')[-1]}: Found {len(content_nodes)} items.")

        for node in content_nodes:
            card = node.xpath('./ancestor::article[contains(@class, "gallery-item")]')
            src = node.xpath('./@src').get() or node.xpath('./source/@srcset').get() or node.xpath('./@data-src').get()
            title = card.xpath('.//a[contains(@class, "item-header-title")]/text()').get()
            tags = card.xpath('.//div[contains(@class, "tags-container")]/a/text()').getall()

            if src:
                if title:
                    title = title.strip()

                try:
                    deterministic_id = str(uuid.uuid5(uuid.NAMESPACE_URL, str(src)))
                except ValueError:
                    deterministic_id = str(uuid.uuid4())

                yield {
                    "id": deterministic_id,
                    "media_type": "video" if "mp4" in str(src) else "image",
                    "title": title,
                    "media_src": src,
                    "tags": tags,
                }
