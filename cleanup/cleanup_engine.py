"""
Central cleanup orchestrator that coordinates all service-specific cleanups.
Author: Mithin Sagar S
"""

from datetime import datetime
from utils.logger import log


class CleanupEngine:
    def __init__(self, ec2_cleanup, ebs_cleanup, s3_cleanup, rds_cleanup, dry_run=True):
        self.ec2_cleanup = ec2_cleanup
        self.ebs_cleanup = ebs_cleanup
        self.s3_cleanup = s3_cleanup
        self.rds_cleanup = rds_cleanup
        self.dry_run = dry_run
        self.results = []

    def run_full_cleanup(self):
        log.info(
            "Starting full cleanup (dry_run=%s) at %s",
            self.dry_run,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        ec2_results = self.ec2_cleanup.execute(dry_run=self.dry_run)
        self.results.extend(ec2_results)

        ebs_results = self.ebs_cleanup.execute(dry_run=self.dry_run)
        self.results.extend(ebs_results)

        s3_results = self.s3_cleanup.execute(dry_run=self.dry_run)
        self.results.extend(s3_results)

        rds_results = self.rds_cleanup.execute(dry_run=self.dry_run)
        self.results.extend(rds_results)

        log.info("Cleanup complete. %d actions taken.", len(self.results))
        return self.results

    def get_summary(self):
        summary = {
            "total_actions": len(self.results),
            "dry_run": self.dry_run,
            "by_service": {},
            "timestamp": datetime.now().isoformat(),
        }
        for result in self.results:
            service = result.get("service", "unknown")
            if service not in summary["by_service"]:
                summary["by_service"][service] = 0
            summary["by_service"][service] += 1
        return summary
