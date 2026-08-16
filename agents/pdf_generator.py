from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.platypus.flowables import HRFlowable


INDIGO      = colors.HexColor("#4F46E5")
TEAL        = colors.HexColor("#0F766E")
AMBER       = colors.HexColor("#B45309")
DARK        = colors.HexColor("#1E1B4B")
SLATE       = colors.HexColor("#334155")
MUTED       = colors.HexColor("#64748B")
LIGHT_BG    = colors.HexColor("#EEF2FF")
TEAL_BG     = colors.HexColor("#F0FDFA")
AMBER_BG    = colors.HexColor("#FFFBEB")
GRAY_BG     = colors.HexColor("#F8FAFC")
WHITE       = colors.white
BORDER      = colors.HexColor("#E2E8F0")


def build_styles():
    """
    Build all paragraph styles used in the PDF.
    ParagraphStyle lets you define font, size, colour, spacing per style.
    """
    base = getSampleStyleSheet()

    styles = {}

    styles["cover_title"] = ParagraphStyle(
        "cover_title", fontName="Helvetica-Bold",
        fontSize=32, leading=38, textColor=INDIGO,
        alignment=TA_CENTER, spaceAfter=6
    )
    styles["cover_sub"] = ParagraphStyle(
        "cover_sub", fontName="Helvetica",
        fontSize=16, leading=20, textColor=TEAL,
        alignment=TA_CENTER, spaceAfter=4
    )
    styles["cover_meta"] = ParagraphStyle(
        "cover_meta", fontName="Helvetica",
        fontSize=11, leading=14, textColor=MUTED,
        alignment=TA_CENTER, spaceAfter=3
    )
    styles["section_title"] = ParagraphStyle(
        "section_title", fontName="Helvetica-Bold",
        fontSize=16, leading=20, textColor=DARK,
        spaceBefore=18, spaceAfter=6,
        borderPad=0
    )
    styles["sub_title"] = ParagraphStyle(
        "sub_title", fontName="Helvetica-Bold",
        fontSize=12, leading=15, textColor=SLATE,
        spaceBefore=10, spaceAfter=4
    )
    styles["body"] = ParagraphStyle(
        "body", fontName="Helvetica",
        fontSize=10, textColor=SLATE,
        spaceBefore=2, spaceAfter=4,
        leading=15
    )
    styles["body_muted"] = ParagraphStyle(
        "body_muted", fontName="Helvetica",
        fontSize=9, textColor=MUTED,
        spaceBefore=1, spaceAfter=3,
        leading=13
    )
    styles["tip"] = ParagraphStyle(
        "tip", fontName="Helvetica",
        fontSize=9, textColor=SLATE,
        spaceBefore=2, spaceAfter=2,
        leftIndent=10, leading=14,
        bulletIndent=0,
        bulletText="•"
    )
    styles["day_title"] = ParagraphStyle(
        "day_title", fontName="Helvetica-Bold",
        fontSize=11, textColor=WHITE,
        spaceAfter=0
    )
    styles["time_label"] = ParagraphStyle(
        "time_label", fontName="Helvetica-Bold",
        fontSize=8, textColor=MUTED,
        spaceAfter=1
    )
    styles["agent_badge"] = ParagraphStyle(
        "agent_badge", fontName="Helvetica",
        fontSize=7, textColor=INDIGO,
        spaceBefore=0, spaceAfter=8,
        letterSpacing=0.5
    )

    return styles



def divider(color=BORDER, thickness=0.5):
    return HRFlowable(
        width="100%", thickness=thickness,
        color=color, spaceAfter=8, spaceBefore=4
    )



def section_header(icon, title, agent_name, styles):
    """Returns a KeepTogether block with icon + title + agent badge + divider."""
    return KeepTogether([
        Paragraph(f"{icon}  {title}", styles["section_title"]),
        Paragraph(agent_name.upper(), styles["agent_badge"]),
        divider(INDIGO, 1),
    ])



def kv_table(rows, col_widths, bg=GRAY_BG):
    """
    Creates a simple two-column key-value table.
    rows = [("Label", "Value"), ...]
    """
    table = Table(rows, colWidths=col_widths)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("FONTNAME",   (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",   (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE",   (0, 0), (-1, -1), 9),
        ("TEXTCOLOR",  (0, 0), (0, -1), SLATE),
        ("TEXTCOLOR",  (1, 0), (1, -1), SLATE),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, GRAY_BG]),
        ("GRID",       (0, 0), (-1, -1), 0.5, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return table


def generate_pdf(travel_plan: dict) -> bytes:
    """
    Converts the full travel_plan dict (from the orchestrator)
    into a PDF and returns it as bytes.

    --- CONCEPT: BytesIO ---
    Instead of writing the PDF to disk, we write it to an in-memory
    buffer (BytesIO). Flask then sends those bytes directly as a
    download response. No temp files, no cleanup needed.
    """
    buffer = BytesIO()
    meta   = travel_plan.get("meta", {})
    styles = build_styles()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20*mm, rightMargin=20*mm,
        topMargin=20*mm,  bottomMargin=20*mm,
        title=f"Travel Plan — {meta.get('destination', 'Trip')}",
        author="AI Travel Planner"
    )

    
    story = []
    W = 170*mm  # usable page width (A4 210mm - 40mm margins)

    
    story.append(Spacer(1, 30*mm))
    story.append(Paragraph(meta.get("destination", "Your Trip"), styles["cover_title"]))
    story.append(Paragraph("AI-Generated Travel Plan", styles["cover_sub"]))
    story.append(Spacer(1, 6*mm))
    story.append(divider(INDIGO, 1.5))
    story.append(Spacer(1, 4*mm))

    
    meta_rows = [
        ("From",          meta.get("origin", "—")),
        ("Travel dates",  meta.get("travel_dates", "—")),
        ("Duration",      f"{meta.get('duration_days', '—')} days"),
        ("Travelers",     str(meta.get("num_travelers", "—"))),
        ("Travel style",  meta.get("travel_style", "—").title()),
        ("Budget level",  meta.get("budget_level", "—").replace("_", " ").title()),
    ]
    story.append(kv_table(meta_rows, [60*mm, 110*mm], LIGHT_BG))
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph("Generated by AI Travel Planner · Multi-Agent Architecture", styles["cover_meta"]))
    story.append(PageBreak())

    
    flights = travel_plan.get("flights", {})
    story.append(section_header("✈", "Flights", "Flights Agent", styles))

    if "error" not in flights:
        routes = flights.get("suggested_routes", [])
        if routes:
            rows = [["Route", "Type", "Duration", "Est. Cost (INR)"]]
            for r in routes:
                rows.append([
                    r.get("route", ""),
                    r.get("type", ""),
                    r.get("duration", ""),
                    r.get("estimated_cost_inr", ""),
                ])
            t = Table(rows, colWidths=[55*mm, 30*mm, 35*mm, 50*mm])
            t.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, 0), INDIGO),
                ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
                ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",      (0, 0), (-1, -1), 9),
                ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, GRAY_BG]),
                ("GRID",          (0, 0), (-1, -1), 0.5, BORDER),
                ("TOPPADDING",    (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING",   (0, 0), (-1, -1), 6),
                ("ALIGN",         (0, 0), (-1, -1), "LEFT"),
                ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ]))
            story.append(t)
            story.append(Spacer(1, 4*mm))

        if flights.get("best_time_to_book"):
            story.append(Paragraph(
                f"<b>Best time to book:</b> {flights['best_time_to_book']}",
                styles["body"]
            ))
        if flights.get("airlines"):
            story.append(Paragraph(
                f"<b>Airlines:</b> {', '.join(flights['airlines'])}",
                styles["body"]
            ))
        for tip in flights.get("travel_tips", []):
            story.append(Paragraph(f"• {tip}", styles["tip"]))

    story.append(Spacer(1, 6*mm))

    
    hotels = travel_plan.get("hotels", {})
    story.append(section_header("🏨", "Hotels & Accommodation", "Hotels Agent", styles))

    if "error" not in hotels:
        areas = hotels.get("recommended_areas", [])
        if areas:
            rows = [["Area", "Why stay here", "Hotel type"]]
            for a in areas:
                rows.append([a.get("area",""), a.get("why",""), a.get("hotel_type","")])
            t = Table(rows, colWidths=[40*mm, 90*mm, 40*mm])
            t.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, 0), TEAL),
                ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
                ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",      (0, 0), (-1, -1), 9),
                ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, TEAL_BG]),
                ("GRID",          (0, 0), (-1, -1), 0.5, BORDER),
                ("TOPPADDING",    (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING",   (0, 0), (-1, -1), 6),
                ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(t)
            story.append(Spacer(1, 4*mm))

        bd = hotels.get("budget_breakdown", {})
        if bd:
            story.append(Paragraph("<b>Price ranges per night:</b>", styles["sub_title"]))
            story.append(kv_table([
                ("Budget",    bd.get("budget", "—")),
                ("Mid-range", bd.get("mid_range", "—")),
                ("Luxury",    bd.get("luxury", "—")),
            ], [40*mm, 130*mm], TEAL_BG))
            story.append(Spacer(1, 4*mm))

        if hotels.get("booking_tips"):
            for tip in hotels["booking_tips"]:
                story.append(Paragraph(f"• {tip}", styles["tip"]))

    story.append(Spacer(1, 6*mm))

    
    itinerary = travel_plan.get("itinerary", {})
    story.append(section_header("🗓", "Day-by-Day Itinerary", "Itinerary Agent", styles))

    DAY_COLORS = [INDIGO, TEAL, colors.HexColor("#B45309"),
                  colors.HexColor("#DC2626"), colors.HexColor("#0891B2")]

    for day in itinerary.get("itinerary", []):
        day_num = day.get("day", 1)
        color   = DAY_COLORS[(day_num - 1) % len(DAY_COLORS)]

        
        header_table = Table(
            [[Paragraph(f"Day {day_num}  ·  {day.get('title','')}", styles["day_title"])]],
            colWidths=[W]
        )
        header_table.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), color),
            ("TOPPADDING",    (0,0), (-1,-1), 7),
            ("BOTTOMPADDING", (0,0), (-1,-1), 7),
            ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ]))

        
        body_rows = []
        for slot_label, slot_key in [("🌅 Morning", "morning"), ("☀️ Afternoon", "afternoon"), ("🌙 Evening", "evening")]:
            if day.get(slot_key):
                body_rows.append([
                    Paragraph(slot_label, styles["time_label"]),
                    Paragraph(day[slot_key], styles["body"])
                ])

        if day.get("places"):
            body_rows.append([
                Paragraph("📍 Places", styles["time_label"]),
                Paragraph(", ".join(day["places"]), styles["body_muted"])
            ])

        if day.get("estimated_local_spend_inr"):
            body_rows.append([
                Paragraph("💰 Daily est.", styles["time_label"]),
                Paragraph(f"₹{day['estimated_local_spend_inr']}", styles["body"])
            ])

        body_table = Table(body_rows, colWidths=[30*mm, 140*mm])
        body_table.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), GRAY_BG),
            ("VALIGN",        (0,0), (-1,-1), "TOP"),
            ("TOPPADDING",    (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("LEFTPADDING",   (0,0), (-1,-1), 8),
            ("RIGHTPADDING",  (0,0), (-1,-1), 8),
            ("LINEBELOW",     (0,0), (-1,-2), 0.3, BORDER),
        ]))

        
        story.append(KeepTogether([header_table, body_table, Spacer(1, 4*mm)]))

    if itinerary.get("must_visit"):
        story.append(Paragraph("<b>Must visit:</b> " + " · ".join(itinerary["must_visit"]), styles["body"]))

    
    story.append(Spacer(1, 6*mm))

    # ── FEASIBILITY SECTION ───────────────────────────────────────────
    feasibility = travel_plan.get("feasibility", {})
    if feasibility and feasibility.get("overall_feasibility") not in (None, "unknown"):
        story.append(section_header("🔍", "Feasibility Review", "Feasibility Agent", styles))

        verdict = feasibility.get("overall_feasibility", "—")
        VERDICT_HEX = {"high": "#0F766E", "medium": "#B45309", "low": "#DC2626"}
        verdict_hex = VERDICT_HEX.get(verdict, "#64748B")

        story.append(Paragraph(
            f'<font color="{verdict_hex}"><b>Overall feasibility: {verdict.upper()}</b></font>',
            styles["body"]
        ))
        if feasibility.get("summary"):
            story.append(Paragraph(feasibility["summary"], styles["body"]))
        story.append(Spacer(1, 3*mm))

        day_reviews = feasibility.get("day_reviews", [])
        if day_reviews:
            rows = [["Day", "Status", "Note"]]
            for r in day_reviews:
                rows.append([
                    str(r.get("day", "")),
                    r.get("status", "").replace("_", " ").title(),
                    r.get("note", "")
                ])
            t = Table(rows, colWidths=[15*mm, 30*mm, 125*mm])
            t.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#334155")),
                ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
                ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",      (0, 0), (-1, -1), 9),
                ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, GRAY_BG]),
                ("GRID",          (0, 0), (-1, -1), 0.5, BORDER),
                ("TOPPADDING",    (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING",   (0, 0), (-1, -1), 6),
                ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(t)
            story.append(Spacer(1, 4*mm))

        for suggestion in feasibility.get("suggestions", []):
            story.append(Paragraph(f"• {suggestion}", styles["tip"]))

        story.append(Spacer(1, 6*mm))

    # ── BUDGET SECTION ────────────────────────────────────────────────

    
    budget = travel_plan.get("budget", {})
    story.append(section_header("💰", "Budget Breakdown", "Budget Agent", styles))

    if "error" not in budget:
        breakdown = budget.get("budget_breakdown", {})
        if breakdown:
            rows = [["Category", "Min (₹)", "Max (₹)", "Note"]]
            for cat, vals in breakdown.items():
                rows.append([
                    cat.replace("_", " ").title(),
                    str(vals.get("min", "")),
                    str(vals.get("max", "")),
                    vals.get("note", "")
                ])
            t = Table(rows, colWidths=[45*mm, 25*mm, 25*mm, 75*mm])
            t.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#92400E")),
                ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
                ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",      (0, 0), (-1, -1), 9),
                ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, AMBER_BG]),
                ("GRID",          (0, 0), (-1, -1), 0.5, BORDER),
                ("TOPPADDING",    (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING",   (0, 0), (-1, -1), 6),
                ("ALIGN",         (1, 0), (2, -1), "RIGHT"),
                ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
            ]))
            story.append(t)
            story.append(Spacer(1, 4*mm))

        total = budget.get("total", {})
        if total:
            story.append(Paragraph("<b>Total trip estimates:</b>", styles["sub_title"]))
            story.append(kv_table([
                ("Budget trip",    f"₹{total.get('budget_trip', '—')}"),
                ("Comfortable",    f"₹{total.get('comfortable_trip', '—')}"),
                ("Luxury",         f"₹{total.get('luxury_trip', '—')}"),
            ], [50*mm, 120*mm], AMBER_BG))
            story.append(Spacer(1, 4*mm))

        for tip in budget.get("money_saving_tips", []):
            story.append(Paragraph(f"• {tip}", styles["tip"]))

    story.append(Spacer(1, 6*mm))

    
    culture = travel_plan.get("culture", {})
    story.append(section_header("🍛", "Local Food & Culture", "Culture Agent", styles))

    if "error" not in culture:
        foods = culture.get("must_try_food", [])
        if foods:
            story.append(Paragraph("<b>Must-try food:</b>", styles["sub_title"]))
            rows = [["Dish", "Description", "Where to try"]]
            for f in foods:
                rows.append([f.get("dish",""), f.get("description",""), f.get("where_to_try","")])
            t = Table(rows, colWidths=[40*mm, 90*mm, 40*mm])
            t.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, 0), TEAL),
                ("TEXTCOLOR",     (0, 0), (-1, 0), WHITE),
                ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE",      (0, 0), (-1, -1), 9),
                ("ROWBACKGROUNDS",(0, 1), (-1, -1), [WHITE, TEAL_BG]),
                ("GRID",          (0, 0), (-1, -1), 0.5, BORDER),
                ("TOPPADDING",    (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING",   (0, 0), (-1, -1), 6),
                ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ]))
            story.append(t)
            story.append(Spacer(1, 4*mm))

        if culture.get("cultural_tips"):
            story.append(Paragraph("<b>Cultural tips:</b>", styles["sub_title"]))
            for tip in culture["cultural_tips"]:
                story.append(Paragraph(f"• {tip}", styles["tip"]))
            story.append(Spacer(1, 3*mm))

        gems = culture.get("hidden_gems", [])
        if gems:
            story.append(Paragraph("<b>Hidden gems:</b>", styles["sub_title"]))
            for g in gems:
                story.append(Paragraph(
                    f"<b>{g.get('place','')}</b> — {g.get('why','')}",
                    styles["body"]
                ))

        if culture.get("things_to_avoid"):
            story.append(Paragraph("<b>Things to avoid:</b>", styles["sub_title"]))
            for thing in culture["things_to_avoid"]:
                story.append(Paragraph(f"• {thing}", styles["tip"]))

    
    
    doc.build(story)

    
    return buffer.getvalue()
