"""Shared plotting helpers for analytical notebooks.

This module establishes a cohesive visual language and export configuration
for all figures generated across the project's exploratory, operational, and
forecasting analyses.
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Color Palette & Styling Constants
# ---------------------------------------------------------------------------

# Curated categorical color palette designed for high contrast and presentation readability:
#   - #1f4e79: Deep Navy (primary baseline/actuals)
#   - #2a9d8f: Teal Green (secondary comparisons/positive effects)
#   - #e9c46a: Warm Saffron (promotions/highlights)
#   - #f4a261: Sandy Coral (holidays/events)
#   - #e76f51: Burnt Sienna (outliers/volatility/error)
PROJECT_COLORS = ["#1f4e79", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51"]


def set_project_style() -> None:
    """Apply a readable, restrained presentation style to matplotlib.

    Configures global matplotlib rcParams with:
        - Consistent 11x6 inch default aspect ratio
        - Readable font sizing for axes labels and titles
        - Subtle, low-opacity grid lines (alpha=0.2) to guide the eye without clutter
        - Minimalist Tufte-style framing by removing top and right chart spines
    """
    plt.rcParams.update(
        {
            "figure.figsize": (11, 6),
            "axes.titlesize": 14,
            "axes.labelsize": 11,
            "axes.grid": True,
            "grid.alpha": 0.2,
            # Despine top and right borders to reduce chart junk
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def save_figure(figure: plt.Figure, output_dir: Path, filename: str) -> Path:
    """Save a presentation-ready PNG and return its absolute path.

    Ensures the target output folder exists, applies high-resolution rasterization (180 DPI),
    trims redundant outer whitespace with `bbox_inches='tight'`, and enforces an opaque white
    background suitable for both slides and printed reports.

    Args:
        figure: Matplotlib Figure instance to export.
        output_dir: Path to directory where image should be saved.
        filename: Destination image filename (e.g. 'eda_sales_trend.png').

    Returns:
        Path: Full path to the saved image file.
    """
    # Ensure target directory structure exists prior to writing
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / filename

    # Save with high-DPI and tight bounding box to prevent label clipping
    figure.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    return path


# ---------------------------------------------------------------------------
# Specialized EDA Visualizations
# ---------------------------------------------------------------------------

def plot_demand_classification(
    classification_df: pd.DataFrame,
    output_dir: Path | None = None,
    filename: str = "eda_09_demand_classification.png",
) -> plt.Figure:
    """Plot the Syntetos-Boylan demand classification grid (ADI vs CV^2).

    Renders a 4-quadrant scatter plot (Smooth, Intermittent, Erratic, Lumpy)
    with threshold reference lines at ADI=1.32 and CV^2=0.49.

    Args:
        classification_df: DataFrame from `classify_demand_patterns`.
        output_dir: Optional directory to save the figure.
        filename: Output image filename if saving.

    Returns:
        plt.Figure: The rendered matplotlib figure.
    """
    fig, ax = plt.subplots(figsize=(12, 7))

    category_colors = {
        "Smooth": PROJECT_COLORS[1],        # Teal
        "Intermittent": PROJECT_COLORS[0],  # Navy
        "Erratic": PROJECT_COLORS[3],       # Coral
        "Lumpy": PROJECT_COLORS[4],         # Burnt sienna
    }

    for cat, color in category_colors.items():
        subset = classification_df[classification_df["demand_category"] == cat]
        if not subset.empty:
            ax.scatter(
                subset["adi"],
                subset["cv2"],
                c=color,
                label=f"{cat} (n={len(subset)})",
                s=70,
                alpha=0.85,
                edgecolors="white",
                linewidth=0.8,
            )

    # Reference threshold lines
    ax.axvline(1.32, color="gray", linestyle="--", linewidth=1.2, alpha=0.7)
    ax.axhline(0.49, color="gray", linestyle="--", linewidth=1.2, alpha=0.7)

    # Annotate quadrant labels in corners
    x_max = max(classification_df["adi"].max() * 1.05, 2.5)
    y_max = max(classification_df["cv2"].max() * 1.05, 1.5)

    ax.text(1.02, 0.05, "SMOOTH\n(Regular, Low Var)", fontsize=9, color="#2a9d8f", fontweight="bold")
    ax.text(1.35, 0.05, "INTERMITTENT\n(Sporadic, Low Var)", fontsize=9, color="#1f4e79", fontweight="bold")
    ax.text(1.02, y_max * 0.85, "ERRATIC\n(Regular, High Var)", fontsize=9, color="#f4a261", fontweight="bold")
    ax.text(1.35, y_max * 0.85, "LUMPY\n(Sporadic, High Var)", fontsize=9, color="#e76f51", fontweight="bold")

    # Annotate prominent product families if 'family' column is present
    if "family" in classification_df.columns:
        for _, row in classification_df.iterrows():
            if row["adi"] > 1.32 or row["cv2"] > 0.49 or row["zero_sales_pct"] > 20:
                ax.annotate(
                    row["family"],
                    (row["adi"], row["cv2"]),
                    xytext=(5, 4),
                    textcoords="offset points",
                    fontsize=8,
                    alpha=0.85,
                )

    ax.set_xlim(0.95, x_max)
    ax.set_ylim(-0.05, y_max)
    ax.set(
        title="Demand Pattern Classification (Syntetos-Boylan / Croston Framework)",
        xlabel="Average Demand Interval (ADI) — Spacing between non-zero days",
        ylabel="Squared Coefficient of Variation (CV²) of non-zero demand size",
    )
    ax.legend(loc="upper right", frameon=True)
    fig.tight_layout()

    if output_dir:
        save_figure(fig, output_dir, filename)

    return fig


def plot_payday_comparison(
    payday_family_df: pd.DataFrame,
    top_n: int = 15,
    output_dir: Path | None = None,
    filename: str = "eda_10_payday_quincena_effect.png",
) -> plt.Figure:
    """Plot the Quincena (payday) sales lift percentage across product categories.

    Args:
        payday_family_df: DataFrame with 'payday_lift_pct' from `analyze_payday_effects`.
        top_n: Number of categories to display.
        output_dir: Optional directory to save the figure.
        filename: Output image filename if saving.

    Returns:
        plt.Figure: The rendered matplotlib figure.
    """
    top = payday_family_df.head(top_n).sort_values("payday_lift_pct")

    fig, ax = plt.subplots(figsize=(11, 7))
    bars = ax.barh(top.index, top["payday_lift_pct"], color=PROJECT_COLORS[1], alpha=0.9)

    # Add numeric labels to each bar
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width + 0.5,
            bar.get_y() + bar.get_height() / 2,
            f"+{width:.1f}%" if width >= 0 else f"{width:.1f}%",
            va="center",
            ha="left",
            fontsize=9,
        )

    ax.axvline(0, color="black", linestyle="-", linewidth=0.8)
    ax.set(
        title=f"Semi-Monthly Payday Surge (Quincena) — Top {top_n} Families by Lift %",
        xlabel="Average Sales Lift on Paydays vs Regular Days (%)",
        ylabel="Product Family",
    )
    fig.tight_layout()

    if output_dir:
        save_figure(fig, output_dir, filename)

    return fig


def plot_earthquake_impact(
    earthquake_results: dict[str, pd.DataFrame],
    output_dir: Path | None = None,
    filename: str = "eda_11_earthquake_impact.png",
) -> plt.Figure:
    """Plot regional and category demand shifts during the April 2016 earthquake.

    Args:
        earthquake_results: Dict containing 'regional_impact' and 'family_shift'.
        output_dir: Optional directory to save the figure.
        filename: Output image filename if saving.

    Returns:
        plt.Figure: The rendered matplotlib figure.
    """
    regional = earthquake_results["regional_impact"].sort_values("total_change_pct")
    family = earthquake_results["family_shift"]
    # Top 8 surging categories and bottom 4 declining categories
    notable_families = pd.concat([family.head(8), family.tail(4)]).sort_values("sales_change_pct")

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # 1. Regional shift
    colors_reg = [PROJECT_COLORS[4] if v > 0 else PROJECT_COLORS[0] for v in regional["total_change_pct"]]
    axes[0].barh(regional.index, regional["total_change_pct"], color=colors_reg, alpha=0.9)
    axes[0].axvline(0, color="black", linestyle="--", linewidth=0.8)
    axes[0].set(
        title="Regional Sales Change (30-Day Post vs Pre Earthquake)",
        xlabel="Sales Change (%)",
        ylabel="Province / State",
    )

    # 2. Product family shift
    colors_fam = [PROJECT_COLORS[4] if v > 0 else PROJECT_COLORS[0] for v in notable_families["sales_change_pct"]]
    axes[1].barh(notable_families.index, notable_families["sales_change_pct"], color=colors_fam, alpha=0.9)
    axes[1].axvline(0, color="black", linestyle="--", linewidth=0.8)
    axes[1].set(
        title="Category Shift (Surging Essentials vs Discretionary)",
        xlabel="Sales Change (%)",
        ylabel="Product Family",
    )

    fig.tight_layout()

    if output_dir:
        save_figure(fig, output_dir, filename)

    return fig


def plot_correlation_heatmap(
    corr_matrix: pd.DataFrame,
    top_families: Sequence[str] | None = None,
    output_dir: Path | None = None,
    filename: str = "eda_12_family_correlation_heatmap.png",
) -> plt.Figure:
    """Plot a correlation heatmap showing demand co-movements across categories.

    Args:
        corr_matrix: Symmetrical correlation matrix from `compute_cross_family_correlations`.
        top_families: Optional subset of family names to plot. If None, uses top 12.
        output_dir: Optional directory to save the figure.
        filename: Output image filename if saving.

    Returns:
        plt.Figure: The rendered matplotlib figure.
    """
    if top_families is not None:
        sub_corr = corr_matrix.loc[top_families, top_families]
    else:
        sub_corr = corr_matrix.iloc[:12, :12]

    fig, ax = plt.subplots(figsize=(10, 8))
    cax = ax.imshow(sub_corr, cmap="YlGnBu", aspect="auto", vmin=0, vmax=1)
    fig.colorbar(cax, ax=ax, label="Pearson Correlation")

    labels = list(sub_corr.columns)
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
    ax.set_yticklabels(labels, fontsize=9)

    # Annotate values inside cells
    for i in range(len(labels)):
        for j in range(len(labels)):
            val = sub_corr.iloc[i, j]
            text_color = "white" if val > 0.65 else "black"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=text_color, fontsize=8)

    ax.set_title("Cross-Category Demand Co-Movement Correlation Heatmap", pad=15)
    fig.tight_layout()

    if output_dir:
        save_figure(fig, output_dir, filename)

    return fig
