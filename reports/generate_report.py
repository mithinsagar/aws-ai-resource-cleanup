"""
Cleanup report orchestrator. Delegates to PDF and CSV exporters.
Author: Mithin Sagar S
"""

import os
from datetime import datetime
from utils.logger import log
from reports.pdf_report import PDFReport
from reports.csv_export import CSVExport

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")


class ReportGenerator:
    def __init__(self, output_dir=None):
        self.output_dir = output_dir or OUTPUT_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def generate(self, idle_results, fmt="both"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log.info("Generating report (format=%s)...", fmt)

        paths = []

        if fmt in ("pdf", "both"):
            pdf_path = os.path.join(self.output_dir, f"cleanup_report_{timestamp}.pdf")
            pdf = PDFReport()
            pdf.build(idle_results, pdf_path)
            paths.append(pdf_path)
            log.info("PDF report saved to %s", pdf_path)

        if fmt in ("csv", "both"):
            csv_path = os.path.join(self.output_dir, f"cleanup_report_{timestamp}.csv")
            exporter = CSVExport()
            exporter.export(idle_results, csv_path)
            paths.append(csv_path)
            log.info("CSV report saved to %s", csv_path)

        return paths
