import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any

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



# Asti Dark Style definitions
BG_COLOR = '#0F0F11'
TEXT_COLOR = '#EAEAEA'
ACCENT_COLOR = '#C8B592'
MUTED_TEXT = '#6B6B73'

def make_background_drawer(bg_img_name="onboarding.png", alpha=0.85):
    def draw_background(canvas, doc):
        canvas.saveState()
        w, h = 595.27, 841.89
        
        # Build the correct absolute path to the images folder
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        bg_img = os.path.join(base_dir, "assets", "images", bg_img_name)
        
        if os.path.exists(bg_img):
            from reportlab.lib.utils import ImageReader
            try:
                img = ImageReader(bg_img)
                img_w, img_h = img.getSize()
                img_aspect = img_w / float(img_h)
                target_aspect = w / float(h)
                if img_aspect > target_aspect:
                    draw_h = h
                    draw_w = draw_h * img_aspect
                    x_offset = (w - draw_w) / 2
                    y_offset = 0
                else:
                    draw_w = w
                    draw_h = draw_w / img_aspect
                    x_offset = 0
                    y_offset = (h - draw_h) / 2
                canvas.drawImage(bg_img, x_offset, y_offset, width=draw_w, height=draw_h, preserveAspectRatio=True)
            except Exception as e:
                logger.error(f"Failed to draw background image {bg_img}: {e}")
                
        from reportlab.lib import colors
        canvas.setFillColor(colors.HexColor(BG_COLOR))
        try:
            canvas.setFillAlpha(alpha)
        except AttributeError:
            pass
        canvas.rect(0, 0, w, h, fill=1, stroke=0)
        try:
            canvas.setFillAlpha(1.0)
        except AttributeError:
            pass
        
        canvas.setStrokeColor(colors.HexColor(ACCENT_COLOR))
        canvas.setLineWidth(0.3)
        margin = 40
        canvas.line(margin, h - margin, w - margin, h - margin)
        
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(colors.HexColor(MUTED_TEXT))
        canvas.drawString(margin, h - margin + 8, "PRIVATE PSYCHOLOGICAL INTELLIGENCE REPORT")
        canvas.drawRightString(w - margin, h - margin + 8, "ID: SC-99482A")
        canvas.drawString(margin, margin - 15, f"PAGE {str(doc.page).zfill(2)}")
        canvas.drawRightString(w - margin, margin - 15, "SELFCODE SYSTEM V1.3")
        
        canvas.restoreState()
    return draw_background


def _get_reportlab():
    """Lazy import of ReportLab to prevent module load crashes when reportlab is not installed."""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, PageBreak
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        return {
            "A4": A4,
            "colors": colors,
            "getSampleStyleSheet": getSampleStyleSheet,
            "ParagraphStyle": ParagraphStyle,
            "SimpleDocTemplate": SimpleDocTemplate,
            "Paragraph": Paragraph,
            "Spacer": Spacer,
            "HRFlowable": HRFlowable,
            "PageBreak": PageBreak,
            "pdfmetrics": pdfmetrics,
            "TTFont": TTFont,
        }
    except ImportError as e:
        logger.error("ReportLab import failed: %s", e)
        raise ImportError(
            "Модуль 'reportlab' не найден. Убедитесь, что 'reportlab' установлен в окружении Python."
        ) from e


def _get_cyrillic_font(pdfmetrics, TTFont):
    """Detect and register a Cyrillic-compatible TTF font if available."""
    font_candidates = [
        ("Arial", "C:/Windows/Fonts/arial.ttf"),
        ("Arial-Bold", "C:/Windows/Fonts/arialbd.ttf"),
        ("LiberationSans", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
        ("LiberationSans-Bold", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
        ("DejaVuSans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ("DejaVuSans-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ]
    
    reg_font = None
    reg_bold = None

    for name, path in font_candidates:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont(name, path))
                if "Bold" in name or "bd" in name:
                    if not reg_bold:
                        reg_bold = name
                else:
                    if not reg_font:
                        reg_font = name
            except Exception as font_err:
                logger.warning(f"Failed to register font {name} from {path}: {font_err}")

    font_regular = reg_font or "Helvetica"
    font_bold = reg_bold or (reg_font if reg_font else "Helvetica-Bold")
    return font_regular, font_bold


def generate_pdf_report(session_id: str, report_data: Dict[str, Any]) -> str:
    """
    Generate styled PDF document using ReportLab (cross-platform compatible).
    """
    rl = _get_reportlab()

    A4 = rl["A4"]
    colors = rl["colors"]
    getSampleStyleSheet = rl["getSampleStyleSheet"]
    ParagraphStyle = rl["ParagraphStyle"]
    SimpleDocTemplate = rl["SimpleDocTemplate"]
    Paragraph = rl["Paragraph"]
    Spacer = rl["Spacer"]
    HRFlowable = rl["HRFlowable"]
    PageBreak = rl["PageBreak"]

    font_reg, font_bold = _get_cyrillic_font(rl["pdfmetrics"], rl["TTFont"])

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
        fontName=font_bold, fontSize=24, leading=28,
        textColor=colors.HexColor(ACCENT_COLOR), alignment=1, spaceAfter=15
    )
    subtitle_style = ParagraphStyle(
        'CoverSubTitle', parent=styles['Normal'],
        fontName=font_reg, fontSize=14, leading=18,
        textColor=colors.HexColor(MUTED_TEXT), alignment=1, spaceAfter=30
    )
    section_style = ParagraphStyle(
        'SectionHeader', parent=styles['Normal'],
        fontName=font_bold, fontSize=14, leading=18,
        textColor=colors.HexColor(ACCENT_COLOR), spaceBefore=20, spaceAfter=10
    )
    heading_style = ParagraphStyle(
        'ChapterHeader', parent=styles['Normal'],
        fontName=font_bold, fontSize=11, leading=14,
        textColor=colors.HexColor(TEXT_COLOR), spaceBefore=10, spaceAfter=4
    )
    body_style = ParagraphStyle(
        'ChapterBody', parent=styles['Normal'],
        fontName=font_reg, fontSize=9.5, leading=13,
        textColor=colors.HexColor(TEXT_COLOR), spaceAfter=8
    )
    meta_style = ParagraphStyle(
        'MetaBox', parent=styles['Normal'],
        fontName=font_reg, fontSize=9, leading=12,
        textColor=colors.HexColor('#718096'), alignment=1, spaceAfter=20
    )
    rule_style = ParagraphStyle(
        'RuleCard', parent=styles['Normal'],
        fontName=font_reg, fontSize=9.5, leading=13,
        textColor=colors.HexColor('#2c5282'), spaceAfter=6
    )

    story = []

    # Cover Page
    story.append(Spacer(1, 40))
    story.append(Paragraph("ИНСТРУКЦИЯ К СЕБЕ", title_style))
    story.append(Paragraph("Персональная карта психологической архитектуры", subtitle_style))
    story.append(HRFlowable(width="80%", thickness=1, color=colors.HexColor(ACCENT_COLOR), spaceAfter=30))
    
    date_str = datetime.now(timezone.utc).strftime("%d.%m.%Y")
    story.append(Paragraph(f"<b>Дата отчета:</b> {date_str} | <b>Версия:</b> Architecture V1.3", meta_style))
    story.append(Paragraph(f"<b>Идентификатор сессии:</b> {session_id}", meta_style))
    story.append(PageBreak())

    # Section I: Chapters
    story.append(Paragraph("I. Архитектура и главы самопонимания", section_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#2b6cb0'), spaceAfter=12))

    chapters = report_data.get("chapters", {})
    if isinstance(chapters, dict):
        chapter_items = chapters.items()
    elif isinstance(chapters, list):
        # If it's a list of dicts like [{"title": "...", "text": "..."}]
        chapter_items = []
        for i, ch in enumerate(chapters):
            if isinstance(ch, dict):
                title = ch.get("title", ch.get("name", f"Глава {i+1}"))
                text = ch.get("text", ch.get("content", str(ch)))
                chapter_items.append((title, text))
            else:
                chapter_items.append((f"Глава {i+1}", str(ch)))
    else:
        chapter_items = []

    for ch_key, ch_text in chapter_items:
        ch_title = CHAPTER_TITLES.get(ch_key, ch_key)
        
        # Ensure text is a string and escape XML tags
        if isinstance(ch_text, dict):
            ch_text = ch_text.get("text", ch_text.get("content", str(ch_text)))
        ch_text = str(ch_text).replace('<', '&lt;').replace('>', '&gt;')
        ch_title = str(ch_title).replace('<', '&lt;').replace('>', '&gt;')

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

    bg_drawer = make_background_drawer("full_report.png", 0.85)
    doc.build(story, onFirstPage=bg_drawer, onLaterPages=bg_drawer)
    return output_path


def generate_core_pdf_report(session_id: str, report_data: Dict[str, Any]) -> str:
    """
    Generate 3-page CORE PDF report (SelfCore) using ReportLab.
    """
    rl = _get_reportlab()
    A4 = rl["A4"]
    colors = rl["colors"]
    getSampleStyleSheet = rl["getSampleStyleSheet"]
    ParagraphStyle = rl["ParagraphStyle"]
    SimpleDocTemplate = rl["SimpleDocTemplate"]
    Paragraph = rl["Paragraph"]
    Spacer = rl["Spacer"]
    HRFlowable = rl["HRFlowable"]
    PageBreak = rl["PageBreak"]

    font_reg, font_bold = _get_cyrillic_font(rl["pdfmetrics"], rl["TTFont"])

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    pdf_filename = f"SelfCore_Report_{session_id[:8]}_{int(datetime.now(timezone.utc).timestamp())}.pdf"
    output_path = os.path.join(OUTPUT_DIR, pdf_filename)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'CoverTitle', parent=styles['Normal'], fontName=font_bold, fontSize=22, leading=26,
        textColor=colors.HexColor(TEXT_COLOR), alignment=1, spaceAfter=20
    )
    core_phrase_style = ParagraphStyle(
        'CorePhrase', parent=styles['Normal'], fontName=font_bold, fontSize=16, leading=22,
        textColor=colors.HexColor(ACCENT_COLOR), alignment=1, spaceAfter=25
    )
    section_title = ParagraphStyle(
        'SectionTitle', parent=styles['Normal'], fontName=font_bold, fontSize=16, leading=20,
        textColor=colors.HexColor(TEXT_COLOR), spaceAfter=15, spaceBefore=20
    )
    body_style = ParagraphStyle(
        'Body', parent=styles['Normal'], fontName=font_reg, fontSize=11, leading=16,
        textColor=colors.HexColor(TEXT_COLOR), spaceAfter=12
    )
    metric_title_style = ParagraphStyle(
        'MetricTitle', parent=styles['Normal'], fontName=font_bold, fontSize=12, leading=16,
        textColor=colors.HexColor(ACCENT_COLOR), spaceAfter=4, spaceBefore=10
    )
    metric_desc_style = ParagraphStyle(
        'MetricDesc', parent=styles['Normal'], fontName=font_reg, fontSize=10, leading=14,
        textColor=colors.HexColor(MUTED_TEXT), spaceAfter=10
    )
    cycle_flow_style = ParagraphStyle(
        'CycleFlow', parent=styles['Normal'], fontName=font_bold, fontSize=11, leading=18,
        textColor=colors.HexColor(ACCENT_COLOR), alignment=1, spaceAfter=15, spaceBefore=10
    )
    list_style = ParagraphStyle(
        'ListStyle', parent=styles['Normal'], fontName=font_reg, fontSize=11, leading=16,
        textColor=colors.HexColor(TEXT_COLOR), spaceAfter=8, leftIndent=15
    )
    marketing_style = ParagraphStyle(
        'Marketing', parent=styles['Normal'], fontName=font_bold, fontSize=11, leading=16,
        textColor=colors.HexColor(ACCENT_COLOR), spaceAfter=10, spaceBefore=20
    )

    story = []
    report = report_data.get("report", {})

    # PAGE 1: ВАШ SELFCORE
    story.append(Paragraph("ИНСТРУКЦИЯ К СЕБЕ", ParagraphStyle('Top', fontName=font_bold, fontSize=10, textColor=colors.HexColor(MUTED_TEXT), alignment=1)))
    story.append(Spacer(1, 15))
    story.append(Paragraph("ВАШ SELFCORE", title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor(ACCENT_COLOR), spaceAfter=25))
    
    if report.get("core_phrase"):
        story.append(Paragraph(report["core_phrase"], core_phrase_style))

    if report.get("portrait"):
        story.append(Paragraph(report["portrait"], body_style))
        story.append(Spacer(1, 20))

    story.append(Paragraph("ЧЕТЫРЕ КЛЮЧЕВЫХ ПОКАЗАТЕЛЯ", section_title))
    metrics = report.get("metrics", [])
    for m in metrics:
        story.append(Paragraph(f"{m.get('name')} — {m.get('score')}/100", metric_title_style))
        story.append(Paragraph(m.get("description", ""), metric_desc_style))

    story.append(PageBreak())

    # PAGE 2: ЦИКЛ, РЕСУРСЫ, ОГРАНИЧЕНИЯ
    story.append(Paragraph("ВАШ ГЛАВНЫЙ ВНУТРЕННИЙ ЦИКЛ", section_title))
    loop = report.get("main_loop", {})
    if loop.get("flow"):
        story.append(Paragraph(loop["flow"], cycle_flow_style))
    if loop.get("description"):
        story.append(Paragraph(loop["description"], body_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("ЧТО ВАС УСИЛИВАЕТ", section_title))
    for res in report.get("resources", []):
        story.append(Paragraph(f"• {res}", list_style))

    story.append(Spacer(1, 20))

    story.append(Paragraph("ГДЕ ВАШ РЕСУРС МОЖЕТ СТАНОВИТЬСЯ ЛОВУШКОЙ", section_title))
    for lim in report.get("limitations", []):
        story.append(Paragraph(f"• {lim}", list_style))

    story.append(PageBreak())

    # PAGE 3: ПРАВИЛА, ПРОТИВОРЕЧИЯ, МАРКЕТИНГ
    story.append(Paragraph("ПЯТЬ ПРАВИЛ ВЗАИМОДЕЙСТВИЯ С СОБОЙ", section_title))
    for idx, rule in enumerate(report.get("rules", []), 1):
        story.append(Paragraph(f"<b>0{idx}.</b> {rule}", list_style))
        
    story.append(Spacer(1, 20))

    conflict = report.get("conflict")
    if conflict:
        story.append(Paragraph("ПРОТИВОРЕЧИЕ, КОТОРОЕ СТОИТ ЗАМЕТИТЬ", section_title))
        story.append(Paragraph(conflict, body_style))
        story.append(Spacer(1, 20))

    story.append(Paragraph("ЭТО ТОЛЬКО ВЕРХНИЙ СЛОЙ", marketing_style))
    border = report.get("border_of_knowledge", {})
    story.append(Paragraph("Первые 30 вопросов позволяют увидеть базовую архитектуру вашей внутренней системы. Но они ещё не показывают, почему она сформировалась именно такой и как её элементы взаимодействуют между собой.", body_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("В полном SelfCore исследуются:", ParagraphStyle('B', fontName=font_bold, fontSize=11, textColor=colors.HexColor(TEXT_COLOR), spaceAfter=5)))
    for unk in border.get("unknowns", []):
        story.append(Paragraph(f"• {unk}", list_style))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph("Мы уже видим несколько противоречий в ваших ответах. Но данных CORE недостаточно, чтобы определить, являются ли они случайными или образуют устойчивый внутренний конфликт.", body_style))
    story.append(Paragraph("Для этого нужен следующий уровень диагностики.", ParagraphStyle('B2', fontName=font_bold, fontSize=11, textColor=colors.HexColor(ACCENT_COLOR))))

    bg_drawer = make_background_drawer("core_report.png", 0.85)
    doc.build(story, onFirstPage=bg_drawer, onLaterPages=bg_drawer)
    return output_path

