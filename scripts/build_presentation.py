"""Build the final editable PowerPoint deck for the demand forecasting project."""

from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "reports" / "figures"
OUT = ROOT / "presentation" / "data-driven-demand-forecasting-research-readout.pptx"

SW, SH = 13.333, 7.5
INK = "0B1F33"
GROUND = "F5F7F4"
PRIMARY = "0E7C7B"
MUTED = "6B7785"
ACCENT = "F28C28"
WHITE = "FFFFFF"
PALE_TEAL = "DDEDEC"
PALE_ORANGE = "FCE8D1"
PALE_BLUE = "E7EDF3"


def rgb(hex_value):
    return RGBColor.from_string(hex_value)


prs = Presentation()
prs.slide_width = Inches(SW)
prs.slide_height = Inches(SH)
blank = prs.slide_layouts[6]


def shape(slide, x, y, w, h, fill, line=None, radius=False):
    kind = MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE if radius else MSO_AUTO_SHAPE_TYPE.RECTANGLE
    shp = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = rgb(fill)
    shp.line.color.rgb = rgb(line or fill)
    if radius:
        try:
            shp.adjustments[0] = 0.12
        except Exception:
            pass
    return shp


def textbox(slide, text, x, y, w, h, size=20, color=INK, bold=False,
            align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP, margin=0.04,
            font="Arial", line_spacing=1.0):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(margin)
    tf.margin_top = tf.margin_bottom = Inches(margin)
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = line_spacing
    r = p.add_run()
    r.text = text
    r.font.name = font
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = rgb(color)
    return box


def rich_text(slide, runs, x, y, w, h, size=20, align=PP_ALIGN.LEFT,
              valign=MSO_ANCHOR.TOP, margin=0.04):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(margin)
    tf.margin_top = tf.margin_bottom = Inches(margin)
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = align
    for text, size_, color, bold in runs:
        r = p.add_run()
        r.text = text
        r.font.name = "Arial"
        r.font.size = Pt(size_ or size)
        r.font.bold = bold
        r.font.color.rgb = rgb(color)
    return box


def base_slide(title, number, section=None):
    slide = prs.slides.add_slide(blank)
    bg = slide.background.fill
    bg.solid()
    bg.fore_color.rgb = rgb(GROUND)
    shape(slide, 0, 0, SW, 0.12, PRIMARY)
    if section:
        textbox(slide, section.upper(), 0.65, 0.26, 2.8, 0.28, 11, PRIMARY, True)
    textbox(slide, title, 0.65, 0.55, 12.0, 0.78, 30, INK, True,
            valign=MSO_ANCHOR.MIDDLE)
    textbox(slide, str(number), 12.08, 7.03, 0.55, 0.22, 12, MUTED,
            align=PP_ALIGN.RIGHT)
    return slide


def source(slide, text):
    textbox(slide, text, 0.68, 7.03, 10.9, 0.24, 12, MUTED)


def notes(slide, text):
    tf = slide.notes_slide.notes_text_frame
    tf.text = text


def add_picture_contain(slide, filename, x, y, w, h, pad=0.0):
    path = FIG / filename
    with Image.open(path) as im:
        iw, ih = im.size
    target = w / h
    ratio = iw / ih
    if ratio >= target:
        pw = w - 2 * pad
        ph = pw / ratio
    else:
        ph = h - 2 * pad
        pw = ph * ratio
    px = x + (w - pw) / 2
    py = y + (h - ph) / 2
    return slide.shapes.add_picture(str(path), Inches(px), Inches(py), Inches(pw), Inches(ph))


def stat(slide, value, label, x, y, w, accent=PRIMARY):
    shape(slide, x, y, w, 1.36, WHITE, PALE_BLUE, True)
    textbox(slide, value, x + 0.18, y + 0.12, w - 0.36, 0.62, 30, accent, True)
    textbox(slide, label, x + 0.18, y + 0.77, w - 0.36, 0.40, 14, INK)


def bullet_list(slide, items, x, y, w, h, size=19, color=INK, bullet_color=ACCENT):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.02)
    tf.margin_top = tf.margin_bottom = Inches(0.02)
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(12)
        p.line_spacing = 1.05
        r1 = p.add_run()
        r1.text = "●  "
        r1.font.name = "Arial"
        r1.font.size = Pt(size - 2)
        r1.font.color.rgb = rgb(bullet_color)
        r2 = p.add_run()
        r2.text = item
        r2.font.name = "Arial"
        r2.font.size = Pt(size)
        r2.font.color.rgb = rgb(color)
    return box


def add_table(slide, rows, cols, data, x, y, w, h, widths=None, font_size=14):
    table = slide.shapes.add_table(rows, cols, Inches(x), Inches(y), Inches(w), Inches(h)).table
    if widths:
        for i, width in enumerate(widths):
            table.columns[i].width = Inches(width)
    for r in range(rows):
        for c in range(cols):
            cell = table.cell(r, c)
            cell.text = str(data[r][c])
            cell.margin_left = cell.margin_right = Inches(0.08)
            cell.margin_top = cell.margin_bottom = Inches(0.05)
            cell.fill.solid()
            cell.fill.fore_color.rgb = rgb(INK if r == 0 else (WHITE if r % 2 else PALE_BLUE))
            cell.border = None
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.LEFT if c == 0 else PP_ALIGN.CENTER
            p.vertical_anchor = MSO_ANCHOR.MIDDLE
            for run in p.runs:
                run.font.name = "Arial"
                run.font.size = Pt(font_size if r else font_size - 1)
                run.font.bold = r == 0
                run.font.color.rgb = rgb(WHITE if r == 0 else INK)
    return table


# Slide 1
slide = prs.slides.add_slide(blank)
bg = slide.background.fill
bg.solid(); bg.fore_color.rgb = rgb(INK)
shape(slide, 0, 0, 0.18, SH, PRIMARY)
shape(slide, 10.55, -0.2, 3.2, 7.9, PRIMARY)
for i, height in enumerate([0.8, 1.3, 2.1, 2.8, 3.8]):
    shape(slide, 10.9 + i * 0.48, 6.55 - height, 0.22, height, ACCENT if i == 4 else PALE_TEAL)
textbox(slide, "Data reveals where retail planning must differ", 0.72, 0.95, 8.9, 1.55,
        36, WHITE, True, valign=MSO_ANCHOR.MIDDLE)
textbox(slide, "Demand analysis and forecasting for grocery operations", 0.75, 2.72, 8.3, 0.52,
        21, PALE_TEAL)
shape(slide, 0.75, 3.48, 1.15, 0.07, ACCENT)
textbox(slide, "MBA Year 1 · Operations Management", 0.75, 3.76, 6.7, 0.42, 17, WHITE, True)
textbox(slide, "Student: [Name]  ·  Institution: [Institution]  ·  [Presentation Date]",
        0.75, 6.55, 8.8, 0.34, 14, PALE_TEAL)
notes(slide, "This project examines how retail sales history and operational context can support demand planning. The emphasis is on business interpretation and operating decisions, with forecasting used as one supporting stage rather than as a model leaderboard.")

# Slide 2
slide = base_slide("Concentration and peaks demand differentiated planning", 2, "Executive verdict")
stat(slide, "72.7%", "sales from four families", 0.68, 1.62, 2.62, PRIMARY)
stat(slide, "825.2k", "Sunday mixed units", 3.48, 1.62, 2.62, ACCENT)
stat(slide, "+19.1%", "holiday store-day sales", 6.28, 1.62, 2.62, PRIMARY)
stat(slide, "414.4", "best average forecast MAE", 9.08, 1.62, 3.02, ACCENT)
shape(slide, 0.68, 3.35, 11.42, 2.55, WHITE, PALE_BLUE, True)
textbox(slide, "One rule cannot fit every store, family, and operating period.", 1.02, 3.78, 10.75, 0.72,
        28, INK, True, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)
textbox(slide, "Stable high-volume flows need routines; volatile and peak periods need flexibility.",
        1.45, 4.72, 9.9, 0.55, 19, MUTED, align=PP_ALIGN.CENTER)
source(slide, "Source: project analysis of Kaggle Store Sales data")
notes(slide, "The analysis supports differentiated planning. Stable high-volume categories can use regular routines. Volatile important categories, weekend peaks, holidays, promotion periods, and high-variability stores need shorter review cycles and more operating flexibility.")

# Slide 3
slide = base_slide("Historical evidence can sharpen retail planning choices", 3, "Business question")
shape(slide, 0.68, 1.5, 12.0, 1.25, PRIMARY, PRIMARY, True)
textbox(slide, "How can sales history and operational factors support better planning?", 1.05, 1.76, 11.25, 0.62,
        26, WHITE, True, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)
for i, (n, text_) in enumerate([
    ("01", "Map demand patterns"), ("02", "Compare stores and families"),
    ("03", "Assess operating factors"), ("04", "Test forecast support"),
    ("05", "Translate evidence into action")]):
    x = 0.78 + i * 2.42
    shape(slide, x, 3.28, 2.12, 1.75, WHITE, PALE_BLUE, True)
    textbox(slide, n, x + 0.16, 3.48, 0.58, 0.40, 15, ACCENT, True)
    textbox(slide, text_, x + 0.16, 3.98, 1.80, 0.66, 17, INK, True)
textbox(slide, "Boundary: the dataset supports planning insight—not inventory optimization.",
        1.0, 5.75, 11.2, 0.42, 18, MUTED, align=PP_ALIGN.CENTER)
notes(slide, "The business question stays broad enough to follow the evidence. The project examines demand patterns, operating associations, store and family differences, and forecast usefulness. It does not claim direct inventory optimization because stock, lead-time, service, and cost data are unavailable.")

# Slide 4
slide = base_slide("A complete panel anchors the analysis at daily family level", 4, "Data foundation")
stat(slide, "3,000,888", "unique sales rows", 0.68, 1.5, 2.85)
stat(slide, "1,684", "observed dates", 3.72, 1.5, 2.85, ACCENT)
stat(slide, "54 × 33", "stores × families", 6.76, 1.5, 2.85)
shape(slide, 9.80, 1.5, 2.48, 1.36, INK, INK, True)
textbox(slide, "date × store × family", 10.02, 1.83, 2.04, 0.62, 19, WHITE, True, align=PP_ALIGN.CENTER)
data = [
    ["Source", "Rows", "Role"], ["Sales", "3,000,888", "Demand + promotions"],
    ["Transactions", "83,488", "Traffic proxy"], ["Stores", "54", "Format + geography"],
    ["Holidays", "350", "Event scope"], ["Oil", "1,218", "Economic context"],
]
add_table(slide, 6, 3, data, 0.68, 3.25, 11.6, 2.88, widths=[3.0, 2.1, 6.5], font_size=15)
source(slide, "Coverage: 1 Jan 2013–15 Aug 2017 · Kaggle Store Sales")
notes(slide, "The source files operate at different grains. Stores are static; transactions are daily by store; oil is daily; and holidays can overlap by geographic scope. Join validation is essential because an incorrect merge could duplicate sales or apply local events to every store.")

# Slide 5
slide = base_slide("The workflow keeps business decisions ahead of model complexity", 5, "Method")
steps = ["Question", "Audit", "Prepare", "Explore", "Diagnose", "Forecast", "Act"]
for i, label in enumerate(steps):
    x = 0.68 + i * 1.72
    fill = PRIMARY if i in [0, 6] else WHITE
    text_color = WHITE if i in [0, 6] else INK
    shape(slide, x, 2.25, 1.42, 1.12, fill, PRIMARY, True)
    textbox(slide, label, x + 0.08, 2.55, 1.26, 0.38, 16, text_color, True, align=PP_ALIGN.CENTER)
    if i < len(steps) - 1:
        textbox(slide, "→", x + 1.43, 2.55, 0.30, 0.38, 19, ACCENT, True, align=PP_ALIGN.CENTER)
shape(slide, 1.15, 4.18, 10.98, 1.25, PALE_TEAL, PALE_TEAL, True)
textbox(slide, "Full panel for network patterns · transparent subset for detail · chronological forecast validation",
        1.42, 4.56, 10.42, 0.42, 18, INK, True, align=PP_ALIGN.CENTER)
notes(slide, "The workflow starts with a business question and ends with operating choices. Data-quality checks protect the analysis. Forecasts are evaluated only after patterns and operational differences are understood, and only by whether they add useful information beyond transparent baselines.")

# Slide 6
slide = base_slide("Preparation preserves signals instead of deleting inconvenient variation", 6, "Data quality")
stat(slide, "31.30%", "rows with zero sales—retained", 0.68, 1.58, 3.50)
stat(slide, "8.19%", "store-dates missing transactions", 4.38, 1.58, 3.50, ACCENT)
stat(slide, "43", "missing oil observations—flagged", 8.08, 1.58, 3.50)
bullet_list(slide, [
    "No duplicate sales keys or negative sales",
    "Holiday scope matched to relevant stores",
    "Every join preserved all 3,000,888 rows",
    "Retail spikes remained visible for investigation",
], 1.15, 3.52, 10.9, 2.15, 19)
source(slide, "Quality principle: preserve uncertainty and validate every merge")
notes(slide, "Blind deletion would remove operationally meaningful variation. Zeros can reflect genuine low demand, closures, or store lifecycle. Missing transactions remain missing rather than becoming zero traffic. Oil values are filled over a daily index and flagged, while holiday scope is matched before joining.")

# Slide 7
slide = base_slide("A transparent subset makes detailed comparisons credible", 7, "Analytical scope")
shape(slide, 0.68, 1.52, 12.0, 0.72, INK, INK, True)
textbox(slide, "16 Aug 2015", 0.95, 1.72, 2.0, 0.28, 15, WHITE, True)
textbox(slide, "Two-year analytical window", 4.88, 1.72, 3.6, 0.28, 16, PALE_TEAL, True, align=PP_ALIGN.CENTER)
textbox(slide, "15 Aug 2017", 10.37, 1.72, 1.95, 0.28, 15, WHITE, True, align=PP_ALIGN.RIGHT)
stat(slide, "5 stores", "44 · 45 · 17 · 32 · 25", 0.92, 2.78, 3.45, PRIMARY)
stat(slide, "5 families", "Grocery I · Beverages · Produce · Cleaning · Frozen", 4.72, 2.78, 4.20, ACCENT)
stat(slide, "≥90%", "transaction + active-sales coverage", 9.27, 2.78, 3.05, PRIMARY)
textbox(slide, "Selection spans high, median, low, and volatile mature stores.", 1.05, 5.06, 11.15, 0.5,
        21, INK, True, align=PP_ALIGN.CENTER)
textbox(slide, "Lifecycle rules prevent pre-opening zeros from masquerading as volatility.", 1.2, 5.67, 10.85, 0.42,
        17, MUTED, align=PP_ALIGN.CENTER)
notes(slide, "The full dataset still supports network findings. The subset makes detailed comparisons manageable without choosing cases arbitrarily. Lifecycle eligibility prevents late-opening stores from appearing artificially volatile because of pre-opening zero rows.")

# Slide 8
slide = base_slide("Average daily network sales doubled before 2017", 8, "Demand patterns")
shape(slide, 0.68, 1.38, 12.0, 5.32, WHITE, PALE_BLUE, True)
add_picture_contain(slide, "eda_01_total_sales_trend.png", 0.86, 1.55, 11.64, 4.60)
shape(slide, 8.82, 5.76, 3.34, 0.62, INK, INK, True)
textbox(slide, "385.8k → 790.8k", 9.02, 5.91, 2.95, 0.30, 17, WHITE, True, align=PP_ALIGN.CENTER)
source(slide, "Observed network sales; 2017 is partial through 15 August")
notes(slide, "Average daily observed network sales rose from about 385.8 thousand mixed units in 2013 to 790.8 thousand in 2016. This is not confirmed same-store growth; store openings, assortment changes, promotions, and other factors may contribute.")

# Slide 9
slide = base_slide("Weekends and December create recurring operating pressure", 9, "Calendar effects")
shape(slide, 0.68, 1.38, 12.0, 5.32, WHITE, PALE_BLUE, True)
add_picture_contain(slide, "eda_02_calendar_patterns.png", 0.82, 1.62, 11.72, 4.45)
shape(slide, 0.94, 5.78, 3.05, 0.58, PRIMARY, PRIMARY, True)
textbox(slide, "Sunday 825.2k", 1.12, 5.92, 2.70, 0.28, 16, WHITE, True, align=PP_ALIGN.CENTER)
shape(slide, 4.18, 5.78, 3.05, 0.58, ACCENT, ACCENT, True)
textbox(slide, "December 808.6k", 4.36, 5.92, 2.70, 0.28, 16, WHITE, True, align=PP_ALIGN.CENTER)
textbox(slide, "Review staffing, checkout, receiving, and shelf replenishment before peaks.",
        7.52, 5.83, 4.65, 0.48, 15, INK, True, align=PP_ALIGN.CENTER)
source(slide, "Values are network averages in mixed units")
notes(slide, "Sunday and Saturday have the highest weekday averages, while December has the highest monthly average. These network patterns support advance peak reviews, but store and family histories should refine the final operating plan rather than applying one universal multiplier.")

# Slide 10
slide = base_slide("Store scale and mature-store variability require local rules", 10, "Store differences")
shape(slide, 0.68, 1.38, 8.55, 5.34, WHITE, PALE_BLUE, True)
add_picture_contain(slide, "eda_03_store_performance.png", 0.82, 1.64, 8.27, 4.62)
stat(slide, "62.1M", "Store 44 mixed units", 9.50, 1.62, 2.75, PRIMARY)
stat(slide, "0.702", "Store 25 mature CV", 9.50, 3.22, 2.75, ACCENT)
textbox(slide, "7 stores stay outside mature-store variability comparisons.",
        9.55, 5.05, 2.65, 0.90, 16, INK, True, align=PP_ALIGN.CENTER)
source(slide, "Lifecycle context prevents false underperformance or volatility labels")
notes(slide, "Store 44 has the highest observed sales. Among mature stores with adequate transaction and active-sales coverage, Store 25 has the highest daily-demand coefficient of variation. Newer or incompletely covered stores remain separate from mature-store comparisons.")

# Slide 11
slide = base_slide("Four families contribute nearly three quarters of sales", 11, "Family portfolio")
shape(slide, 0.68, 1.38, 8.55, 5.34, WHITE, PALE_BLUE, True)
add_picture_contain(slide, "eda_04_family_importance_variability.png", 0.82, 1.60, 8.27, 4.75)
shape(slide, 9.50, 1.55, 2.75, 4.62, WHITE, PALE_BLUE, True)
textbox(slide, "31.99%", 9.76, 1.90, 2.22, 0.54, 28, PRIMARY, True, align=PP_ALIGN.CENTER)
textbox(slide, "Grocery I", 9.76, 2.45, 2.22, 0.30, 15, INK, True, align=PP_ALIGN.CENTER)
shape(slide, 9.86, 3.06, 2.02, 0.04, PALE_BLUE)
textbox(slide, "Produce", 9.76, 3.40, 2.22, 0.30, 17, INK, True, align=PP_ALIGN.CENTER)
textbox(slide, "high-volume + volatile", 9.72, 3.82, 2.30, 0.62, 15, ACCENT, True, align=PP_ALIGN.CENTER)
textbox(slide, "Monitor closer; plan flexibly.", 9.74, 4.78, 2.28, 0.58, 15, MUTED, align=PP_ALIGN.CENTER)
source(slide, "Sales shares and daily-demand CV use the full historical panel")
notes(slide, "Grocery I, Beverages, Produce, and Cleaning contribute 72.7 percent of observed family-level sales. Grocery I and Cleaning combine scale with relative stability. Produce combines commercial importance with much greater variability and therefore merits closer monitoring.")

# Slide 12
slide = base_slide("Promotion and holiday associations vary across operating contexts", 12, "Demand drivers")
shape(slide, 0.68, 1.38, 8.10, 5.34, WHITE, PALE_BLUE, True)
add_picture_contain(slide, "eda_06_promotion_association.png", 0.82, 1.58, 7.82, 4.76)
stat(slide, "3.08×", "Produce promotion ratio", 9.06, 1.58, 3.00, PRIMARY)
stat(slide, "+19.1%", "holiday store-day sales", 9.06, 3.20, 3.00, ACCENT)
textbox(slide, "Coordinate campaigns and events with supply, shelf space, receiving, and labor.",
        9.13, 4.94, 2.86, 1.02, 15, INK, True, align=PP_ALIGN.CENTER)
source(slide, "Associations, not causal lift; timing and targeting may confound comparisons")
notes(slide, "Promotion ratios indicate where operating pressure may be stronger, but they do not estimate incremental lift because promotions were not randomly assigned. Holiday store-days also differ by month, weekday, promotion mix, and location.")

# Slide 13
slide = base_slide("Transactions inform workload; oil remains exploratory context", 13, "Operational context")
shape(slide, 0.68, 1.42, 7.12, 5.15, WHITE, PALE_BLUE, True)
add_picture_contain(slide, "eda_07_transactions.png", 0.82, 1.64, 6.84, 4.52)
shape(slide, 8.10, 1.42, 4.58, 5.15, WHITE, PALE_BLUE, True)
add_picture_contain(slide, "eda_08_oil_context.png", 8.28, 1.66, 4.22, 2.55)
textbox(slide, "0.837", 8.48, 4.42, 1.55, 0.48, 28, PRIMARY, True, align=PP_ALIGN.CENTER)
textbox(slide, "sales–transaction correlation", 10.00, 4.48, 2.10, 0.40, 15, INK, True)
textbox(slide, "Oil correlation −0.788 may reflect shared trends and omitted factors.",
        8.52, 5.19, 3.76, 0.70, 15, ACCENT, True, align=PP_ALIGN.CENTER)
source(slide, "Correlation supports investigation—not causation")
notes(slide, "Transactions provide a useful traffic proxy for staffing and checkout planning. Sales divided by transactions is still a mixed-unit basket proxy, not revenue per transaction. The oil relationship is exploratory because time trends and omitted variables can create strong contemporaneous correlation.")

# Slide 14
slide = base_slide("Demand level and variability define four planning postures", 14, "Operations segmentation")
shape(slide, 0.68, 1.38, 7.52, 5.30, WHITE, PALE_BLUE, True)
add_picture_contain(slide, "operations_01_family_segments.png", 0.85, 1.58, 7.18, 4.78)
data = [
    ["Segment", "Families"], ["High / stable", "13"], ["High / volatile", "4"],
    ["Low / stable", "3"], ["Low / volatile", "13"],
]
add_table(slide, 5, 2, data, 8.47, 1.55, 3.83, 2.90, widths=[2.65, 1.18], font_size=15)
shape(slide, 8.47, 4.72, 3.83, 1.30, PALE_ORANGE, PALE_ORANGE, True)
textbox(slide, "Produce deserves shorter reviews: scale and volatility compound operating risk.",
        8.72, 4.96, 3.33, 0.78, 16, INK, True, align=PP_ALIGN.CENTER)
source(slide, "Median demand and median CV are transparent portfolio cutoffs")
notes(slide, "The segmentation uses median daily demand and median coefficient of variation. It is a practical framework for differentiated review cadence, not a universal retail classification or an inventory-policy prescription.")

# Slide 15
slide = base_slide("Forecasting tests value beyond transparent operating baselines", 15, "Forecast design")
for i, (head, body) in enumerate([
    ("Target", "3 daily store–family series"),
    ("Validation", "Final 60 days held out"),
    ("Models", "Naive · seasonal · Holt-Winters · RF"),
    ("Metrics", "MAE · RMSE · RMSLE"),
]):
    x = 0.68 + i * 3.02
    shape(slide, x, 1.58, 2.72, 1.46, WHITE, PALE_BLUE, True)
    textbox(slide, head, x + 0.18, 1.79, 2.35, 0.31, 15, PRIMARY, True)
    textbox(slide, body, x + 0.18, 2.20, 2.35, 0.54, 17, INK, True)
shape(slide, 0.68, 3.55, 12.0, 1.28, INK, INK, True)
textbox(slide, "Shifted lags + chronological split + no future transactions", 1.05, 3.87, 11.25, 0.48,
        24, WHITE, True, align=PP_ALIGN.CENTER)
textbox(slide, "No confusion matrix: continuous sales require regression errors and forecast plots.",
        1.15, 5.42, 11.05, 0.48, 19, MUTED, align=PP_ALIGN.CENTER)
notes(slide, "Forecasts use chronological validation rather than a random split. Lag and rolling features are shifted to avoid leakage, and future realized transactions are excluded. MAE measures average unit error, RMSE emphasizes large misses, and RMSLE emphasizes proportional error.")

# Slide 16
slide = base_slide("Random Forest leads on average, but winners vary", 16, "Forecast results")
shape(slide, 0.68, 1.38, 8.20, 5.34, WHITE, PALE_BLUE, True)
add_picture_contain(slide, "forecast_02_model_mae.png", 0.86, 1.60, 7.84, 4.66)
stat(slide, "414.41", "Random Forest average MAE", 9.15, 1.58, 3.05, PRIMARY)
stat(slide, "−42.3%", "vs weekly seasonal baseline", 9.15, 3.16, 3.05, ACCENT)
shape(slide, 9.15, 4.80, 3.05, 1.22, PALE_TEAL, PALE_TEAL, True)
textbox(slide, "Holt-Winters wins Store 32 · Frozen Foods", 9.38, 5.05, 2.59, 0.72,
        16, INK, True, align=PP_ALIGN.CENTER)
source(slide, "60-day holdout · rolling RF and fixed-path Holt-Winters differ operationally")
notes(slide, "Random Forest has the best average errors and a 42.3 percent lower average MAE than the weekly seasonal baseline. Holt-Winters still wins one series, so the operational conclusion is to retain a transparent baseline and monitor errors by store-family series.")

# Slide 17
slide = base_slide("Evidence supports differentiated operating policies", 17, "Managerial actions")
cards = [
    ("Protect core flow", "Routine cycles for stable, high-volume families", PRIMARY),
    ("Flex for volatility", "Shorter reviews for Produce and volatile stores", ACCENT),
    ("Prepare recurring peaks", "Roster and receive ahead of weekends and December", PRIMARY),
    ("Coordinate promotions", "Link campaigns to supply, shelf space, and labor", ACCENT),
    ("Benchmark forecasts", "Track each model against seasonal naive", PRIMARY),
    ("Separate lifecycle effects", "Treat new and mature stores differently", ACCENT),
]
for i, (head, body, col) in enumerate(cards):
    row, c = divmod(i, 3)
    x, y = 0.68 + c * 4.02, 1.50 + row * 2.34
    shape(slide, x, y, 3.68, 1.92, WHITE, PALE_BLUE, True)
    shape(slide, x, y, 0.12, 1.92, col)
    textbox(slide, head, x + 0.28, y + 0.25, 3.08, 0.38, 18, col, True)
    textbox(slide, body, x + 0.28, y + 0.80, 3.05, 0.72, 16, INK)
source(slide, "Actions are planning routines—not precise inventory prescriptions")
notes(slide, "These actions translate observed patterns into practical planning routines. They remain intentionally non-prescriptive because the dataset lacks stock positions, labor productivity, shelf capacity, lead times, supplier constraints, costs, and service targets.")

# Slide 18
slide = base_slide("Better choices emerge when uncertainty stays visible", 18, "Conclusion")
shape(slide, 0.68, 1.47, 7.42, 4.92, INK, INK, True)
textbox(slide, "Plan differently where the evidence differs.", 1.05, 1.88, 6.68, 0.72,
        28, WHITE, True, align=PP_ALIGN.CENTER)
bullet_list(slide, [
    "Prioritize volume without assuming equal predictability",
    "Prepare for calendar and promotion pressure",
    "Benchmark forecasts by store–family series",
    "Separate mature stores from lifecycle effects",
], 1.32, 2.98, 6.14, 2.42, 18, WHITE, ACCENT)
shape(slide, 8.42, 1.47, 3.86, 4.92, WHITE, PALE_BLUE, True)
textbox(slide, "What remains unknown", 8.75, 1.83, 3.18, 0.46, 19, PRIMARY, True)
bullet_list(slide, [
    "Unconstrained demand",
    "Inventory and stockouts",
    "Lead times and service targets",
    "Costs, margins, and capacity",
], 8.77, 2.60, 3.06, 2.65, 17)
textbox(slide, "Next step: pilot forecasts beside seasonal baselines and monitor errors.",
        8.72, 5.50, 3.20, 0.54, 15, ACCENT, True, align=PP_ALIGN.CENTER)
source(slide, "Project conclusion: trustworthy evidence supports planning without overstating causality")
notes(slide, "The main contribution is not one best model. It is a structured way to distinguish scale, variability, calendar peaks, store lifecycle, and forecast uncertainty so managers can apply different planning responses where the evidence justifies them.")


OUT.parent.mkdir(parents=True, exist_ok=True)
prs.save(OUT)
print(OUT)
