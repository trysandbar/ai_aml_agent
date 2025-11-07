"""
Together AI client with tool calling and vision support for MCP Agent.
Integrates with Llama 4 Maverick for autonomous browser automation.
"""

import os
import base64
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class TogetherAgentClient:
    """Together AI client with tool calling and vision support."""

    def __init__(
        self,
        model: str = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
        api_key: Optional[str] = None
    ):
        """
        Initialize Together AI client.

        Args:
            model: Model name to use (default: Llama 4 Maverick)
            api_key: Together API key (uses TOGETHER_API_KEY env var if not provided)
        """
        self.model = model
        api_key = api_key or os.getenv("TOGETHER_API_KEY")
        if not api_key:
            raise ValueError("TOGETHER_API_KEY not found in environment")

        # Use OpenAI client with Together AI base URL (like working playwright_agent)
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.together.xyz/v1"
        )
        self.conversation_history: List[Dict[str, Any]] = []
        self.system_prompt: Optional[str] = None

    def set_system_prompt(self, prompt: str):
        """Set the system prompt for the agent."""
        self.system_prompt = prompt

    def reset_conversation(self):
        """Reset conversation history."""
        self.conversation_history = []

    def encode_image_base64(self, image_path: str) -> str:
        """
        Encode an image to base64 for vision input.

        Args:
            image_path: Path to the image file

        Returns:
            Base64-encoded image string
        """
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    def create_vision_message(self, text: str, image_path: str) -> Dict[str, Any]:
        """
        Create a vision message with text and image.

        Args:
            text: Text content
            image_path: Path to screenshot image

        Returns:
            Message dict with text and image content
        """
        image_b64 = self.encode_image_base64(image_path)

        return {
            "role": "user",
            "content": [
                {"type": "text", "text": text},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{image_b64}"}
                }
            ]
        }

    def call_with_tools(
        self,
        message: str,
        tools: List[Dict[str, Any]],
        screenshot_path: Optional[str] = None,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Call the model with tool calling enabled.

        Args:
            message: User message text
            tools: List of tool definitions in OpenAI format
            screenshot_path: Optional path to screenshot for vision input
            max_tokens: Maximum tokens to generate

        Returns:
            Response from the model including any tool calls
        """
        # Build messages
        messages = []

        # Add system prompt if set
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})

        # Add conversation history
        messages.extend(self.conversation_history)

        # Add current message (with or without vision)
        if screenshot_path:
            messages.append(self.create_vision_message(message, screenshot_path))
        else:
            messages.append({"role": "user", "content": message})

        # Call Together AI with tools
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            max_tokens=max_tokens
        )

        # Update conversation history
        self.conversation_history.append(messages[-1])  # User message

        # Add assistant response to history
        assistant_message = {
            "role": "assistant",
            "content": response.choices[0].message.content
        }

        # Add tool calls if present
        if response.choices[0].message.tool_calls:
            assistant_message["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in response.choices[0].message.tool_calls
            ]

        self.conversation_history.append(assistant_message)

        return {
            "content": response.choices[0].message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": json.loads(tc.function.arguments)
                }
                for tc in (response.choices[0].message.tool_calls or [])
            ],
            "finish_reason": response.choices[0].finish_reason
        }

    def add_tool_result(self, tool_call_id: str, result: Any):
        """
        Add a tool execution result to conversation history.

        Args:
            tool_call_id: ID of the tool call
            result: Result from executing the tool
        """
        self.conversation_history.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": json.dumps(result) if not isinstance(result, str) else result
        })
