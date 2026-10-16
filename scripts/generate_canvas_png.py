"""Generate a publication-grade visual Data Science Project Canvas as a PNG."""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Resolve repository paths
ROOT = Path(__file__).resolve().parents[1]
FIGURE_DIR = ROOT / "reports" / "figures"
FIGURE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PNG = FIGURE_DIR / "data_science_canvas.png"
ROOT_PNG = ROOT / "data_science_canvas.png"


def create_canvas_png():
    # High-resolution canvas dimensions (16:9 widescreen layout, 22 x 12.5 inches)
    fig = plt.figure(figsize=(22, 12.5), dpi=200, facecolor="#0f172a")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # ---------------------------------------------------------------------------
    # Canvas Header
    # ---------------------------------------------------------------------------
    # Main header bar
    header_rect = patches.FancyBboxPatch(
        (1.5, 90.5), 97, 7.5,
        boxstyle="round,pad=0.2,rounding_size=0.8",
        facecolor="#1e293b", edgecolor="#334155", linewidth=1.5
    )
    ax.add_patch(header_rect)

    ax.text(3.5, 95.2, "DATA SCIENCE PROJECT CANVAS", fontsize=20, fontweight="bold", color="#38bdf8", va="center")
    ax.text(3.5, 92.5, "Demand Analysis & Forecasting for Grocery Retail Operations | MBA Operations Management",
            fontsize=12, color="#94a3b8", va="center")

    # Badge on right side of header
    badge = patches.FancyBboxPatch(
        (78.5, 92.2), 18.5, 4.2,
        boxstyle="round,pad=0.2,rounding_size=0.5",
        facecolor="#0284c7", edgecolor="none"
    )
    ax.add_patch(badge)
    ax.text(87.75, 94.3, "Kaggle Store Sales Panel (3M Rows)", fontsize=10.5, fontweight="bold",
            color="white", ha="center", va="center")

    # ---------------------------------------------------------------------------
    # Card Drawing Helper
    # ---------------------------------------------------------------------------
    def draw_card(x, y, w, h, title, category, accent_color, items):
        """Draws a modern UI card with header, badge, accent stripe, and bullet points."""
        # Main background card
        card = patches.FancyBboxPatch(
            (x, y), w, h,
            boxstyle="round,pad=0.2,rounding_size=0.6",
            facecolor="#1e293b", edgecolor="#334155", linewidth=1.2
        )
        ax.add_patch(card)

        # Top accent bar
        accent_bar = patches.FancyBboxPatch(
            (x + 0.1, y + h - 0.7), w - 0.2, 0.6,
            boxstyle="round,pad=0.0,rounding_size=0.2",
            facecolor=accent_color, edgecolor="none"
        )
        ax.add_patch(accent_bar)

        # Category badge (tiny tag)
        ax.text(x + 1.2, y + h - 1.6, category.upper(), fontsize=7.5, fontweight="bold", color=accent_color)

        # Card Title
        ax.text(x + 1.2, y + h - 3.0, title, fontsize=11.5, fontweight="bold", color="#f8fafc")

        # Divider line
        ax.plot([x + 1.2, x + w - 1.2], [y + h - 3.8, y + h - 3.8], color="#334155", linewidth=0.8)

        # Content bullets
        line_y = y + h - 5.0
        for header, detail in items:
            # Bullet point bullet
            ax.plot(x + 1.6, line_y, marker="o", markersize=3.5, color=accent_color)
            # Header text
            ax.text(x + 2.3, line_y, header, fontsize=9.2, fontweight="bold", color="#e2e8f0", va="center")
            line_y -= 1.3
            # Detail body text
            ax.text(x + 2.3, line_y, detail, fontsize=8.2, color="#94a3b8", va="center")
            line_y -= 1.7

    # ---------------------------------------------------------------------------
    # Define 10 Canvas Blocks across a 4-Column Layout
    # ---------------------------------------------------------------------------
    # Grid coordinates:
    # Column X positions: Col 0 (1.5), Col 1 (26.2), Col 2 (50.9), Col 3 (75.6)
    # Width = 22.8
    # Row Y positions:
    # Row 1 (top): y = 57.5, h = 31.0
    # Row 2 (bottom): y = 2.0, h = 53.5 (split into smaller boxes)

    # ---------------- ROW 1: CORE BUSINESS & DATA ARCHITECTURE (4 cards) ----------------
    # 1. Problem & Value Proposition
    draw_card(
        x=1.5, y=60.0, w=22.8, h=28.5,
        title="1. Value Proposition & Problem",
        category="Strategic Objective",
        accent_color="#38bdf8",
        items=[
            ("Business Problem", "Erratic daily demand drives stockouts in velocity lines,"),
            ("Operational Waste", "perishable shrinkage in fresh foods & weekend checkout queues."),
            ("Value Proposition", "Evidence-based replenishment & synchronized labor scheduling,"),
            ("Portfolio Shift", "replacing static ordering with volume-volatility segmentation."),
            ("Core Question", "How can historical data inform store replenishment & staffing?"),
        ]
    )

    # 2. Stakeholders & Decisions
    draw_card(
        x=26.2, y=60.0, w=22.8, h=28.5,
        title="2. Stakeholders & Decisions",
        category="Organizational Impact",
        accent_color="#2dd4bf",
        items=[
            ("Store Operations", "Shift scheduling, checkout lanes, Fri-Sun capacity spikes."),
            ("Category Planners", "Replenishment cycle length (daily fresh vs weekly dry goods)."),
            ("Supply Chain / DC", "Distribution center dispatch schedules & truck allocations."),
            ("Labor Workflows", "Staff allocation for Quincena paydays (15th & month-end)."),
            ("Promotional Staging", "Identify categories with genuine volume lift vs cannibalism."),
        ]
    )

    # 3. Data Sources & Ingestion
    draw_card(
        x=50.9, y=60.0, w=22.8, h=28.5,
        title="3. Data Sources & Grain",
        category="Data Architecture",
        accent_color="#818cf8",
        items=[
            ("Core Fact Grain", "train.csv: 3,000,888 rows across 1,684 dates (2013-2017)."),
            ("Unit of Analysis", "Exactly 1 record per (date x store_nbr x product_family)."),
            ("Store Master", "stores.csv: 54 stores across 16 states, 5 types & 17 clusters."),
            ("Foot Traffic", "transactions.csv: 83,488 daily store transaction counts."),
            ("Macro & Events", "holidays_events.csv (350 rows) & daily WTI oil.csv prices."),
        ]
    )

    # 4. Preparation & Quality Controls
    draw_card(
        x=75.6, y=60.0, w=22.8, h=28.5,
        title="4. Data Cleaning & Integrity",
        category="Data Quality",
        accent_color="#f472b6",
        items=[
            ("Oil Imputation", "Continuous daily calendar; ffill/bfill with missing audit flag."),
            ("Holiday Hierarchy", "Scope matching (National vs Regional/State vs Local/City)."),
            ("Join Assertions", "validate='many_to_one'; row count strictly preserved at 3.0M."),
            ("Zero Sales Review", "31.3% zero demand modeled as intermittency, not missing data."),
            ("Leakage Prevention", "Chronological sorting; lag & rolling metrics strictly shifted."),
        ]
    )

    # ---------------- ROW 2: MODELING, METRICS & DEPLOYMENT (6 cards) ----------------
    # 5. Feature Engineering
    draw_card(
        x=1.5, y=31.0, w=22.8, h=27.0,
        title="5. Feature Engineering",
        category="Predictive Signals",
        accent_color="#fbbf24",
        items=[
            ("Calendar Features", "Day of week, month, ISO week, quarter, weekend indicator."),
            ("Temporal Lags", "Lags 1, 7, 14, 28 (yesterday, weekly, bi-weekly, monthly)."),
            ("Rolling Windows", "Trailing 7-day & 28-day means (shifted by 1 to avoid leakage)."),
            ("Quincena Paydays", "15th and month-end wage payment cycle indicators."),
            ("Promotions", "Log-transformed active items: log(1 + onpromotion)."),
        ]
    )

    # 6. Modeling & Baselines
    draw_card(
        x=26.2, y=31.0, w=22.8, h=27.0,
        title="6. Modeling Strategy",
        category="Machine Learning",
        accent_color="#a78bfa",
        items=[
            ("Trend Baseline", "28-day Moving Average (trailing baseline demand)."),
            ("Seasonal Baseline", "7-day Seasonal Naive (repeats last week's pattern)."),
            ("Linear Regression", "Ridge/OLS with lags for interpretable operational weights."),
            ("Random Forest", "Non-linear trees capturing promo x calendar interactions."),
            ("Validation Scheme", "Chronological 16-day rolling backtest (no random shuffling)."),
        ]
    )

    # 7. Evaluation & Loss Metrics
    draw_card(
        x=50.9, y=31.0, w=22.8, h=27.0,
        title="7. Metrics & Trade-offs",
        category="Model Evaluation",
        accent_color="#34d399",
        items=[
            ("MAE (Primary)", "Mean Absolute Error in raw units; directly informs buffer size."),
            ("RMSE", "Root Mean Squared Error; heavily penalizes severe stockout misses."),
            ("RMSLE (Kaggle)", "Root Mean Squared Log Error; scales across category volumes."),
            ("Non-Negativity", "Predictions post-clipped at 0 (negative demand is unphysical)."),
            ("Cost Trade-offs", "Over-forecasting = Perishable waste vs Under-forecasting = Lost sales."),
        ]
    )

    # 8. Operational Segmentation
    draw_card(
        x=75.6, y=31.0, w=22.8, h=27.0,
        title="8. Decision Matrix & Policy",
        category="Operations Execution",
        accent_color="#60a5fa",
        items=[
            ("Smooth (Grocery/Bev)", "High volume, low CV: automated weekly batch replenishment."),
            ("Erratic (Produce/Meat)", "High volume, high CV: daily agile review & dynamic buffers."),
            ("Lumpy (Books/Hardware)", "Low volume, high CV: pull-based / Croston intermittency."),
            ("Weekend Staffing", "Sunday (825k) & Sat (772k) peak: +40% labor vs midweek."),
            ("Store Tiering", "Flagships (Stores 44, 45) get dedicated supply lanes."),
        ]
    )

    # ---------------- ROW 3: CONSTRAINTS & GOVERNANCE (2 wide cards) ----------------
    # 9. Constraints & Limitations
    draw_card(
        x=1.5, y=2.0, w=47.5, h=27.0,
        title="9. Methodological Constraints & Assumptions",
        category="Project Boundaries",
        accent_color="#f87171",
        items=[
            ("Observed Sales != Demand", "The dataset records censored historical sales. Stockout days appear as zero sales, not unmet demand."),
            ("No Inventory / Margin Data", "The dataset lacks stock-on-hand, lead times, ordering costs, and margins; inventory optimization cannot be claimed."),
            ("Descriptive != Causal Lift", "Promotions, oil prices, and transactions are observed associations; selection bias prevents claiming causal lift."),
            ("Mixed Physical Units", "Sales combines kilograms, liters, and item packs into a single number; aggregates represent activity index, not revenue."),
        ]
    )

    # 10. Monitoring, Drift & Governance
    draw_card(
        x=50.9, y=2.0, w=47.5, h=27.0,
        title="10. Continuous Monitoring, Drift & Governance",
        category="Production Governance",
        accent_color="#c084fc",
        items=[
            ("Macro & Shock Tracking", "Monitoring natural disasters (e.g. 2016 Manabí earthquake) which cause sharp regional divergence & essential surges."),
            ("Oil & Purchasing Power", "Tracking macroeconomic crude price fluctuations as context indicators for Ecuadorian purchasing power shifts."),
            ("Calendar / Floating Holidays", "Auditing floating national holidays (Carnival, Easter) and updating scope assignments annually."),
            ("Model Retraining Cadence", "Monthly model retraining with newly completed 28-day lags and dynamic recalibration of volatility coefficients."),
        ]
    )

    # Save outputs
    fig.savefig(OUTPUT_PNG, dpi=200, bbox_inches="tight", facecolor="#0f172a")
    fig.savefig(ROOT_PNG, dpi=200, bbox_inches="tight", facecolor="#0f172a")
    plt.close(fig)
    print(f"Canvas PNG generated successfully at:\n  - {OUTPUT_PNG}\n  - {ROOT_PNG}")


if __name__ == "__main__":
    create_canvas_png()
