"""
RDS instance cleanup execution.
Author: Mithin Sagar S
"""

from utils.logger import log


class RDSCleanup:
    def __init__(self, rds_manager):
        self.rds = rds_manager

    def execute(self, dry_run=True):
        log.info("Running RDS cleanup (dry_run=%s)...", dry_run)
        stopped = self.rds.list_stopped_instances()
        results = []

        for db in stopped:
            db_id = db["db_instance_id"]
            result = self.rds.delete_instance(db_id, dry_run=dry_run)
            result["service"] = "rds"
            result["resource_type"] = "db_instance"
            results.append(result)

        log.info("RDS cleanup: %d instances processed", len(results))
        return results
