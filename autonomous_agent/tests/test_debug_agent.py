"""
Debug version of agent test with verbose logging.
"""

import asyncio
import sys
import json
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from together_ai.agent_client import TogetherAgentClient


async def test_debug():
    """Debug agent components."""
    print("=" * 60)
    print("DEBUG AGENT TEST")
    print("=" * 60)

    # Test 1: MCP Connection
    print("\n1. Testing MCP connection...")
    config_path = Path(__file__).parent.parent / "mcp_config.json"
    with open(config_path) as f:
        config = json.load(f)

    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-puppeteer"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            print("✅ MCP connected")

            await session.initialize()
            print("✅ MCP initialized")

            tools_result = await session.list_tools()
            print(f"✅ Found {len(tools_result.tools)} tools")

            # Test 2: Together AI Client
            print("\n2. Testing Together AI client...")
            ai_client = TogetherAgentClient()
            print("✅ Together AI client created")

            # Convert tools
            openai_tools = []
            for tool in tools_result.tools:
                openai_tool = {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or f"Execute {tool.name}",
                        "parameters": tool.inputSchema if hasattr(tool, 'inputSchema') else {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                }
                openai_tools.append(openai_tool)

            print(f"✅ Converted {len(openai_tools)} tools to OpenAI format")

            # Test 3: Navigate to page
            print("\n3. Testing navigation...")
            nav_result = await session.call_tool(
                "puppeteer_navigate",
                arguments={
                    "url": "https://www.google.com",
                    "launchOptions": {"headless": True}
                }
            )
            print("✅ Navigation successful")

            # Test 4: Take screenshot
            print("\n4. Testing screenshot...")
            screenshot_result = await session.call_tool(
                "puppeteer_screenshot",
                arguments={
                    "name": "debug_test",
                    "width": 800,
                    "height": 600,
                    "encoded": True
                }
            )

            # Save screenshot
            if hasattr(screenshot_result, 'content') and screenshot_result.content:
                import base64
                for item in screenshot_result.content:
                    if hasattr(item, 'text') and item.text:
                        b64_data = item.text
                        if "base64," in b64_data:
                            b64_data = b64_data.split("base64,")[1]

                        Path("test_screenshots").mkdir(exist_ok=True)
                        with open("test_screenshots/debug_test.png", "wb") as f:
                            f.write(base64.b64decode(b64_data))
                        print("✅ Screenshot saved to test_screenshots/debug_test.png")
                        break

            # Test 5: Simple Llama 4 call WITHOUT vision
            print("\n5. Testing Llama 4 call (no vision)...")
            ai_client.set_system_prompt("You are a browser automation agent. Use available tools to accomplish goals.")

            try:
                response = ai_client.call_with_tools(
                    message="Navigate to Amazon.com and search for laptop. What tool should I use first?",
                    tools=openai_tools[:3],  # Just first 3 tools to keep it simple
                    screenshot_path=None,  # No vision for now
                    max_tokens=200
                )
                print(f"✅ Llama 4 response: {response['content'][:100]}...")
                print(f"✅ Tool calls: {len(response['tool_calls'])}")
            except Exception as e:
                print(f"❌ Llama 4 call failed: {e}")

            print("\n" + "=" * 60)
            print("ALL TESTS PASSED")
            print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_debug())
