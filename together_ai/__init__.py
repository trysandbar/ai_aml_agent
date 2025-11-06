"""
Together AI Python library for Element.

A simple interface to Together AI's text models using OpenAI-compatible API.
"""

from .togetherai import TogetherAIClient, chat_completion, create_client, generate_text

__version__ = "1.0.0"

__all__ = [
    "TogetherAIClient",
    "create_client",
    "generate_text",
    "chat_completion",
]
