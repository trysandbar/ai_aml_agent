#!/usr/bin/env python3
"""
Save authenticated session for browser automation

Opens a browser window for manual login, then saves the session state
for reuse in automated workflows (bypasses Google bot detection).

Usage:
    python save_session.py --url https://app.dev.sandbar.ai --output sandbar_session.json
"""

import asyncio
import argparse
from pathlib import Path
from playwright.async_api import async_playwright


async def save_session(url: str, output_path: str, wait_time: int):
    """Open browser for manual login and save session state"""

    print(f"🌐 Opening browser for manual login to: {url}")
    print(f"📝 Session will be saved to: {output_path}")
    print()
    print("Instructions:")
    print("1. Complete the login process manually (including 2FA)")
    print("2. Navigate to the page where you want automation to start")
    print(f"3. Session will auto-save after {wait_time} seconds")
    print()

    async with async_playwright() as p:
        # Launch browser in headful mode for manual interaction
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Navigate to the login page
        await page.goto(url)

        # Wait for user to complete login manually
        print(f"⏳ Waiting {wait_time} seconds for you to complete login...")
        await asyncio.sleep(wait_time)

        # Save storage state (cookies, localStorage, sessionStorage)
        await context.storage_state(path=output_path)

        print(f"✅ Session saved to: {output_path}")
        print(f"🔍 Current URL: {page.url}")

        await browser.close()

    print()
    print(f"To use this session, add to your .env file:")
    print(f"STORAGE_STATE_PATH={output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Save authenticated browser session for automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Save Sandbar session
  python save_session.py --url https://app.dev.sandbar.ai --output sandbar_session.json

  # Save session for different site
  python save_session.py --url https://example.com/login --output example_session.json
        """
    )

    parser.add_argument(
        "--url",
        required=True,
        help="URL to navigate to for login"
    )

    parser.add_argument(
        "--output",
        default="session.json",
        help="Output path for saved session (default: session.json)"
    )

    parser.add_argument(
        "--wait",
        type=int,
        default=120,
        help="Seconds to wait before auto-saving session (default: 120)"
    )

    args = parser.parse_args()

    # Run the session saver
    asyncio.run(save_session(args.url, args.output, args.wait))


if __name__ == "__main__":
    main()
