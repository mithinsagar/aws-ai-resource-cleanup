"""
EC2 instance cleanup execution.
Author: Mithin Sagar S
"""

from utils.logger import log


class EC2Cleanup:
    def __init__(self, ec2_manager, max_age_days=90):
        self.ec2 = ec2_manager
        self.max_age_days = max_age_days

    def execute(self, dry_run=True):
        log.info("Running EC2 cleanup (dry_run=%s)...", dry_run)
        stopped = self.ec2.list_stopped_instances(self.max_age_days)
        results = []

        for instance in stopped:
            iid = instance["instance_id"]
            result = self.ec2.terminate_instance(iid, dry_run=dry_run)
            result["service"] = "ec2"
            result["resource_type"] = "instance"
            result["age_days"] = instance["age_days"]
            results.append(result)

        log.info("EC2 cleanup: %d instances processed", len(results))
        return results
