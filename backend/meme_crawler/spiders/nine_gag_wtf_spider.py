import asyncio
import json
import os
import logging
from playwright.async_api import async_playwright, Page

logger = logging.getLogger(__name__)

AD_BLOCK_LIST = [
    "google-analytics.com", "googletagservices.com", "googlesyndication.com",
    "amazon-adsystem.com", "adnxs.com", "doubleclick.net", "facebook.net"
]

async def handle_cookie_banner(page: Page):
    logger.info("Checking for cookie banner...")
    selector = "button[title='Accept']"
    await page.wait_for_timeout(3000)
    try:
        for frame in page.frames:
            if await frame.query_selector(selector):
                await frame.click(selector)
                logger.info("Clicked cookies in iframe")
                return
        if await page.is_visible(selector):
            await page.click(selector)
            logger.info("Clicked cookies on main page")
    except Exception:
        pass

async def scrape_visible_articles(page: Page, memes_dict: dict):
    articles = await page.query_selector_all("article")
    for article in articles:
        try:
            raw_id = await article.get_attribute("id")
            if not raw_id or raw_id in memes_dict:
                continue

            title_el = await article.query_selector("h1, h2")
            title = await title_el.inner_text() if title_el else ""

            tag_elements = await article.query_selector_all("a[href*='/tag/']")
            tags = [(await t.inner_text()).strip().lstrip('#') for t in tag_elements]

            video_el = await article.query_selector("video source")
            img_el = await article.query_selector("img.post-img, .image-container img")

            if video_el:
                media_src = await video_el.get_attribute("src")
                media_type = "video"
            elif img_el:
                media_src = await img_el.get_attribute("src")
                media_type = "image"
            else:
                continue

            if media_src:
                memes_dict[raw_id] = {
                    "id": raw_id.replace("jsid-", ""),
                    "title": title.strip(),
                    "media_type": media_type,
                    "media_src": media_src,
                    "tags": list(set(tags))
                }
        except:
            continue

async def run():
    memes = {}
    target_scrolls = 100
    output_file = "raw_data/9gag_memes_wtf.json"

    if not os.path.exists("raw_data"):
        os.makedirs("raw_data")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 1000},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        page = await context.new_page()
        await page.route("**/*", lambda route: route.abort()
        if any(ad in route.request.url for ad in AD_BLOCK_LIST)
        else route.continue_())

        logger.info("Opening 9GAG WTF...")
        await page.goto("https://9gag.com/interest/wtf", wait_until="domcontentloaded")
        await handle_cookie_banner(page)

        last_count = 0
        stuck_count = 0

        for i in range(target_scrolls):
            await scrape_visible_articles(page, memes)
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(3000)

            current_count = len(memes)
            logger.info(f"9GAGSpider WTF: Scroll {i + 1} - Memes found so far: {current_count}")

            if current_count == last_count:
                stuck_count += 1
                if stuck_count >= 3:
                    logger.warning("Page seems stuck, nudging...")
                    await page.mouse.wheel(0, -500)
                    await page.wait_for_timeout(1000)
                    await page.keyboard.press("End")
                    stuck_count = 0
            else:
                stuck_count = 0

            last_count = current_count

        logger.info("Saving memes...")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(list(memes.values()), f, indent=2, ensure_ascii=False)

        logger.info(f"9GAGSpider WTF: Saved {len(memes)} memes to {output_file}")

        await browser.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    asyncio.run(run())
