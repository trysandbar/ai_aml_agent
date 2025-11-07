"""
Simple test to validate MCP connection to Puppeteer server.
"""

import asyncio
import json
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_connection():
    """Test basic connection to Puppeteer MCP server."""
    print("Testing MCP connection to Puppeteer server...")

    # Load config
    config_path = Path(__file__).parent.parent / "mcp_config.json"
    with open(config_path) as f:
        config = json.load(f)

    puppeteer_config = config["mcpServers"]["puppeteer"]

    server_params = StdioServerParameters(
        command=puppeteer_config["command"],
        args=puppeteer_config["args"]
    )

    # Connect
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            print("Initializing session...")
            await session.initialize()
            print("✅ Session initialized")

            # List tools
            print("\nListing available tools...")
            tools_result = await session.list_tools()
            print(f"✅ Found {len(tools_result.tools)} tools:")
            for tool in tools_result.tools:
                print(f"  - {tool.name}: {tool.description}")

            # Test navigation with headless mode
            print("\n🌐 Testing navigation with headless mode...")
            nav_result = await session.call_tool(
                "puppeteer_navigate",
                arguments={
                    "url": "https://www.google.com",
                    "launchOptions": {"headless": True}
                }
            )
            print(f"✅ Navigation successful: {nav_result}")

            # Take screenshot
            print("\n📸 Testing screenshot...")
            screenshot_result = await session.call_tool(
                "puppeteer_screenshot",
                arguments={
                    "name": "test_screenshot",
                    "width": 1280,
                    "height": 800,
                    "encoded": True
                }
            )
            print(f"✅ Screenshot successful")

            print("\n✅ All tests passed!")


if __name__ == "__main__":
    asyncio.run(test_connection())
