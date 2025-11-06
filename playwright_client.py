"""
Playwright Browser Client

Headless browser automation using Playwright + Llama 4 (Together.AI).
This replaces MCP Puppeteer with a pure Python implementation.

Production features:
- Headless Chrome/Chromium automation
- Screenshot capture with base64 encoding
- Automatic screenshot saving to disk
- Full page and element-specific screenshots
- JavaScript execution
- Form filling, clicking, navigation
"""

import base64
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import asyncio

from playwright.async_api import async_playwright, Browser, Page, BrowserContext

logger = logging.getLogger(__name__)


class PlaywrightClient:
    """
    Playwright-based browser client for headless automation.

    Uses async/await for optimal performance.
    Integrates with BrowserAgent and Llama 4 decision making.
    """

    def __init__(self, headless: bool = True, browser_type: str = "chromium", storage_state: Optional[str] = None):
        """
        Initialize Playwright client.

        Args:
            headless: Run browser in headless mode (default: True)
            browser_type: Browser to use - chromium, firefox, or webkit (default: chromium)
            storage_state: Path to storage state file for auth persistence (optional)
        """
        self.headless = headless
        self.browser_type = browser_type
        self.storage_state = storage_state
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.current_url: Optional[str] = None

        logger.info(f"🌐 Playwright Client initialized (headless={headless}, browser={browser_type}, storage_state={storage_state})")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def start(self):
        """Start the browser instance."""
        try:
            logger.info("🚀 Starting Playwright browser...")

            self.playwright = await async_playwright().start()

            # Get the appropriate browser
            if self.browser_type == "chromium":
                browser_launcher = self.playwright.chromium
            elif self.browser_type == "firefox":
                browser_launcher = self.playwright.firefox
            elif self.browser_type == "webkit":
                browser_launcher = self.playwright.webkit
            else:
                raise ValueError(f"Unknown browser type: {self.browser_type}")

            # Launch browser with production settings
            self.browser = await browser_launcher.launch(
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',  # Overcome limited resource problems
                    '--disable-blink-features=AutomationControlled'  # Avoid detection
                ]
            )

            # Create browser context (isolated session)
            context_options = {
                'viewport': {'width': 1280, 'height': 800},
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }

            # Load storage state if provided and file exists
            if self.storage_state and Path(self.storage_state).exists():
                context_options['storage_state'] = self.storage_state
                logger.info(f"📂 Loading auth state from {self.storage_state}")

            self.context = await self.browser.new_context(**context_options)

            # Create page
            self.page = await self.context.new_page()

            logger.info("✅ Browser started successfully")

        except Exception as e:
            logger.error(f"❌ Failed to start browser: {e}")
            raise

    async def save_storage_state(self, path: str):
        """
        Save current authentication state to file.

        Args:
            path: Path to save storage state JSON file
        """
        try:
            if not self.context:
                raise RuntimeError("Browser context not available")

            await self.context.storage_state(path=path)
            logger.info(f"💾 Saved auth state to {path}")

        except Exception as e:
            logger.error(f"❌ Failed to save storage state: {e}")
            raise

    async def close(self):
        """Close the browser instance."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()

            logger.info("🛑 Browser closed")

        except Exception as e:
            logger.error(f"❌ Error closing browser: {e}")

    async def navigate(self, url: str, wait_until: str = "networkidle") -> bool:
        """
        Navigate to a URL.

        Args:
            url: URL to navigate to
            wait_until: Wait condition - 'load', 'domcontentloaded', 'networkidle', or 'commit'

        Returns:
            True if successful
        """
        try:
            if not self.page:
                raise RuntimeError("Browser not started. Call start() first.")

            logger.info(f"🔗 Navigating to: {url}")

            await self.page.goto(url, wait_until=wait_until, timeout=30000)
            self.current_url = url

            logger.info(f"✅ Navigation complete: {url}")
            return True

        except Exception as e:
            logger.error(f"❌ Navigation failed: {e}")
            return False

    async def screenshot(self, name: str, path: Optional[Path] = None,
                        selector: Optional[str] = None,
                        full_page: bool = False,
                        save_metadata: bool = True,
                        tenant_slug: Optional[str] = None,
                        session_id: Optional[str] = None) -> Optional[str]:
        """
        Take a screenshot and return as base64.

        Args:
            name: Name for the screenshot
            path: Optional path to save screenshot to disk (overrides tenant/session structure)
            selector: Optional CSS selector to screenshot specific element
            full_page: Capture full scrollable page (default: False)
            save_metadata: Save JSON metadata file with URL, timestamp, etc. (default: True)
            tenant_slug: Tenant identifier for S3-ready directory structure
            session_id: Session identifier for organizing screenshots

        Returns:
            Screenshot as base64 string, or None if failed
        """
        try:
            if not self.page:
                raise RuntimeError("Browser not started")

            logger.info(f"📸 Taking screenshot: {name}")

            # Get current page info for metadata
            from datetime import datetime, timezone
            import json

            current_url = self.page.url
            page_title = await self.page.title()
            viewport_size = self.page.viewport_size

            # Take screenshot
            if selector:
                # Element-specific screenshot
                element = await self.page.query_selector(selector)
                if not element:
                    logger.error(f"Element not found: {selector}")
                    return None
                screenshot_bytes = await element.screenshot()
            else:
                # Full page or viewport screenshot
                screenshot_bytes = await self.page.screenshot(full_page=full_page)

            # Determine save path using S3-ready structure or explicit path
            save_path = path
            if not save_path and tenant_slug and session_id:
                # Use S3-ready directory structure: ai_agent_audit/{tenant}/{session}/screenshots/
                base_dir = Path("ai_agent_audit") / tenant_slug / session_id / "screenshots"
                save_path = base_dir / f"{name}.png"

            # Save to disk if path determined
            if save_path:
                save_path.parent.mkdir(parents=True, exist_ok=True)
                with open(save_path, 'wb') as f:
                    f.write(screenshot_bytes)
                logger.info(f"📸 Screenshot saved to disk: {save_path} ({len(screenshot_bytes)} bytes)")

                # Save metadata JSON alongside screenshot
                if save_metadata:
                    metadata = {
                        "screenshot_name": name,
                        "screenshot_path": str(save_path),
                        "screenshot_size_bytes": len(screenshot_bytes),
                        "url": current_url,
                        "page_title": page_title,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "viewport": viewport_size,
                        "full_page": full_page,
                        "selector": selector,
                        "browser": "chromium",
                        "headless": self.headless,
                        "tenant_slug": tenant_slug,
                        "session_id": session_id
                    }

                    metadata_path = save_path.with_suffix('.json')
                    with open(metadata_path, 'w') as f:
                        json.dump(metadata, f, indent=2)
                    logger.info(f"📋 Metadata saved: {metadata_path}")

            # Convert to base64
            screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            screenshot_data_uri = f"data:image/png;base64,{screenshot_base64}"

            logger.info(f"✅ Screenshot captured: {name} ({len(screenshot_bytes)} bytes) at {current_url}")
            return screenshot_data_uri

        except Exception as e:
            logger.error(f"❌ Screenshot failed: {e}")
            return None

    async def click(self, selector: str, timeout: int = 30000) -> bool:
        """
        Click an element on the page.

        Args:
            selector: CSS selector for element to click
            timeout: Maximum time to wait for element (ms)

        Returns:
            True if successful
        """
        try:
            if not self.page:
                raise RuntimeError("Browser not started")

            logger.info(f"🖱️  Clicking: {selector}")

            await self.page.click(selector, timeout=timeout)

            logger.info(f"✅ Click complete: {selector}")
            return True

        except Exception as e:
            logger.error(f"❌ Click failed: {e}")
            return False

    async def fill(self, selector: str, value: str, timeout: int = 30000) -> bool:
        """
        Fill an input field.

        Args:
            selector: CSS selector for input field
            value: Value to fill
            timeout: Maximum time to wait for element (ms)

        Returns:
            True if successful
        """
        try:
            if not self.page:
                raise RuntimeError("Browser not started")

            logger.info(f"✍️  Filling '{selector}' with: {value[:50]}...")

            await self.page.fill(selector, value, timeout=timeout)

            logger.info(f"✅ Fill complete: {selector}")
            return True

        except Exception as e:
            logger.error(f"❌ Fill failed: {e}")
            return False

    async def select_option(self, selector: str, value: str, timeout: int = 30000) -> bool:
        """
        Select an option from a dropdown.

        Args:
            selector: CSS selector for select element
            value: Value to select
            timeout: Maximum time to wait for element (ms)

        Returns:
            True if successful
        """
        try:
            if not self.page:
                raise RuntimeError("Browser not started")

            logger.info(f"🔽 Selecting '{value}' in: {selector}")

            await self.page.select_option(selector, value, timeout=timeout)

            logger.info(f"✅ Select complete: {selector}")
            return True

        except Exception as e:
            logger.error(f"❌ Select failed: {e}")
            return False

    async def hover(self, selector: str, timeout: int = 30000) -> bool:
        """
        Hover over an element.

        Args:
            selector: CSS selector for element to hover
            timeout: Maximum time to wait for element (ms)

        Returns:
            True if successful
        """
        try:
            if not self.page:
                raise RuntimeError("Browser not started")

            logger.info(f"👆 Hovering: {selector}")

            await self.page.hover(selector, timeout=timeout)

            logger.info(f"✅ Hover complete: {selector}")
            return True

        except Exception as e:
            logger.error(f"❌ Hover failed: {e}")
            return False

    async def evaluate(self, script: str) -> Optional[Any]:
        """
        Execute JavaScript in the browser console.

        Args:
            script: JavaScript code to execute

        Returns:
            Result of the script execution
        """
        try:
            if not self.page:
                raise RuntimeError("Browser not started")

            logger.info(f"⚙️  Evaluating JS: {script[:100]}...")

            result = await self.page.evaluate(script)

            logger.info(f"✅ Evaluation complete")
            return result

        except Exception as e:
            logger.error(f"❌ Evaluation failed: {e}")
            return None

    async def wait_for_selector(self, selector: str, state: str = "visible",
                               timeout: int = 30000) -> bool:
        """
        Wait for an element to reach a specific state.

        Args:
            selector: CSS selector to wait for
            state: State to wait for - 'attached', 'detached', 'visible', 'hidden'
            timeout: Maximum time to wait (ms)

        Returns:
            True if element reached the state
        """
        try:
            if not self.page:
                raise RuntimeError("Browser not started")

            logger.info(f"⏳ Waiting for '{selector}' to be {state}...")

            await self.page.wait_for_selector(selector, state=state, timeout=timeout)

            logger.info(f"✅ Element ready: {selector}")
            return True

        except Exception as e:
            logger.error(f"❌ Wait failed: {e}")
            return False

    async def get_page_content(self) -> Optional[str]:
        """
        Get the full HTML content of the current page.

        Returns:
            HTML content as string
        """
        try:
            if not self.page:
                raise RuntimeError("Browser not started")

            content = await self.page.content()
            return content

        except Exception as e:
            logger.error(f"❌ Failed to get page content: {e}")
            return None

    async def get_text(self, selector: str) -> Optional[str]:
        """
        Get text content of an element.

        Args:
            selector: CSS selector

        Returns:
            Text content of the element
        """
        try:
            if not self.page:
                raise RuntimeError("Browser not started")

            text = await self.page.text_content(selector)
            return text

        except Exception as e:
            logger.error(f"❌ Failed to get text: {e}")
            return None

    async def get_cookies(self) -> List[Dict[str, Any]]:
        """
        Get all cookies for the current context.

        Returns:
            List of cookie dictionaries
        """
        try:
            if not self.context:
                raise RuntimeError("Browser not started")

            cookies = await self.context.cookies()
            return cookies

        except Exception as e:
            logger.error(f"❌ Failed to get cookies: {e}")
            return []

    async def set_cookies(self, cookies: List[Dict[str, Any]]):
        """
        Set cookies for the current context.

        Args:
            cookies: List of cookie dictionaries
        """
        try:
            if not self.context:
                raise RuntimeError("Browser not started")

            await self.context.add_cookies(cookies)
            logger.info(f"✅ Set {len(cookies)} cookies")

        except Exception as e:
            logger.error(f"❌ Failed to set cookies: {e}")


# Synchronous wrapper for easier integration
class SyncPlaywrightClient:
    """
    Synchronous wrapper around PlaywrightClient.

    Provides blocking API for simpler integration with BrowserAgent.
    """

    def __init__(self, headless: bool = True, browser_type: str = "chromium"):
        self.client = PlaywrightClient(headless=headless, browser_type=browser_type)
        self.loop = None

    def _run_async(self, coro):
        """Run async coroutine in event loop."""
        if self.loop is None:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        return self.loop.run_until_complete(coro)

    def start(self):
        """Start the browser."""
        return self._run_async(self.client.start())

    def close(self):
        """Close the browser."""
        return self._run_async(self.client.close())

    def navigate(self, url: str, wait_until: str = "networkidle") -> bool:
        """Navigate to URL."""
        return self._run_async(self.client.navigate(url, wait_until))

    def screenshot(self, name: str, path: Optional[Path] = None,
                  selector: Optional[str] = None, full_page: bool = False,
                  tenant_slug: Optional[str] = None, session_id: Optional[str] = None) -> Optional[str]:
        """Take screenshot."""
        return self._run_async(self.client.screenshot(name, path, selector, full_page,
                                                       tenant_slug=tenant_slug, session_id=session_id))

    def click(self, selector: str, timeout: int = 30000) -> bool:
        """Click element."""
        return self._run_async(self.client.click(selector, timeout))

    def fill(self, selector: str, value: str, timeout: int = 30000) -> bool:
        """Fill input field."""
        return self._run_async(self.client.fill(selector, value, timeout))

    def select_option(self, selector: str, value: str, timeout: int = 30000) -> bool:
        """Select dropdown option."""
        return self._run_async(self.client.select_option(selector, value, timeout))

    def hover(self, selector: str, timeout: int = 30000) -> bool:
        """Hover over element."""
        return self._run_async(self.client.hover(selector, timeout))

    def evaluate(self, script: str) -> Optional[Any]:
        """Execute JavaScript."""
        return self._run_async(self.client.evaluate(script))

    def wait_for_selector(self, selector: str, state: str = "visible",
                         timeout: int = 30000) -> bool:
        """Wait for element."""
        return self._run_async(self.client.wait_for_selector(selector, state, timeout))

    def get_page_content(self) -> Optional[str]:
        """Get page HTML."""
        return self._run_async(self.client.get_page_content())

    def get_text(self, selector: str) -> Optional[str]:
        """Get element text."""
        return self._run_async(self.client.get_text(selector))

    def get_cookies(self) -> List[Dict[str, Any]]:
        """Get cookies."""
        return self._run_async(self.client.get_cookies())

    def set_cookies(self, cookies: List[Dict[str, Any]]):
        """Set cookies."""
        return self._run_async(self.client.set_cookies(cookies))
