"""Test Together AI client only, no MCP."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from together_ai.agent_client import TogetherAgentClient


def test_together():
    """Test Together AI client."""
    print("Testing Together AI client...")

    # Simple tools for testing
    tools = [
        {
            "type": "function",
            "function": {
                "name": "navigate",
                "description": "Navigate to a URL",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to navigate to"}
                    },
                    "required": ["url"]
                }
            }
        }
    ]

    client = TogetherAgentClient()
    client.set_system_prompt("You are a browser automation agent. Use tools to navigate websites.")

    print("Calling Llama 4...")
    response = client.call_with_tools(
        message="Navigate to Amazon.com. What tool should I call?",
        tools=tools,
        max_tokens=100
    )

    print(f"✅ Response: {response['content']}")
    print(f"✅ Tool calls: {response['tool_calls']}")


if __name__ == "__main__":
    test_together()
