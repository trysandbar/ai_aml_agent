#!/usr/bin/env python3
"""
Workflow Runner for Browser-Use Agent

Executes predefined workflows using the Browser-Use agent
with logging, state tracking, and template variable support.

Usage:
    python run_workflow.py --workflow test_workflow.txt
    python run_workflow.py --workflow sandbar.txt --email user@example.com --password mypass
"""

import os
import sys
import argparse
import asyncio
import traceback
from pathlib import Path
from dotenv import load_dotenv

from agent import BrowserUseAgent, AgentConfig
from workflow import WorkflowExecutor, WorkflowConfig


async def run_workflow(args):
    """Execute a workflow with the Browser-Use agent"""

    # Load environment variables
    load_dotenv()

    # Create agent config
    agent_config = AgentConfig.from_env()

    if not agent_config.together_api_key:
        print("❌ Error: TOGETHER_API_KEY not set in environment")
        print("   Copy .env.example to .env and add your API key")
        return 1

    # Prepare template variables
    template_vars = {}

    # Load EMAIL and PASSWORD from .env if not provided via CLI
    email = args.email or os.getenv("GOOGLE_LOGIN")
    password = args.password or os.getenv("GOOGLE_PW")

    if email:
        template_vars["EMAIL"] = email
    if password:
        template_vars["PASSWORD"] = password

    # Add any custom variables
    if args.vars:
        for var in args.vars:
            if "=" in var:
                key, value = var.split("=", 1)
                template_vars[key] = value

    # Create workflow config with audit structure
    workflow_config = WorkflowConfig(
        workflow_file=args.workflow,
        template_vars=template_vars,
        tenant=args.tenant,
        audit_base_dir=args.audit_base_dir
    )

    # Create workflow executor
    executor = WorkflowExecutor(workflow_config)

    # Clean up old runs for this workflow (keep only last 2)
    from pathlib import Path
    import shutil
    from datetime import datetime
    workflow_name = Path(args.workflow).stem
    date_str = datetime.now().strftime("%Y-%m-%d")
    tenant_dir = Path(workflow_config.audit_base_dir) / workflow_config.tenant / date_str
    if tenant_dir.exists():
        old_runs = sorted([d for d in tenant_dir.glob(f"{workflow_name}_*") if d.is_dir()],
                         key=lambda x: x.stat().st_mtime, reverse=True)
        for old_run in old_runs[2:]:  # Keep latest 2, delete rest
            shutil.rmtree(old_run)
            print(f"🗑️  Deleted old run: {old_run.name}")

    # Load workflow
    print(f"📋 Loading workflow: {args.workflow}")

    # Show full absolute path to screenshots
    screenshots_dir = Path(executor.config.session_dir) / "screenshots"
    abs_screenshots_path = screenshots_dir.resolve()
    print(f"\n{'='*70}")
    print(f"📸 SCREENSHOTS PATH (open in Finder):")
    print(f"   {abs_screenshots_path}")
    print(f"{'='*70}\n")

    task = executor.load_workflow()

    # Create agent
    agent = BrowserUseAgent(agent_config)

    # Execute workflow
    print(f"\n{'='*60}")
    print(f"Starting workflow execution: {Path(args.workflow).stem}")
    print(f"{'='*60}\n")

    try:
        # Run the workflow
        result = await agent.run_task(task)

        # Save screenshots with metadata from Browser-Use to audit directory
        if result["history"]:
            print(f"\n📸 Saving screenshots with metadata to audit directory...")
            executor.save_screenshots_with_metadata(result["history"])

        # Update state
        executor.state.completed = (result["status"] == "completed")
        executor.state.result = {
            "status": result["status"],
            "final_result": str(result["final_result"]) if result["final_result"] else None,
            "screenshots_captured": executor.state.screenshots_captured,
            "errors": result["errors"]
        }

        if result["errors"]:
            executor.state.errors.extend(result["errors"])

        # Log completion
        executor.logger.log_completion(executor.state)

        # Save final state (always saved in audit structure)
        executor.save_state()
        print(f"State saved to: {workflow_config.state_file}")

        # Print summary
        print(f"\n{'='*60}")
        print(f"✅ Workflow completed")
        print(f"Status: {result['status']}")
        print(f"Screenshots captured: {executor.state.screenshots_captured}")
        print(f"Audit directory: {executor.config.session_dir}")
        print(f"{'='*60}\n")

        return 0 if result["status"] == "completed" else 1

    except Exception as e:
        print(f"\n❌ Workflow failed: {e}")
        print(f"\n🔍 Full traceback:")
        traceback.print_exc()
        executor.logger.log_error(str(e), {"exception": str(type(e).__name__), "traceback": traceback.format_exc()})

        # Update state
        executor.state.errors.append(str(e))

        # Save error state
        executor.save_state()

        return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Execute workflows with the Browser-Use agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run test workflow
  python run_workflow.py --workflow test_workflow.txt

  # Run sandbar.txt workflow
  python run_workflow.py --workflow sandbar.txt \\
      --email user@example.com --password mypass

  # Run with specific tenant
  python run_workflow.py --workflow sandbar.txt \\
      --tenant acme_corp --email user@example.com --password mypass

  # Run with custom variables
  python run_workflow.py --workflow custom.txt \\
      --var TENANT_NAME=current --var URL=https://app.example.com

Audit Structure:
  All outputs are organized for audit compliance:
  audit_logs/{tenant}/{date}/{workflow}_{session}/
    ├── screenshots/     (screenshots from browser automation)
    ├── logs/           (structured JSONL logs)
    └── state/          (workflow state for debugging)
        """
    )

    parser.add_argument(
        "--workflow",
        required=True,
        help="Path to workflow file (e.g., test_workflow.txt)"
    )

    parser.add_argument(
        "--tenant",
        default="default",
        help="Tenant identifier for multi-tenant systems (default: default)"
    )

    parser.add_argument(
        "--email",
        help="Email address (replaces {EMAIL} in workflow)"
    )

    parser.add_argument(
        "--password",
        help="Password (replaces {PASSWORD} in workflow)"
    )

    parser.add_argument(
        "--var",
        dest="vars",
        action="append",
        help="Custom template variable (format: KEY=VALUE, can be used multiple times)"
    )

    # Always use browser_use_agent/audit_logs regardless of where script is run from
    script_dir = Path(__file__).parent.resolve()
    default_audit_dir = script_dir / "audit_logs"

    parser.add_argument(
        "--audit-base-dir",
        default=str(default_audit_dir),
        help=f"Base directory for audit storage (default: {default_audit_dir})"
    )

    args = parser.parse_args()

    # Validate workflow file exists
    if not os.path.exists(args.workflow):
        print(f"❌ Error: Workflow file not found: {args.workflow}")
        return 1

    # Run workflow
    exit_code = asyncio.run(run_workflow(args))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
