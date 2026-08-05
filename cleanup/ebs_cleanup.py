"""
EBS snapshot cleanup execution.
Author: Mithin Sagar S
"""

from utils.logger import log


class EBSCleanup:
    def __init__(self, ebs_manager, max_age_days=90):
        self.ebs = ebs_manager
        self.max_age_days = max_age_days

    def execute(self, dry_run=True):
        log.info("Running EBS snapshot cleanup (dry_run=%s)...", dry_run)
        old_snapshots = self.ebs.list_old_snapshots(self.max_age_days)
        results = []

        for snap in old_snapshots:
            sid = snap["snapshot_id"]
            result = self.ebs.delete_snapshot(sid, dry_run=dry_run)
            result["service"] = "ebs"
            result["resource_type"] = "snapshot"
            result["age_days"] = snap["age_days"]
            results.append(result)

        log.info("EBS cleanup: %d snapshots processed", len(results))
        return results
