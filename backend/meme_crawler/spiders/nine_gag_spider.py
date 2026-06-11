import asyncio
import json
import logging

from playwright.async_api import Page, Response, async_playwright

logger = logging.getLogger(__name__)

API_PREFIX = "https://9gag.com/v1/feed-posts"


async def handle_cookie_banner(page: Page):
    logger.info("9GAGSpider: Checking for cookie banner...")

    selector = "button[title='Accept']"

    try:
        if await page.is_visible(selector):
            await page.click(selector)
            logger.info("9GAGSpider: Clicked cookies")
        await page.wait_for_timeout(2000)

        for frame in page.frames:
            try:
                btn = await frame.query_selector(selector)
                if btn:
                    await btn.click()
                    logger.info("9GAGSpider: Clicked cookies")
                    return
            except:
                continue

        logger.info("9GAGSpider: No cookie banner found (or already accepted).")

    except Exception as e:
        logger.warning(f"9GAGSpider: Warning: specific cookie error: {e}")


def parse_post_data(post: dict):
    try:
        images_data = post.get("images", {})

        return {
            "id": post.get("id"),
            "media_type": "image" if post.get("type") == "Photo" else "video",
            "title": post.get("title"),
            "media_src": images_data.get("image460sv", {}).get("url") or images_data.get("image460", {}).get("url"),
            "tags": [t["key"] for t in post.get("tags", [])],
        }
    except Exception as e:
        logger.error(f"9GAGSpider: Error parsing post {post.get('id')}: {e}")
        return None


async def run():
    memes = {}
    target_scrolls = 200

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])

        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        )
        page = await context.new_page()

        async def handle_response(response: Response):
            if API_PREFIX not in response.url or response.status != 200:
                return

            try:
                json_data = await response.json()

                if "data" not in json_data or "posts" not in json_data["data"]:
                    return

                new_posts = json_data["data"]["posts"]

                for post in new_posts:
                    parsed = parse_post_data(post)
                    if parsed and parsed["id"] not in memes:
                        memes[parsed["id"]] = parsed

            except Exception:
                pass

        page.on("response", handle_response)

        logger.info("9GAGSpider: Opening 9GAG...")
        await page.goto("https://9gag.com/", wait_until="domcontentloaded")

        await handle_cookie_banner(page)

        logger.info(f"9GAGSpider: Starting scroll loop ({target_scrolls} iterations)...")

        for i in range(target_scrolls):
            await page.keyboard.press("End")
            await page.wait_for_timeout(1000)

            logger.info(f"9GAGSpider: Scroll {i + 1}/{target_scrolls} - Memes found so far: {len(memes)}")

        logger.info("Saving memes...")
        output_file = "raw_data/9gag_memes.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(list(memes.values()), f, indent=2, ensure_ascii=False)

        logger.info(f"9GAGSpider: Saved {len(memes)} memes to {output_file}")

        await browser.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    asyncio.run(run())
