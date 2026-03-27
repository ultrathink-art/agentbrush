"""AgentBrush — Image editing toolkit for AI agents."""

__version__ = "0.3.0"

from agentbrush.core.result import Result
from agentbrush.background.ops import remove_background
from agentbrush.greenscreen.ops import remove_greenscreen
from agentbrush.border.ops import cleanup_border
from agentbrush.text.ops import add_text, render_text
from agentbrush.composite.ops import composite, paste_centered
from agentbrush.resize.ops import resize_image
from agentbrush.validate.ops import validate_design, compare_images
from agentbrush.convert.ops import convert_image
from agentbrush.crop.ops import smart_crop
from agentbrush.palette.ops import extract_palette
from agentbrush.diff.ops import diff_images
from agentbrush.batch.ops import batch_process

# generate is optional (requires openai package)
try:
    from agentbrush.generate.ops import generate_image
    _has_generate = True
except ImportError:
    _has_generate = False

__all__ = [
    "Result",
    "remove_background",
    "remove_greenscreen",
    "cleanup_border",
    "add_text",
    "render_text",
    "composite",
    "paste_centered",
    "resize_image",
    "validate_design",
    "compare_images",
    "convert_image",
    "smart_crop",
    "extract_palette",
    "diff_images",
    "batch_process",
]

if _has_generate:
    __all__.append("generate_image")
