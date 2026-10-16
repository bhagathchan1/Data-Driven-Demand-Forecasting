"""Shared plotting helpers for analytical notebooks."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt


PROJECT_COLORS = ["#1f4e79", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51"]


def set_project_style() -> None:
    """Apply a readable, restrained presentation style."""
    plt.rcParams.update(
        {
            "figure.figsize": (11, 6),
            "axes.titlesize": 14,
            "axes.labelsize": 11,
            "axes.grid": True,
            "grid.alpha": 0.2,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def save_figure(figure: plt.Figure, output_dir: Path, filename: str) -> Path:
    """Save a presentation-ready PNG and return its path."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename
    figure.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    return path
