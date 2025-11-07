"""
Minimal MCP connection test with debugging.
"""

import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_minimal():
    """Minimal MCP connection test."""
    print("Starting minimal MCP test...")
    print(f"Python version: {sys.version}")

    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-puppeteer"],
        env=None
    )

    print(f"Server command: {server_params.command} {' '.join(server_params.args)}")
    print("Connecting...")

    try:
        # Add timeout to the whole operation
        async with asyncio.timeout(30):
            async with stdio_client(server_params) as (read, write):
                print("✅ stdio_client connected")

                async with ClientSession(read, write) as session:
                    print("✅ ClientSession created")

                    print("Initializing session...")
                    init_result = await session.initialize()
                    print(f"✅ Session initialized: {init_result}")

                    print("\nSuccess!")

    except asyncio.TimeoutError:
        print("❌ Timeout - connection took too long")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_minimal())
