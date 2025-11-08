"""
Browser-Use Agent - Simplified browser automation with Kimi K2 via Together.ai

This is a significantly simplified implementation compared to the MCP approach:
- No MCP servers or stdio transport
- No manual tool routing or multi-server management
- Built-in screenshot capture and history tracking
- Automatic error recovery and retry logic
- Uses Kimi K2: #1 on BrowseComp (60.2%), 256K context, native agentic tool use
"""

import asyncio
import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

from browser_use import Agent, Browser, ChatOpenAI
from dotenv import load_dotenv


@dataclass
class AgentConfig:
    """Configuration for the Browser-Use agent"""
    together_api_key: str
    model: str = "moonshotai/Kimi-K2-Instruct-0905"
    max_iterations: int = 50
    headless: bool = True
    storage_state_path: Optional[str] = None  # Path to saved session state

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Load configuration from environment variables"""
        load_dotenv()

        together_api_key = os.getenv("TOGETHER_API_KEY")
        if not together_api_key:
            raise ValueError("TOGETHER_API_KEY not set in environment")

        return cls(
            together_api_key=together_api_key,
            model=os.getenv("TOGETHER_MODEL", "moonshotai/Kimi-K2-Instruct-0905"),
            max_iterations=int(os.getenv("AGENT_MAX_ITERATIONS", "50")),
            headless=os.getenv("AGENT_HEADLESS", "true").lower() == "true",
            storage_state_path=os.getenv("STORAGE_STATE_PATH")  # Optional session cache
        )


class BrowserUseAgent:
    """Simplified autonomous browser agent using Browser-Use library"""

    def __init__(self, config: AgentConfig):
        self.config = config

        # Initialize LLM with Together.ai via OpenAI-compatible endpoint
        self.llm = ChatOpenAI(
            model=config.model,
            api_key=config.together_api_key,
            base_url="https://api.together.xyz/v1",
            temperature=0.6  # K2 recommended temp
        )

        # Initialize browser with optional storage state for session reuse
        browser_kwargs = {"headless": config.headless}
        if config.storage_state_path:
            storage_path = Path(config.storage_state_path)
            if storage_path.exists():
                browser_kwargs["storage_state"] = str(storage_path)
                print(f"🔑 Loading saved session from: {config.storage_state_path}")
            else:
                print(f"⚠️  Storage state file not found: {config.storage_state_path}")

        self.browser = Browser(**browser_kwargs)

    async def run_task(self, task: str) -> dict:
        """
        Run a browser automation task.

        Args:
            task: Natural language description of the task

        Returns:
            Dict with:
                - status: "completed" or "failed"
                - history: AgentHistoryList with execution details
                - screenshots: List of base64 screenshot strings
                - final_result: Final result from the agent
                - errors: List of error messages if any
        """
        try:
            # Create agent with task
            agent = Agent(
                task=task,
                llm=self.llm,
                browser=self.browser
            )

            # Run the agent
            history = await agent.run()

            # Extract screenshots as base64 strings (filter out None values)
            screenshots = []
            if hasattr(history, 'screenshots'):
                screenshots = [s for s in history.screenshots(return_none_if_not_screenshot=False) if s is not None]

            # Extract results
            return {
                "status": "completed",
                "history": history,
                "screenshots": screenshots,
                "final_result": history.final_result() if hasattr(history, 'final_result') else None,
                "errors": history.errors() if hasattr(history, 'errors') else []
            }

        except Exception as e:
            return {
                "status": "failed",
                "history": None,
                "screenshots": [],
                "final_result": None,
                "errors": [str(e)]
            }


async def main():
    """Example usage"""
    config = AgentConfig.from_env()
    agent = BrowserUseAgent(config)

    # Run a simple test task
    task = "Navigate to https://example.com and describe what you see"
    result = await agent.run_task(task)

    print(f"Status: {result['status']}")
    print(f"Final Result: {result['final_result']}")
    print(f"Screenshots: {len(result['screenshots'])} captured")

    if result['errors']:
        print(f"Errors: {result['errors']}")


if __name__ == "__main__":
    asyncio.run(main())
