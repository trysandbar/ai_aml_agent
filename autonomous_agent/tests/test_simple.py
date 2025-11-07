"""
Simple test to verify the autonomous agent works with Playwright.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_loop import BrowserAgent


def test_simple_navigation():
    """Test that the agent can navigate to a simple page."""

    agent = BrowserAgent(
        goal="Navigate to example.com and verify the page loaded",
        client_id="test_simple",
        max_iterations=3,
        screenshot_dir="test_screenshots",
        initial_url="https://example.com",
        headless=True
    )

    print("\n" + "=" * 60)
    print("Running simple navigation test...")
    print("=" * 60)

    result = agent.run()

    print("\n" + "=" * 60)
    print(f"Test Result: {'✅ SUCCESS' if result.success else '❌ FAILED'}")
    print(f"Steps taken: {result.steps_taken}")
    print(f"Final URL: {result.final_state.current_url}")
    print(f"Page title: {result.final_state.page_title}")
    if result.error:
        print(f"Error: {result.error}")
    print("=" * 60 + "\n")

    return result.success


if __name__ == "__main__":
    success = test_simple_navigation()
    sys.exit(0 if success else 1)
