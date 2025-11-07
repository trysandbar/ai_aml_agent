"""
Direct subprocess-based MCP client to work around SDK hanging issues.
"""

import json
import subprocess
import asyncio
from typing import Dict, Any


class MCPSubprocessClient:
    """MCP client using subprocess communication instead of SDK."""

    def __init__(self, command: str, args: list):
        """Initialize MCP subprocess client."""
        self.command = command
        self.args = args
        self.message_id = 0

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any], timeout: int = 30) -> Any:
        """
        Call an MCP tool using direct subprocess communication.

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            timeout: Timeout in seconds

        Returns:
            Tool result
        """
        self.message_id += 1

        # Build MCP request messages
        messages = [
            # Initialize request
            {
                "jsonrpc": "2.0",
                "id": self.message_id,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "mcp-subprocess-client", "version": "1.0.0"}
                }
            },
            # Tool call request
            {
                "jsonrpc": "2.0",
                "id": self.message_id + 1,
                "method": "tools/call",
                "params": {"name": tool_name, "arguments": arguments}
            }
        ]

        # Start subprocess
        proc = await asyncio.create_subprocess_exec(
            self.command,
            *self.args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        try:
            # Send requests
            input_data = "\n".join(json.dumps(msg) for msg in messages) + "\n"

            # Communicate with timeout
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input_data.encode()),
                timeout=timeout
            )

            # Parse responses
            responses = []
            for line in stdout.decode().strip().split("\n"):
                if line.strip():
                    try:
                        responses.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

            # Find tool call response
            for resp in responses:
                if resp.get("id") == self.message_id + 1 and "result" in resp:
                    result = resp["result"]
                    # Extract text content
                    if "content" in result:
                        for item in result["content"]:
                            if item.get("type") == "text" and "text" in item:
                                return item["text"]
                    return "Tool executed"

            return "No result"

        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            raise TimeoutError(f"Tool call {tool_name} timed out")

        except Exception as e:
            if proc.returncode is None:
                proc.kill()
                await proc.wait()
            raise

        finally:
            if proc.returncode is None:
                proc.terminate()
                await proc.wait()
