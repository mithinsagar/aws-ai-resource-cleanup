"""
S3 bucket cleanup execution.
Author: Mithin Sagar S
"""

from utils.logger import log


class S3Cleanup:
    def __init__(self, s3_manager):
        self.s3 = s3_manager

    def execute(self, dry_run=True):
        log.info("Running S3 bucket cleanup (dry_run=%s)...", dry_run)
        empty_buckets = self.s3.list_empty_buckets()
        results = []

        for bucket in empty_buckets:
            name = bucket["name"]
            result = self.s3.delete_bucket(name, dry_run=dry_run)
            result["service"] = "s3"
            result["resource_type"] = "bucket"
            results.append(result)

        log.info("S3 cleanup: %d empty buckets processed", len(results))
        return results
