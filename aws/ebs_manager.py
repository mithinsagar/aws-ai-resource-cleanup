"""
EBS snapshot discovery and management.
Author: Mithin Sagar S
"""

from utils.logger import log
from utils.helper import days_since, format_timestamp, has_protected_tag
from utils.constants import PROTECTED_TAGS


class EBSManager:
    def __init__(self, aws_session):
        self.client = aws_session.client("ec2")

    def list_snapshots(self):
        log.info("Fetching EBS snapshots...")
        snapshots = self.client.describe_snapshots(OwnerIds=["self"])["Snapshots"]
        log.info("Found %d EBS snapshots", len(snapshots))
        return snapshots

    def list_old_snapshots(self, max_age_days=90):
        all_snapshots = self.list_snapshots()
        old = []
        for snap in all_snapshots:
            if has_protected_tag(snap.get("Tags", []), PROTECTED_TAGS):
                log.info("Skipping protected snapshot %s", snap["SnapshotId"])
                continue
            age = days_since(snap.get("StartTime"))
            if age >= max_age_days:
                old.append(
                    {
                        "snapshot_id": snap["SnapshotId"],
                        "volume_id": snap.get("VolumeId", "N/A"),
                        "start_time": format_timestamp(snap.get("StartTime")),
                        "age_days": age,
                        "size_gb": snap.get("VolumeSize", 0),
                        "description": snap.get("Description", ""),
                    }
                )
        log.info(
            "Found %d snapshots older than %d days", len(old), max_age_days
        )
        return old

    def delete_snapshot(self, snapshot_id, dry_run=True):
        if dry_run:
            log.info("[DRY RUN] Would delete EBS snapshot: %s", snapshot_id)
            return {"action": "dry_run", "snapshot_id": snapshot_id}
        log.warning("Deleting EBS snapshot: %s", snapshot_id)
        self.client.delete_snapshot(SnapshotId=snapshot_id)
        return {"action": "deleted", "snapshot_id": snapshot_id}
