"""
Project-wide constants.
Author: Mithin Sagar S
"""

PROJECT_NAME = "AWS AI Resource Cleanup"
VERSION = "1.0.0"
AUTHOR = "Mithin Sagar S"

RESOURCE_TYPES = [
    "ec2_instance",
    "ebs_snapshot",
    "security_group",
    "iam_user",
    "cloudwatch_log_group",
    "key_pair",
    "s3_bucket",
    "rds_instance",
]

ACTIONS = {
    "terminate": "Terminate the resource permanently",
    "delete": "Delete the resource permanently",
    "stop": "Stop the resource (keep data)",
    "tag": "Tag the resource for review",
    "notify": "Send a notification without taking action",
}

PROTECTED_TAGS = ["do-not-delete", "production", "critical", "keep"]

DEFAULT_THRESHOLDS = {
    "ec2_stopped_days": 90,
    "ebs_snapshot_days": 90,
    "iam_inactive_days": 180,
    "cloudwatch_log_days": 365,
    "key_pair_days": 90,
}
