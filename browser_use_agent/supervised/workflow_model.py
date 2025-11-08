"""
Workflow data models for learned automation workflows
"""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class WorkflowStep:
    """A single learned step in a workflow"""
    step_number: int
    action: str  # navigate, click, type, extract, etc
    description: str  # Human-readable description
    selector: Optional[str] = None
    text: Optional[str] = None
    url: Optional[str] = None
    field_name: Optional[str] = None
    screenshot_before: Optional[str] = None
    screenshot_after: Optional[str] = None
    user_hint: Optional[str] = None  # If user provided guidance


@dataclass
class LearnedWorkflow:
    """Complete learned workflow that can be replayed"""
    name: str
    description: str
    created_at: str
    last_trained: str
    steps: List[WorkflowStep]
    success_count: int = 0
    failure_count: int = 0
