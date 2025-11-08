"""
Workflow Executor for Browser-Use Agent

Loads workflow files and integrates them with the Browser-Use agent,
providing template variable replacement, logging, state tracking, and audit screenshots.
"""

import os
import json
import base64
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict


# ============================================================================
# Workflow Configuration
# ============================================================================

@dataclass
class WorkflowConfig:
    """Configuration for workflow execution"""
    workflow_file: str
    template_vars: Dict[str, str]
    tenant: str = "default"  # Tenant identifier for multi-tenant systems
    audit_base_dir: str = "audit_logs"  # Base directory for audit storage
    session_id: Optional[str] = None  # Auto-generated if not provided

    def __post_init__(self):
        """Create audit directory structure"""
        # Generate session_id if not provided
        if not self.session_id:
            self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Get workflow name from file
        workflow_name = Path(self.workflow_file).stem

        # Create audit directory structure: audit_logs/{tenant}/{date}/{workflow}_{session}/
        date_str = datetime.now().strftime("%Y-%m-%d")
        self.session_dir = Path(self.audit_base_dir) / self.tenant / date_str / f"{workflow_name}_{self.session_id}"

        # Create subdirectories
        self.screenshots_dir = self.session_dir / "screenshots"
        self.logs_dir = self.session_dir / "logs"
        self.state_dir = self.session_dir / "state"

        # Create all directories
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # Set file paths
        self.log_file = self.logs_dir / f"{workflow_name}.jsonl"
        self.state_file = self.state_dir / "workflow_state.json"


# ============================================================================
# Workflow State Tracking
# ============================================================================

@dataclass
class WorkflowState:
    """Tracks workflow execution state"""
    workflow_name: str
    started_at: str
    completed: bool = False
    current_step: Optional[str] = None
    iterations: int = 0
    screenshots_captured: int = 0
    errors: list = None
    result: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        self.errors = self.errors if self.errors is not None else []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowState":
        """Create from dictionary"""
        return cls(**data)


# ============================================================================
# Workflow Logger
# ============================================================================

class WorkflowLogger:
    """Structured logger for workflow execution"""

    def __init__(self, log_file: Path, workflow_name: str, session_id: str):
        self.log_file = log_file
        self.workflow_name = workflow_name
        self.session_id = session_id

        # Set up Python logger
        self.logger = logging.getLogger(f"workflow.{workflow_name}")
        self.logger.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        self.logger.addHandler(console_handler)

        # Capture all Browser-Use agent logs to file
        self.agent_log_file = log_file.parent / f"{workflow_name}_agent.log"
        root_logger = logging.getLogger()

        # Add file handler to root logger to capture ALL logs
        file_handler = logging.FileHandler(self.agent_log_file, mode='w')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        root_logger.addHandler(file_handler)
        root_logger.setLevel(logging.INFO)

    def log_event(self, event_type: str, data: Dict[str, Any]):
        """Log an event as JSON line"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "event_type": event_type,
            "data": data
        }

        # Write to JSONL file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(event) + "\n")

        # Also log to console
        self.logger.info(f"{event_type}: {json.dumps(data, indent=2)}")

    def log_start(self, workflow_file: str, template_vars: Dict[str, str]):
        """Log workflow start"""
        self.log_event("workflow_start", {
            "workflow_file": workflow_file,
            "template_vars": {k: "***" if "password" in k.lower() else v
                             for k, v in template_vars.items()}
        })

    def log_screenshot(self, screenshot_path: str):
        """Log screenshot capture"""
        self.log_event("screenshot", {
            "path": screenshot_path
        })

    def log_error(self, error: str, details: Dict[str, Any]):
        """Log an error"""
        self.log_event("error", {
            "error": error,
            "details": details
        })
        self.logger.error(f"Error: {error}")

    def log_completion(self, state: WorkflowState):
        """Log workflow completion"""
        self.log_event("workflow_complete", state.to_dict())
        print(f"\n{'='*60}")
        print(f"Workflow logs (JSONL): {self.log_file}")
        print(f"Agent logs (detailed): {self.agent_log_file}")
        print(f"{'='*60}\n")


# ============================================================================
# Workflow Loader
# ============================================================================

class WorkflowLoader:
    """Loads and processes workflow files"""

    @staticmethod
    def load_workflow(workflow_file: str, template_vars: Dict[str, str]) -> str:
        """
        Load workflow file and replace template variables

        Args:
            workflow_file: Path to workflow file (e.g., test_workflow.txt)
            template_vars: Dictionary of variables to replace (e.g., {EMAIL: "user@example.com"})

        Returns:
            Processed workflow content (task for Browser-Use agent)
        """
        # Read workflow file
        with open(workflow_file, "r") as f:
            content = f.read()

        # Replace template variables
        for key, value in template_vars.items():
            placeholder = f"{{{key}}}"
            content = content.replace(placeholder, value)

        return content


# ============================================================================
# Workflow Executor
# ============================================================================

class WorkflowExecutor:
    """Executes workflows with the Browser-Use agent"""

    def __init__(self, config: WorkflowConfig):
        self.config = config
        workflow_name = Path(config.workflow_file).stem

        # Ensure session_id is always a string
        session_id = config.session_id or datetime.now().strftime("%Y%m%d_%H%M%S")

        self.logger = WorkflowLogger(
            config.log_file,
            workflow_name,
            session_id
        )
        self.state = WorkflowState(
            workflow_name=workflow_name,
            started_at=datetime.now().isoformat()
        )

    def load_workflow(self) -> str:
        """Load and process workflow file"""
        self.logger.log_start(self.config.workflow_file, self.config.template_vars)

        workflow_content = WorkflowLoader.load_workflow(
            self.config.workflow_file,
            self.config.template_vars
        )

        return workflow_content

    def save_screenshots_with_metadata(self, history):
        """
        Save screenshots from Browser-Use with metadata for each step

        Args:
            history: AgentHistoryList from Browser-Use agent.run()
        """
        if not hasattr(history, 'history'):
            print(f"⚠️  History object has no 'history' attribute")
            return

        # Get all screenshots from history
        screenshots_list = []
        if hasattr(history, 'screenshots'):
            screenshots_list = [s for s in history.screenshots(return_none_if_not_screenshot=False) if s]

        for idx, history_item in enumerate(history.history, start=1):
            try:
                # Get screenshot for this step - use from screenshots list if available
                screenshot_base64 = None
                if idx <= len(screenshots_list):
                    screenshot_base64 = screenshots_list[idx - 1]
                elif hasattr(history_item, 'state') and hasattr(history_item.state, 'screenshot'):
                    screenshot_base64 = history_item.state.screenshot

                # Create timestamped filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                filename = f"{timestamp}_step_{idx}"

                # Save screenshot if available
                if screenshot_base64:
                    img_path = self.config.screenshots_dir / f"{filename}.png"
                    img_data = base64.b64decode(screenshot_base64)
                    with open(img_path, "wb") as f:
                        f.write(img_data)
                    self.state.screenshots_captured += 1

                # Extract metadata
                metadata = {
                    "step": idx,
                    "timestamp": timestamp,
                    "screenshot": f"{filename}.png" if screenshot_base64 else None,
                    "url": getattr(history_item.state, 'url', None) if hasattr(history_item, 'state') else None,
                }

                # Add action information if available
                if hasattr(history_item, 'model_output') and history_item.model_output:
                    model_output = history_item.model_output
                    if hasattr(model_output, 'current_state') and hasattr(model_output.current_state, 'evaluation_previous_goal'):
                        metadata['evaluation'] = model_output.current_state.evaluation_previous_goal
                    if hasattr(model_output, 'action') and model_output.action:
                        actions = model_output.action if isinstance(model_output.action, list) else [model_output.action]
                        metadata['actions'] = []
                        for action in actions:
                            if hasattr(action, 'model_dump'):
                                metadata['actions'].append(action.model_dump())
                            else:
                                metadata['actions'].append(str(action))

                # Add timing information
                if hasattr(history_item, 'metadata') and history_item.metadata:
                    if hasattr(history_item.metadata, 'duration_seconds'):
                        metadata['duration_seconds'] = history_item.metadata.duration_seconds

                # Add result information
                if hasattr(history_item, 'result') and history_item.result:
                    results = history_item.result if isinstance(history_item.result, list) else [history_item.result]
                    metadata['results'] = []
                    for result in results:
                        result_data = {}
                        if hasattr(result, 'extracted_content') and result.extracted_content:
                            result_data['extracted_content'] = result.extracted_content
                        if hasattr(result, 'error') and result.error:
                            result_data['error'] = result.error
                        if hasattr(result, 'is_done'):
                            result_data['is_done'] = result.is_done
                        if result_data:
                            metadata['results'].append(result_data)

                # Save metadata JSON
                metadata_path = self.config.screenshots_dir / f"{filename}.json"
                with open(metadata_path, "w") as f:
                    json.dump(metadata, f, indent=2, default=str)

                # Log if screenshot was saved
                if screenshot_base64:
                    self.logger.log_screenshot(str(img_path))

            except Exception as e:
                self.logger.log_error(f"Failed to save screenshot/metadata {idx}", {"error": str(e)})

    def get_screenshot_dir(self) -> str:
        """Get the screenshot directory for this workflow session"""
        return str(self.config.screenshots_dir)

    def save_state(self):
        """Save current state to file"""
        with open(self.config.state_file, "w") as f:
            json.dump(self.state.to_dict(), f, indent=2)

    def load_state(self) -> Optional[WorkflowState]:
        """Load state from file if it exists"""
        if os.path.exists(self.config.state_file):
            with open(self.config.state_file, "r") as f:
                return WorkflowState.from_dict(json.load(f))
        return None


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Example: Load test workflow
    config = WorkflowConfig(
        workflow_file="test_workflow.txt",
        template_vars={}
    )

    executor = WorkflowExecutor(config)
    task = executor.load_workflow()

    print("Generated Task:")
    print("=" * 60)
    print(task)
    print("=" * 60)
