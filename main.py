import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

from crawler.wikipedia import wikipedia_crawler
from src.crawler.chatgpt_crawler import chatgpt_crawler
from src.constants.index import CRAWL4AI_DOC_BASE_URL
from src.configs.browser import base_browser_config

run_config = CrawlerRunConfig(
)

async def main():
    async with AsyncWebCrawler(config=base_browser_config) as crawler:
        result = await crawler.arun(
            url=CRAWL4AI_DOC_BASE_URL,
            config=run_config,
            
        )
        print(result.markdown[:300])  # Show the first 300 characters of extracted text

if __name__ == "__main__":
    # asyncio.run(main())
    asyncio.run(chatgpt_crawler(base_browser_config, "Latest new on indian stock market"))
    # asyncio.run(wikipedia_crawler())
