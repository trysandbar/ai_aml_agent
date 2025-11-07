"""
Autonomous Agent Loop - Browser automation using Llama 4 and Playwright.
Direct Playwright Python integration (no MCP SDK).
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from playwright_client import PlaywrightClient
from browser_tools import TOOL_DEFINITIONS, execute_tool
from together_ai.agent_client import TogetherAgentClient


@dataclass
class AgentState:
    """Current state of the agent."""
    iteration: int = 0
    goal: str = ""
    current_url: str = ""
    page_title: str = ""
    last_action: str = ""
    screenshot_path: Optional[str] = None
    completed: bool = False
    error: Optional[str] = None


@dataclass
class AgentResult:
    """Result of agent execution."""
    success: bool
    steps_taken: int
    final_state: AgentState
    error: Optional[str] = None


class BrowserAgent:
    """
    Autonomous browser agent using Llama 4 vision + Playwright tools.

    Architecture:
    - Playwright Python for browser automation
    - Together AI Llama 4 provides vision + reasoning
    - Agent loop: screenshot → reason → act → repeat
    """

    def __init__(
        self,
        goal: str,
        client_id: str = "default",
        max_iterations: int = 50,
        screenshot_dir: str = "test_screenshots",
        initial_url: str = "about:blank",
        headless: bool = True
    ):
        """
        Initialize the browser agent.

        Args:
            goal: Natural language goal for the agent
            client_id: Client identifier for organizing screenshots/state
            max_iterations: Maximum number of agent loop iterations
            screenshot_dir: Directory to save screenshots
            initial_url: Initial URL to navigate to
            headless: Run browser in headless mode
        """
        print(f"[DEBUG] Initializing BrowserAgent with goal: {goal[:50]}...")
        self.goal = goal
        self.client_id = client_id
        self.max_iterations = max_iterations
        self.screenshot_dir = Path(screenshot_dir) / client_id
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.initial_url = initial_url
        self.headless = headless

        # Agent state
        self.state = AgentState(goal=goal)
        self.iteration_history: List[Dict[str, Any]] = []

        # Playwright and AI clients
        self.playwright_client: Optional[PlaywrightClient] = None
        print("[DEBUG] Creating Together AI client...")
        self.ai_client = TogetherAgentClient()
        print("[DEBUG] Together AI client created")

        # System prompt for agent
        print("[DEBUG] Setting up system prompt...")
        self._setup_system_prompt()
        print("[DEBUG] BrowserAgent initialization complete")

    def _setup_system_prompt(self):
        """Configure the system prompt for the agent."""
        prompt = f"""You are an autonomous browser automation agent using vision and browser control tools.

Goal: {self.goal}

You have access to these browser control tools via Playwright:
- navigate(url) - Navigate to a URL
- click(selector) - Click an element using CSS selector (e.g., "#submit-button", "input[type='submit']")
- fill(selector, value) - Fill a form field with a value
- evaluate(script) - Execute JavaScript in the browser and return the result
- wait_for_timeout(seconds) - Wait for a specified number of seconds

IMPORTANT INSTRUCTIONS:
1. Browser is already running in headless mode
2. Analyze screenshots carefully to understand the current page state
3. Use evaluate() to extract page information (URL, title, text content)
4. Think step-by-step about what needs to be done to achieve the goal
5. Use CSS selectors for click and fill operations (e.g., "#search-button", "input[name='q']")
6. When goal is achieved, explain what was accomplished

Your workflow:
1. I will provide you with a screenshot of the current page state
2. Analyze what you see in the screenshot
3. Decide the next action to move toward the goal
4. Execute action via tool call
5. Repeat until goal achieved

When you've completed the goal, respond with "GOAL_ACHIEVED:" followed by a summary.
"""
        self.ai_client.set_system_prompt(prompt)


    async def _run_agent_loop(self) -> AgentResult:
        """Main agent loop: screenshot → reason → act → repeat."""
        print(f"\n🤖 Agent starting with goal: {self.goal}")
        print(f"Max iterations: {self.max_iterations}\n")

        try:
            # Initialize Playwright browser
            print(f"🌐 Initializing browser (headless={self.headless})...")
            self.playwright_client = PlaywrightClient(headless=self.headless)
            await self.playwright_client.start()
            print(f"✅ Browser initialized\n")

            # Navigate to initial URL
            if self.initial_url != "about:blank":
                print(f"🔗 Navigating to {self.initial_url}...")
                await self.playwright_client.navigate(self.initial_url)
                print(f"✅ Navigation complete\n")

            for iteration in range(self.max_iterations):
                self.state.iteration = iteration + 1
                print(f"\n--- Iteration {self.state.iteration} ---")

                # Step 1: Take screenshot
                print(f"[DEBUG] Taking screenshot...")
                screenshot_path = await self._take_screenshot()
                print(f"[DEBUG] Screenshot complete: {screenshot_path}")

                # Step 2: Get page state
                print(f"[DEBUG] Getting page state...")
                page_state = await self._get_page_state()
                print(f"[DEBUG] Page state: {page_state}")

                # Step 3: Build context for AI
                print(f"[DEBUG] Building context...")
                context = self._build_context(page_state)
                print(f"[DEBUG] Context built: {len(context)} chars")

                # Step 4: Call Llama 4 with tools
                print(f"[DEBUG] Calling Llama 4 with {len(TOOL_DEFINITIONS)} tools...")
                response = self.ai_client.call_with_tools(
                    message=context,
                    tools=TOOL_DEFINITIONS,
                    screenshot_path=screenshot_path
                )
                print(f"[DEBUG] Llama 4 response: {response['content'][:100] if response['content'] else 'No content'}")

                # Check if goal achieved
                if response["content"] and "GOAL_ACHIEVED:" in response["content"]:
                    print(f"\n✅ {response['content']}")
                    self.state.completed = True
                    break

                # Step 5: Execute tool calls
                if response["tool_calls"]:
                    for tool_call in response["tool_calls"]:
                        result = await self._execute_tool(
                            tool_call["name"],
                            tool_call["arguments"]
                        )

                        # Add result to conversation
                        self.ai_client.add_tool_result(tool_call["id"], result)

                        # Update state
                        self.state.last_action = f"{tool_call['name']}({tool_call['arguments']})"

                # Save iteration history
                self.iteration_history.append({
                    "iteration": iteration + 1,
                    "screenshot": screenshot_path,
                    "page_state": page_state,
                    "response": response,
                    "action": self.state.last_action
                })

                # Safety check: detect loops
                if iteration > 5 and self._detect_loop():
                    print("\n⚠️ Loop detected. Stopping.")
                    self.state.error = "Loop detected"
                    break

            # Finalize
            if not self.state.completed:
                print(f"\n⚠️ Agent stopped after {self.state.iteration} iterations without completing goal.")

            return AgentResult(
                success=self.state.completed,
                steps_taken=self.state.iteration,
                final_state=self.state,
                error=self.state.error
            )

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            self.state.error = str(e)
            return AgentResult(
                success=False,
                steps_taken=self.state.iteration,
                final_state=self.state,
                error=str(e)
            )
        finally:
            # Clean up browser
            if self.playwright_client:
                print("\n🛑 Closing browser...")
                await self.playwright_client.close()

    async def _take_screenshot(self) -> str:
        """Take a screenshot of current browser state."""
        screenshot_name = f"iteration_{self.state.iteration:03d}"
        screenshot_path = self.screenshot_dir / f"{screenshot_name}.png"

        # Use Playwright client to take screenshot with metadata
        await self.playwright_client.screenshot(
            name=screenshot_name,
            path=screenshot_path,
            save_metadata=True,  # Save JSON metadata files like playwright_agent
            tenant_slug=self.client_id,
            session_id=f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        self.state.screenshot_path = str(screenshot_path)
        print(f"📸 Screenshot saved: {screenshot_path}")

        return str(screenshot_path)

    async def _get_page_state(self) -> Dict[str, str]:
        """Get current page state (URL, title, etc) via JavaScript."""
        # Execute JavaScript to get page info
        script = """
        JSON.stringify({
            url: window.location.href,
            title: document.title,
            readyState: document.readyState
        })
        """

        result = await self.playwright_client.evaluate(script)

        # Parse result
        page_state = {"url": "unknown", "title": "unknown", "readyState": "unknown"}

        if result:
            try:
                # Result might already be a dict or a JSON string
                if isinstance(result, str):
                    page_state = json.loads(result)
                elif isinstance(result, dict):
                    page_state = result
            except:
                pass

        self.state.current_url = page_state.get("url", "unknown")
        self.state.page_title = page_state.get("title", "unknown")

        return page_state

    def _build_context(self, page_state: Dict[str, str]) -> str:
        """Build context message for the AI."""
        context = f"""Current page state:
- URL: {page_state.get('url', 'unknown')}
- Title: {page_state.get('title', 'unknown')}
- Iteration: {self.state.iteration}/{self.max_iterations}
- Last action: {self.state.last_action or 'None'}

What should I do next to achieve the goal: "{self.goal}"?

Analyze the screenshot and decide the next action using available tools.
"""
        return context

    async def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a browser tool call."""
        print(f"🔧 Executing: {tool_name}({arguments})")

        try:
            result = await execute_tool(self.playwright_client.page, tool_name, arguments)
            return result or "Tool executed successfully"

        except Exception as e:
            error_msg = f"Error executing {tool_name}: {e}"
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
            return error_msg

    def _detect_loop(self) -> bool:
        """Detect if agent is stuck in a loop (same actions repeating)."""
        if len(self.iteration_history) < 4:
            return False

        # Check if last 3 actions are the same
        last_actions = [
            h.get("action", "") for h in self.iteration_history[-3:]
        ]

        return len(set(last_actions)) == 1 and last_actions[0] != ""

    def run(self) -> AgentResult:
        """Run the agent synchronously."""
        print("[DEBUG] Starting async run...")
        return asyncio.run(self._run_agent_loop())
