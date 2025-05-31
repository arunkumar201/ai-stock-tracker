from crawl4ai import AsyncWebCrawler, CrawlResult, CrawlerRunConfig, CacheMode
import os
from base64 import b64decode

from crawl4ai.async_webcrawler import RunManyReturn

from ..constants.index import CHATGPT_BASE_URL
from crawl4ai import BrowserConfig
from ..js_scripts.chatgpt import get_chatgpt_scripts
from typing import Optional
import json
from bs4 import BeautifulSoup
import re
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import BM25ContentFilter

def get_markdown_generator(prompt: str):
    bm25_filter = BM25ContentFilter(
    user_query=prompt,
    bm25_threshold=1.2,
    )

    return DefaultMarkdownGenerator(
       content_source="cleaned_html",
       content_filter=bm25_filter,
        options={
            "ignore_links": False,
            "preserve_headers": True,
            "preserve_lists": True,
            "preserve_code_blocks": True
        }
    )

async def chatgpt_crawler(
    base_browser_config: BrowserConfig,
    prompt: Optional[str] = None,
    wait_seconds: int = 40
):
    if not prompt:
        raise ValueError("Prompt is required")

    print(f"Submitting prompt to ChatGPT: {prompt[:50]}...")
    
    chatgpt_script = get_chatgpt_scripts(prompt)
    
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
    wait_for="css:[data-testid*='conversation-turn-'], .markdown, div[class*='flex flex-col px-3 py-2']",
        delay_before_return_html=wait_seconds,
        magic=True,
        adjust_viewport_to_content=True,
        simulate_user=True,
        capture_console_messages=True,
        scan_full_page=True,
        scroll_delay=0.3,
        override_navigator=True,
        remove_overlay_elements=True,
        js_code=chatgpt_script,
        pdf=True,
        screenshot=True,
        user_agent_mode="random",
        prettiify=True,
        markdown_generator=get_markdown_generator(prompt),
    )
    
    # Run the crawler
    async with AsyncWebCrawler(config=base_browser_config) as crawler:
        result: CrawlResult = await crawler.arun(
            url=CHATGPT_BASE_URL,
            config=run_config,
        )

        # Process results
        markdown = result.markdown
        reference_links = result.links
        print("reference_links", reference_links)
        print("Response received, saving files...")

        # Save PDF and screenshot
        output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "public", "chatgpt")
        os.makedirs(output_dir, exist_ok=True)

        # Create a filesystem-safe filename from the prompt
        prompt_slug = "".join(c if c.isalnum() or c in "-_ " else "_" for c in prompt.lower())
        prompt_slug = "-".join(prompt_slug.split())[:50]  # Limit length

        # Save references to JSON
        if reference_links:
            references_path = os.path.join(output_dir, f"{prompt_slug}_references.json")
            with open(references_path, "w") as f:
                json.dump(reference_links, f, indent=2)
            print(f"Saved references to: {references_path}")

        # Save markdown
        markdown_path = os.path.join(output_dir, f"{prompt_slug}.md")
        with open(markdown_path, "w") as f:
            f.write(markdown)
        print(f"Saved markdown to: {markdown_path}")

        # Save PDF and screenshot
        if result.pdf:
            pdf_path = os.path.join(output_dir, f"{prompt_slug}.pdf")
            with open(pdf_path, "wb") as f:
                f.write(result.pdf)
            print(f"Saved PDF to: {pdf_path}")

        if hasattr(result, 'screenshot') and result.screenshot:
            screenshot_path = os.path.join(output_dir, f"{prompt_slug}.png")
            with open(screenshot_path, "wb") as f:
                f.write(b64decode(result.screenshot))
            print(f"Saved screenshot to: {screenshot_path}")
        
    

        return markdown
