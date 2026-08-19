import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, PageBreak

logger = logging.getLogger(__name__)

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates", "pdf")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "exports", "pdf")

CHAPTER_TITLES = {
    "ch01_overview": "1. Ты в целом (Архитектура личности)",
    "ch02_drivers": "2. Что тобой управляет (Ценности и приоритеты)",
    "ch03_self_worth": "3. Как ты обходишься с собой (Самоценность и критик)",
    "ch04_emotions": "4. Что ты делаешь с чувствами (Эмоциональная регуляция)",
    "ch05_relationships": "5. Как ты любишь (Близость и привязанность)",
    "ch06_decisions": "6. Как ты принимаешь решения (Неопределенность)",
    "ch07_action": "7. Как ты меняешь свою жизнь (Субъектность и действия)",
    "ch08_visibility": "8. Как ты показываешь себя миру (Проявленность)",
    "ch09_money": "9. Что для тебя значать деньги (Регулятор безопасности)",
    "ch10_stress": "10. Ты под нагрузкой (Состояние и дискомфорт)",
    "ch11_cycles": "11. Твоя система (Системные циклы)",
    "ch12_instruction": "12. Твоя инструкция (10 персональных правил)"
}


def generate_pdf_report(session_id: str, report_data: Dict[str, Any]) -> str:
    """
    Generate styled PDF document using ReportLab (cross-platform compatible).
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    pdf_filename = f"SelfManual_Report_{session_id[:8]}_{int(datetime.now(timezone.utc).timestamp())}.pdf"
    output_path = os.path.join(OUTPUT_DIR, pdf_filename)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=24, leading=28,
        textColor=colors.HexColor('#2b6cb0'), alignment=1, spaceAfter=15
    )
    subtitle_style = ParagraphStyle(
        'CoverSubTitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=14, leading=18,
        textColor=colors.HexColor('#4a5568'), alignment=1, spaceAfter=30
    )
    section_style = ParagraphStyle(
        'SectionHeader', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=14, leading=18,
        textColor=colors.HexColor('#2b6cb0'), spaceBefore=20, spaceAfter=10
    )
    heading_style = ParagraphStyle(
        'ChapterHeader', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, leading=14,
        textColor=colors.HexColor('#2d3748'), spaceBefore=10, spaceAfter=4
    )
    body_style = ParagraphStyle(
        'ChapterBody', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9.5, leading=13,
        textColor=colors.HexColor('#1a202c'), spaceAfter=8
    )
    meta_style = ParagraphStyle(
        'MetaBox', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9, leading=12,
        textColor=colors.HexColor('#718096'), alignment=1, spaceAfter=20
    )
    rule_style = ParagraphStyle(
        'RuleCard', parent=styles['Normal'],
        fontName='Helvetica', fontSize=9.5, leading=13,
        textColor=colors.HexColor('#2c5282'), spaceAfter=6
    )

    story = []

    # Cover Page
    story.append(Spacer(1, 40))
    story.append(Paragraph("ИНСТРУКЦИЯ К СЕБЕ", title_style))
    story.append(Paragraph("Персональная карта психологической архитектуры", subtitle_style))
    story.append(HRFlowable(width="80%", thickness=1, color=colors.HexColor('#e2e8f0'), spaceAfter=30))
    
    date_str = datetime.now(timezone.utc).strftime("%d.%m.%Y")
    story.append(Paragraph(f"<b>Дата отчета:</b> {date_str} | <b>Версия:</b> Architecture V1.3", meta_style))
    story.append(Paragraph(f"<b>Идентификатор сессии:</b> {session_id}", meta_style))
    story.append(PageBreak())

    # Section I: Chapters
    story.append(Paragraph("I. Архитектура и главы самопонимания", section_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2b6cb0'), spaceAfter=12))

    chapters = report_data.get("chapters", {})
    for ch_key, ch_text in chapters.items():
        ch_title = CHAPTER_TITLES.get(ch_key, ch_key)
        story.append(Paragraph(ch_title, heading_style))
        story.append(Paragraph(ch_text, body_style))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 10))

    # Section II: 10 Personal Rules
    story.append(Paragraph("II. 10 Персональных правил обращения с собой", section_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2b6cb0'), spaceAfter=12))

    personal_rules = report_data.get("personal_rules", [])
    for rule in personal_rules:
        story.append(Paragraph(f"• {rule}", rule_style))

    story.append(Spacer(1, 10))

    # Section III: Synthesis
    story.append(Paragraph("III. Главный синтез вашей системы", section_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2b6cb0'), spaceAfter=12))

    synthesis = report_data.get("final_synthesis", {})
    story.append(Paragraph(f"<b>Главная опора (Top Resource):</b> {synthesis.get('top_resource', 'Н/Д')}", body_style))
    story.append(Paragraph(f"<b>Системная ловушка (Top Trap):</b> {synthesis.get('top_trap', 'Н/Д')}", body_style))
    story.append(Paragraph(f"<b>Рычаг изменений (Top Leverage):</b> {synthesis.get('top_leverage', 'Н/Д')}", body_style))

    story.append(Spacer(1, 20))
    story.append(Paragraph("<font size=7 color='#a0aec0'>Документ сформирован системой «Инструкция к себе» V1.3. Не является медицинским диагнозом.</font>", meta_style))

    doc.build(story)
    return output_path
