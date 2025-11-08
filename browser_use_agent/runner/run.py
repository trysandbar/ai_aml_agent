#!/usr/bin/env python3
"""
Workflow Runner - Execute trained workflows

Runs workflows that were trained using the supervised training app.

Usage:
    python run.py --workflow ../supervised/workflows/sandbar_review.yml
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import argparse

from agent import AgentConfig
from supervised.supervisor import SupervisedAgent


async def run_workflow(workflow_path: Path):
    """Execute a trained workflow"""

    if not workflow_path.exists():
        print(f"❌ Workflow not found: {workflow_path}")
        return 1

    print(f"\n{'='*70}")
    print(f"▶️  EXECUTING TRAINED WORKFLOW")
    print(f"{'='*70}\n")

    # Load config
    config = AgentConfig.from_env()

    # Create agent in replay mode (training_mode=False)
    agent = SupervisedAgent(config, training_mode=False)

    # Load workflow
    workflow = agent.load_workflow(workflow_path)

    print(f"Workflow: {workflow.name}")
    print(f"Description: {workflow.description}")
    print(f"Steps: {len(workflow.steps)}")
    print(f"Success history: {workflow.success_count} / {workflow.success_count + workflow.failure_count}")
    print(f"\n{'='*70}\n")

    # Execute workflow
    result = await agent.replay_workflow(workflow)

    # Save updated stats
    agent.save_workflow(workflow, workflow_path)

    if result['status'] == 'completed':
        print(f"\n{'='*70}")
        print(f"✅ Workflow executed successfully!")
        print(f"{'='*70}\n")
        return 0
    else:
        print(f"\n{'='*70}")
        print(f"⚠️  Workflow execution failed")
        print(f"{'='*70}")
        print(f"\nYou can re-train this workflow with:")
        print(f"  cd ../supervised")
        print(f"  python train.py --retrain {workflow_path.name}")
        print(f"{'='*70}\n")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="Execute trained browser automation workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run a trained workflow
  python run.py --workflow ../supervised/workflows/sandbar_review.yml

  # Run with custom API key
  TOGETHER_API_KEY=xxx python run.py --workflow ../supervised/workflows/sandbar_review.yml

Workflow Format:
  Workflows are YAML files created by the supervised training app.
  They contain learned steps and user guidance for repeatable automation.

Production Usage:
  1. Train workflows with supervised/train.py
  2. Test replay with this runner
  3. Integrate into production pipelines
  4. Re-train if workflows break (site changes)
        """
    )

    parser.add_argument(
        "--workflow",
        required=True,
        help="Path to trained workflow YAML file"
    )

    args = parser.parse_args()
    workflow_path = Path(args.workflow)

    exit_code = asyncio.run(run_workflow(workflow_path))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
