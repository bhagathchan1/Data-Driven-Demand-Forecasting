"""Interactive presentation site for the grocery demand forecasting project."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parent
FIGURES = ROOT / "reports" / "figures"
TABLES = ROOT / "reports" / "tables"
REPORT = ROOT / "reports" / "Data_Driven_Demand_Forecasting_Final_Report.docx"
PRESENTATION = ROOT / "presentation" / "data-driven-demand-forecasting-research-readout.pptx"


st.set_page_config(
    page_title="Demand Intelligence | Grocery Retail Operations",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    :root {
        --ink: #0b1f33;
        --navy: #17324d;
        --teal: #0e7c7b;
        --orange: #f28c28;
        --paper: #f5f7f4;
        --muted: #627181;
        --line: #dce5e8;
    }
    .stApp { background: linear-gradient(180deg, #f8faf8 0%, #f3f6f5 100%); }
    .block-container { max-width: 1280px; padding-top: 1.4rem; padding-bottom: 3rem; }
    [data-testid="stSidebar"] { background: #0b1f33; }
    [data-testid="stSidebar"] * { color: #f7faf9; }
    [data-testid="stSidebar"] .stRadio label {
        padding: .35rem .45rem; border-radius: .45rem;
    }
    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.16); }
    h1, h2, h3 { color: var(--ink); letter-spacing: -.02em; }
    h1 { font-size: clamp(2.35rem, 5vw, 4.5rem) !important; line-height: .98 !important; }
    h2 { margin-top: .7rem !important; }
    p, li { color: #223343; }
    .hero {
        background: linear-gradient(125deg, #0b1f33 0%, #163f51 70%, #0e7c7b 100%);
        border-radius: 1.2rem; padding: 3.4rem 3.2rem; color: white;
        box-shadow: 0 18px 45px rgba(11,31,51,.16); margin-bottom: 1.25rem;
    }
    .hero h1 { color: white; margin: 0 0 .9rem 0; max-width: 980px; }
    .hero p { color: #dceceb; font-size: 1.12rem; max-width: 850px; margin: 0; }
    .eyebrow { color: #65d0c8; text-transform: uppercase; letter-spacing: .16em; font-weight: 700; font-size: .78rem; }
    .metric-card {
        background: white; border: 1px solid var(--line); border-radius: .9rem;
        padding: 1rem 1.05rem; min-height: 118px; box-shadow: 0 8px 24px rgba(20,49,72,.06);
    }
    .metric-value { color: var(--teal); font-size: 2.05rem; line-height: 1; font-weight: 800; }
    .metric-value.orange { color: var(--orange); }
    .metric-label { color: var(--ink); font-weight: 700; margin-top: .6rem; font-size: .9rem; }
    .metric-note { color: var(--muted); font-size: .76rem; margin-top: .22rem; }
    .insight {
        border-left: 5px solid var(--teal); background: #e9f3f2; border-radius: 0 .8rem .8rem 0;
        padding: 1rem 1.2rem; margin: .7rem 0 1.1rem;
    }
    .insight.orange { border-left-color: var(--orange); background: #fff2e5; }
    .section-card {
        background: white; border: 1px solid var(--line); border-radius: 1rem;
        padding: 1.15rem 1.25rem; height: 100%; box-shadow: 0 7px 22px rgba(20,49,72,.05);
    }
    .section-card h3 { margin-top: 0; }
    .pill {
        display: inline-block; background: #e6f1f0; color: #086d6d; border-radius: 999px;
        padding: .25rem .62rem; margin: .15rem .15rem .15rem 0; font-size: .78rem; font-weight: 700;
    }
    .step {
        color: white; background: var(--navy); padding: .9rem 1rem; border-radius: .65rem;
        text-align: center; font-weight: 700; min-height: 62px;
    }
    .caption { color: var(--muted); font-size: .82rem; text-align: center; margin-top: -.35rem; }
    .caveat { color: var(--muted); font-size: .86rem; border-top: 1px solid var(--line); padding-top: .65rem; }
    .footer { color: var(--muted); font-size: .78rem; text-align: center; margin-top: 2.5rem; }
    div[data-testid="stMetric"] {
        background: white; border: 1px solid var(--line); padding: .75rem 1rem; border-radius: .8rem;
    }
    div[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: .7rem; overflow: hidden; }
    .stDownloadButton button, .stButton button {
        background: var(--teal); color: white; border: none; border-radius: .6rem; font-weight: 700;
    }
    .stDownloadButton button:hover, .stButton button:hover { background: #086666; color: white; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def read_csv(filename: str) -> pd.DataFrame:
    path = TABLES / filename
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


@st.cache_data(show_spinner=False)
def read_bytes(path: str) -> bytes:
    return Path(path).read_bytes()


def image(filename: str, caption: str | None = None):
    path = FIGURES / filename
    if path.exists():
        st.image(str(path), width="stretch")
        if caption:
            st.markdown(f'<div class="caption">{caption}</div>', unsafe_allow_html=True)
    else:
        st.warning(f"Figure unavailable: {filename}")


def metric_card(value: str, label: str, note: str, orange: bool = False):
    color_class = " orange" if orange else ""
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-value{color_class}">{value}</div>
          <div class="metric-label">{label}</div>
          <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_intro(kicker: str, title: str, description: str):
    st.markdown(f'<div class="eyebrow">{kicker}</div>', unsafe_allow_html=True)
    st.header(title)
    st.markdown(description)


def format_table(df: pd.DataFrame, decimals: int = 2):
    if df.empty:
        st.info("The supporting evidence table is not available in this checkout.")
        return
    numeric = df.select_dtypes(include="number").columns
    formats = {col: f"{{:,.{decimals}f}}" for col in numeric}
    st.dataframe(df.style.format(formats), width="stretch", hide_index=True)


with st.sidebar:
    st.markdown("## Demand Intelligence")
    st.caption("Grocery retail operations presentation")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        [
            "Executive overview",
            "Data and method",
            "Demand patterns",
            "Operations analysis",
            "Forecasting",
            "Recommendations",
            "Evidence and downloads",
        ],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption("Use the sidebar as your presentation agenda. Each page is designed as one chapter of the project story.")


if page == "Executive overview":
    st.markdown(
        """
        <div class="hero">
          <div class="eyebrow">MBA Operations Management Project</div>
          <h1>Retail demand differs where planning matters most</h1>
          <p>Historical sales, operating context, and transparent forecasts show why one network-wide rule cannot serve every family, store, and peak period.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cols = st.columns(4)
    with cols[0]: metric_card("72.7%", "Sales concentration", "Four leading product families")
    with cols[1]: metric_card("825.2k", "Sunday demand", "Average daily mixed units", True)
    with cols[2]: metric_card("+19.1%", "Holiday association", "Holiday vs normal store-days")
    with cols[3]: metric_card("414.4", "Best average MAE", "Rolling one-day Random Forest", True)

    st.markdown("### The management verdict")
    st.markdown(
        """
        <div class="insight">
        <b>Different demand profiles require different operating routines.</b> Stable high-volume categories can anchor regular supplier and review cycles. High-volume volatile categories, recurring peaks, promotion periods, and variable stores require shorter reviews and more flexibility.
        </div>
        """,
        unsafe_allow_html=True,
    )
    left, right = st.columns([1.2, 1])
    with left:
        image("eda_04_family_importance_variability.png", "Volume and variability create different planning problems")
    with right:
        st.markdown("### What the analysis establishes")
        st.markdown(
            """
            - Demand is concentrated but not equally predictable.
            - Weekends and December create recurring network pressure.
            - Store lifecycle must be separated from mature-store volatility.
            - Promotion and holiday results are useful associations, not causal lift.
            - Forecast winners vary by series, so transparent baselines remain essential.
            """
        )
        st.markdown("### What it cannot establish")
        st.markdown(
            """
            - Optimal safety stock or reorder points
            - Financial benefit or margin impact
            - Unconstrained demand when stockouts may suppress sales
            - Causal effects from observational promotion or holiday comparisons
            """
        )

elif page == "Data and method":
    section_intro(
        "Foundation",
        "The analysis begins with a complete, validated sales panel",
        "Seven Kaggle source files were audited at their natural grains before any integration. The core panel contains one observation for each date, store, and product family.",
    )
    cols = st.columns(4)
    with cols[0]: metric_card("3,000,888", "Sales observations", "Unique date × store × family rows")
    with cols[1]: metric_card("1,684", "Observed dates", "1 Jan 2013 to 15 Aug 2017", True)
    with cols[2]: metric_card("54 × 33", "Network coverage", "Stores × product families")
    with cols[3]: metric_card("0", "Duplicate core keys", "Validated after integration", True)

    st.markdown("### Source files")
    source_profile = read_csv("phase1_dataset_profile.csv")
    if not source_profile.empty:
        format_table(source_profile)
    else:
        fallback = pd.DataFrame(
            {
                "Dataset": ["train.csv", "test.csv", "stores.csv", "transactions.csv", "holidays_events.csv", "oil.csv"],
                "Rows": [3_000_888, 28_512, 54, 83_488, 350, 1_218],
                "Role": ["Sales and promotions", "Forecast horizon", "Store attributes", "Traffic proxy", "Events", "Economic context"],
            }
        )
        format_table(fallback, 0)

    st.markdown("### Business-led workflow")
    steps = st.columns(7)
    labels = ["Question", "Audit", "Prepare", "Explore", "Diagnose", "Forecast", "Act"]
    for col, label in zip(steps, labels):
        with col:
            st.markdown(f'<div class="step">{label}</div>', unsafe_allow_html=True)

    st.markdown("### Quality decisions")
    q1, q2, q3 = st.columns(3)
    with q1:
        st.markdown('<div class="section-card"><h3>Zero sales</h3><p><b>939,130 rows</b> were retained. A zero may reflect genuine demand, closure, lifecycle, or unavailable stock.</p></div>', unsafe_allow_html=True)
    with q2:
        st.markdown('<div class="section-card"><h3>Transactions</h3><p><b>8.19% of store-dates</b> are missing. Missing values remain missing rather than becoming zero traffic.</p></div>', unsafe_allow_html=True)
    with q3:
        st.markdown('<div class="section-card"><h3>Holiday scope</h3><p>National, regional, and local events were matched only to relevant stores to prevent join multiplication.</p></div>', unsafe_allow_html=True)

    st.markdown("### Detailed analytical scope")
    st.markdown(
        """
        <span class="pill">16 Aug 2015 – 15 Aug 2017</span>
        <span class="pill">Stores 44, 45, 17, 32, 25</span>
        <span class="pill">Grocery I</span><span class="pill">Beverages</span>
        <span class="pill">Produce</span><span class="pill">Cleaning</span>
        <span class="pill">Frozen Foods</span><span class="pill">≥90% mature-store coverage</span>
        """,
        unsafe_allow_html=True,
    )

elif page == "Demand patterns":
    section_intro(
        "Evidence",
        "Demand patterns differ across time, stores, and families",
        "Choose a lens to move from the network trend to the operating detail behind it.",
    )
    topic = st.segmented_control(
        "Analytical lens",
        ["Trend", "Calendar", "Stores", "Families", "Promotions", "Advanced patterns"],
        default="Trend",
    )
    if topic == "Trend":
        image("eda_01_total_sales_trend.png", "Observed daily network sales and the 28-day moving average")
        st.markdown('<div class="insight"><b>Finding.</b> Average daily observed sales increased from about 385.8k mixed units in 2013 to 790.8k in 2016. This is network growth, not confirmed same-store growth.</div>', unsafe_allow_html=True)
    elif topic == "Calendar":
        image("eda_02_calendar_patterns.png", "December and weekends carry the highest average network demand")
        cols = st.columns(3)
        with cols[0]: metric_card("825.2k", "Sunday", "Highest weekday average")
        with cols[1]: metric_card("772.2k", "Saturday", "Second-highest weekday", True)
        with cols[2]: metric_card("808.6k", "December", "Highest monthly average")
        st.markdown('<div class="insight"><b>Operational meaning.</b> Review rosters, checkout capacity, delivery timing, receiving, and shelf replenishment before predictable peaks.</div>', unsafe_allow_html=True)
    elif topic == "Stores":
        image("eda_03_store_performance.png", "Store rankings require lifecycle and format context")
        st.markdown('<div class="insight"><b>Finding.</b> Store 44 leads observed sales at about 62.1 million mixed units. Store 25 has the highest mature-store daily-demand CV at 0.702.</div>', unsafe_allow_html=True)
        st.markdown('<div class="caveat">Seven stores do not meet the 90% mature-store coverage rule and remain separate from ordinary variability comparisons.</div>', unsafe_allow_html=True)
    elif topic == "Families":
        image("eda_04_family_importance_variability.png", "Importance and uncertainty require different responses")
        family = read_csv("family_summary.csv")
        if not family.empty:
            format_table(family.head(10))
    elif topic == "Promotions":
        left, right = st.columns([1.25, .75])
        with left:
            image("eda_06_promotion_association.png", "Observed promoted to non-promoted mean-sales ratios")
        with right:
            st.markdown("### Selected ratios")
            st.markdown("**Produce 3.08×**  \\ **Home Care 3.04×**  \\ **Beverages 2.49×**  \\ **Dairy 1.95×**  \\ **Grocery I 1.62×**")
            st.markdown('<div class="insight orange"><b>Required caveat.</b> These are associations, not causal promotion lift. Timing, targeting, seasonality, and store mix may influence the ratios.</div>', unsafe_allow_html=True)
    else:
        advanced = st.selectbox(
            "Advanced analysis",
            ["Demand intermittency", "Semi-month boundary", "April 2016 shock", "Cross-family co-movement"],
        )
        mapping = {
            "Demand intermittency": ("eda_09_demand_classification.png", "1,782 store-family series split into Smooth, Intermittent, Lumpy, and Erratic patterns."),
            "Semi-month boundary": ("eda_10_payday_quincena_effect.png", "The defined semi-month window averages 4.52% higher network sales before calendar controls."),
            "April 2016 shock": ("eda_11_earthquake_impact.png", "Regional pre/post changes diverge sharply, supporting locally flexible scenario planning."),
            "Cross-family co-movement": ("eda_12_family_correlation_heatmap.png", "Daily log-sales changes show relative category co-movement after removing the daily common component."),
        }
        filename, finding = mapping[advanced]
        image(filename, advanced)
        st.markdown(f'<div class="insight"><b>Finding.</b> {finding}</div>', unsafe_allow_html=True)
        st.markdown('<div class="caveat">Advanced diagnostics are screening and scenario-planning signals. They do not establish causal effects or inventory policy.</div>', unsafe_allow_html=True)

elif page == "Operations analysis":
    section_intro(
        "Operating model",
        "Demand level and variability define four planning postures",
        "The portfolio combines the scale of demand with its relative variation so management attention follows operational importance rather than volatility alone.",
    )
    left, right = st.columns([1.2, .8])
    with left:
        image("operations_01_family_segments.png", "Product-family demand and variability segmentation")
    with right:
        segments = pd.DataFrame(
            {
                "Segment": ["High demand / Stable", "High demand / Volatile", "Low demand / Stable", "Low demand / Volatile"],
                "Families": [13, 4, 3, 13],
                "Planning posture": ["Routine + exceptions", "Short reviews + flexibility", "Lower-frequency review", "Selective monitoring"],
            }
        )
        format_table(segments, 0)
        st.markdown('<div class="insight orange"><b>Management example.</b> Produce combines high demand with high variability, so it merits closer monitoring than a low-volume volatile family.</div>', unsafe_allow_html=True)

    st.markdown("### Store operating profiles")
    image("operations_02_store_profiles.png", "Comparable mature stores still differ in scale and variability")
    st.markdown("### Peak-demand planning checklist")
    c1, c2, c3, c4, c5 = st.columns(5)
    labels = ["Labor and checkout", "Receiving capacity", "Shelf replenishment", "Supplier windows", "Promotion execution"]
    for col, label in zip((c1, c2, c3, c4, c5), labels):
        with col:
            st.markdown(f'<div class="section-card"><h3>{label}</h3><p>Review before weekend, holiday, promotion, and December peaks.</p></div>', unsafe_allow_html=True)

elif page == "Forecasting":
    section_intro(
        "Decision support",
        "Forecasting adds value only when it beats simple baselines",
        "Three representative store-family series were evaluated on a chronological 60-day holdout with leakage-safe lag and rolling features.",
    )
    cols = st.columns(4)
    with cols[0]: metric_card("910.54", "Naive MAE", "Previous day")
    with cols[1]: metric_card("718.64", "Seasonal naive MAE", "Previous week", True)
    with cols[2]: metric_card("647.09", "Holt-Winters MAE", "Fixed 60-day path")
    with cols[3]: metric_card("414.41", "Random Forest MAE", "Rolling one-day", True)

    left, right = st.columns([1.15, .85])
    with left:
        image("forecast_01_validation_comparison.png", "Actual and forecast values across the validation period")
    with right:
        results = read_csv("forecast_model_average.csv")
        if not results.empty:
            format_table(results, 3)
        st.markdown('<div class="insight"><b>Result.</b> Random Forest average MAE is 42.3% lower than the weekly seasonal-naive baseline.</div>', unsafe_allow_html=True)

    st.markdown("### Series-level winners")
    winners = read_csv("forecast_best_by_series.csv")
    format_table(winners)
    st.markdown(
        '<div class="caveat"><b>Comparison caveat.</b> Random Forest uses rolling one-day realized history, while Holt-Winters produces a fixed path from the cutoff. These are useful operating alternatives, not identical information-update experiments.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("### Why no confusion matrix")
    st.write("Daily sales is continuous. MAE, RMSE, RMSLE, per-series comparisons, and validation plots preserve the size and timing of forecast errors; a confusion matrix would discard that information.")

elif page == "Recommendations":
    section_intro(
        "Managerial synthesis",
        "Evidence supports differentiated planning policies",
        "Each action below is tied to a validated finding and remains bounded by the data available.",
    )
    insights = read_csv("managerial_insights.csv")
    if not insights.empty:
        format_table(insights)
    else:
        st.info("Managerial evidence table unavailable.")

    st.markdown("### Controlled pilot sequence")
    p1, p2, p3, p4 = st.columns(4)
    stages = [
        ("1", "Establish baselines", "Record current cadence and seasonal-naive errors."),
        ("2", "Pilot review cadence", "Differentiate stable and volatile families."),
        ("3", "Monitor models", "Compare errors by store-family and horizon."),
        ("4", "Review outcomes", "Add service, waste, labor, and availability data."),
    ]
    for col, (n, title, body) in zip((p1, p2, p3, p4), stages):
        with col:
            st.markdown(f'<div class="section-card"><div class="eyebrow">Stage {n}</div><h3>{title}</h3><p>{body}</p></div>', unsafe_allow_html=True)

    st.markdown("### Additional data needed before inventory optimization")
    st.markdown(
        """
        <span class="pill">Stock on hand</span><span class="pill">Stockouts</span>
        <span class="pill">Orders and receipts</span><span class="pill">Supplier lead times</span>
        <span class="pill">Costs and margins</span><span class="pill">Service targets</span>
        <span class="pill">Labor and capacity</span><span class="pill">Promotion controls</span>
        """,
        unsafe_allow_html=True,
    )

else:
    section_intro(
        "Project handoff",
        "Every claim is backed by an inspectable artifact",
        "Explore the evidence register, download the final report and presentation, or inspect the generated figures and tables directly.",
    )
    d1, d2 = st.columns(2)
    with d1:
        st.markdown("### Final report")
        st.write("A 32-page exhaustive DOCX covering the full methodology, findings, recommendations, limitations, appendices, and viva questions.")
        if REPORT.exists():
            st.download_button(
                "Download DOCX report",
                data=read_bytes(str(REPORT)),
                file_name=REPORT.name,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                width="stretch",
            )
    with d2:
        st.markdown("### Presentation deck")
        st.write("An 18-slide editable PowerPoint with project charts, speaker notes, managerial implications, and limitations.")
        if PRESENTATION.exists():
            st.download_button(
                "Download PPTX deck",
                data=read_bytes(str(PRESENTATION)),
                file_name=PRESENTATION.name,
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                width="stretch",
            )

    st.markdown("### Evidence explorer")
    available_tables = sorted(p.name for p in TABLES.glob("*.csv"))
    selected_table = st.selectbox("Supporting table", available_tables)
    if selected_table:
        format_table(read_csv(selected_table), 3)

    st.markdown("### Figure gallery")
    gallery = {
        "Network demand trend": "eda_01_total_sales_trend.png",
        "Calendar patterns": "eda_02_calendar_patterns.png",
        "Store performance": "eda_03_store_performance.png",
        "Family importance": "eda_04_family_importance_variability.png",
        "Promotion association": "eda_06_promotion_association.png",
        "Demand classification": "eda_09_demand_classification.png",
        "Operations segmentation": "operations_01_family_segments.png",
        "Forecast validation": "forecast_01_validation_comparison.png",
    }
    selected_figure = st.selectbox("Presentation figure", list(gallery))
    image(gallery[selected_figure], selected_figure)

    st.markdown("### Reproducibility")
    st.markdown(
        """
        - Six executed notebooks cover data understanding through managerial synthesis.
        - Reusable logic is organized in `src/`.
        - Numerical claims are exported to `reports/tables/`.
        - Presentation-ready visuals are stored in `reports/figures/`.
        - Raw Kaggle data remains local and excluded from Git.
        """
    )


st.markdown(
    '<div class="footer">Data Driven Demand Analysis and Forecasting for Grocery Retail Operations · Academic project · Observational evidence is not causal</div>',
    unsafe_allow_html=True,
)
