"""
EC2 instance discovery and management.
Author: Mithin Sagar S
"""

from utils.logger import log
from utils.helper import days_since, format_timestamp, has_protected_tag
from utils.constants import PROTECTED_TAGS


class EC2Manager:
    def __init__(self, aws_session):
        self.client = aws_session.client("ec2")

    def list_all_instances(self):
        log.info("Fetching all EC2 instances...")
        instances = []
        paginator = self.client.get_paginator("describe_instances")
        for page in paginator.paginate():
            for reservation in page["Reservations"]:
                for instance in reservation["Instances"]:
                    instances.append(instance)
        log.info("Found %d EC2 instances", len(instances))
        return instances

    def list_stopped_instances(self, max_age_days=90):
        all_instances = self.list_all_instances()
        stopped = []
        for inst in all_instances:
            if inst["State"]["Name"] != "stopped":
                continue
            if has_protected_tag(inst.get("Tags", []), PROTECTED_TAGS):
                log.info(
                    "Skipping protected instance %s", inst["InstanceId"]
                )
                continue
            age = days_since(inst.get("LaunchTime"))
            if age >= max_age_days:
                stopped.append(
                    {
                        "instance_id": inst["InstanceId"],
                        "state": inst["State"]["Name"],
                        "launch_time": format_timestamp(inst.get("LaunchTime")),
                        "age_days": age,
                        "instance_type": inst.get("InstanceType", "unknown"),
                        "tags": inst.get("Tags", []),
                    }
                )
        log.info(
            "Found %d stopped instances older than %d days",
            len(stopped),
            max_age_days,
        )
        return stopped

    def terminate_instance(self, instance_id, dry_run=True):
        if dry_run:
            log.info("[DRY RUN] Would terminate EC2 instance: %s", instance_id)
            return {"action": "dry_run", "instance_id": instance_id}
        log.warning("Terminating EC2 instance: %s", instance_id)
        response = self.client.terminate_instances(InstanceIds=[instance_id])
        return response
