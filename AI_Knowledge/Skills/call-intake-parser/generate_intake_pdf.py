#!/usr/bin/env python3
"""
RSG Commercial Client Intake Report Generator
Generates a professional PDF from parsed call intake JSON.
Usage: python3 generate_intake_pdf.py --input parsed_data.json --output report.pdf
"""

import json
import argparse
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

# ── Brand colors ────────────────────────────────────────────────────────────
RSG_DARK   = colors.HexColor('#1a2744')
RSG_BLUE   = colors.HexColor('#1e4d8c')
RSG_ACCENT = colors.HexColor('#c8a84b')
RED_FLAG   = colors.HexColor('#c0392b')
GREEN_OK   = colors.HexColor('#1a7a4a')
GRAY_BG    = colors.HexColor('#f4f5f7')
GRAY_LINE  = colors.HexColor('#d0d3da')

def build_styles():
    styles = getSampleStyleSheet()
    custom = {
        'ReportTitle': ParagraphStyle('ReportTitle', fontSize=22, textColor=RSG_DARK,
            fontName='Helvetica-Bold', spaceAfter=4, alignment=TA_LEFT),
        'ReportSubtitle': ParagraphStyle('ReportSubtitle', fontSize=11, textColor=RSG_BLUE,
            fontName='Helvetica', spaceAfter=2),
        'SectionHeader': ParagraphStyle('SectionHeader', fontSize=12, textColor=colors.white,
            fontName='Helvetica-Bold', leftIndent=6),
        'FieldLabel': ParagraphStyle('FieldLabel', fontSize=9, textColor=colors.HexColor('#666'),
            fontName='Helvetica', spaceAfter=1),
        'FieldValue': ParagraphStyle('FieldValue', fontSize=10, textColor=RSG_DARK,
            fontName='Helvetica-Bold', spaceAfter=4),
        'FlagRed': ParagraphStyle('FlagRed', fontSize=10, textColor=RED_FLAG,
            fontName='Helvetica-Bold'),
        'FlagGreen': ParagraphStyle('FlagGreen', fontSize=10, textColor=GREEN_OK,
            fontName='Helvetica-Bold'),
        'BodyText': ParagraphStyle('BodyText', fontSize=10, textColor=RSG_DARK,
            fontName='Helvetica', leading=14, spaceAfter=6),
        'SmallGray': ParagraphStyle('SmallGray', fontSize=8, textColor=colors.HexColor('#888'),
            fontName='Helvetica'),
    }
    return custom


def section_header(text, styles):
    """Dark blue section header bar."""
    data = [[Paragraph(f'  {text}', styles['SectionHeader'])]]
    t = Table(data, colWidths=[7.5 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), RSG_BLUE),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
    ]))
    return t

def field_row(label, value, styles, flag=None):
    """Single label+value row. flag='red'|'green'|None."""
    val_style = styles['FlagRed'] if flag == 'red' else \
                styles['FlagGreen'] if flag == 'green' else styles['FieldValue']
    display = str(value) if value not in (None, '', [], {}) else '—'
    if flag == 'red' and display == '—':
        display = 'MISSING ⚠'
    return [
        Paragraph(label, styles['FieldLabel']),
        Paragraph(display, val_style)
    ]

def two_col_table(rows, styles):
    """Render a list of [label, value] rows as a 2-col table."""
    t = Table(rows, colWidths=[2.5 * inch, 5.0 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), GRAY_BG),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, GRAY_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, GRAY_LINE),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    return t

def score_bar(score, styles):
    """Submission readiness score bar."""
    color = GREEN_OK if score >= 80 else RSG_ACCENT if score >= 50 else RED_FLAG
    label = 'READY TO SUBMIT' if score >= 80 else \
            'NEEDS FOLLOW-UP' if score >= 50 else 'NOT READY — MISSING CRITICAL FIELDS'
    bar_data = [[
        Paragraph(f'  Submission Readiness: {score}%', ParagraphStyle(
            'ScoreLabel', fontSize=13, textColor=colors.white,
            fontName='Helvetica-Bold')),
        Paragraph(f'{label}  ', ParagraphStyle(
            'ScoreResult', fontSize=11, textColor=colors.white,
            fontName='Helvetica', alignment=TA_RIGHT))
    ]]
    t = Table(bar_data, colWidths=[4.0 * inch, 3.5 * inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), color),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    return t


def generate_report(parsed_data: dict, client_name: str, call_date: str, output_path: str):
    styles = build_styles()
    doc = SimpleDocTemplate(output_path, pagesize=letter,
        leftMargin=0.75*inch, rightMargin=0.75*inch,
        topMargin=0.75*inch, bottomMargin=0.75*inch)
    story = []

    bi   = parsed_data.get('business_identity', {})
    loc  = parsed_data.get('location', {})
    kp   = parsed_data.get('key_people', {})
    fin  = parsed_data.get('financials', {})
    ops  = parsed_data.get('operations', {})
    upd  = parsed_data.get('recent_updates', {})
    cov  = parsed_data.get('existing_coverage', {})
    aut  = parsed_data.get('auto', {})
    missing  = parsed_data.get('missing_required_fields', [])
    xsell    = parsed_data.get('cross_sell_flags', [])
    actions  = parsed_data.get('next_actions', [])
    summary  = parsed_data.get('call_summary', '')
    confidence = parsed_data.get('ai_confidence', 0)

    # ── Compute readiness score ──────────────────────────────────────────────
    required_total = 22
    missing_count = len(missing)
    score = max(0, int(((required_total - missing_count) / required_total) * 100))

    # ── Header ───────────────────────────────────────────────────────────────
    header_data = [[
        Paragraph('RISK SOLUTIONS GROUP', ParagraphStyle('Co', fontSize=9,
            textColor=colors.white, fontName='Helvetica-Bold')),
        Paragraph('COMMERCIAL CLIENT INTAKE REPORT', ParagraphStyle('Title', fontSize=9,
            textColor=RSG_ACCENT, fontName='Helvetica-Bold', alignment=TA_RIGHT))
    ]]
    header_t = Table(header_data, colWidths=[3.75*inch, 3.75*inch])
    header_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), RSG_DARK),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(header_t)
    story.append(Spacer(1, 10))

    # ── Client name + date ───────────────────────────────────────────────────
    story.append(Paragraph(client_name.upper(), styles['ReportTitle']))
    story.append(Paragraph(
        f'Intake call: {call_date}  ·  Generated: {datetime.now().strftime("%B %d, %Y %I:%M %p")}  ·  AI Confidence: {confidence}%',
        styles['ReportSubtitle']))
    story.append(Spacer(1, 6))

    # ── Readiness score bar ──────────────────────────────────────────────────
    story.append(score_bar(score, styles))
    story.append(Spacer(1, 12))

    # ── Call summary ─────────────────────────────────────────────────────────
    if summary:
        story.append(section_header('Call Summary', styles))
        story.append(Spacer(1, 4))
        story.append(Paragraph(summary, styles['BodyText']))
        story.append(Spacer(1, 10))

    # ── Business identity ────────────────────────────────────────────────────
    story.append(section_header('1. Business Identity', styles))
    story.append(Spacer(1, 4))
    rows = [
        field_row('Legal name', bi.get('legal_name'), styles,
            'red' if 'legal_name' in str(missing) else None),
        field_row('DBA', bi.get('dba'), styles),
        field_row('Entity type', bi.get('entity_type'), styles,
            'red' if 'entity_type' in str(missing) else None),
        field_row('FEIN / EIN', bi.get('fein'), styles,
            'red' if 'fein' in str(missing) else None),
        field_row('Date established', bi.get('date_established'), styles),
        field_row('NAICS code', bi.get('naics_code'), styles),
        field_row('SIC code', bi.get('sic_code'), styles),
        field_row('SOS status', bi.get('sos_status'), styles),
    ]
    story.append(two_col_table(rows, styles))
    story.append(Spacer(1, 10))


    # ── Location & premises ──────────────────────────────────────────────────
    story.append(section_header('2. Location & Premises', styles))
    story.append(Spacer(1, 4))
    rows = [
        field_row('Mailing address', loc.get('mailing_address'), styles,
            'red' if 'mailing_address' in str(missing) else None),
        field_row('Square footage', loc.get('sq_footage'), styles,
            'red' if 'sq_footage' in str(missing) else None),
        field_row('Year built', loc.get('year_built'), styles,
            'red' if 'year_built' in str(missing) else None),
        field_row('Construction type', loc.get('construction_type'), styles,
            'red' if 'construction_type' in str(missing) else None),
        field_row('Owned or leased', loc.get('owned_or_leased'), styles),
        field_row('Flood zone', loc.get('flood_zone'), styles),
        field_row('Building value', loc.get('building_value'), styles),
        field_row('Business personal property', loc.get('bpp_value'), styles),
        field_row('Sprinkler system', loc.get('sprinkler'), styles),
        field_row('Security / alarm', loc.get('security_system'), styles),
    ]
    story.append(two_col_table(rows, styles))
    story.append(Spacer(1, 10))

    # ── Financials & payroll ─────────────────────────────────────────────────
    story.append(section_header('3. Financials & Payroll', styles))
    story.append(Spacer(1, 4))
    rows = [
        field_row('Annual revenue — current year', fin.get('annual_revenue_current'), styles,
            'red' if 'annual_revenue' in str(missing) else None),
        field_row('Annual revenue — prior year 1', fin.get('annual_revenue_prior_1'), styles),
        field_row('Annual revenue — prior year 2', fin.get('annual_revenue_prior_2'), styles),
        field_row('Annual payroll — current', fin.get('annual_payroll_current'), styles,
            'red' if 'annual_payroll' in str(missing) else None),
        field_row('Employees — full time', fin.get('employees_ft'), styles,
            'red' if 'employees_ft' in str(missing) else None),
        field_row('Employees — part time', fin.get('employees_pt'), styles),
        field_row('Employees — seasonal', fin.get('employees_seasonal'), styles),
        field_row('Subcontractor spend', fin.get('subcontractor_spend'), styles,
            'red' if 'subcontractor' in str(missing) else None),
        field_row('Subs carry own insurance?', fin.get('subs_insured'), styles),
    ]
    story.append(two_col_table(rows, styles))
    story.append(Spacer(1, 10))

    # ── Operations ───────────────────────────────────────────────────────────
    story.append(section_header('4. Operations', styles))
    story.append(Spacer(1, 4))
    rows = [
        field_row('Operations description', ops.get('description'), styles,
            'red' if 'description' in str(missing) else None),
        field_row('Multi-state work?', ops.get('multi_state'), styles),
        field_row('Alcohol % of revenue', ops.get('alcohol_pct'), styles),
        field_row('Vehicles in operations?', ops.get('vehicles_in_ops'), styles),
        field_row('Sells products?', ops.get('sells_products'), styles),
        field_row('Professional advice given?', ops.get('professional_advice'), styles),
        field_row('Stores customer PII / data?', ops.get('stores_pii'), styles),
        field_row('Government contracts?', ops.get('government_contracts'), styles),
    ]
    story.append(two_col_table(rows, styles))
    story.append(Spacer(1, 10))

    # ── Existing coverage ────────────────────────────────────────────────────
    story.append(section_header('5. Existing Coverage', styles))
    story.append(Spacer(1, 4))
    rows = [
        field_row('Current carriers', ', '.join(cov.get('carriers', [])) or None, styles,
            'red' if 'carriers' in str(missing) else None),
        field_row('Policy numbers', ', '.join(cov.get('policy_numbers', [])) or None, styles),
        field_row('Expiration dates', ', '.join(cov.get('expiration_dates', [])) or None, styles,
            'red' if 'expiration' in str(missing) else None),
        field_row('Current premiums', ', '.join(str(p) for p in cov.get('current_premiums', [])) or None, styles),
        field_row('Loss runs received?', cov.get('loss_runs_received'), styles,
            'red' if 'loss_runs' in str(missing) else None),
        field_row('Umbrella in place?', cov.get('umbrella_in_place'), styles),
        field_row('Umbrella limit', cov.get('umbrella_limit'), styles),
        field_row('Prior non-renewal reason', cov.get('prior_non_renewal_reason'), styles),
    ]
    story.append(two_col_table(rows, styles))
    story.append(Spacer(1, 10))


    # ── Missing required fields ──────────────────────────────────────────────
    story.append(section_header('⚠  Missing Required Fields', styles))
    story.append(Spacer(1, 4))
    if missing:
        miss_rows = [[Paragraph(f'• {f}', styles['FlagRed'])] for f in missing]
        t = Table(miss_rows, colWidths=[7.5 * inch])
        t.setStyle(TableStyle([
            ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, colors.HexColor('#fff5f5')]),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 16),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#f5c0c0')),
        ]))
        story.append(t)
    else:
        story.append(Paragraph('✓ All required fields confirmed.', styles['FlagGreen']))
    story.append(Spacer(1, 10))

    # ── Cross-sell opportunities ─────────────────────────────────────────────
    if xsell:
        story.append(section_header('💰  Cross-Sell Opportunities', styles))
        story.append(Spacer(1, 4))
        xs_map = {
            'umbrella_needed':    'Umbrella / Excess Liability — no umbrella on file',
            'cyber_exposure':     'Cyber Liability — client stores PII or payment data',
            'epli_exposure':      'EPLI — 5+ employees detected',
            'products_liability': 'Products Liability — client sells physical goods',
            'eo_professional':    'E&O / Professional Liability — professional advice given',
            'liquor_liability':   'Liquor Liability — alcohol exceeds 25% of revenue',
            'hnoa_exposure':      'Hired & Non-Owned Auto — employees using personal vehicles',
            'surety_bonding':     'Surety / Bonding — government contracts detected',
            'commercial_auto_gap':'Commercial Auto — vehicles in operations, coverage unclear',
            'aflac_cross_sell':   'Aflac Supplemental — employee benefits conversation needed',
        }
        xs_rows = [[Paragraph(f'💰  {xs_map.get(f, f)}', ParagraphStyle(
            'XS', fontSize=10, textColor=colors.HexColor('#7d4e00'),
            fontName='Helvetica-Bold'))] for f in xsell]
        t = Table(xs_rows, colWidths=[7.5 * inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fffbf0')),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 16),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#f5e0a0')),
        ]))
        story.append(t)
        story.append(Spacer(1, 10))

    # ── Next actions ─────────────────────────────────────────────────────────
    if actions:
        story.append(section_header('Next Actions', styles))
        story.append(Spacer(1, 4))
        for i, action in enumerate(actions, 1):
            story.append(Paragraph(f'{i}.  {action}', styles['BodyText']))
        story.append(Spacer(1, 10))

    # ── Footer ───────────────────────────────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=1, color=GRAY_LINE))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f'Risk Solutions Group  ·  Atlanta, GA  ·  Confidential Client File  ·  '
        f'Generated by RSG OpenClaw  ·  {datetime.now().strftime("%Y-%m-%d")}',
        styles['SmallGray']))

    doc.build(story)
    print(f'PDF generated: {output_path}')


# ── CLI entry point ──────────────────────────────────────────────────────────
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate RSG intake report PDF')
    parser.add_argument('--input', required=True, help='Path to parsed_data JSON file')
    parser.add_argument('--output', required=True, help='Output PDF path')
    parser.add_argument('--client', required=True, help='Client business name')
    parser.add_argument('--date', default=datetime.now().strftime('%Y-%m-%d'),
                        help='Call date (YYYY-MM-DD)')
    args = parser.parse_args()

    with open(args.input) as f:
        data = json.load(f)

    generate_report(data, args.client, args.date, args.output)
