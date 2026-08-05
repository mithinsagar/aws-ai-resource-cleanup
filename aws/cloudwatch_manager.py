"""
CloudWatch log group discovery and management.
Author: Mithin Sagar S
"""

import datetime
from dateutil import tz
from utils.logger import log


class CloudWatchManager:
    def __init__(self, aws_session):
        self.client = aws_session.client("logs")

    def list_log_groups(self):
        log.info("Fetching CloudWatch log groups...")
        groups = []
        paginator = self.client.get_paginator("describe_log_groups")
        for page in paginator.paginate():
            for group in page.get("logGroups", []):
                groups.append(group)
        log.info("Found %d CloudWatch log groups", len(groups))
        return groups

    def list_stale_log_groups(self, max_age_days=365):
        all_groups = self.list_log_groups()
        cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(
            days=max_age_days
        )
        stale = []
        for group in all_groups:
            last_ingestion = group.get("lastIngestionTime")
            if last_ingestion is None:
                stale.append(
                    {
                        "log_group_name": group["logGroupName"],
                        "retention_days": group.get("retentionInDays", "Never"),
                        "stored_bytes": group.get("storedBytes", 0),
                        "last_ingestion": "Never",
                    }
                )
                continue
            last_date = datetime.datetime.fromtimestamp(
                last_ingestion / 1000, tz=tz.UTC
            )
            if last_date < cutoff:
                stale.append(
                    {
                        "log_group_name": group["logGroupName"],
                        "retention_days": group.get("retentionInDays", "Never"),
                        "stored_bytes": group.get("storedBytes", 0),
                        "last_ingestion": last_date.strftime("%Y-%m-%d %H:%M:%S UTC"),
                    }
                )
        log.info(
            "Found %d stale log groups (no ingestion for %d+ days)",
            len(stale),
            max_age_days,
        )
        return stale

    def delete_log_group(self, log_group_name, dry_run=True):
        if dry_run:
            log.info(
                "[DRY RUN] Would delete log group: %s", log_group_name
            )
            return {"action": "dry_run", "log_group": log_group_name}
        log.warning("Deleting log group: %s", log_group_name)
        self.client.delete_log_group(logGroupName=log_group_name)
        return {"action": "deleted", "log_group": log_group_name}
