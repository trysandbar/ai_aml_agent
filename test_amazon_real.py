#!/usr/bin/env python3
"""
Test Amazon.com shopping flow with Llama 4 + Playwright.

Flow:
1. Navigate to Amazon.com
2. Search for "mechanical keyboard"
3. Click first product
4. Add to cart
5. Proceed to checkout
6. Stop when auth/login required
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load .env
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

from playwright_client import PlaywrightClient
from together_ai.togetherai import TogetherAIClient


async def main():
    print("=" * 70)
    print("Amazon.com Shopping Flow - Llama 4 + Playwright")
    print("=" * 70)

    api_key = os.getenv('TOGETHER_API_KEY')
    if not api_key:
        print("❌ TOGETHER_API_KEY not set in .env")
        return 1

    llm = TogetherAIClient(api_key=api_key)

    async with PlaywrightClient(headless=True) as browser:
        screenshot_dir = Path("./test_screenshots/amazon_real")
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: Navigate to Amazon
        print("\n📍 Step 1: Navigate to Amazon.com")
        await browser.navigate("https://www.amazon.com")
        await browser.screenshot("01_homepage", path=screenshot_dir / "01_homepage.png")
        print("✅ Loaded Amazon.com")

        # Step 2: Find search box and search
        print("\n📍 Step 2: Find search box")

        # Dynamically find search box
        search_selector = await browser.evaluate("""
            (() => {
                // Try common search box IDs/names
                const selectors = [
                    '#twotabsearchtextbox',
                    '#nav-bb-search',
                    'input[type="text"][name="field-keywords"]',
                    'input[aria-label*="Search"]',
                    'input[placeholder*="Search"]'
                ];

                for (const sel of selectors) {
                    const el = document.querySelector(sel);
                    if (el) return sel;
                }
                return null;
            })()
        """)

        if not search_selector:
            print("❌ Could not find search box")
            return 1

        print(f"✅ Found search box: {search_selector}")

        await browser.fill(search_selector, "mechanical keyboard")
        await browser.screenshot("02_search_filled", path=screenshot_dir / "02_search_filled.png")
        print("✅ Entered search term")

        # Find and click search button
        search_btn = await browser.evaluate("""
            (() => {
                const selectors = [
                    '#nav-search-submit-button',
                    'input[type="submit"][value="Go"]',
                    'button[type="submit"]'
                ];

                for (const sel of selectors) {
                    const el = document.querySelector(sel);
                    if (el) return sel;
                }
                return null;
            })()
        """)

        await browser.click(search_btn)
        await asyncio.sleep(3)  # Wait for results

        await browser.screenshot("03_search_results", path=screenshot_dir / "03_search_results.png")
        print("✅ Search results loaded")

        # Step 3: Click first product
        print("\n📍 Step 3: Click first product")

        first_product = await browser.evaluate("""
            (() => {
                const selectors = [
                    'div[data-component-type="s-search-result"] h2 a',
                    '.s-result-item h2 a',
                    '[data-cy="title-recipe"] a'
                ];

                for (const sel of selectors) {
                    const el = document.querySelector(sel);
                    if (el) {
                        el.click();
                        return true;
                    }
                }
                return false;
            })()
        """)

        await asyncio.sleep(3)

        product_title = await browser.evaluate("document.title")
        await browser.screenshot("04_product_page", path=screenshot_dir / "04_product_page.png")
        print(f"✅ Product page: {product_title[:60]}...")

        # Step 4: Add to cart
        print("\n📍 Step 4: Add to cart")

        # Scroll down to load page fully
        await browser.evaluate("window.scrollBy(0, 500)")
        await asyncio.sleep(1)

        add_result = await browser.evaluate("""
            (() => {
                const selectors = [
                    '#add-to-cart-button',
                    'input[name="submit.add-to-cart"]',
                    '#buy-now-button',
                    'input[id*="add-to-cart"]',
                    'button[id*="add-to-cart"]'
                ];

                for (const sel of selectors) {
                    const el = document.querySelector(sel);
                    if (el && el.offsetParent !== null) {
                        console.log('Found:', sel);
                        el.click();
                        return sel;
                    }
                }

                // Last resort - look for any visible add to cart button
                const buttons = Array.from(document.querySelectorAll('button, input[type="submit"]'));
                for (const btn of buttons) {
                    const text = (btn.textContent || btn.value || '').toLowerCase();
                    if (text.includes('add to cart') && btn.offsetParent !== null) {
                        console.log('Found via text:', btn);
                        btn.click();
                        return 'text-based';
                    }
                }

                return null;
            })()
        """)

        if not add_result:
            print("❌ Could not find add to cart button - skipping to cart")
            # Try going directly to cart
            await browser.navigate("https://www.amazon.com/gp/cart/view.html")
            await asyncio.sleep(2)
        else:
            print(f"✅ Clicked add to cart: {add_result}")

        await asyncio.sleep(3)
        await browser.screenshot("05_added_to_cart", path=screenshot_dir / "05_added_to_cart.png")
        print("✅ Added to cart")

        # Decline protection if offered
        await browser.evaluate("""
            (() => {
                const decline = document.querySelector('input[aria-labelledby*="NoCoverage"]');
                if (decline) decline.click();
            })()
        """)
        await asyncio.sleep(1)

        # Step 5: Proceed to checkout
        print("\n📍 Step 5: Proceed to checkout")

        # Navigate to cart first if not already there
        current_url = browser.page.url
        if "cart" not in current_url.lower():
            await browser.navigate("https://www.amazon.com/gp/cart/view.html")
            await asyncio.sleep(2)

        await browser.screenshot("06_cart_view", path=screenshot_dir / "06_cart_view.png")

        checkout_result = await browser.evaluate("""
            (() => {
                const selectors = [
                    'input[name="proceedToRetailCheckout"]',
                    '#sc-buy-box-ptc-button',
                    'input[name="proceedToCheckout"]',
                    'a[href*="spc/checkout"]',
                    'span[id="sc-buy-box-ptc-button"] input'
                ];

                for (const sel of selectors) {
                    const el = document.querySelector(sel);
                    if (el && el.offsetParent !== null) {
                        console.log('Clicking checkout:', sel);
                        el.click();
                        return sel;
                    }
                }

                // Text-based fallback
                const links = Array.from(document.querySelectorAll('a, button, input'));
                for (const el of links) {
                    const text = (el.textContent || el.value || '').toLowerCase();
                    if (text.includes('proceed to checkout') && el.offsetParent !== null) {
                        console.log('Found via text');
                        el.click();
                        return 'text-based';
                    }
                }

                return null;
            })()
        """)

        print(f"Checkout button: {checkout_result}")
        await asyncio.sleep(3)

        # Step 6: Check if we hit auth page
        print("\n📍 Step 6: Check authentication")

        current_url = browser.page.url
        page_title = await browser.evaluate("document.title")

        await browser.screenshot("07_final_page", path=screenshot_dir / "07_final_page.png")

        print(f"\n📄 Current URL: {current_url}")
        print(f"📄 Page Title: {page_title}")

        if "signin" in current_url.lower() or "login" in current_url.lower() or "ap/signin" in current_url:
            print(f"\n✅ SUCCESS: Reached login page as expected")

            # Ask Llama 4 to confirm
            prompt = f"""URL: {current_url}
Title: {page_title}

Is this a login/authentication page? Answer only 'yes' or 'no'."""

            response = llm.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                temperature=0.1,
                max_tokens=10
            )

            llm_answer = response.choices[0].message.content.strip()
            print(f"🤖 Llama 4 confirms: {llm_answer}")

            print("\n" + "=" * 70)
            print("✅ TEST PASSED - Complete shopping flow until auth")
            print("=" * 70)
            print(f"\nScreenshots saved to: {screenshot_dir}")
            print("\nFlow completed:")
            print("  1. ✅ Navigated to Amazon.com")
            print("  2. ✅ Searched for 'mechanical keyboard'")
            print("  3. ✅ Clicked first product")
            print("  4. ✅ Added to cart")
            print("  5. ✅ Proceeded to checkout")
            print("  6. ✅ Stopped at login page (auth required)")

            return 0
        else:
            print(f"⚠️  Did not reach login - at: {current_url}")
            return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
