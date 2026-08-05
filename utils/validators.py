"""
Input validation utilities.
Author: Mithin Sagar S
"""

import re


def validate_instance_id(instance_id):
    pattern = r"^i-[0-9a-f]{8,17}$"
    return bool(re.match(pattern, instance_id))


def validate_snapshot_id(snapshot_id):
    pattern = r"^snap-[0-9a-f]{8,17}$"
    return bool(re.match(pattern, snapshot_id))


def validate_security_group_id(sg_id):
    pattern = r"^sg-[0-9a-f]{8,17}$"
    return bool(re.match(pattern, sg_id))


def validate_bucket_name(name):
    pattern = r"^[a-z0-9][a-z0-9.\-]{1,61}[a-z0-9]$"
    return bool(re.match(pattern, name))


def validate_region(region):
    pattern = r"^[a-z]{2}-[a-z]+-\d$"
    return bool(re.match(pattern, region))


def validate_threshold(value):
    return isinstance(value, (int, float)) and value > 0
