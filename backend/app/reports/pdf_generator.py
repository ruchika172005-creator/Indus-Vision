import os
from pathlib import Path
from typing import Dict, Any, List
import json

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether, HRFlowable
)
from reportlab.lib.units import inch

from app.core.config import settings
from app.core.logging import logger

class PDFReportGenerator:
    """
    Generates industrial quality assurance audit PDF inspection reports.
    """

    @staticmethod
    def generate_inspection_report(inspection_data: Dict[str, Any], output_path: str) -> str:
        """
        Builds a multi-section industrial QA report.
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()

        # Custom typography
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Heading1"],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#0B132B"),
            fontName="Helvetica-Bold"
        )
        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#475569")
        )
        section_style = ParagraphStyle(
            "SectionHeader",
            parent=styles["Heading2"],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#1E293B"),
            fontName="Helvetica-Bold",
            spaceBefore=10,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            "BodyDark",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#1E293B")
        )
        bullet_style = ParagraphStyle(
            "BulletText",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155"),
            leftIndent=14
        )

        elements = []

        # 1. Header Banner
        header_data = [
            [
                Paragraph("<b>INDUSTRIAL QUALITY ASSURANCE REPORT</b>", title_style),
                Paragraph(f"<b>STATUS: {inspection_data.get('overall_decision', 'PASS')}</b>", ParagraphStyle(
                    "StatusH",
                    fontSize=13,
                    textColor=colors.HexColor("#EF4444" if inspection_data.get('overall_decision') == 'FAIL' else "#10B981" if inspection_data.get('overall_decision') == 'PASS' else "#F59E0B"),
                    alignment=2,
                    fontName="Helvetica-Bold"
                ))
            ],
            [
                Paragraph(f"Inspection Code: <b>{inspection_data.get('inspection_code', 'QA-8821')}</b> | Date: {inspection_data.get('timestamp', '')[:19]}", subtitle_style),
                Paragraph(f"Severity: <b>{inspection_data.get('max_severity', 'LOW')}</b>", ParagraphStyle("SevH", fontSize=9, alignment=2, textColor=colors.HexColor("#475569")))
            ]
        ]
        header_table = Table(header_data, colWidths=[4.0 * inch, 3.2 * inch])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 8))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563EB"), spaceBefore=2, spaceAfter=10))

        # 2. Metadata Grid
        meta_table_data = [
            [
                Paragraph(f"<b>Component:</b> {inspection_data.get('product_name', 'Steel Plate')}", body_style),
                Paragraph(f"<b>Category:</b> {inspection_data.get('product_category', 'Cold Rolled Steel')}", body_style)
            ],
            [
                Paragraph(f"<b>Detection Model:</b> {inspection_data.get('model_name', 'YOLOv8n-NEU-DET')}", body_style),
                Paragraph(f"<b>Inference Latency:</b> {inspection_data.get('inference_time_ms', 0)} ms", body_style)
            ],
            [
                Paragraph(f"<b>Total Anomalies:</b> {inspection_data.get('total_defects', 0)}", body_style),
                Paragraph(f"<b>Inspection Source:</b> {inspection_data.get('inference_source', 'Real YOLOv8 Inference')}", body_style)
            ]
        ]
        meta_table = Table(meta_table_data, colWidths=[3.6 * inch, 3.6 * inch])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 12))

        # 3. Annotated Optical Inspection Image
        img_path = inspection_data.get("annotated_image_path") or inspection_data.get("original_image_path")
        if img_path and Path(img_path).exists():
            elements.append(Paragraph("<b>OPTICAL INSPECTION & DEFECT LOCALIZATION</b>", section_style))
            try:
                rl_img = RLImage(img_path, width=4.5 * inch, height=3.0 * inch)
                elements.append(rl_img)
                elements.append(Spacer(1, 10))
            except Exception as e:
                logger.warning(f"Could not embed image into PDF: {e}")

        # 4. Detected Defects Table
        defects = inspection_data.get("defects", [])
        if defects:
            elements.append(Paragraph("<b>DEFECT TELEMETRY & QUANTITATIVE METRICS</b>", section_style))
            defect_headers = ["Defect Name", "Confidence", "Bounding Box [x1,y1,x2,y2]", "Area %", "Severity"]
            table_rows = [defect_headers]

            for d in defects:
                bbox_str = f"[{int(d['bbox'][0])}, {int(d['bbox'][1])}, {int(d['bbox'][2])}, {int(d['bbox'][3])}]"
                table_rows.append([
                    d.get("defect_name", "Unknown"),
                    f"{int(d.get('confidence', 0) * 100)}%",
                    bbox_str,
                    f"{d.get('area_ratio', 0):.2%}",
                    d.get("severity_level", "LOW")
                ])

            defect_table = Table(table_rows, colWidths=[1.8 * inch, 1.0 * inch, 2.4 * inch, 1.0 * inch, 1.0 * inch])
            defect_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1E293B")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(defect_table)
            elements.append(Spacer(1, 12))

        # 5. Multimodal AI Explanation & Corrective Actions
        explanation = inspection_data.get("explanation") or {}
        elements.append(Paragraph("<b>MULTIMODAL AI DEFECT INTERPRETATION & ROOT CAUSES</b>", section_style))

        provider_name = explanation.get("provider_used", "Rule-Based Industrial Engine")
        elements.append(Paragraph(f"<b>AI Engine:</b> {provider_name}", subtitle_style))
        elements.append(Spacer(1, 4))

        desc = explanation.get("description", "No visual defects detected on part surface.")
        loc = explanation.get("location", "Full surface")
        elements.append(Paragraph(f"<b>Observed Characteristics:</b> {desc} (Location: {loc})", body_style))
        elements.append(Spacer(1, 6))

        # Possible causes
        causes = explanation.get("possible_causes", [])
        if causes:
            elements.append(Paragraph("<b>Potential Root Causes (Hypotheses):</b>", body_style))
            for c in causes:
                elements.append(Paragraph(f"• {c}", bullet_style))
            elements.append(Spacer(1, 6))

        # Corrective Actions
        actions = explanation.get("recommended_actions", [])
        if actions:
            elements.append(Paragraph("<b>Recommended Corrective & Preventative Actions:</b>", body_style))
            for a in actions:
                elements.append(Paragraph(f"• {a}", bullet_style))
            elements.append(Spacer(1, 8))

        # Quality Summary
        q_sum = explanation.get("quality_summary")
        if q_sum:
            summary_p = Paragraph(f"<b>Engineering Disposition:</b> {q_sum}", ParagraphStyle(
                "SummaryBox",
                parent=body_style,
                fontSize=9,
                textColor=colors.HexColor("#0F172A")
            ))
            sum_table = Table([[summary_p]], colWidths=[7.2 * inch])
            sum_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#93C5FD")),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(sum_table)

        # 6. Audit Footer
        elements.append(Spacer(1, 16))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E1"), spaceBefore=4, spaceAfter=6))
        elements.append(Paragraph(
            "IndusVision — Automated Computer Vision & Multimodal VLM Quality Assurance System | Compliance: ISO 9001 / ASTM Surface Standards | Confidential",
            ParagraphStyle("Footer", fontSize=7, textColor=colors.HexColor("#94A3B8"), alignment=1)
        ))

        doc.build(elements)
        logger.info(f"Generated PDF inspection report at: {output_path}")
        return output_path

pdf_report_generator = PDFReportGenerator()
