"""
S3 bucket discovery and management.
Author: Mithin Sagar S
"""

from utils.logger import log
from utils.helper import days_since, format_timestamp


class S3Manager:
    def __init__(self, aws_session):
        self.client = aws_session.client("s3")
        self.resource = aws_session.resource("s3")

    def list_buckets(self):
        log.info("Fetching S3 buckets...")
        response = self.client.list_buckets()
        buckets = []
        for bucket in response.get("Buckets", []):
            buckets.append(
                {
                    "name": bucket["Name"],
                    "creation_date": format_timestamp(bucket.get("CreationDate")),
                }
            )
        log.info("Found %d S3 buckets", len(buckets))
        return buckets

    def get_bucket_size(self, bucket_name):
        try:
            total_size = 0
            total_objects = 0
            bucket = self.resource.Bucket(bucket_name)
            for obj in bucket.objects.all():
                total_size += obj.size
                total_objects += 1
            return {"size_bytes": total_size, "object_count": total_objects}
        except Exception as e:
            log.error("Error getting size for bucket %s: %s", bucket_name, e)
            return {"size_bytes": 0, "object_count": 0}

    def list_empty_buckets(self):
        buckets = self.list_buckets()
        empty = []
        for bucket in buckets:
            info = self.get_bucket_size(bucket["name"])
            if info["object_count"] == 0:
                empty.append(bucket)
        log.info("Found %d empty S3 buckets", len(empty))
        return empty

    def delete_bucket(self, bucket_name, dry_run=True):
        if dry_run:
            log.info("[DRY RUN] Would delete S3 bucket: %s", bucket_name)
            return {"action": "dry_run", "bucket": bucket_name}
        log.warning("Deleting S3 bucket: %s", bucket_name)
        bucket = self.resource.Bucket(bucket_name)
        bucket.objects.all().delete()
        bucket.delete()
        return {"action": "deleted", "bucket": bucket_name}
