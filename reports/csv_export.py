"""
CSV export for cleanup results.
Author: Mithin Sagar S
"""

import csv
from utils.logger import log


class CSVExport:
    def export(self, idle_results, output_path):
        rows = []
        for category, items in idle_results.items():
            for item in items:
                row = {"category": category}
                row.update(item)
                rows.append(row)

        if not rows:
            log.info("No data to export.")
            return

        fieldnames = list(rows[0].keys())
        for row in rows[1:]:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)

        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

        log.info("CSV report exported: %s (%d rows)", output_path, len(rows))
