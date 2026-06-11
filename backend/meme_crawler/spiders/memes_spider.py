import json

import scrapy


class MemesSpider(scrapy.Spider):
    name = "memes_spider"

    def start_requests(self):
        page = 1
        url = f"https://api.memes.com/api/trending/feed?page={page}"

        yield scrapy.Request(
            url,
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps({}),
            meta={"page": page},
            callback=self.parse,
        )

    def parse(self, response):
        page = response.meta["page"]
        data = json.loads(response.text)

        posts = data.get("posts", [])

        # Stop when no more posts
        if not posts:
            self.logger.info("No more posts. Finished.")
            return

        # Yield posts
        for post in posts:
            yield {
                "id": post.get("id"),
                "media_type": "image",
                "title": post.get("postText"),
                "media_src": f"https://cdn.memes.com/{post.get('path')}",
                "tags": [],
            }

        # Next page
        next_page = page + 1
        next_url = f"https://api.memes.com/api/trending/feed?page={next_page}"

        yield scrapy.Request(
            next_url,
            method="POST",
            headers={"Content-Type": "application/json"},
            body=json.dumps({}),
            meta={"page": next_page},
            callback=self.parse,
        )
