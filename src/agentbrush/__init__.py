"""AgentBrush — Image editing toolkit for AI agents."""

__version__ = "0.1.0"

from agentbrush.core.result import Result
from agentbrush.background.ops import remove_background
from agentbrush.greenscreen.ops import remove_greenscreen
from agentbrush.border.ops import cleanup_border

__all__ = [
    "Result",
    "remove_background",
    "remove_greenscreen",
    "cleanup_border",
]
