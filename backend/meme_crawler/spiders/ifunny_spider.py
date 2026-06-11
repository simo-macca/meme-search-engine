import uuid

import scrapy
from scrapy_playwright.page import PageMethod


class IFunnySpider(scrapy.Spider):
    name = "ifunny_spider"

    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    }

    async def start(self):
        scroll_actions = []
        times_to_scroll = 200

        self.logger.info(
            f"IFunnySpider: preparing to scroll the page {times_to_scroll} times. This might take a while..."
        )

        for i in range(times_to_scroll):
            scroll_actions.append(PageMethod("evaluate", "window.scrollTo(0, document.body.scrollHeight)"))
            scroll_actions.append(PageMethod("wait_for_timeout", 1500))
            self.logger.info(f"IFunnySpider: Scroll {i + 1}/{times_to_scroll}")

        self.logger.info("IFunnySpider: Downloading memes... this might take a while.")

        yield scrapy.Request(
            "https://ifunny.co/",
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "img[src*='images'], video", timeout=20000),
                    PageMethod("wait_for_timeout", 3000),
                    *scroll_actions,
                ],
            },
        )

    def parse(self, response):
        content_nodes = response.xpath('//img[contains(@src, "images")] | //video')

        self.logger.info(f"IFunnySpider: Finished scrolling. Found {len(content_nodes)} memes.")

        for node in content_nodes:
            card = node.xpath("./ancestor::div[3]")
            src = (
                node.xpath("./@src").get() or node.xpath("./source/@src").get() or node.xpath("./video/@data-src").get()
            )
            title = card.xpath(".//a[string-length(text()) > 1]/text()").get()
            tags = card.xpath(".//div//a//span/text()").getall()

            if src:
                deterministic_id = str(uuid.uuid5(uuid.NAMESPACE_URL, src))
                yield {
                    "id": deterministic_id,
                    "media_type": "video" if "mp4" in src else "image",
                    "title": title,
                    "media_src": src,
                    "tags": tags,
                }
