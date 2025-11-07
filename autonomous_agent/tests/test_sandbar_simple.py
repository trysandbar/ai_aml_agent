"""
Simplified Sandbar workflow test for autonomous agent.
Tests navigation and basic interaction without full authentication.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_loop import BrowserAgent


def test_sandbar_simple():
    """Test simplified Sandbar navigation."""

    # Simplified goal - just navigate and explore the page structure
    goal = """Navigate to https://app.dev.sandbar.ai and verify the login page loads.
    Look for a 'Sign in with Google' button or similar authentication element.
    Describe what you see on the page without attempting to login."""

    agent = BrowserAgent(
        goal=goal,
        client_id="test_sandbar_simple",
        max_iterations=5,
        screenshot_dir="test_screenshots",
        initial_url="https://app.dev.sandbar.ai",
        headless=True
    )

    print("\n" + "=" * 60)
    print("Running simplified Sandbar navigation test...")
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
    success = test_sandbar_simple()
    sys.exit(0 if success else 1)
