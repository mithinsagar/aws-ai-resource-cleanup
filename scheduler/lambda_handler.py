"""
AWS Lambda handler for scheduled cleanup execution.
Deploy this as a Lambda function triggered by EventBridge.
Author: Mithin Sagar S
"""

import json
import boto3
import datetime
from dateutil import tz


def lambda_handler(event, context):
    print(f"Cleanup triggered at {datetime.datetime.now(tz.UTC).isoformat()}")
    print(f"Event: {json.dumps(event)}")

    ec2 = boto3.client("ec2")
    logs_client = boto3.client("logs")
    iam = boto3.client("iam")

    summary = {"timestamp": datetime.datetime.now(tz.UTC).isoformat(), "actions": []}

    summary["actions"].extend(_cleanup_stopped_ec2(ec2, max_age_days=90))
    summary["actions"].extend(_cleanup_old_snapshots(ec2, max_age_days=90))
    summary["actions"].extend(_cleanup_stale_logs(logs_client, max_age_days=365))
    summary["actions"].extend(_cleanup_unused_security_groups(ec2))

    print(f"Cleanup complete: {len(summary['actions'])} actions taken")
    return {"statusCode": 200, "body": json.dumps(summary, default=str)}


def _cleanup_stopped_ec2(ec2, max_age_days):
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=max_age_days)
    actions = []
    reservations = ec2.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["stopped"]}]
    )["Reservations"]

    for res in reservations:
        for inst in res["Instances"]:
            if inst["LaunchTime"] < cutoff:
                iid = inst["InstanceId"]
                print(f"Terminating stopped instance: {iid}")
                ec2.terminate_instances(InstanceIds=[iid])
                actions.append({"type": "ec2_terminate", "id": iid})
    return actions


def _cleanup_old_snapshots(ec2, max_age_days):
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=max_age_days)
    actions = []
    snapshots = ec2.describe_snapshots(OwnerIds=["self"])["Snapshots"]

    for snap in snapshots:
        if snap["StartTime"] < cutoff:
            sid = snap["SnapshotId"]
            print(f"Deleting old snapshot: {sid}")
            ec2.delete_snapshot(SnapshotId=sid)
            actions.append({"type": "ebs_delete", "id": sid})
    return actions


def _cleanup_stale_logs(logs_client, max_age_days):
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=max_age_days)
    actions = []
    paginator = logs_client.get_paginator("describe_log_groups")

    for page in paginator.paginate():
        for group in page.get("logGroups", []):
            last = group.get("lastIngestionTime")
            if last is None:
                continue
            last_date = datetime.datetime.fromtimestamp(last / 1000, tz=tz.UTC)
            if last_date < cutoff:
                name = group["logGroupName"]
                print(f"Deleting stale log group: {name}")
                logs_client.delete_log_group(logGroupName=name)
                actions.append({"type": "log_delete", "id": name})
    return actions


def _cleanup_unused_security_groups(ec2):
    actions = []
    sgs = ec2.describe_security_groups()["SecurityGroups"]

    for sg in sgs:
        if sg["GroupName"] == "default":
            continue
        nis = ec2.describe_network_interfaces(
            Filters=[{"Name": "group-id", "Values": [sg["GroupId"]]}]
        )["NetworkInterfaces"]
        if not nis:
            sg_id = sg["GroupId"]
            print(f"Deleting unused security group: {sg_id}")
            try:
                ec2.delete_security_group(GroupId=sg_id)
                actions.append({"type": "sg_delete", "id": sg_id})
            except Exception as e:
                print(f"Error deleting {sg_id}: {e}")
    return actions
