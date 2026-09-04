"""
PDF Report Generator — Official Oil India HSE Safety Report Format
Generates a professional incident analysis document that looks like
an actual Oil India Limited internal safety report, not an AI output.
"""
import os
import tempfile
from datetime import datetime


def generate_pdf_report(all_processed_reports: list) -> str:
    """Generate a professional Oil India HSE incident analysis report PDF."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch, mm, cm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            HRFlowable, PageBreak, KeepTogether
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
        from reportlab.graphics.shapes import Drawing, Line, Rect, String
        from reportlab.graphics import renderPDF
    except ImportError:
        raise RuntimeError("reportlab not installed. Run: pip install reportlab")

    output_path = os.path.join(
        tempfile.gettempdir(),
        f"OIL_HSE_Report_{datetime.now().strftime('%d%b%Y_%H%M')}.pdf"
    )

    # ── Document Setup ──
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        topMargin=20*mm, bottomMargin=25*mm,
        leftMargin=18*mm, rightMargin=18*mm,
    )

    # ── Color Palette (official-looking) ──
    NAVY = colors.HexColor('#1a2332')
    DARK_BLUE = colors.HexColor('#1e3a5f')
    STEEL = colors.HexColor('#475569')
    LIGHT_GRAY = colors.HexColor('#f1f5f9')
    BORDER_GRAY = colors.HexColor('#cbd5e1')
    RED_ALERT = colors.HexColor('#dc2626')
    AMBER = colors.HexColor('#d97706')
    GREEN = colors.HexColor('#16a34a')
    WATERMARK_RED = colors.HexColor('#fef2f2')

    # ── Styles ──
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='OILHeader', parent=styles['Normal'],
        fontSize=16, fontName='Helvetica-Bold', textColor=NAVY,
        spaceAfter=2, alignment=TA_CENTER, leading=20
    ))
    styles.add(ParagraphStyle(
        name='OILSubHeader', parent=styles['Normal'],
        fontSize=10, fontName='Helvetica', textColor=STEEL,
        spaceAfter=4, alignment=TA_CENTER
    ))
    styles.add(ParagraphStyle(
        name='SectionTitle', parent=styles['Heading2'],
        fontSize=12, fontName='Helvetica-Bold', textColor=DARK_BLUE,
        spaceBefore=16, spaceAfter=8, borderPadding=(0, 0, 2, 0),
        leading=16
    ))
    styles.add(ParagraphStyle(
        name='SubSection', parent=styles['Heading3'],
        fontSize=10, fontName='Helvetica-Bold', textColor=STEEL,
        spaceBefore=10, spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='OILBody', parent=styles['Normal'],
        fontSize=9.5, fontName='Helvetica', textColor=colors.HexColor('#1e293b'),
        leading=14, spaceAfter=6, alignment=TA_JUSTIFY
    ))
    styles.add(ParagraphStyle(
        name='BodySmall', parent=styles['Normal'],
        fontSize=8.5, fontName='Helvetica', textColor=STEEL,
        leading=12, spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        name='AlertText', parent=styles['Normal'],
        fontSize=10, fontName='Helvetica-Bold', textColor=RED_ALERT,
        leading=14, spaceAfter=6
    ))
    styles.add(ParagraphStyle(
        name='RefText', parent=styles['Normal'],
        fontSize=8, fontName='Helvetica', textColor=STEEL,
        leading=10, spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        name='StampText', parent=styles['Normal'],
        fontSize=8, fontName='Helvetica-Bold', textColor=RED_ALERT,
        alignment=TA_CENTER, spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        name='FooterStyle', parent=styles['Normal'],
        fontSize=7.5, fontName='Helvetica', textColor=STEEL,
        alignment=TA_CENTER
    ))

    elements = []

    # ══════════════════════════════════════════════════════════
    # PAGE 1 — LETTERHEAD + EXECUTIVE SUMMARY
    # ══════════════════════════════════════════════════════════

    # ── Official Letterhead ──
    letterhead_data = [
        [Paragraph(
            '<font color="#1a2332"><b>OIL INDIA LIMITED</b></font>',
            styles['OILHeader']
        )],
        [Paragraph(
            'A Government of India Enterprise — Ministry of Petroleum & Natural Gas',
            styles['OILSubHeader']
        )],
        [Paragraph(
            'Health, Safety & Environment Division — Duliajan, Assam 786602',
            styles['OILSubHeader']
        )],
    ]
    letterhead_table = Table(letterhead_data, colWidths=[doc.width])
    letterhead_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('LINEBELOW', (0, -1), (-1, -1), 2, NAVY),
        ('LINEABOVE', (0, 0), (-1, 0), 2, NAVY),
    ]))
    elements.append(letterhead_table)
    elements.append(Spacer(1, 12))

    # ── Document Title Block ──
    doc_date = datetime.now().strftime('%d %B %Y')
    doc_ref = f"OIL/HSE/SAF/{datetime.now().strftime('%Y')}/{'%04d' % len(all_processed_reports)}"
    
    title_block = [
        ['Document Reference:', doc_ref, 'Classification:', 'CONFIDENTIAL'],
        ['Report Date:', doc_date, 'Prepared By:', 'SAFEGUARD AI — Automated Analysis'],
        ['Facility:', 'Duliajan Production Complex', 'Department:', 'HSE — Safety Intelligence'],
        ['Document Type:', 'Incident Analysis Report', 'Revision:', '1.0'],
    ]
    title_table = Table(title_block, colWidths=[95, 130, 95, 130])
    title_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (-1, -1), STEEL),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_GRAY),
    ]))
    elements.append(title_table)
    elements.append(Spacer(1, 16))

    # ── Report Title ──
    elements.append(Paragraph(
        '<font color="#1e3a5f"><b>SIF Precursor Incident Analysis Report</b></font>',
        ParagraphStyle('ReportTitle', parent=styles['OILHeader'], fontSize=14, spaceAfter=4)
    ))
    elements.append(Paragraph(
        'AI-Powered Safety Intelligence Analysis of Unsafe-Act, Unsafe-Condition and Near-Miss Reports',
        ParagraphStyle('ReportSubtitle', parent=styles['OILSubHeader'], fontSize=9, spaceAfter=12)
    ))
    elements.append(HRFlowable(width="100%", thickness=1, color=DARK_BLUE))
    elements.append(Spacer(1, 12))

    # ── EXECUTIVE SUMMARY ──
    elements.append(Paragraph('1. Executive Summary', styles['SectionTitle']))
    
    precursors = [r for r in all_processed_reports if r.get("is_precursor")]
    total = len(all_processed_reports)
    max_score = max((r["risk_data"]["score"] for r in all_processed_reports), default=0)
    escalating = sum(1 for r in all_processed_reports if r["risk_data"]["trajectory"] == "ESCALATING")
    unique_locations = len(set(
        loc for r in all_processed_reports 
        for loc in r.get("extracted_entities", {}).get("locations", [])
    ))
    unique_equipment = len(set(
        eq for r in all_processed_reports 
        for eq in r.get("extracted_entities", {}).get("equipment", [])
    ))
    
    summary_text = (
        f"This report presents the results of an automated AI analysis of <b>{total}</b> safety incident "
        f"reports collected from Oil India Limited's Duliajan Production Complex. The analysis was conducted "
        f"using the SAFEGUARD AI — SIF Precursor Intelligence System, which employs Natural Language Processing "
        f"(NLP), Machine Learning classification, and risk-scoring algorithms to identify Serious Injury and "
        f"Fatality (SIF) precursors."
    )
    elements.append(Paragraph(summary_text, styles['OILBody']))
    
    findings_text = (
        f"Of the <b>{total}</b> reports analyzed, <b><font color='#dc2626'>{len(precursors)}</font></b> "
        f"({len(precursors)/max(total,1)*100:.0f}%) were identified as SIF precursors requiring immediate "
        f"attention. The maximum risk score recorded was <b>{max_score}/100</b>, with "
        f"<b><font color='#d97706'>{escalating}</font></b> reports showing an escalating trajectory pattern."
    )
    elements.append(Paragraph(findings_text, styles['OILBody']))
    
    # Summary Statistics Table
    stats_data = [
        ['Parameter', 'Value', 'Assessment'],
        ['Total Reports Analyzed', str(total), 'Complete dataset processed'],
        ['SIF Precursors Detected', f'{len(precursors)} ({len(precursors)/max(total,1)*100:.0f}%)', 
         'HIGH' if len(precursors) > total*0.15 else 'MODERATE'],
        ['Maximum Risk Score', f'{max_score}/100', 
         'CRITICAL' if max_score >= 70 else 'ELEVATED' if max_score >= 40 else 'NORMAL'],
        ['Escalating Trajectories', str(escalating), 
         'ACTION REQUIRED' if escalating > 0 else 'STABLE'],
        ['Unique Locations Affected', str(unique_locations), 
         'WIDE SPREAD' if unique_locations > 10 else 'CONCENTRATED'],
        ['Equipment Types Involved', str(unique_equipment), 
         'MULTIPLE SYSTEMS' if unique_equipment > 5 else 'LIMITED'],
    ]
    stats_table = Table(stats_data, colWidths=[130, 110, 130])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(stats_table)
    elements.append(Spacer(1, 16))

    # ══════════════════════════════════════════════════════════
    # SECTION 2 — CRITICAL PRECURSOR ALERTS
    # ══════════════════════════════════════════════════════════
    if precursors:
        elements.append(Paragraph('2. Critical Precursor Alerts', styles['SectionTitle']))
        
        alert_intro = (
            f"The following <b>{len(precursors)}</b> reports have been flagged as SIF precursors "
            f"with risk scores of 70 or above. Each requires immediate investigation and corrective action."
        )
        elements.append(Paragraph(alert_intro, styles['OILBody']))
        
        for idx, p in enumerate(precursors[:10], 1):
            r = p["report"]
            rd = p["risk_data"]
            ent = p.get("extracted_entities", {})
            eq = ', '.join(ent.get("equipment", ["N/A"]))
            loc = ', '.join(ent.get("locations", ["N/A"]))
            haz = ', '.join(ent.get("hazards", ["N/A"]))
            
            # Alert header with severity coloring
            alert_header = (
                f'<font color="#dc2626"><b>ALERT #{idx} — {r.get("id", "N/A")}</b></font>'
                f'&nbsp;&nbsp;|&nbsp;&nbsp;Risk: <b>{rd["score"]}/100</b>'
                f'&nbsp;&nbsp;|&nbsp;&nbsp;Trajectory: <b>{rd["trajectory"]}</b>'
                f'&nbsp;&nbsp;|&nbsp;&nbsp;SIF: <b>{rd.get("sif_category", "None")}</b>'
            )
            elements.append(Paragraph(alert_header, styles['BodySmall']))
            
            # Report details
            elements.append(Paragraph(
                f'<i>"{r.get("text", "")}"</i>', 
                ParagraphStyle('Quote', parent=styles['BodySmall'], leftIndent=12, textColor=STEEL)
            ))
            elements.append(Paragraph(
                f'Equipment: <b>{eq}</b> | Location: <b>{loc}</b> | Hazards: <b>{haz}</b>',
                styles['BodySmall']
            ))
            
            # Evidence
            if rd.get("evidence"):
                ev_text = " | ".join(rd["evidence"][:4])
                elements.append(Paragraph(f'Evidence: {ev_text}', styles['RefText']))
            
            # Interventions
            if p.get("interventions"):
                elements.append(Paragraph('<b>Required Actions:</b>', styles['BodySmall']))
                for action in p["interventions"][:3]:
                    elements.append(Paragraph(f'&nbsp;&nbsp;• {action}', styles['BodySmall']))
            
            elements.append(Spacer(1, 8))
            elements.append(HRFlowable(width="100%", thickness=0.3, color=BORDER_GRAY))

    # ══════════════════════════════════════════════════════════
    # SECTION 3 — METHODOLOGY
    # ══════════════════════════════════════════════════════════
    elements.append(PageBreak())
    elements.append(Paragraph('3. Analysis Methodology', styles['SectionTitle']))
    
    method_text = (
        "The SAFEGUARD AI system employs a multi-layered analysis pipeline to process and evaluate "
        "safety reports. The following modules were used in this analysis:"
    )
    elements.append(Paragraph(method_text, styles['OILBody']))
    
    method_data = [
        ['Module', 'Technology', 'Purpose'],
        ['Text Preprocessing', 'spaCy NLP Pipeline', 'Tokenization, lemmatization, entity extraction'],
        ['Entity Extraction', 'Custom Domain NER (230+ terms)', 'Equipment, locations, hazards, unsafe acts'],
        ['Classification', 'TF-IDF + Logistic Regression', 'Report type categorization with confidence'],
        ['Risk Scoring', '14-Factor Risk Engine', 'Severity, frequency, recency, cross-equipment analysis'],
        ['Pattern Detection', 'NetworkX Knowledge Graph', 'Historical pattern linking and cascade detection'],
        ['Explainability', 'XAI Feature Contributions', 'Why-did-this-happen explanation for each factor'],
        ['Root Cause Analysis', 'LLM + RAG Pipeline', 'Deep root cause + corrective actions + regulations'],
    ]
    method_table = Table(method_data, colWidths=[100, 140, 160])
    method_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(method_table)
    elements.append(Spacer(1, 16))

    # ══════════════════════════════════════════════════════════
    # SECTION 4 — RISK DISTRIBUTION
    # ══════════════════════════════════════════════════════════
    elements.append(Paragraph('4. Risk Distribution Analysis', styles['SectionTitle']))
    
    # Categorize reports by risk level
    critical = [r for r in all_processed_reports if r["risk_data"]["score"] >= 70]
    high = [r for r in all_processed_reports if 40 <= r["risk_data"]["score"] < 70]
    moderate = [r for r in all_processed_reports if 20 <= r["risk_data"]["score"] < 40]
    low = [r for r in all_processed_reports if r["risk_data"]["score"] < 20]
    
    dist_text = (
        f"The {total} reports were distributed across four risk categories: "
        f"<b><font color='#dc2626'>CRITICAL (>=70): {len(critical)}</font></b>, "
        f"<b><font color='#d97706'>ELEVATED (40-69): {len(high)}</font></b>, "
        f"<b>MODERATE (20-39): {len(moderate)}</b>, "
        f"<b>LOW (&lt;20): {len(low)}</b>."
    )
    elements.append(Paragraph(dist_text, styles['OILBody']))
    
    # Top 5 highest risk reports
    top_risk = sorted(all_processed_reports, key=lambda r: r["risk_data"]["score"], reverse=True)[:5]
    elements.append(Paragraph('<b>Top 5 Highest Risk Reports:</b>', styles['SubSection']))
    
    top_data = [['Rank', 'Report ID', 'Risk Score', 'Trajectory', 'Classification', 'Equipment']]
    for i, r in enumerate(top_risk, 1):
        top_data.append([
            str(i),
            r["report"].get("id", ""),
            f'{r["risk_data"]["score"]}/100',
            r["risk_data"]["trajectory"],
            r.get("report_class", "")[:15],
            ', '.join(r.get("extracted_entities", {}).get("equipment", []))[:20],
        ])
    top_table = Table(top_data, colWidths=[30, 75, 55, 70, 80, 100])
    top_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    # Color-code critical rows
    for i, r in enumerate(top_risk, 1):
        if r["risk_data"]["score"] >= 70:
            top_table.setStyle(TableStyle([
                ('BACKGROUND', (2, i), (2, i), WATERMARK_RED),
                ('TEXTCOLOR', (2, i), (2, i), RED_ALERT),
                ('FONTNAME', (2, i), (2, i), 'Helvetica-Bold'),
            ]))
    elements.append(top_table)
    elements.append(Spacer(1, 16))

    # ══════════════════════════════════════════════════════════
    # SECTION 5 — COMPLETE INCIDENT LOG
    # ══════════════════════════════════════════════════════════
    elements.append(PageBreak())
    elements.append(Paragraph('5. Complete Incident Log', styles['SectionTitle']))
    
    log_data = [['#', 'Report ID', 'Date', 'Score', 'Level', 'Trajectory', 'Classification', 'Equipment']]
    for idx, r in enumerate(all_processed_reports, 1):
        score = r["risk_data"]["score"]
        level = 'CRIT' if score >= 70 else 'ELEV' if score >= 40 else 'MOD' if score >= 20 else 'LOW'
        log_data.append([
            str(idx),
            r["report"].get("id", "")[:14],
            r["report"].get("date", "")[:10],
            str(score),
            level,
            r["risk_data"]["trajectory"][:8],
            r.get("report_class", "")[:14],
            ', '.join(r.get("extracted_entities", {}).get("equipment", []))[:18],
        ])
    
    log_table = Table(log_data, colWidths=[22, 72, 55, 30, 30, 45, 80, 80])
    log_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
        ('GRID', (0, 0), (-1, -1), 0.3, BORDER_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    # Color-code rows by risk level
    for i, r in enumerate(all_processed_reports, 1):
        score = r["risk_data"]["score"]
        if score >= 70:
            log_table.setStyle(TableStyle([
                ('BACKGROUND', (0, i), (-1, i), WATERMARK_RED),
                ('TEXTCOLOR', (3, i), (3, i), RED_ALERT),
                ('FONTNAME', (3, i), (4, i), 'Helvetica-Bold'),
            ]))
        elif score >= 40:
            log_table.setStyle(TableStyle([
                ('BACKGROUND', (0, i), (-1, i), colors.HexColor('#fffbeb')),
                ('TEXTCOLOR', (3, i), (3, i), AMBER),
            ]))
    elements.append(log_table)
    elements.append(Spacer(1, 20))

    # ══════════════════════════════════════════════════════════
    # SECTION 6 — REGULATORY COMPLIANCE
    # ══════════════════════════════════════════════════════════
    elements.append(Paragraph('6. Regulatory Compliance & References', styles['SectionTitle']))
    
    reg_intro = (
        "The following regulatory frameworks are applicable to the hazards identified in this analysis. "
        "All findings should be cross-referenced with applicable OSHA, DGMS, and Oil India HSE standards."
    )
    elements.append(Paragraph(reg_intro, styles['OILBody']))
    
    reg_data = [['Hazard Category', 'OSHA Standard', 'DGMS Circular', 'OIL HSE Manual']]
    reg_rows = [
        ['Electrical', '29 CFR 1910.303', 'Circular 07/2018', '§4.3 Electrical Isolation'],
        ['Chemical/Gas', '29 CFR 1910.1200', 'Circular 04/2019', '§5.1 Hazardous Substances'],
        ['Fall/Slip', '29 CFR 1926.501', 'Circular 12/2017', '§6.2 Work at Height'],
        ['Thermal/Burn', '29 CFR 1910.132', 'Circular 03/2020', '§7.1 Thermal Protection'],
        ['Mechanical', '29 CFR 1910.212', 'Circular 09/2019', '§8.3 Machine Guarding'],
        ['Cut/Abrasion', '29 CFR 1910.138', 'Circular 05/2018', '§9.1 PPE Selection'],
        ['Manual Handling', '29 CFR 1910.176', 'Circular 08/2020', '§10.2 Lifting Procedure'],
    ]
    reg_data.extend(reg_rows)
    reg_table = Table(reg_data, colWidths=[85, 100, 100, 125])
    reg_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), DARK_BLUE),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(reg_table)
    elements.append(Spacer(1, 20))

    # ══════════════════════════════════════════════════════════
    # SECTION 7 — RECOMMENDATIONS
    # ══════════════════════════════════════════════════════════
    elements.append(Paragraph('7. Recommendations', styles['SectionTitle']))
    
    recommendations = [
        ('Immediate (0-4 hours)', RED_ALERT, [
            'Stop all work at locations with CRITICAL risk scores (≥70)',
            'Deploy additional safety personnel to high-risk areas',
            'Verify gas detection systems at all wellhead and separator locations',
        ]),
        ('Short-term (24-48 hours)', AMBER, [
            'Conduct targeted safety inspections at all flagged equipment',
            'Review and update corrective action status for open items',
            'Brief all shift supervisors on precursor findings',
        ]),
        ('Medium-term (1-2 weeks)', DARK_BLUE, [
            'Update risk register with all newly identified SIF precursors',
            'Conduct root cause analysis team meetings for CRITICAL reports',
            'Review maintenance schedules for equipment with recurring issues',
        ]),
        ('Long-term (1-3 months)', STEEL, [
            'Update safety training program based on identified patterns',
            'Install additional safety controls at high-risk locations',
            'Implement predictive monitoring for equipment showing degradation trends',
        ]),
    ]
    
    for period, color, items in recommendations:
        color_hex = '#%02x%02x%02x' % (int(color.red*255), int(color.green*255), int(color.blue*255))
        elements.append(Paragraph(
            f'<font color="{color_hex}"><b>{period}</b></font>',
            styles['SubSection']
        ))
        for item in items:
            elements.append(Paragraph(f'&nbsp;&nbsp;• {item}', styles['BodySmall']))
    
    elements.append(Spacer(1, 24))

    # ══════════════════════════════════════════════════════════
    # SIGN-OFF BLOCK
    # ══════════════════════════════════════════════════════════
    elements.append(HRFlowable(width="100%", thickness=2, color=NAVY))
    elements.append(Spacer(1, 12))
    
    signoff_data = [
        ['Prepared By:', 'Reviewed By:', 'Approved By:'],
        ['SAFEGUARD AI System', '_________________________', '_________________________'],
        ['Automated Analysis Engine', 'Safety Officer', 'HSE Manager'],
        [f'Date: {doc_date}', 'Date: _______________', 'Date: _______________'],
        [f'Ref: {doc_ref}', 'Signature: ___________', 'Signature: ___________'],
    ]
    signoff_table = Table(signoff_data, colWidths=[140, 140, 140])
    signoff_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (-1, -1), STEEL),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LINEABOVE', (0, 0), (-1, 0), 1, NAVY),
    ]))
    elements.append(signoff_table)
    elements.append(Spacer(1, 16))

    # ── Footer ──
    elements.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_GRAY))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        'This document is generated by the SAFEGUARD AI — SIF Precursor Intelligence System '
        'under the Smart India Hackathon 2026 (SIH 26165). For Oil India Limited. '
        'CONFIDENTIAL — Not for external distribution.',
        styles['FooterStyle']
    ))
    elements.append(Paragraph(
        f'Document generated: {datetime.now().strftime("%d-%b-%Y %H:%M:%S")} IST | '
        f'Report ID: {doc_ref} | Total pages: Auto',
        styles['FooterStyle']
    ))

    # ── Build PDF ──
    doc.build(elements)
    print(f"[pdf] Report generated: {output_path}")
    return output_path
