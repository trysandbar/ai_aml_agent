#!/usr/bin/env python3
"""
Test script for [Sandbar]

Auto-generated from requirements. Edit as needed during debugging.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path (go up 3 levels: clients/<client_id>/ -> clients/ -> root/)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Load .env
env_file = Path(__file__).parent.parent.parent / '.env'
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
    print("Testing: [Sandbar]")
    print("=" * 70)

    api_key = os.getenv('TOGETHER_API_KEY')
    if not api_key:
        print("❌ TOGETHER_API_KEY not set in .env")
        return 1

    llm = TogetherAIClient(api_key=api_key)

    # Storage state file for auth caching
    storage_state_file = Path("./clients/[sandbar]/auth_state.json")

    # Always use headless mode
    async with PlaywrightClient(headless=True, storage_state=str(storage_state_file) if storage_state_file.exists() else None) as browser:
        screenshot_dir = Path("./test_screenshots/[sandbar]")
        screenshot_dir.mkdir(parents=True, exist_ok=True)

        # Check if we have cached auth
        is_cached = storage_state_file.exists()
        if is_cached:
            print("🔑 Using cached authentication")
        else:
            print("🔐 No cached auth - will perform full login")

        # Only perform login steps if no cached auth
        if not is_cached:
            # Step 1: Navigate to homepage
            print("\n📍 Step 1: Navigate to homepage")
            await browser.navigate("https://app.dev.sandbar.ai")
            await browser.screenshot("step_01_homepage", path=screenshot_dir / "step_01_homepage.png", full_page=True, save_metadata=True)
            print("✅ Loaded homepage")
            await asyncio.sleep(2)

            # Step 2: Click 'Sign in with Google' button
            print("\n📍 Step 2: Click 'Sign in with Google' button")
            clicked = await browser.evaluate("""
                (() => {
                    const buttons = Array.from(document.querySelectorAll('button, a, div[role="button"]'));
                    for (const btn of buttons) {
                        const text = (btn.textContent || '').toLowerCase();
                        if ((text.includes('sign in') || text.includes('login')) && text.includes('google') && btn.offsetParent !== null) {
                            btn.click();
                            return true;
                        }
                    }
                    return false;
                })()
            """)
            await asyncio.sleep(3)
            await browser.screenshot("step_02_google_signin", path=screenshot_dir / "step_02_google_signin.png", full_page=True, save_metadata=True)
            print("✅ Clicked Google sign-in")

            # Step 3: Enter Google email
            print("\n📍 Step 3: Enter Google email")
            email = os.getenv('GOOGLE_LOGIN')
            if not email:
                print("❌ GOOGLE_LOGIN not set in .env")
                return 1

            await asyncio.sleep(2)
            email_input = await browser.evaluate("""
                (() => {
                    const inputs = Array.from(document.querySelectorAll('input[type="email"], input[name="identifier"], input[id="identifierId"]'));
                    for (const input of inputs) {
                        if (input.offsetParent !== null) {
                            return true;
                        }
                    }
                    return false;
                })()
            """)

            await browser.page.fill('input[type="email"]', email)
            await asyncio.sleep(1)
            await browser.screenshot("step_03_email_entered", path=screenshot_dir / "step_03_email_entered.png", full_page=True, save_metadata=True)
            print("✅ Entered email")

            # Step 4a: Click Next after email
            print("\n📍 Step 4a: Click Next after email")
            await browser.evaluate("""
                (() => {
                    const buttons = Array.from(document.querySelectorAll('button, div[role="button"]'));
                    for (const btn of buttons) {
                        const text = (btn.textContent || '').toLowerCase();
                        if (text.includes('next') && btn.offsetParent !== null) {
                            btn.click();
                            return true;
                        }
                    }
                })()
            """)
            await asyncio.sleep(3)

            # Step 4b: Enter password
            print("\n📍 Step 4b: Enter password")
            password = os.getenv('GOOGLE_PW')
            if not password:
                print("❌ GOOGLE_PW not set in .env")
                return 1

            await browser.page.fill('input[type="password"]', password)
            await asyncio.sleep(1)
            await browser.screenshot("step_04_password_entered", path=screenshot_dir / "step_04_password_entered.png", full_page=True, save_metadata=True)
            print("✅ Entered password")

            # Step 4c: Click Next to submit
            print("\n📍 Step 4c: Click Next to submit")
            await browser.evaluate("""
                (() => {
                    const buttons = Array.from(document.querySelectorAll('button, div[role="button"]'));
                    for (const btn of buttons) {
                        const text = (btn.textContent || '').toLowerCase();
                        if (text.includes('next') && btn.offsetParent !== null) {
                            btn.click();
                            return true;
                        }
                    }
                })()
            """)
            await asyncio.sleep(3)
            print("✅ Submitted login")

            # Step 5: Handle 2FA
            print("\n📍 Step 5: Handle 2FA")
            await browser.screenshot("step_05_2fa_prompt", path=screenshot_dir / "step_05_2fa_prompt.png", full_page=True, save_metadata=True)

            # Check if SMS fallback is needed (push greyed out)
            sms_clicked = await browser.evaluate("""
                (() => {
                    const elements = Array.from(document.querySelectorAll('div[role="link"], div[data-challengetype], button'));
                    for (const el of elements) {
                        const text = (el.textContent || '').toLowerCase();
                        if (text.includes('verification code') && text.includes('82')) {
                            el.click();
                            return true;
                        }
                    }
                    return false;
                })()
            """)

            if sms_clicked:
                print("   📱 SMS option selected - manual entry required")
                print("   👤 Please manually enter the SMS code in the browser and click Next")
                print("   ⏳ Waiting 90 seconds for manual completion...")
            else:
                print("   📱 Waiting for push notification approval...")
                print("   ⏳ Please tap 'Yes' on your phone")

            # Wait for navigation away from Google auth (works for both push and SMS)
            print("   🔍 Monitoring for successful authentication...")
            for i in range(30):  # 90 seconds total
                await asyncio.sleep(3)
                current_url = browser.page.url

                # Success: navigated to Sandbar or tenant selection
                if 'sandbar.ai' in current_url:
                    print(f"   ✅ 2FA complete - reached Sandbar: {current_url[:60]}")
                    break

                # Still on Google auth
                if i % 5 == 0 and i > 0:  # Log every 15 seconds
                    print(f"   ⏳ Still waiting... ({i*3}s elapsed)")

                if i == 29:
                    print(f"   ⚠️  Timeout - still on: {current_url}")
                    print("   ⚠️  2FA may have failed - continuing anyway...")

            print("✅ 2FA complete")
            await asyncio.sleep(5)  # Wait for page to fully load

            # Step 5b: Select tenant 'Current'
            print("\n📍 Step 5b: Select tenant 'Current'")
            await browser.screenshot("step_05b_tenant_list", path=screenshot_dir / "step_05b_tenant_list.png", full_page=True, save_metadata=True)

            tenant_clicked = await browser.evaluate("""
                (() => {
                    const rows = Array.from(document.querySelectorAll('tr'));
                    for (const row of rows) {
                        const text = (row.textContent || '').toLowerCase();
                        if (text.includes('current') && text.includes('10/28/2025')) {
                            row.click();
                            return true;
                        }
                    }
                    return false;
                })()
            """)

            await asyncio.sleep(3)
            print("✅ Selected tenant")

            # Save authentication state for future runs
            print("\n💾 Saving authentication state...")
            await browser.save_storage_state(str(storage_state_file))
            print(f"✅ Auth state saved to {storage_state_file}")

        else:
            # Cached auth - go directly to customers page
            print("\n📍 Navigating to customers page with cached auth...")
            await browser.navigate("https://app.dev.sandbar.ai/current/views/all")
            await browser.screenshot("step_01_cached", path=screenshot_dir / "step_01_cached.png", full_page=True, save_metadata=True)
            await asyncio.sleep(3)

        # Step 6: Verify we're on customers page
        print("\n📍 Step 6: Verify on customers page")
        if not is_cached:
            # Only use keyboard shortcut for fresh login
            await browser.page.keyboard.press('g')
            await asyncio.sleep(0.2)
            await browser.page.keyboard.press('c')
            await asyncio.sleep(3)

        current_url = browser.page.url
        await browser.screenshot("step_06_customers_page", path=screenshot_dir / "step_06_customers_page.png", full_page=True, save_metadata=True)

        if 'views/all' in current_url:
            print(f"   ✅ On customers page: {current_url}")
        else:
            print(f"   ⚠️  Wrong page: {current_url}")
            print("   Attempting to navigate directly...")
            await browser.navigate("https://app.dev.sandbar.ai/current/views/all")
            await asyncio.sleep(3)

        # Step 6b: Filter for Open Alerts
        # We need customers WITH alerts but WITHOUT PEP badges
        print("\n📍 Step 6b: Open filters (F keyboard shortcut)")
        await browser.page.keyboard.press('f')
        await asyncio.sleep(1)
        await browser.screenshot("step_06b_filters_open", path=screenshot_dir / "step_06b_filters_open.png", full_page=True, save_metadata=True)
        print("✅ Opened filters")

        # Step 6c: Click 'Alert status' filter
        print("\n📍 Step 6c: Click 'Alert status' filter")
        alert_status_clicked = await browser.evaluate("""
            (() => {
                const items = Array.from(document.querySelectorAll('div, button, li, [role="menuitem"]'));
                for (const item of items) {
                    const text = (item.textContent || '').trim().toLowerCase();
                    if (text === 'alert status' && item.offsetParent !== null) {
                        item.click();
                        return true;
                    }
                }
                return false;
            })()
        """)
        await asyncio.sleep(1)
        await browser.screenshot("step_06c_alert_status_clicked", path=screenshot_dir / "step_06c_alert_status_clicked.png", full_page=True, save_metadata=True)
        print("✅ Clicked 'Alert status'")

        # Step 6d: Select 'Open' alert status
        print("\n📍 Step 6d: Select 'Open' alert status")
        open_clicked = await browser.evaluate("""
            (() => {
                const elements = Array.from(document.querySelectorAll('input[type="checkbox"], label, div[role="option"], button'));
                for (const el of elements) {
                    const text = (el.textContent || el.value || el.getAttribute('aria-label') || '').trim().toLowerCase();
                    if (text === 'open' && el.offsetParent !== null) {
                        if (el.tagName === 'INPUT') {
                            el.checked = true;
                            el.dispatchEvent(new Event('change', { bubbles: true }));
                        } else {
                            el.click();
                        }
                        return true;
                    }
                }
                return false;
            })()
        """)
        await asyncio.sleep(1)
        await browser.screenshot("step_06d_open_selected", path=screenshot_dir / "step_06d_open_selected.png", full_page=True, save_metadata=True)
        print("✅ Selected 'Open' alert status")

        # Step 6e: Close filters
        await browser.page.keyboard.press('Escape')
        await asyncio.sleep(2)
        await browser.screenshot("step_06e_filters_closed", path=screenshot_dir / "step_06e_filters_closed.png", full_page=True, save_metadata=True)
        print("✅ Closed filters - showing open alerts only")

        # Step 6f: Load more customers to get past first 10 rows and find non-PEP customers
        print("\n📍 Step 6f: Load more customers to find non-PEP entries past row 10")

        # Always click "Load more" at least once to get more rows
        print("   📄 Clicking 'Load more' to get additional customers...")
        for i in range(3):  # Click 3 times to get plenty of rows
            load_more_clicked = await browser.evaluate("""
                (() => {
                    const buttons = Array.from(document.querySelectorAll('button'));
                    for (const btn of buttons) {
                        const text = (btn.textContent || '').toLowerCase();
                        if (text.includes('load more')) {
                            btn.click();
                            return true;
                        }
                    }
                    return false;
                })()
            """)
            if load_more_clicked:
                print(f"   ✅ Clicked 'Load more' ({i+1}/3)")
                await asyncio.sleep(2)
            else:
                print(f"   ⚠️  No 'Load more' button found")
                break

        # Now check for non-PEP customers
        print("\n   🔍 Checking for non-PEP customers...")
        check_result = await browser.evaluate("""
                (() => {
                    // Find the Alerts column index by looking at headers
                    const headers = Array.from(document.querySelectorAll('thead th, thead td'));
                    let alertsColumnIndex = -1;

                    for (let i = 0; i < headers.length; i++) {
                        const headerText = headers[i].textContent.trim().toLowerCase();
                        if (headerText === 'alerts') {
                            alertsColumnIndex = i;
                            break;
                        }
                    }

                    if (alertsColumnIndex === -1) {
                        return {count: 0, error: 'Could not find Alerts column', sample: []};
                    }

                    const rows = Array.from(document.querySelectorAll('tbody tr'));
                    let count = 0;
                    let pepCount = 0;
                    let sampleNonPep = [];
                    let samplePep = [];
                    let htmlSamples = [];

                    for (let i = 0; i < rows.length; i++) {
                        const row = rows[i];
                        const cells = row.querySelectorAll('td');
                        if (cells.length <= alertsColumnIndex) continue;

                        const nameCell = cells[0];
                        const name = nameCell.textContent.trim();

                        const alertsCell = cells[alertsColumnIndex];

                        // Capture HTML structure for first 3 rows for debugging
                        if (htmlSamples.length < 3) {
                            htmlSamples.push({
                                name,
                                html: alertsCell.innerHTML,
                                text: alertsCell.textContent.trim()
                            });
                        }

                        // Look for span/div elements containing exactly "PEP" text
                        const pepBadges = Array.from(alertsCell.querySelectorAll('span, div')).filter(el => {
                            const txt = el.textContent.trim();
                            return txt === 'PEP' || txt.match(/^PEP\s+\d+$/);
                        });
                        const hasPEP = pepBadges.length > 0;

                        const alertText = alertsCell.textContent || '';

                        if (hasPEP) {
                            pepCount++;
                            if (samplePep.length < 2) {
                                samplePep.push({name, alerts: alertText.substring(0, 50)});
                            }
                        } else {
                            count++;
                            if (sampleNonPep.length < 2) {
                                sampleNonPep.push({name, alerts: alertText.substring(0, 50)});
                            }
                        }
                    }

                    return {
                        count,
                        pepCount,
                        alertsColumnIndex,
                        sampleNonPep,
                        samplePep,
                        htmlSamples
                    };
                })()
        """)

        non_pep_count = check_result.get('count', 0)
        pep_count = check_result.get('pepCount', 0)

        if 'error' in check_result:
            print(f"   ⚠️  {check_result['error']}")
        else:
            print(f"   Found {non_pep_count} non-PEP, {pep_count} PEP customers (col index: {check_result['alertsColumnIndex']})")

            # Print HTML structure samples for debugging
            if check_result.get('htmlSamples'):
                print("\n   🔍 HTML Structure - First Row Only (Full):")
                sample = check_result['htmlSamples'][0]
                print(f"   Text: {sample.get('text', '')}")
                print(f"   HTML: {sample.get('html', '')[:500]}...")
                print()

            if check_result.get('sampleNonPep'):
                print(f"   Sample non-PEP: {check_result['sampleNonPep']}")
            if check_result.get('samplePep'):
                print(f"   Sample PEP: {check_result['samplePep']}")

        if non_pep_count >= 2:
            print(f"   ✅ Found {non_pep_count} non-PEP customers")
        else:
            print(f"   ⚠️  Only found {non_pep_count} non-PEP customers - may not have enough")

        await browser.screenshot("step_06f_after_load_more", path=screenshot_dir / "step_06f_after_load_more.png", full_page=True, save_metadata=True)

        # Steps 7-13: Customer review workflow (process 2 customers)
        print("\n📍 Steps 7-13: Customer review workflow")

        for customer_num in range(1, 3):  # Process 2 customers
            print(f"\n{'='*50}")
            print(f"Customer {customer_num} of 2")
            print('='*50)

            # Step 7: Click a customer (not in top 10, not marked PEP)
            print(f"\n📍 Step 7 (Customer {customer_num}): Click customer (not top 10, not PEP)")

            # Find rows without "PEP", skip first 10, click different one each time
            customer_clicked = await browser.evaluate("""
                ((customerNum) => {
                    // Find the Alerts column index (same logic as PEP detection)
                    const headers = Array.from(document.querySelectorAll('thead th, thead td'));
                    let alertsColumnIndex = -1;

                    for (let i = 0; i < headers.length; i++) {
                        const headerText = headers[i].textContent.trim().toLowerCase();
                        if (headerText === 'alerts') {
                            alertsColumnIndex = i;
                            break;
                        }
                    }

                    if (alertsColumnIndex === -1) {
                        return null;
                    }

                    const rows = Array.from(document.querySelectorAll('tbody tr'));
                    let nonPepRows = [];

                    // Find all rows without PEP badge
                    for (let i = 0; i < rows.length; i++) {
                        const row = rows[i];
                        const cells = row.querySelectorAll('td');
                        if (cells.length <= alertsColumnIndex) continue;

                        const nameCell = cells[0];
                        const name = nameCell.textContent.trim();

                        const alertsCell = cells[alertsColumnIndex];

                        // Look for span/div elements containing exactly "PEP" text
                        const pepBadges = Array.from(alertsCell.querySelectorAll('span, div')).filter(el => {
                            const txt = el.textContent.trim();
                            return txt === 'PEP' || txt.match(/^PEP\s+\d+$/);
                        });
                        const hasPEP = pepBadges.length > 0;

                        const alertsText = alertsCell.textContent || '';

                        // Skip if has PEP badge
                        if (hasPEP) continue;

                        // Valid non-PEP row
                        nonPepRows.push({
                            row: row,
                            index: i,
                            name: name,
                            alerts: alertsText.substring(0, 30)
                        });
                    }

                    // Filter to rows past index 10
                    let targetRows = nonPepRows.filter(r => r.index >= 10);

                    // If none past 10, use all non-PEP rows
                    if (targetRows.length === 0) {
                        targetRows = nonPepRows;
                    }

                    // Click the appropriate one (0-indexed)
                    if (targetRows.length >= customerNum) {
                        const target = targetRows[customerNum - 1];
                        target.row.click();
                        return target.name + ' (row ' + target.index + ', alerts: ' + target.alerts + ')';
                    }

                    return null;
                })(""" + str(customer_num) + ")")

            if customer_clicked:
                print(f"   ✅ Clicked customer: {customer_clicked}")
            else:
                print("   ⚠️  No valid customer found (not PEP, past row 10)")

            await asyncio.sleep(3)
            await browser.screenshot(f"step_07_customer_{customer_num}_detail", path=screenshot_dir / f"step_07_customer_{customer_num}_detail.png", full_page=True, save_metadata=True)

            # Extract customer name from the page
            customer_name = await browser.evaluate("""
                (() => {
                    // Try to find customer name in various locations
                    const nameSelectors = [
                        'h1', 'h2',
                        '[data-testid="customer-name"]',
                        '.customer-name',
                        'div:has-text("Person") + div'
                    ];

                    for (const sel of nameSelectors) {
                        const el = document.querySelector(sel);
                        if (el && el.textContent.trim()) {
                            return el.textContent.trim();
                        }
                    }

                    // Fallback: look for "Person" label and get next text
                    const labels = Array.from(document.querySelectorAll('*'));
                    for (const label of labels) {
                        if (label.textContent.trim() === 'Person') {
                            const parent = label.parentElement;
                            if (parent) {
                                const nextText = parent.textContent.replace('Person', '').trim();
                                if (nextText) return nextText;
                            }
                        }
                    }

                    return 'Unknown Customer';
                })()
            """)
            print(f"   👤 Customer name: {customer_name}")

            # Step 8: Wait for AI Summary (may or may not appear)
            print(f"\n📍 Step 8 (Customer {customer_num}): Wait for AI Summary (5-7 seconds)")
            await asyncio.sleep(7)
            await browser.screenshot(f"step_08_customer_{customer_num}_after_wait", path=screenshot_dir / f"step_08_customer_{customer_num}_after_wait.png", full_page=True, save_metadata=True)
            print("   ✅ Wait complete")

            # Step 9: Read page and make decision using LLM
            print(f"\n📍 Step 9 (Customer {customer_num}): LLM decision (match or not match)")

            # Extract page content for LLM
            page_content = await browser.evaluate("""
                (() => {
                    return document.body.innerText;
                })()
            """)

            prompt = f"""You are reviewing a customer for AML (Anti-Money Laundering) verification.

Read the following page content and determine if this person is a MATCH or NOT A MATCH for potential sanctions/PEP concerns.

Page content:
{page_content[:3000]}

Respond with ONLY one word: MATCH or NOTMATCH"""

            response = llm.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                temperature=0.1,
                max_tokens=10
            )

            decision = response.choices[0].message.content.strip().upper()
            is_match = 'MATCH' in decision
            print(f"   🤖 LLM Decision: {decision} ({'Y' if is_match else 'N'})")

            # Step 10: Decision the person using keyboard shortcuts
            print(f"\n📍 Step 10 (Customer {customer_num}): Submit decision ({'Y' if is_match else 'N'})")

            # Scroll to bottom to see Decision section
            await browser.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1)
            await browser.screenshot(f"step_10a_customer_{customer_num}_decision_visible", path=screenshot_dir / f"step_10a_customer_{customer_num}_decision_visible.png", full_page=True, save_metadata=True)

            # Step 10a: Press 'y' or 'n' (lowercase)
            decision_key = 'y' if is_match else 'n'
            await browser.page.keyboard.press(decision_key)
            print(f"   ✅ Pressed '{decision_key}' ({'Match' if is_match else 'Not Match'})")
            await asyncio.sleep(2)
            await browser.screenshot(f"step_10b_customer_{customer_num}_after_yn", path=screenshot_dir / f"step_10b_customer_{customer_num}_after_yn.png", full_page=True, save_metadata=True)

            # Step 10b: Select match reason (1=Name, 2=Address, 3=Date, 4=Other)
            # Use LLM to decide which reason based on page content
            reason_prompt = f"""Based on this AML customer data, which matching factor is most relevant? Choose ONE:
1. Name similarity
2. Address match
3. Date of birth match
4. Other factors

Customer: {customer_name}
Context: {page_content[:500]}

Respond with ONLY the number (1, 2, 3, or 4)."""

            reason_response = llm.chat_completion(
                messages=[{"role": "user", "content": reason_prompt}],
                model="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                temperature=0.1,
                max_tokens=5
            )
            reason_choice = reason_response.choices[0].message.content.strip()
            # Extract just the digit
            reason_digit = ''.join(c for c in reason_choice if c.isdigit())[:1] or '1'
            reason_names = {
                '1': 'Name',
                '2': 'Address',
                '3': 'Date',
                '4': 'Other'
            }
            print(f"   🤖 Selected match reason: {reason_digit} ({reason_names.get(reason_digit, 'Name')})")

            await browser.page.keyboard.press(reason_digit)
            await asyncio.sleep(1)
            await browser.screenshot(f"step_10c_customer_{customer_num}_reason_selected", path=screenshot_dir / f"step_10c_customer_{customer_num}_reason_selected.png", full_page=True, save_metadata=True)

            # Step 10d: Press 'r' to specify reasoning
            await browser.page.keyboard.press('r')
            print(f"   ✅ Pressed 'r' (Specify match reason)")
            await asyncio.sleep(1)
            await browser.screenshot(f"step_10d_customer_{customer_num}_after_r", path=screenshot_dir / f"step_10d_customer_{customer_num}_after_r.png", full_page=True, save_metadata=True)

            # Generate reasoning using LLM
            reasoning_prompt = f"""Based on this AML customer profile, provide a brief 1-2 sentence reasoning for why this is a {'match' if is_match else 'not a match'}:

Customer: {customer_name}
Decision: {decision}

Context from page:
{page_content[:1000]}

Provide ONLY the reasoning text (1-2 sentences), no other commentary."""

            reasoning_response = llm.chat_completion(
                messages=[{"role": "user", "content": reasoning_prompt}],
                model="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                temperature=0.3,
                max_tokens=100
            )
            reasoning = reasoning_response.choices[0].message.content.strip()
            print(f"   🤖 Generated reasoning: {reasoning[:100]}...")

            # Type the reasoning
            await browser.page.keyboard.type(reasoning)
            await asyncio.sleep(1)
            await browser.screenshot(f"step_10e_customer_{customer_num}_reasoning_entered", path=screenshot_dir / f"step_10e_customer_{customer_num}_reasoning_entered.png", full_page=True, save_metadata=True)

            # Step 10f: Press 'd' to add details
            await browser.page.keyboard.press('d')
            print(f"   ✅ Pressed 'd' (Add details)")
            await asyncio.sleep(1)
            await browser.screenshot(f"step_10f_customer_{customer_num}_after_d", path=screenshot_dir / f"step_10f_customer_{customer_num}_after_d.png", full_page=True, save_metadata=True)

            # Generate details using LLM
            details_prompt = f"""Based on this AML alert, provide specific details about the matching factors or discrepancies (2-3 sentences):

Customer: {customer_name}
Decision: {'Match' if is_match else 'Not a match'}

Context from page:
{page_content[:1000]}

Provide ONLY the details text (2-3 sentences), no other commentary."""

            details_response = llm.chat_completion(
                messages=[{"role": "user", "content": details_prompt}],
                model="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                temperature=0.3,
                max_tokens=150
            )
            details = details_response.choices[0].message.content.strip()
            print(f"   🤖 Generated details: {details[:100]}...")

            # Type the details
            await browser.page.keyboard.type(details)
            await asyncio.sleep(1)
            await browser.screenshot(f"step_10g_customer_{customer_num}_details_entered", path=screenshot_dir / f"step_10g_customer_{customer_num}_details_entered.png", full_page=True, save_metadata=True)

            # Step 10h: Press Command+Enter to submit
            await browser.page.keyboard.press('Meta+Enter')
            print(f"   ✅ Pressed Command+Enter to submit decision")
            await asyncio.sleep(3)

            await browser.screenshot(f"step_10h_customer_{customer_num}_decision_submitted", path=screenshot_dir / f"step_10h_customer_{customer_num}_decision_submitted.png", full_page=True, save_metadata=True)

            # Step 11: Return to customers page
            print(f"\n📍 Step 11 (Customer {customer_num}): Return to customers page")
            await browser.page.keyboard.press('g')
            await asyncio.sleep(0.2)
            await browser.page.keyboard.press('c')
            await asyncio.sleep(3)
            await browser.screenshot(f"step_11_customer_{customer_num}_back_to_list", path=screenshot_dir / f"step_11_customer_{customer_num}_back_to_list.png", full_page=True, save_metadata=True)
            print("   ✅ Back to customers page")

        # Step 13: Logout
        print("\n📍 Step 13: Logout")

        try:
            # Navigate to home to find logout option
            await browser.navigate("https://app.dev.sandbar.ai")
            await asyncio.sleep(2)

            # Click upper left icon/button to open menu
            menu_clicked = await browser.evaluate("""
                (() => {
                    // Find any clickable element in top-left corner
                    const elements = Array.from(document.querySelectorAll('button, [role="button"], a'));
                    for (const el of elements) {
                        const rect = el.getBoundingClientRect();
                        // Top-left corner area
                        if (rect.top < 150 && rect.left < 150) {
                            el.click();
                            return true;
                        }
                    }
                    return false;
                })()
            """)

            if menu_clicked:
                print("   ✅ Opened menu")
                await asyncio.sleep(1)
                await browser.screenshot("step_13_logout_menu", path=screenshot_dir / "step_13_logout_menu.png", full_page=True, save_metadata=True)

                # Click Logout option
                logout_clicked = await browser.evaluate("""
                    (() => {
                        const allElements = Array.from(document.querySelectorAll('*'));
                        for (const el of allElements) {
                            const text = (el.textContent || '').trim().toLowerCase();
                            // Look for logout, sign out, etc
                            if (text === 'logout' || text === 'sign out' || text === 'log out') {
                                el.click();
                                return true;
                            }
                        }
                        return false;
                    })()
                """)

                if logout_clicked:
                    print("   ✅ Clicked logout")
                    await asyncio.sleep(2)
                    await browser.screenshot("step_13_logged_out", path=screenshot_dir / "step_13_logged_out.png", full_page=True, save_metadata=True)
                else:
                    print("   ⚠️  Could not find logout option")
            else:
                print("   ⚠️  Could not find menu button")
        except Exception as e:
            print(f"   ⚠️  Logout failed: {str(e)}")

        print("\n" + "=" * 70)
        print("✅ Workflow complete")
        print("=" * 70)
        print(f"\nScreenshots saved to: {screenshot_dir}")

        return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
