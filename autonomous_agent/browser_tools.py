"""
Browser Tools - Playwright wrapper functions for Llama 4 tool calling.

Provides OpenAI-format tool definitions and execution wrappers for browser automation.
"""

from typing import Dict, Any, List
from playwright.async_api import Page
import json


# OpenAI-format tool definitions for Llama 4
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "navigate",
            "description": "Navigate to a URL. Use this to visit web pages.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to navigate to (e.g., https://example.com)"
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "click",
            "description": "Click an element on the page using a CSS selector.",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for the element to click (e.g., '#submit-button', '.menu-item')"
                    }
                },
                "required": ["selector"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fill",
            "description": "Fill a form field with a value.",
            "parameters": {
                "type": "object",
                "properties": {
                    "selector": {
                        "type": "string",
                        "description": "CSS selector for the input field (e.g., 'input[name=\"email\"]')"
                    },
                    "value": {
                        "type": "string",
                        "description": "The value to fill into the field"
                    }
                },
                "required": ["selector", "value"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "evaluate",
            "description": "Execute JavaScript code in the browser and return the result.",
            "parameters": {
                "type": "object",
                "properties": {
                    "script": {
                        "type": "string",
                        "description": "JavaScript code to execute (e.g., 'document.title' or 'JSON.stringify({url: window.location.href})')"
                    }
                },
                "required": ["script"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "wait_for_timeout",
            "description": "Wait for a specified number of seconds. Use this to allow pages to load or animations to complete.",
            "parameters": {
                "type": "object",
                "properties": {
                    "seconds": {
                        "type": "number",
                        "description": "Number of seconds to wait (can be decimal, e.g., 1.5)"
                    }
                },
                "required": ["seconds"]
            }
        }
    }
]


async def navigate(page: Page, url: str) -> str:
    """Navigate to a URL."""
    await page.goto(url, wait_until="domcontentloaded")
    return f"Navigated to {url}"


async def click(page: Page, selector: str) -> str:
    """Click an element by CSS selector."""
    await page.click(selector)
    return f"Clicked element: {selector}"


async def fill(page: Page, selector: str, value: str) -> str:
    """Fill a form field with a value."""
    await page.fill(selector, value)
    return f"Filled '{selector}' with value: {value}"


async def evaluate(page: Page, script: str) -> Any:
    """Execute JavaScript and return the result."""
    result = await page.evaluate(script)
    # Convert result to string if it's not already JSON-serializable
    if isinstance(result, (dict, list)):
        return json.dumps(result)
    return str(result)


async def wait_for_timeout(page: Page, seconds: float) -> str:
    """Wait for a specified number of seconds."""
    await page.wait_for_timeout(int(seconds * 1000))  # Convert to milliseconds
    return f"Waited for {seconds} seconds"


# Tool execution dispatcher
async def execute_tool(page: Page, tool_name: str, arguments: Dict[str, Any]) -> Any:
    """
    Execute a tool by name with the given arguments.

    Args:
        page: Playwright page object
        tool_name: Name of the tool to execute
        arguments: Dictionary of arguments for the tool

    Returns:
        Result of the tool execution

    Raises:
        ValueError: If tool_name is not recognized
    """
    tools = {
        "navigate": navigate,
        "click": click,
        "fill": fill,
        "evaluate": evaluate,
        "wait_for_timeout": wait_for_timeout
    }

    if tool_name not in tools:
        raise ValueError(f"Unknown tool: {tool_name}")

    tool_func = tools[tool_name]
    return await tool_func(page, **arguments)
