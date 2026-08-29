"""
PDF Report Generator — Creates formatted incident analysis documents.
Uses reportlab for PDF generation.
"""
import os
import tempfile
from datetime import datetime


def generate_pdf_report(all_processed_reports: list) -> str:
    """
    Generate a PDF report of all processed incidents.
    Returns the path to the generated PDF file.
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch, mm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
    except ImportError:
        raise RuntimeError("reportlab not installed. Run: pip install reportlab")

    output_path = os.path.join(tempfile.gettempdir(), f"sif_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")

    doc = SimpleDocTemplate(output_path, pagesize=A4,
                            topMargin=25*mm, bottomMargin=20*mm,
                            leftMargin=20*mm, rightMargin=20*mm)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Title2', parent=styles['Title'], fontSize=22, spaceAfter=6))
    styles.add(ParagraphStyle(name='Subtitle', parent=styles['Normal'], fontSize=11, textColor=colors.grey, spaceAfter=20))
    styles.add(ParagraphStyle(name='SectionHead', parent=styles['Heading2'], fontSize=14, textColor=colors.HexColor('#1e40af'), spaceBefore=16, spaceAfter=8))
    styles.add(ParagraphStyle(name='BodySmall', parent=styles['Normal'], fontSize=9, leading=12))
    styles.add(ParagraphStyle(name='Critical', parent=styles['Normal'], fontSize=10, textColor=colors.red, fontName='Helvetica-Bold'))

    elements = []

    # ── Title ──
    elements.append(Paragraph("SIF Precursor Intelligence — Incident Analysis Report", styles['Title2']))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Reports Analyzed: {len(all_processed_reports)}", styles['Subtitle']))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#334155')))
    elements.append(Spacer(1, 12))

    # ── Executive Summary ──
    precursors = [r for r in all_processed_reports if r.get("is_precursor")]
    total = len(all_processed_reports)
    max_score = max((r["risk_data"]["score"] for r in all_processed_reports), default=0)
    escalating = sum(1 for r in all_processed_reports if r["risk_data"]["trajectory"] == "ESCALATING")

    elements.append(Paragraph("Executive Summary", styles['SectionHead']))
    summary_data = [
        ["Metric", "Value"],
        ["Total Reports Analyzed", str(total)],
        ["Precursors Detected", f"{len(precursors)} ({len(precursors)/max(total,1)*100:.0f}%)"],
        ["Max Risk Score", str(max_score)],
        ["Escalating Trajectories", str(escalating)],
    ]
    summary_table = Table(summary_data, colWidths=[200, 200])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.HexColor('#e2e8f0')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 16))

    # ── Critical Alerts ──
    if precursors:
        elements.append(Paragraph("Critical Precursor Alerts", styles['SectionHead']))
        for p in precursors:
            r = p["report"]
            rd = p["risk_data"]
            ent = p["extracted_entities"]
            eq = ', '.join(ent.get("equipment", ["N/A"]))
            loc = ', '.join(ent.get("locations", ["N/A"]))
            haz = ', '.join(ent.get("hazards", ["N/A"]))

            elements.append(Paragraph(
                f"<b>{r.get('id', 'N/A')}</b> — Score: <font color='red'><b>{rd['score']}</b></font> — "
                f"Trajectory: <b>{rd['trajectory']}</b> — SIF: <b>{rd.get('sif_category', 'None')}</b>",
                styles['BodySmall']
            ))
            elements.append(Paragraph(f"Equipment: {eq} | Location: {loc} | Hazards: {haz}", styles['BodySmall']))
            elements.append(Paragraph(f"<i>\"{r.get('text', '')}\"</i>", styles['BodySmall']))

            if rd.get("evidence"):
                evidence_text = " | ".join(rd["evidence"])
                elements.append(Paragraph(f"Evidence: {evidence_text}", styles['BodySmall']))

            if p.get("interventions"):
                elements.append(Paragraph("Recommended Actions:", styles['BodySmall']))
                for action in p["interventions"]:
                    elements.append(Paragraph(f"  • {action}", styles['BodySmall']))

            elements.append(Spacer(1, 10))
            elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e2e8f0')))

    # ── Full Report Log ──
    elements.append(Paragraph("Complete Incident Log", styles['SectionHead']))
    log_data = [["ID", "Date", "Score", "Trajectory", "SIF", "Equipment"]]
    for r in all_processed_reports:
        log_data.append([
            r["report"].get("id", "")[:15],
            r["report"].get("date", "")[:10],
            str(r["risk_data"]["score"]),
            r["risk_data"]["trajectory"],
            r["risk_data"].get("sif_category", "")[:12],
            ", ".join(r["extracted_entities"].get("equipment", []))[:20],
        ])

    log_table = Table(log_data, colWidths=[70, 65, 40, 65, 65, 100])
    log_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f1f5f9')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))

    # Color-code precursor rows
    for i, r in enumerate(all_processed_reports, start=1):
        if r.get("is_precursor"):
            log_table.setStyle(TableStyle([
                ('BACKGROUND', (0, i), (-1, i), colors.HexColor('#fef2f2')),
                ('TEXTCOLOR', (2, i), (2, i), colors.red),
            ]))

    elements.append(log_table)
    elements.append(Spacer(1, 20))

    # ── Footer ──
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#334155')))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(
        "Generated by SIF Precursor Intelligence System — Smart India Hackathon 2026 (SIH 26165)",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    ))

    doc.build(elements)
    print(f"[pdf] Report generated: {output_path}")
    return output_path
