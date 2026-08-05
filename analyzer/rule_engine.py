"""
Configurable rule engine for cleanup decisions.
Author: Mithin Sagar S
"""

from utils.logger import log


class RuleEngine:
    def __init__(self, rules_config):
        self.rules = rules_config.get("rules", [])
        self.exclusions = rules_config.get("exclusions", {})

    def get_rules_for_type(self, resource_type):
        return [r for r in self.rules if r["resource_type"] == resource_type]

    def is_excluded(self, resource):
        excluded_tags = self.exclusions.get("tags", [])
        excluded_ids = self.exclusions.get("resource_ids", [])

        resource_id = resource.get(
            "instance_id",
            resource.get(
                "snapshot_id",
                resource.get("user_name", resource.get("log_group_name", "")),
            ),
        )
        if resource_id in excluded_ids:
            log.info("Resource %s is in exclusion list, skipping", resource_id)
            return True

        tags = resource.get("tags", [])
        for tag in tags:
            key = tag.get("Key", "").lower()
            value = tag.get("Value", "").lower()
            if key in excluded_tags or value in excluded_tags:
                log.info(
                    "Resource %s has excluded tag '%s', skipping",
                    resource_id,
                    key,
                )
                return True
        return False

    def evaluate(self, resource, rule):
        if self.is_excluded(resource):
            return False

        max_age = rule.get("max_age_days")
        if max_age is not None:
            age = resource.get("age_days", resource.get("inactive_days", 0))
            if age < max_age:
                return False

        condition = rule.get("condition")
        if condition == "unused":
            return True
        if condition == "stopped" and resource.get("state") == "stopped":
            return True
        if condition in ("age_exceeded", "stale", "inactive"):
            return True

        return False
