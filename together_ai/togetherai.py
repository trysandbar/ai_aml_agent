"""
Together AI client library using OpenAI-compatible API.

This library provides a simple interface to Together AI's text models
using the OpenAI Python client for API compatibility.
"""

import logging
import os
from typing import Any, Dict, List, Optional, Union

from openai import OpenAI

logger = logging.getLogger(__name__)


class TogetherAIClient:
    """
    A client for interacting with Together AI's text models using
    OpenAI-compatible API.

    Default model: meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8
    """

    DEFAULT_MODEL = "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"
    BASE_URL = "https://api.together.xyz/v1"

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        max_retries: int = 3,
        timeout: Optional[float] = None,
    ):
        """
        Initialize the Together AI client.

        Args:
            api_key: Together AI API key. If not provided, will look for
                TOGETHER_API_KEY env var.
            base_url: Base URL for the API. Defaults to Together AI's
                OpenAI-compatible endpoint.
            max_retries: Maximum number of retries for API calls (default: 3).
                The OpenAI client has built-in exponential backoff.
            timeout: Request timeout in seconds.
        """
        self.api_key = api_key or os.getenv("TOGETHER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key is required. Provide it directly or set "
                "TOGETHER_API_KEY environment variable."
            )

        self.base_url = base_url or self.BASE_URL
        self.max_retries = max_retries

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            max_retries=max_retries,
            timeout=timeout,
        )

        # Configure logging to capture retry attempts
        logging.getLogger("openai._base_client").setLevel(logging.INFO)

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs,
    ) -> Union[Dict[str, Any], Any]:
        """
        Create a chat completion using Together AI's text models.

        Args:
            messages: List of message objects with 'role' and 'content' keys
            model: Model to use. Defaults to DEFAULT_MODEL
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            stream: Whether to stream the response
            **kwargs: Additional parameters to pass to the API

        Returns:
            Chat completion response object or stream iterator
        """
        response = self.client.chat.completions.create(
            model=model or self.DEFAULT_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            **kwargs,
        )

        return response

    def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_message: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        Generate text from a simple prompt.

        Args:
            prompt: The text prompt to generate from
            model: Model to use. Defaults to DEFAULT_MODEL
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            system_message: Optional system message to set context
            **kwargs: Additional parameters to pass to the API

        Returns:
            Generated text content
        """
        messages = []

        if system_message:
            messages.append({"role": "system", "content": system_message})

        messages.append({"role": "user", "content": prompt})

        response = self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False,
            **kwargs,
        )

        return response.choices[0].message.content

    def stream_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system_message: Optional[str] = None,
        **kwargs,
    ):
        """
        Generate streaming text from a prompt.

        Args:
            prompt: The text prompt to generate from
            model: Model to use. Defaults to DEFAULT_MODEL
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            system_message: Optional system message to set context
            **kwargs: Additional parameters to pass to the API

        Yields:
            Stream chunks with generated text
        """
        messages = []

        if system_message:
            messages.append({"role": "system", "content": system_message})

        messages.append({"role": "user", "content": prompt})

        stream = self.chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs,
        )

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content


# Convenience functions for quick usage
def create_client(api_key: Optional[str] = None) -> TogetherAIClient:
    """Create a Together AI client instance."""
    return TogetherAIClient(api_key=api_key)


def generate_text(
    prompt: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    system_message: Optional[str] = None,
    max_retries: int = 3,
    timeout: Optional[float] = None,
    **kwargs,
) -> str:
    """
    Quick function to generate text without creating a client instance.

    Args:
        prompt: The text prompt to generate from
        api_key: Together AI API key
        model: Model to use. Defaults to DEFAULT_MODEL
        temperature: Sampling temperature (0-2)
        max_tokens: Maximum tokens in response
        system_message: Optional system message to set context
        max_retries: Maximum number of retries (default: 3)
        timeout: Request timeout in seconds
        **kwargs: Additional parameters to pass to the API

    Returns:
        Generated text content
    """
    client = TogetherAIClient(api_key=api_key, max_retries=max_retries, timeout=timeout)
    return client.generate_text(
        prompt=prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        system_message=system_message,
        **kwargs,
    )


def chat_completion(
    messages: List[Dict[str, str]],
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    stream: bool = False,
    max_retries: int = 3,
    timeout: Optional[float] = None,
    **kwargs,
) -> Union[Dict[str, Any], Any]:
    """
    Quick function to create chat completion without creating a client instance.

    Args:
        messages: List of message objects with 'role' and 'content' keys
        api_key: Together AI API key
        model: Model to use. Defaults to DEFAULT_MODEL
        temperature: Sampling temperature (0-2)
        max_tokens: Maximum tokens in response
        stream: Whether to stream the response
        max_retries: Maximum number of retries (default: 3)
        timeout: Request timeout in seconds
        **kwargs: Additional parameters to pass to the API

    Returns:
        Chat completion response object or stream iterator
    """
    client = TogetherAIClient(api_key=api_key, max_retries=max_retries, timeout=timeout)
    return client.chat_completion(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=stream,
        **kwargs,
    )


if __name__ == "__main__":
    import sys

    # Simple test of the library
    try:
        # Test basic text generation
        print("Testing Together AI library...")
        print("=" * 50)

        # You can set your API key as an environment variable or pass it
        # directly
        api_key = os.getenv("TOGETHER_API_KEY")
        if not api_key:
            print(
                "Please set TOGETHER_API_KEY environment variable or modify "
                "this script to include your API key"
            )
            sys.exit(1)

        # Test 1: Simple text generation
        print("Test 1: Simple text generation")
        response = generate_text(
            prompt="What is the capital of France?", api_key=api_key, max_tokens=50
        )
        print(f"Response: {response}")
        print()

        # Test 2: Using client class
        print("Test 2: Using client class")
        client = TogetherAIClient(api_key=api_key)
        response = client.generate_text(
            prompt="Explain machine learning in one sentence.",
            max_tokens=100,
            temperature=0.5,
        )
        print(f"Response: {response}")
        print()

        # Test 3: Chat completion with system message
        print("Test 3: Chat completion with system message")
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that answers in exactly 10 words."
                ),
            },
            {"role": "user", "content": "What is Python programming language?"},
        ]
        chat_response = chat_completion(
            messages=messages, api_key=api_key, max_tokens=50
        )
        print(f"Response: {chat_response.choices[0].message.content}")
        print()

        # Test 4: Streaming response
        print("Test 4: Streaming text generation")
        print("Streaming response: ", end="", flush=True)
        for chunk in client.stream_text(
            prompt="Count from 1 to 5:", max_tokens=30, temperature=0.1
        ):
            print(chunk, end="", flush=True)
        print("\n")

        print("\nAll tests completed successfully!")

    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have:")
        print("1. Set TOGETHER_API_KEY environment variable")
        print("2. Installed the 'openai' package: pip install openai")
        sys.exit(1)
