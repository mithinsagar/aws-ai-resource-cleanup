"""
RDS instance discovery and management.
Author: Mithin Sagar S
"""

from utils.logger import log
from utils.helper import days_since, format_timestamp


class RDSManager:
    def __init__(self, aws_session):
        self.client = aws_session.client("rds")

    def list_instances(self):
        log.info("Fetching RDS instances...")
        instances = []
        paginator = self.client.get_paginator("describe_db_instances")
        for page in paginator.paginate():
            for db in page["DBInstances"]:
                instances.append(
                    {
                        "db_instance_id": db["DBInstanceIdentifier"],
                        "engine": db["Engine"],
                        "status": db["DBInstanceStatus"],
                        "instance_class": db["DBInstanceClass"],
                        "create_time": format_timestamp(db.get("InstanceCreateTime")),
                        "multi_az": db.get("MultiAZ", False),
                    }
                )
        log.info("Found %d RDS instances", len(instances))
        return instances

    def list_stopped_instances(self):
        all_instances = self.list_instances()
        stopped = [i for i in all_instances if i["status"] == "stopped"]
        log.info("Found %d stopped RDS instances", len(stopped))
        return stopped

    def delete_instance(self, db_instance_id, dry_run=True):
        if dry_run:
            log.info(
                "[DRY RUN] Would delete RDS instance: %s", db_instance_id
            )
            return {"action": "dry_run", "db_instance_id": db_instance_id}
        log.warning("Deleting RDS instance: %s", db_instance_id)
        self.client.delete_db_instance(
            DBInstanceIdentifier=db_instance_id,
            SkipFinalSnapshot=True,
        )
        return {"action": "deleted", "db_instance_id": db_instance_id}
