"""
Full Sandbar AML workflow test for autonomous agent.
Converts the 854-line Playwright script to a natural language goal.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_loop import BrowserAgent

# Load environment variables
env_file = Path(__file__).parent.parent.parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value


def test_sandbar_full_workflow():
    """Test full Sandbar AML review workflow."""

    # Clean up previous test screenshots
    test_screenshot_dir = Path(__file__).parent.parent / "test_screenshots" / "test_sandbar_full"
    if test_screenshot_dir.exists():
        print(f"🧹 Cleaning up previous test screenshots from {test_screenshot_dir}")
        import shutil
        shutil.rmtree(test_screenshot_dir)
        print("✅ Previous screenshots removed\n")

    # Get credentials from environment
    google_email = os.getenv('GOOGLE_LOGIN', '')
    google_password = os.getenv('GOOGLE_PW', '')

    if not google_email or not google_password:
        print("❌ ERROR: GOOGLE_LOGIN and GOOGLE_PW must be set in .env")
        print("Cannot proceed without valid credentials")
        return False

    # Read workflow from sandbar.txt and substitute credentials
    # NOTE: Including password in goal - in production, use storage_state or secure credential management
    sandbar_txt = Path(__file__).parent.parent / "sandbar.txt"
    if not sandbar_txt.exists():
        print(f"❌ ERROR: {sandbar_txt} not found")
        return False

    with open(sandbar_txt) as f:
        goal_template = f.read()

    # Substitute credentials
    goal = goal_template.replace("{EMAIL}", google_email).replace("{PASSWORD}", google_password)

    agent = BrowserAgent(
        goal=goal,
        client_id="test_sandbar_full",
        max_iterations=50,  # Increased for full 44-step workflow
        screenshot_dir="test_screenshots",
        initial_url="https://app.dev.sandbar.ai",
        headless=True
    )

    print("\n" + "=" * 80)
    print("Running FULL Sandbar AML workflow with autonomous agent...")
    print("=" * 80)

    result = agent.run()

    print("\n" + "=" * 80)
    print(f"Test Result: {'✅ SUCCESS' if result.success else '⚠️  PARTIAL'}")
    print(f"Steps taken: {result.steps_taken}")
    print(f"Final URL: {result.final_state.current_url}")
    print(f"Page title: {result.final_state.page_title}")
    if result.error:
        print(f"Error: {result.error}")
    print("=" * 80 + "\n")

    return result.success


if __name__ == "__main__":
    success = test_sandbar_full_workflow()
    sys.exit(0 if success else 1)
