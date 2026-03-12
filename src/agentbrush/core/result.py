"""Uniform result type returned by all agentbrush operations."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class Result:
    """Uniform return type for all agentbrush operations.

    Every operation (remove-bg, greenscreen, border-cleanup, etc.)
    returns a Result so callers get a consistent interface.
    """

    output_path: Optional[Path] = None
    width: int = 0
    height: int = 0
    transparent_pct: float = 0.0
    opaque_pct: float = 0.0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> str:
        """Human-readable summary for stdout."""
        status = "OK" if self.success else "FAILED"
        lines = [f"[{status}] {self.output_path or '(no output)'}"]
        if self.width and self.height:
            lines.append(f"  Size: {self.width}x{self.height}px")
        if self.transparent_pct or self.opaque_pct:
            lines.append(
                f"  Transparent: {self.transparent_pct:.1f}%  "
                f"Opaque: {self.opaque_pct:.1f}%"
            )
        for w in self.warnings:
            lines.append(f"  WARNING: {w}")
        for e in self.errors:
            lines.append(f"  ERROR: {e}")
        if self.metadata:
            for k, v in self.metadata.items():
                lines.append(f"  {k}: {v}")
        return "\n".join(lines)

    @staticmethod
    def from_image(img, output_path: Path) -> Result:
        """Build a Result with stats computed from a Pillow RGBA image."""
        data = list(img.get_flattened_data())
        total = len(data)
        transparent = sum(1 for p in data if p[3] == 0) if total else 0
        opaque = total - transparent
        return Result(
            output_path=output_path,
            width=img.width,
            height=img.height,
            transparent_pct=100.0 * transparent / total if total else 0.0,
            opaque_pct=100.0 * opaque / total if total else 0.0,
        )
