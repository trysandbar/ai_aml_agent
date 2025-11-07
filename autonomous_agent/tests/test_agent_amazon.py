"""
Test Amazon workflow using MCP Agent.
Simple navigation test to validate basic agent loop.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_loop import BrowserAgent


def test_amazon_search():
    """
    Test agent can navigate to Amazon and search for a product.

    Goal: Go to Amazon, search for "laptop", and find the search results page.
    """
    agent = BrowserAgent(
        goal="""
        1. Navigate to https://www.amazon.com
        2. Find the search box
        3. Search for "laptop"
        4. Wait for search results to load
        5. Confirm you can see the search results
        """,
        client_id="amazon_test",
        max_iterations=10,
        initial_url="about:blank",
        headless=True
    )

    print("=" * 60)
    print("Testing Amazon Search with MCP Agent")
    print("=" * 60)

    result = agent.run()

    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    print(f"Success: {result.success}")
    print(f"Steps taken: {result.steps_taken}")
    print(f"Final URL: {result.final_state.current_url}")
    print(f"Final title: {result.final_state.page_title}")

    if result.error:
        print(f"Error: {result.error}")

    # Verify results
    if result.success:
        print("\n✅ Test PASSED")
    else:
        print("\n❌ Test FAILED")

    return result


if __name__ == "__main__":
    test_amazon_search()
