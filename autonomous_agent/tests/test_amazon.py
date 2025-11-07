"""
Test autonomous agent navigation on Amazon.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_loop import BrowserAgent


def test_amazon_navigation():
    """Test that the agent can navigate to Amazon and search for a product."""

    agent = BrowserAgent(
        goal="Navigate to amazon.com, search for 'laptop', and verify search results appear",
        client_id="test_amazon",
        max_iterations=10,
        screenshot_dir="test_screenshots",
        initial_url="https://www.amazon.com",
        headless=True
    )

    print("\n" + "=" * 60)
    print("Running Amazon navigation test...")
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
    success = test_amazon_navigation()
    sys.exit(0 if success else 1)
