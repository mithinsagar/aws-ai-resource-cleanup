"""
Configuration loader for AWS AI Resource Cleanup.
Author: Mithin Sagar S
"""

import os
import yaml
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "config")


def load_settings():
    path = os.path.join(CONFIG_DIR, "settings.yaml")
    with open(path, "r") as f:
        return yaml.safe_load(f)


def load_cleanup_rules():
    path = os.path.join(CONFIG_DIR, "cleanup_rules.json")
    with open(path, "r") as f:
        return json.load(f)


SETTINGS = load_settings()
CLEANUP_RULES = load_cleanup_rules()

AWS_PROFILE = SETTINGS.get("aws", {}).get("profile", "default")
AWS_REGION = SETTINGS.get("aws", {}).get("region", "us-east-1")
DRY_RUN = SETTINGS.get("cleanup", {}).get("dry_run", True)
LOG_LEVEL = SETTINGS.get("logging", {}).get("level", "INFO")
DASHBOARD_PORT = SETTINGS.get("dashboard", {}).get("port", 5000)
