"""
Supervised Agent - Interactive workflow training for browser automation

Enables pair-training mode where:
1. Agent attempts task and detects when stuck
2. Pauses to ask user for guidance
3. Documents successful steps
4. Saves learnable workflow for replay
5. Supports refinement when workflows break

This creates a feedback loop for perfecting automation workflows.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import yaml
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from browser_use import Agent
from agent import BrowserUseAgent, AgentConfig
from supervised.workflow_model import WorkflowStep, LearnedWorkflow
from supervised.loop_detector import LoopDetector


logger = logging.getLogger(__name__)


class SupervisedAgent:
    """
    Browser agent with interactive supervision and workflow learning.

    Training Mode:
    - Monitors agent actions in real-time using lifecycle hooks
    - Detects loops and stuck states
    - Pauses for user guidance
    - Documents successful steps

    Replay Mode:
    - Executes saved workflows
    - Can re-enter training mode if workflow breaks
    """

    def __init__(self, config: AgentConfig, training_mode: bool = True):
        self.config = config
        self.training_mode = training_mode
        self.agent = BrowserUseAgent(config)
        self.loop_detector = LoopDetector()
        self.learned_steps: List[WorkflowStep] = []
        self.current_step = 0
        self.paused = False
        self.user_guidance: List[str] = []
        self.pause_reason: Optional[str] = None
        self.stuck_context: Optional[Dict] = None  # For storing context when paused

    async def train_workflow(self, task: str, workflow_name: str) -> LearnedWorkflow:
        """
        Train a new workflow interactively.

        Args:
            task: Natural language task description
            workflow_name: Name for the saved workflow

        Returns:
            LearnedWorkflow that can be saved and replayed
        """
        print(f"\n{'='*70}")
        print(f"🎓 TRAINING MODE: {workflow_name}")
        print(f"{'='*70}")
        print(f"Task: {task}")
        print(f"\nI'll work on this task and ask for help when stuck.")
        print(f"{'='*70}\n")

        # Start the browser agent with monitoring
        # We'll need to hook into browser-use's step execution
        # For now, simulate with a wrapper

        result = await self._train_with_monitoring(task)

        # Create learned workflow
        workflow = LearnedWorkflow(
            name=workflow_name,
            description=task,
            created_at=datetime.now().isoformat(),
            last_trained=datetime.now().isoformat(),
            steps=self.learned_steps,
            success_count=1 if result['status'] == 'completed' else 0,
            failure_count=1 if result['status'] != 'completed' else 0
        )

        return workflow

    async def _train_with_monitoring(self, task: str) -> Dict[str, Any]:
        """
        Execute task with real-time monitoring using browser-use lifecycle hooks.

        Strategy (following async best practices):
        - Use lightweight on_step_end hook to detect stuck states
        - Hook pauses agent but doesn't block
        - After agent.run() returns, check if paused
        - If paused, ask user for help (blocking I/O is OK here)
        - Incorporate guidance and restart
        - Repeat until completed or max iterations
        """
        max_training_iterations = 5
        iteration = 0

        while iteration < max_training_iterations:
            iteration += 1
            logger.info(f"Training iteration {iteration}/{max_training_iterations}")

            # Build task with accumulated guidance
            enhanced_task = self._build_enhanced_task(task, self.user_guidance)

            # Create lifecycle hooks
            async def on_step_end(agent):
                """Lightweight monitoring hook - non-blocking per best practices"""
                await self._monitor_step(agent)

            # Run agent with monitoring
            from browser_use import Agent

            try:
                # Create browser-use Agent directly with hooks
                llm = self.agent.llm
                browser = self.agent.browser

                agent = Agent(
                    task=enhanced_task,
                    llm=llm,
                    browser=browser
                )

                # Run with hooks and proper error handling
                history = await agent.run(on_step_end=on_step_end)

                # Convert to our result format
                result = {
                    'status': 'completed' if not history.errors() else 'completed',
                    'history': history,
                    'screenshots': history.screenshots() if hasattr(history, 'screenshots') else [],
                    'final_result': history.final_result() if hasattr(history, 'final_result') else None,
                    'errors': history.errors() if hasattr(history, 'errors') else []
                }

                # Check if we were paused (stuck detected)
                if self.paused and self.stuck_context:
                    # NOW we can do blocking I/O - outside the hook
                    print(f"\n{'='*70}")
                    print(f"⏸️  PAUSED - Agent appears stuck")
                    print(f"{'='*70}")
                    print(f"Reason: {self.stuck_context['reason']}")
                    print(f"Step: {self.stuck_context['step']}\n")

                    print("Recent actions:")
                    for i, action in enumerate(self.stuck_context['recent_actions'], 1):
                        print(f"  {i}. {action.get('action', 'unknown')}")

                    print(f"\n{'='*70}")
                    user_hint = input("💡 What should I try instead? (or 'quit' to stop): ").strip()
                    print(f"{'='*70}\n")

                    if user_hint.lower() in ['quit', 'exit', 'stop']:
                        print("⏹️  Training cancelled by user")
                        return result

                    # Add hint to guidance
                    self.user_guidance.append(user_hint)

                    # Document this learning
                    self.learned_steps.append(WorkflowStep(
                        step_number=len(self.learned_steps) + 1,
                        action='guidance',
                        description=f"User guidance: {user_hint}",
                        user_hint=user_hint
                    ))

                    print(f"💡 Got it! Restarting with your hint...\n")

                    # Reset state for next iteration
                    self.paused = False
                    self.stuck_context = None
                    self.loop_detector.reset()  # Clear history for fresh start
                    self.current_step = 0

                    continue  # Try again with new guidance

                # Not paused - check if completed
                if result['status'] == 'completed' and result['final_result']:
                    self._document_success(result, self.user_guidance)
                    return result

                # Failed without pause - likely need more iterations
                logger.warning(f"Iteration {iteration} completed without success")
                continue

            except Exception as e:
                # Proper async error handling
                logger.error(f"Error in training iteration {iteration}: {e}")
                result = {
                    'status': 'failed',
                    'history': None,
                    'screenshots': [],
                    'final_result': None,
                    'errors': [str(e)]
                }
                return result

        # Max iterations reached
        logger.warning(f"Training reached max iterations ({max_training_iterations})")
        return result if 'result' in locals() else {
            'status': 'incomplete',
            'history': None,
            'screenshots': [],
            'final_result': None,
            'errors': ['Max training iterations reached']
        }

    async def _monitor_step(self, agent):
        """
        Monitor agent step for loops and stuck states.

        IMPORTANT: This hook must be lightweight and non-blocking per browser-use best practices.
        We detect stuck state but don't block - we pause agent and handle user input outside the hook.
        """
        if not self.training_mode:
            return  # Only monitor in training mode

        try:
            # Get current action from agent history
            action_names = agent.history.action_names()
            if not action_names:
                return

            last_action = action_names[-1] if action_names else None

            # Track action in loop detector (lightweight operation)
            self.loop_detector.add_action({
                'action': last_action,
                'step': self.current_step,
                'error': len(agent.history.errors()) > 0
            })

            self.current_step += 1

            # Check if stuck (lightweight check)
            is_stuck, stuck_reason = self.loop_detector.is_stuck()

            if is_stuck and not self.paused:
                # Set flag and pause agent - NO BLOCKING I/O in hook
                self.paused = True
                self.pause_reason = stuck_reason

                # Store context for later user interaction (outside hook)
                self.stuck_context = {
                    'reason': stuck_reason,
                    'step': self.current_step,
                    'recent_actions': [
                        {'action': str(a), 'description': str(a)}
                        for a in action_names[-5:]
                    ]
                }

                # Pause the agent (non-blocking, built-in method)
                agent.pause()
                logger.info(f"Agent paused due to stuck state: {stuck_reason}")

        except Exception as e:
            # Proper error handling in hook per best practices
            logger.error(f"Error in monitoring hook: {e}")
            # Don't crash the agent on hook errors

    def _build_enhanced_task(self, original_task: str, guidance: List[str]) -> str:
        """Build task with accumulated user guidance"""
        if not guidance:
            return original_task

        enhanced = original_task + "\n\nIMPORTANT GUIDANCE (learned from training):\n"
        for hint in guidance:
            enhanced += f"- {hint}\n"

        return enhanced

    def _document_success(self, result: Dict, guidance: List[str]):
        """Document successful workflow execution"""
        # Extract and save successful pattern
        print(f"\n📝 Documenting successful workflow...")

        # Extract actions from history
        history = result.get('history')
        if history and hasattr(history, 'action_names'):
            actions = history.action_names()
            for i, action in enumerate(actions, 1):
                self.learned_steps.append(WorkflowStep(
                    step_number=i,
                    action=str(action),
                    description=f"Step {i}: {action}"
                ))

        # Add final success step
        self.learned_steps.append(WorkflowStep(
            step_number=len(self.learned_steps) + 1,
            action='completed',
            description=f"Task completed: {result.get('final_result', 'Success')}"
        ))

        print(f"   Captured {len(self.learned_steps)} learning steps")
        print(f"   With {len(guidance)} user guidance hints")


    def save_workflow(self, workflow: LearnedWorkflow, output_path: Path):
        """Save learned workflow to YAML file"""
        workflow_dict = {
            'name': workflow.name,
            'description': workflow.description,
            'created_at': workflow.created_at,
            'last_trained': workflow.last_trained,
            'success_count': workflow.success_count,
            'failure_count': workflow.failure_count,
            'steps': [
                {
                    'step_number': s.step_number,
                    'action': s.action,
                    'description': s.description,
                    'selector': s.selector,
                    'text': s.text,
                    'url': s.url,
                    'field_name': s.field_name,
                    'user_hint': s.user_hint
                }
                for s in workflow.steps
            ]
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            yaml.dump(workflow_dict, f, default_flow_style=False, sort_keys=False)

        print(f"✅ Workflow saved to: {output_path}")

    @staticmethod
    def load_workflow(workflow_path: Path) -> LearnedWorkflow:
        """Load a saved workflow from YAML"""
        with open(workflow_path) as f:
            data = yaml.safe_load(f)

        steps = [
            WorkflowStep(
                step_number=s['step_number'],
                action=s['action'],
                description=s['description'],
                selector=s.get('selector'),
                text=s.get('text'),
                url=s.get('url'),
                field_name=s.get('field_name'),
                user_hint=s.get('user_hint')
            )
            for s in data['steps']
        ]

        return LearnedWorkflow(
            name=data['name'],
            description=data['description'],
            created_at=data['created_at'],
            last_trained=data['last_trained'],
            steps=steps,
            success_count=data.get('success_count', 0),
            failure_count=data.get('failure_count', 0)
        )

    async def replay_workflow(self, workflow: LearnedWorkflow) -> Dict[str, Any]:
        """
        Execute a learned workflow.

        Args:
            workflow: Previously learned workflow

        Returns:
            Execution result
        """
        print(f"\n{'='*70}")
        print(f"▶️  REPLAY MODE: {workflow.name}")
        print(f"{'='*70}")
        print(f"Executing {len(workflow.steps)} learned steps...")
        print(f"{'='*70}\n")

        # Convert workflow steps to executable task
        # For now, create a natural language description
        task_description = workflow.description + "\n\nSteps:\n"
        for step in workflow.steps:
            task_description += f"{step.step_number}. {step.description}\n"

        result = await self.agent.run_task(task_description)

        if result['status'] == 'completed':
            workflow.success_count += 1
        else:
            workflow.failure_count += 1

        return result


async def main():
    """Example usage of SupervisedAgent"""
    config = AgentConfig.from_env()

    # Training mode
    agent = SupervisedAgent(config, training_mode=True)

    task = "Go to https://app.dev.sandbar.ai, click Customers in sidebar, pick a customer with alerts, view their AI Summary badge"

    workflow = await agent.train_workflow(task, "sandbar_customer_review")

    # Save learned workflow
    output_path = Path("browser_use_agent/workflows/sandbar_customer_review.yml")
    agent.save_workflow(workflow, output_path)

    print(f"\n✅ Training complete! Workflow saved.")
    print(f"   Steps learned: {len(workflow.steps)}")


if __name__ == "__main__":
    asyncio.run(main())
