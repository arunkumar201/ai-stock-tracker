from crawl4ai import BrowserConfig
import os

ENV_TYPE = os.getenv("ENV_TYPE") or "development"

base_browser_config = BrowserConfig(
    headless=False,  # Set to True for headless mode
    viewport_height=1080,
    viewport_width=1920,
   use_managed_browser=False,  # Use real browser instead of managed browser
    extra_args=[
        "--start-maximized",
    ],
    user_agent_mode="random",
 
)
