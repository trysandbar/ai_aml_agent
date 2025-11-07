"""
Minimal agent test with extensive debugging.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_loop import BrowserAgent


def test_minimal():
    """Test agent with verbose output."""
    print("\n" + "=" * 60)
    print("MINIMAL AGENT TEST WITH DEBUGGING")
    print("=" * 60 + "\n")

    agent = BrowserAgent(
        goal="Navigate to google.com and take a screenshot",
        client_id="minimal_test",
        max_iterations=2,  # Just 2 iterations
        initial_url="about:blank",
        headless=True
    )

    print("Agent created. Starting run...")
    result = agent.run()

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Success: {result.success}")
    print(f"Steps: {result.steps_taken}")
    print(f"Error: {result.error}")


if __name__ == "__main__":
    test_minimal()
