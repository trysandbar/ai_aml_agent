"""
Loop detection for browser automation agents

Detects when agent is stuck in loops:
- Repeated actions (same click 3+ times)
- Error loops (multiple errors in sequence)
- Scroll loops (scrolling without progress)
"""

from typing import Dict, Any, List, Optional


class LoopDetector:
    """Detects when agent is stuck in loops"""

    def __init__(self, window_size: int = 5, repeat_threshold: int = 3):
        """
        Initialize loop detector.

        Args:
            window_size: Number of recent actions to analyze
            repeat_threshold: Number of repeats that indicate a loop
        """
        self.window_size = window_size
        self.repeat_threshold = repeat_threshold
        self.action_history: List[Dict[str, Any]] = []

    def add_action(self, action: Dict[str, Any]):
        """Track an action"""
        self.action_history.append(action)
        # Keep only recent actions
        if len(self.action_history) > self.window_size * 2:
            self.action_history = self.action_history[-self.window_size * 2:]

    def is_stuck(self) -> tuple[bool, Optional[str]]:
        """
        Check if agent is stuck in a loop.

        Returns:
            (is_stuck, reason)
        """
        if len(self.action_history) < self.repeat_threshold:
            return False, None

        recent = self.action_history[-self.window_size:]

        # Check for repeated identical actions
        if len(recent) >= self.repeat_threshold:
            last_action = recent[-1]
            action_type = last_action.get('action')
            selector = last_action.get('selector')

            # Count how many times this exact action appears
            repeat_count = sum(
                1 for a in recent
                if a.get('action') == action_type and a.get('selector') == selector
            )

            if repeat_count >= self.repeat_threshold:
                return True, f"Repeated {action_type} on '{selector}' {repeat_count} times"

        # Check for error loops
        error_count = sum(1 for a in recent if a.get('error'))
        if error_count >= self.repeat_threshold:
            return True, f"Hit {error_count} errors in last {self.window_size} steps"

        # Check for scroll loops (scrolling but not progressing)
        scroll_count = sum(1 for a in recent if a.get('action') == 'scroll')
        if scroll_count >= 4:
            return True, f"Scrolling {scroll_count} times without progress"

        return False, None

    def reset(self):
        """Clear action history"""
        self.action_history = []
