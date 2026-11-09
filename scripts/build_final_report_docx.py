"""Create the exhaustive MBA project report as a polished DOCX."""

from __future__ import annotations

import csv
import re
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "reports" / "final_report.md"
OUT = ROOT / "reports" / "Data_Driven_Demand_Forecasting_Final_Report.docx"
FIGURES = ROOT / "reports" / "figures"
TABLES = ROOT / "reports" / "tables"

NAVY = "17324D"
TEAL = "167D7F"
ORANGE = "D97721"
PALE_BLUE = "EDF3F7"
PALE_TEAL = "E8F3F2"
LIGHT_GRAY = "D9D9D9"
MID_GRAY = "666666"
BLACK = "000000"
WHITE = "FFFFFF"


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_border(cell, color=LIGHT_GRAY, size="6"):
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = borders.find(qn(f"w:{edge}"))
        if element is None:
            element = OxmlElement(f"w:{edge}")
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), size)
        element.set(qn("w:color"), color)


def set_cell_margins(cell, top=110, start=110, bottom=110, end=110):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for m, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{m}"))
        if node is None:
            node = OxmlElement(f"w:{m}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_keep_with_next(paragraph, value=True):
    p_pr = paragraph._p.get_or_add_pPr()
    keep = p_pr.find(qn("w:keepNext"))
    if value and keep is None:
        p_pr.append(OxmlElement("w:keepNext"))


def remove_paragraph_border(paragraph_or_style):
    element = paragraph_or_style._element
    p_pr = element.get_or_add_pPr()
    border = p_pr.find(qn("w:pBdr"))
    if border is not None:
        p_pr.remove(border)


def clean_heading(text):
    text = text.replace("&", "and").replace("²", " squared ")
    text = re.sub(r"[^A-Za-z0-9 ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def set_cant_split(row):
    tr_pr = row._tr.get_or_add_trPr()
    tr_pr.append(OxmlElement("w:cantSplit"))


def set_font(run, name="Arial", size=None, bold=None, italic=None, color=BLACK):
    run.font.name = name
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), name)
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    run.font.color.rgb = RGBColor.from_string(color)


def add_field(paragraph, field_code):
    run = paragraph.add_run()
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = field_code
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "separate")
    fld_char3 = OxmlElement("w:fldChar")
    fld_char3.set(qn("w:fldCharType"), "end")
    run._r.extend([fld_char1, instr, fld_char2, fld_char3])
    return run


def style_document(doc):
    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(0.72)
    section.bottom_margin = Inches(0.72)
    section.left_margin = Inches(0.82)
    section.right_margin = Inches(0.82)
    section.header_distance = Inches(0.32)
    section.footer_distance = Inches(0.32)
    section.different_first_page_header_footer = True

    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor.from_string(BLACK)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.13

    title = doc.styles["Title"]
    title.font.name = "Arial"
    title._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
    title._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
    title.font.size = Pt(28)
    title.font.bold = True
    title.font.color.rgb = RGBColor.from_string(BLACK)
    title.paragraph_format.space_after = Pt(12)
    title.paragraph_format.line_spacing = 1.0
    remove_paragraph_border(title)

    for name, size, before, after in (
        ("Heading 1", 17, 16, 7),
        ("Heading 2", 13.5, 12, 5),
        ("Heading 3", 11.5, 9, 4),
    ):
        style = doc.styles[name]
        style.font.name = "Arial"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(BLACK)
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True

    for name in ("List Bullet", "List Number"):
        style = doc.styles[name]
        style.font.name = "Arial"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
        style.font.size = Pt(10.5)
        style.font.color.rgb = RGBColor.from_string(BLACK)
        style.paragraph_format.space_after = Pt(3)
        style.paragraph_format.line_spacing = 1.08

    if "Caption" in doc.styles:
        style = doc.styles["Caption"]
        style.font.name = "Arial"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Arial")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Arial")
        style.font.size = Pt(9)
        style.font.italic = True
        style.font.color.rgb = RGBColor.from_string(MID_GRAY)
        style.paragraph_format.space_before = Pt(3)
        style.paragraph_format.space_after = Pt(8)


def add_inline(paragraph, text):
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    tokens = re.split(r"(\*\*.*?\*\*|`.*?`|\*.*?\*)", text)
    for token in tokens:
        if not token:
            continue
        if token.startswith("**") and token.endswith("**"):
            run = paragraph.add_run(token[2:-2])
            set_font(run, bold=True)
        elif token.startswith("`") and token.endswith("`"):
            run = paragraph.add_run(token[1:-1])
            set_font(run, name="Courier New", size=9.2, color=NAVY)
        elif token.startswith("*") and token.endswith("*"):
            run = paragraph.add_run(token[1:-1])
            set_font(run, italic=True)
        else:
            run = paragraph.add_run(token)
            set_font(run)


def add_paragraph(doc, text, style=None, alignment=None, keep=False):
    p = doc.add_paragraph(style=style)
    if alignment is not None:
        p.alignment = alignment
    add_inline(p, text)
    if keep:
        set_keep_with_next(p)
    return p


def add_table(doc, data, widths=None, font_size=9.2):
    rows, cols = len(data), len(data[0])
    table = doc.add_table(rows=rows, cols=cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    if widths:
        for c, width in enumerate(widths):
            for cell in table.columns[c].cells:
                cell.width = Inches(width)
    for r, row in enumerate(data):
        set_cant_split(table.rows[r])
        if r == 0:
            set_repeat_table_header(table.rows[r])
        for c, value in enumerate(row):
            cell = table.cell(r, c)
            cell.text = ""
            set_cell_border(cell)
            set_cell_margins(cell)
            set_cell_shading(cell, NAVY if r == 0 else (PALE_BLUE if r % 2 == 0 else WHITE))
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c == 0 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            add_inline(p, str(value))
            for run in p.runs:
                set_font(run, size=font_size, bold=(r == 0), color=(WHITE if r == 0 else BLACK))
    doc.add_paragraph().paragraph_format.space_after = Pt(1)
    return table


def add_figure(doc, rel_path, alt, figure_number):
    path = SOURCE.parent / rel_path
    if not path.exists():
        return figure_number
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(4)
    p.add_run().add_picture(str(path), width=Inches(6.65))
    cap = doc.add_paragraph(style="Caption")
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.add_run(f"Figure {figure_number}  {alt}")
    return figure_number + 1


def parse_markdown_body(doc, text):
    lines = text.splitlines()
    i = 0
    figure_number = 1
    while i < len(lines):
        line = lines[i].rstrip()
        if not line:
            i += 1
            continue
        if i < 4 and line.startswith("#"):
            i += 1
            continue
        if line.startswith("## "):
            heading = clean_heading(line[3:].replace("Appendix —", "Appendix "))
            p = doc.add_paragraph(heading, style="Heading 1")
            if heading not in ("Executive Summary",):
                p.paragraph_format.page_break_before = True
            i += 1
            continue
        if line.startswith("### "):
            heading = clean_heading(line[4:])
            style = "Heading 1" if heading == "Executive Summary" else "Heading 2"
            doc.add_paragraph(heading, style=style)
            i += 1
            continue
        if line.startswith("#### "):
            doc.add_paragraph(clean_heading(line[5:]), style="Heading 3")
            i += 1
            continue
        if line.strip() == "---":
            i += 1
            continue
        image_match = re.match(r"!\[([^\]]+)\]\(([^\)]+)\)", line)
        if image_match:
            figure_number = add_figure(doc, image_match.group(2), image_match.group(1), figure_number)
            i += 1
            continue
        if line.startswith("|"):
            block = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                block.append(lines[i].strip())
                i += 1
            parsed = []
            for idx, row in enumerate(block):
                cells = [c.strip() for c in row.strip("|").split("|")]
                if idx == 1 and all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                    continue
                parsed.append(cells)
            if parsed:
                cols = len(parsed[0])
                if cols == 2:
                    widths = [4.8, 1.7]
                elif cols == 3:
                    widths = [2.15, 1.30, 3.05]
                else:
                    widths = [6.5 / cols] * cols
                add_table(doc, parsed, widths=widths, font_size=8.7 if cols >= 3 else 9.1)
            continue
        if re.match(r"^\d+\. ", line):
            match = re.match(r"^(\d+)\.\s+(.*)", line)
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.28)
            p.paragraph_format.first_line_indent = Inches(-0.28)
            p.paragraph_format.space_after = Pt(2)
            add_inline(p, f"{match.group(1)}.  {match.group(2)}")
            i += 1
            continue
        if line.startswith("- "):
            add_paragraph(doc, line[2:], style="List Bullet")
            i += 1
            continue
        if line.startswith("> "):
            p = add_paragraph(doc, line[2:])
            p.paragraph_format.left_indent = Inches(0.35)
            p.paragraph_format.right_indent = Inches(0.35)
            for run in p.runs:
                run.italic = True
                run.font.color.rgb = RGBColor.from_string(NAVY)
            i += 1
            continue
        paragraph_lines = [line]
        i += 1
        while i < len(lines):
            nxt = lines[i].rstrip()
            if not nxt or nxt.startswith(("#", "|", "- ", "> ", "![")) or re.match(r"^\d+\. ", nxt):
                break
            paragraph_lines.append(nxt)
            i += 1
        add_paragraph(doc, " ".join(paragraph_lines))
    return figure_number


def add_cover(doc):
    for _ in range(3):
        doc.add_paragraph()
    p = doc.add_paragraph(style="Title")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run("Data Driven Demand Analysis and Forecasting for Grocery Retail Operations")
    remove_paragraph_border(p)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(24)
    r = p.add_run("Final MBA Project Report")
    set_font(r, size=15, bold=True, color=NAVY)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(20)
    r = p.add_run("Operations Management supported by Data Science")
    set_font(r, size=12, color=MID_GRAY)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(FIGURES / "data_science_canvas.png"), width=Inches(5.9))
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(14)
    add_inline(p, "Dataset  Kaggle Store Sales Time Series Forecasting\nHistorical coverage  1 January 2013 to 15 August 2017\nPrepared for  MBA Year 1 Operations Management\nReport date  November 2026")
    for run in p.runs:
        set_font(run, size=10.5, color=MID_GRAY)
    doc.add_page_break()


def add_report_orientation(doc):
    doc.add_paragraph("Report Purpose and Main Conclusion", style="Heading 1")
    add_paragraph(doc, "This report explains how historical sales and operational context can support grocery retail planning. It documents the full analytical workflow, the evidence behind each finding, the forecasting design, the managerial implications, and the limits of the available data.")
    add_paragraph(doc, "The main conclusion is that retail demand should not be managed through one network-wide rule. Product families differ in scale and variability, stores differ in maturity and operating profile, and predictable calendar peaks create recurring pressure. Forecasting adds value when each store-family series is compared with a transparent baseline and monitored over time.")
    add_paragraph(doc, "The project does not claim causal promotion effects or optimal inventory policies. The data contains observed sales, not unconstrained demand, and does not include stock positions, stockouts, supplier lead times, costs, margins, or service targets.")

    doc.add_paragraph("Contents", style="Heading 1")
    contents = [
        "Executive Summary", "1  Introduction and Business Context", "2  Project Objectives",
        "3  Dataset and Analytical Scope", "4  Data Preparation and Quality Decisions",
        "5  Exploratory Data Analysis", "6  Operations Analysis",
        "7  Forecasting as Operational Support", "8  Managerial Recommendations",
        "9  Inventory Implications", "10  Limitations", "11  Conclusion",
        "12  Implementation and Monitoring Plan", "13  Additional Data Requirements",
        "Appendix A  Detailed Analytical Workflow", "Appendix B  Metric Definitions",
        "Appendix C  Detailed Forecast Results", "Appendix D  Reproducibility",
        "Appendix E  Viva Questions and Answers",
    ]
    for item in contents:
        p = doc.add_paragraph(style="List Bullet")
        add_inline(p, item)
    doc.add_page_break()


def add_implementation_section(doc):
    h = doc.add_paragraph("12 Implementation and Monitoring Plan", style="Heading 1")
    h.paragraph_format.page_break_before = True
    add_paragraph(doc, "The findings support a controlled planning pilot rather than immediate network-wide automation. The pilot should preserve current decision ownership while measuring whether differentiated reviews and forecast monitoring improve planning reliability.")
    phases = [
        ["Stage", "Operational work", "Evidence to retain"],
        ["1  Establish baselines", "Define current review cadence for selected stores and families. Record weekly seasonal-naive forecast errors.", "MAE, RMSE, RMSLE, coverage, zero-sales frequency, and exceptions"],
        ["2  Pilot differentiated reviews", "Use shorter review cycles for high-demand volatile families and routine cycles for stable high-volume families.", "Planner overrides, peak-period exceptions, and supplier or capacity constraints"],
        ["3  Add model monitoring", "Compare Random Forest and Holt-Winters with the seasonal baseline by store-family series.", "Error by horizon and series, model winner, stability, and failure cases"],
        ["4  Review operating outcomes", "Assess whether peak preparation and promotion coordination reduce avoidable surprises.", "Service, waste, availability, labor, and receiving measures when available"],
    ]
    add_table(doc, phases, widths=[1.35, 3.1, 2.05], font_size=8.5)
    doc.add_paragraph("Monitoring Principles", style="Heading 2")
    for text in [
        "Retain the seasonal-naive forecast as a transparent benchmark.",
        "Evaluate errors by store-family series rather than relying only on network averages.",
        "Record model update frequency because rolling and fixed-path forecasts use different information.",
        "Separate forecast error from execution problems such as stockouts, closures, and supplier constraints.",
        "Revalidate calendar and promotion patterns periodically because historical associations can change.",
    ]:
        add_paragraph(doc, text, style="List Bullet")


def add_data_requirements(doc):
    h = doc.add_paragraph("13 Additional Data Requirements", style="Heading 1")
    h.paragraph_format.page_break_before = True
    add_paragraph(doc, "The current dataset supports descriptive planning and forecast comparison. The following data would be required before calculating inventory policies, estimating financial effects, or attributing causal impact.")
    rows = [
        ["Data required", "Decision enabled", "Reason"],
        ["Stock on hand and stockouts", "Estimate unconstrained demand and availability", "Observed zero sales can represent either no demand or unavailable stock"],
        ["Orders and receipts", "Evaluate replenishment execution", "Sales alone does not show planned quantities or delivery performance"],
        ["Supplier lead times and variability", "Design reorder points and safety stock", "Buffer requirements depend on replenishment uncertainty"],
        ["Costs, prices, and margins", "Estimate financial trade-offs", "Mixed sales units cannot measure profit, holding cost, or waste"],
        ["Service-level targets", "Set policy objectives", "Inventory choices require an explicit availability or fill-rate goal"],
        ["Labor and capacity measures", "Translate peaks into staffing and receiving plans", "Sales volume does not directly measure workload or bottlenecks"],
        ["Promotion assignment and controls", "Estimate causal lift", "Descriptive promoted versus non-promoted ratios are confounded"],
    ]
    add_table(doc, rows, widths=[1.75, 2.15, 2.60], font_size=8.4)


def add_appendices(doc):
    h = doc.add_paragraph("Appendix A Detailed Analytical Workflow", style="Heading 1")
    h.paragraph_format.page_break_before = True
    steps = [
        ("Data understanding", "Verified all seven source files, documented grains and keys, checked dates, shapes, missing values, duplicates, invalid values, and orphan store keys."),
        ("Cleaning and integration", "Added calendar fields, prepared daily oil data with imputation flags, retained missing transactions, matched holiday scope, and validated every merge."),
        ("Exploratory analysis", "Measured network trends, calendar patterns, store and family differences, promotion and holiday associations, traffic relationships, and oil co-movement."),
        ("Advanced analysis", "Classified 1,782 store-family series by ADI and CV squared, tested semi-month windows, compared the April 2016 shock period, and examined cross-family log-change correlations."),
        ("Operations analysis", "Segmented families by demand level and variability, profiled mature stores, and identified recurring peak periods and promotion-planning needs."),
        ("Forecasting", "Evaluated naive, seasonal-naive, Holt-Winters, and rolling Random Forest procedures on a chronological 60-day holdout for three representative series."),
        ("Managerial synthesis", "Linked each validated finding to an operational implication, a possible action, and a stated limitation."),
    ]
    for title, body in steps:
        doc.add_paragraph(title, style="Heading 2")
        add_paragraph(doc, body)

    h = doc.add_paragraph("Appendix B Metric Definitions", style="Heading 1")
    h.paragraph_format.page_break_before = True
    rows = [
        ["Metric", "Definition", "Interpretation"],
        ["Coefficient of variation", "Standard deviation divided by mean demand", "Relative variability across differently scaled series"],
        ["ADI", "Average interval between positive-demand observations", "Frequency of nonzero demand for intermittency screening"],
        ["CV squared", "Squared coefficient of variation for positive demand", "Variation in nonzero demand quantities"],
        ["MAE", "Mean absolute error", "Average forecast miss in sales units"],
        ["RMSE", "Square root of mean squared error", "Gives more weight to large misses"],
        ["RMSLE", "Root mean squared logarithmic error", "Emphasizes proportional error"],
        ["Pearson correlation", "Linear association from minus one to plus one", "Descriptive association, not causation"],
    ]
    add_table(doc, rows, widths=[1.55, 2.55, 2.40], font_size=8.7)

    h = doc.add_paragraph("Appendix C Detailed Forecast Results", style="Heading 1")
    h.paragraph_format.page_break_before = True
    add_paragraph(doc, "The table reports every evaluated model and store-family series from the 60-day validation window. Results should be interpreted with the update-schedule caveat described in Section 7.")
    forecast_path = TABLES / "forecast_model_results.csv"
    if forecast_path.exists():
        with forecast_path.open(newline="", encoding="utf-8") as f:
            data = list(csv.reader(f))
        selected = []
        header = data[0]
        keep = [header.index(c) for c in ("store_nbr", "family", "model", "MAE", "RMSE", "RMSLE")]
        selected.append([header[i].replace("store_nbr", "Store").replace("family", "Family") for i in keep])
        for row in data[1:]:
            formatted = []
            for i in keep:
                value = row[i]
                if header[i] in ("MAE", "RMSE", "RMSLE"):
                    try:
                        value = f"{float(value):,.3f}" if header[i] == "RMSLE" else f"{float(value):,.2f}"
                    except ValueError:
                        pass
                formatted.append(value)
            selected.append(formatted)
        add_table(doc, selected, widths=[0.55, 1.35, 2.05, 0.85, 0.90, 0.80], font_size=7.7)
    add_figure(doc, Path("figures/forecast_02_model_mae.png"), "Average validation MAE by forecasting procedure", 16)

    h = doc.add_paragraph("Appendix D Reproducibility", style="Heading 1")
    h.paragraph_format.page_break_before = True
    add_paragraph(doc, "The repository separates raw data, reusable code, executed notebooks, evidence tables, figures, forecast outputs, and written reporting. Raw Kaggle files remain unchanged and are excluded from Git.")
    inventory = [
        ["Component", "Location", "Purpose"],
        ["Raw data", "data/raw", "Seven Kaggle competition files"],
        ["Executed analysis", "notebooks/01 through 06", "Auditable end-to-end workflow"],
        ["Reusable functions", "src", "Loading, preparation, EDA, features, visualization, and forecasting"],
        ["Evidence tables", "reports/tables", "Values supporting report claims"],
        ["Figures", "reports/figures", "Presentation and report visuals"],
        ["Generated outputs", "outputs", "Validated subset and forecast records"],
        ["Detailed walkthrough", "PROJECT_SUMMARY.md", "Step-by-step record of methods and controls"],
    ]
    add_table(doc, inventory, widths=[1.50, 2.05, 2.95], font_size=8.6)
    doc.add_paragraph("Execution Controls", style="Heading 2")
    for text in [
        "All six notebooks were executed from top to bottom with no recorded cell errors.",
        "The sales panel retained 3,000,888 rows and a unique date-store-family key after integration.",
        "Chronological validation and shifted lag features protected the forecast comparison from leakage.",
        "Numerical report claims are linked to executed notebooks and exported evidence tables.",
    ]:
        add_paragraph(doc, text, style="List Bullet")

    h = doc.add_paragraph("Appendix E Viva Questions and Answers", style="Heading 1")
    h.paragraph_format.page_break_before = True
    qas = [
        ("Why retain zero sales", "Zeros may reflect genuine low demand, closures, store lifecycle, or suppressed sales. Deleting them without operational evidence could bias the demand distribution."),
        ("Why not use a confusion matrix", "Daily sales is a continuous target. MAE, RMSE, RMSLE, and actual-versus-forecast plots preserve the magnitude and timing of errors."),
        ("Why are promotion ratios not promotion lift", "Promotions were not randomly assigned. Timing, product selection, store selection, seasonality, and expected demand can influence both promotion decisions and sales."),
        ("Why treat oil cautiously", "Sales and oil both trend through time and may respond to omitted variables. A contemporaneous correlation does not prove that oil prices drive grocery demand."),
        ("Why use a subset", "The subset makes detailed store-family analysis and forecasting interpretable. Transparent eligibility and selection rules reduce arbitrary choices while the full panel remains available for network findings."),
        ("Can the project calculate safety stock", "No. Safety stock requires inventory positions, stockouts, replenishment lead times, demand during lead time, service targets, costs, and supplier constraints."),
        ("Why compare multiple forecast models", "Demand behavior differs by series. A model that performs well for a high-volume stable family may not perform well for a low-volume or intermittent series."),
    ]
    for question, answer in qas:
        doc.add_paragraph(question, style="Heading 2")
        add_paragraph(doc, answer)


def add_headers_and_footers(doc):
    for section in doc.sections:
        section.different_first_page_header_footer = True
        header = section.header
        p = header.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run("Data Driven Demand Forecasting for Grocery Retail Operations")
        set_font(r, size=8.5, color=MID_GRAY)
        footer = section.footer
        p = footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        r = p.add_run("MBA Project Report   |   ")
        set_font(r, size=8.5, color=MID_GRAY)
        r = add_field(p, "PAGE")
        set_font(r, size=8.5, color=MID_GRAY)


def set_document_properties(doc):
    props = doc.core_properties
    props.title = "Data Driven Demand Analysis and Forecasting for Grocery Retail Operations"
    props.subject = "MBA Operations Management project report supported by data science"
    props.author = "MBA Year 1 Project"
    props.keywords = "demand forecasting, grocery retail, operations management, time series, MBA"
    props.comments = "Generated from the executed project notebooks, evidence tables, and validated report sources."


def main():
    doc = Document()
    style_document(doc)
    add_cover(doc)
    add_report_orientation(doc)
    markdown = SOURCE.read_text(encoding="utf-8")
    parse_markdown_body(doc, markdown)
    add_implementation_section(doc)
    add_data_requirements(doc)
    add_appendices(doc)
    add_headers_and_footers(doc)
    set_document_properties(doc)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
