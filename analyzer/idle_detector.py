"""
Detects idle and underutilized AWS resources.
Author: Mithin Sagar S
"""

from utils.logger import log


class IdleDetector:
    def __init__(self, ec2_mgr, ebs_mgr, iam_mgr, cw_mgr, rules):
        self.ec2 = ec2_mgr
        self.ebs = ebs_mgr
        self.iam = iam_mgr
        self.cw = cw_mgr
        self.rules = rules

    def detect_all(self):
        log.info("Running idle resource detection across all services...")
        results = {
            "ec2_instances": [],
            "ebs_snapshots": [],
            "iam_users": [],
            "cloudwatch_log_groups": [],
        }

        for rule in self.rules:
            rtype = rule["resource_type"]
            max_age = rule.get("max_age_days", 90)

            if rtype == "ec2_instance":
                results["ec2_instances"] = self.ec2.list_stopped_instances(max_age)
            elif rtype == "ebs_snapshot":
                results["ebs_snapshots"] = self.ebs.list_old_snapshots(max_age)
            elif rtype == "iam_user":
                results["iam_users"] = self.iam.list_inactive_users(max_age)
            elif rtype == "cloudwatch_log_group":
                results["cloudwatch_log_groups"] = self.cw.list_stale_log_groups(
                    max_age
                )

        total = sum(len(v) for v in results.values())
        log.info("Idle detection complete. %d resources flagged.", total)
        return results

    def summary(self, results):
        lines = ["Idle Resource Detection Summary", "=" * 40]
        for category, items in results.items():
            lines.append(f"  {category}: {len(items)} resource(s) flagged")
        lines.append("=" * 40)
        return "\n".join(lines)
