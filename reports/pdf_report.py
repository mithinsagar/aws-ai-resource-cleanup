"""
PDF report generation using ReportLab.
Author: Mithin Sagar S
"""

from datetime import datetime
from utils.logger import log

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class PDFReport:
    def build(self, idle_results, output_path):
        if not REPORTLAB_AVAILABLE:
            log.warning(
                "reportlab is not installed. Run: pip install reportlab"
            )
            return

        doc = SimpleDocTemplate(output_path, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("AWS AI Resource Cleanup Report", styles["Title"]))
        elements.append(Paragraph(f"Author: Mithin Sagar S", styles["Normal"]))
        elements.append(
            Paragraph(
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                styles["Normal"],
            )
        )
        elements.append(Spacer(1, 20))

        for category, items in idle_results.items():
            elements.append(Paragraph(category.replace("_", " ").title(), styles["Heading2"]))

            if not items:
                elements.append(Paragraph("No idle resources detected.", styles["Normal"]))
                elements.append(Spacer(1, 12))
                continue

            headers = list(items[0].keys())
            table_data = [headers]
            for item in items:
                row = [str(item.get(h, "")) for h in headers]
                table_data.append(row)

            table = Table(table_data, repeatRows=1)
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#232f3e")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTSIZE", (0, 0), (-1, -1), 7),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
                    ]
                )
            )
            elements.append(table)
            elements.append(Spacer(1, 16))

        doc.build(elements)
        log.info("PDF report generated: %s", output_path)
