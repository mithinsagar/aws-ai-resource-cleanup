"""
IAM user discovery and management.
Author: Mithin Sagar S
"""

from utils.logger import log
from utils.helper import days_since, format_timestamp


class IAMManager:
    def __init__(self, aws_session):
        self.client = aws_session.client("iam")

    def list_users(self):
        log.info("Fetching IAM users...")
        users = []
        paginator = self.client.get_paginator("list_users")
        for page in paginator.paginate():
            for user in page["Users"]:
                users.append(user)
        log.info("Found %d IAM users", len(users))
        return users

    def list_inactive_users(self, max_inactive_days=180):
        all_users = self.list_users()
        inactive = []
        for user in all_users:
            last_used = user.get("PasswordLastUsed")
            age = days_since(last_used)
            if age >= max_inactive_days:
                inactive.append(
                    {
                        "user_name": user["UserName"],
                        "user_id": user["UserId"],
                        "create_date": format_timestamp(user.get("CreateDate")),
                        "last_used": format_timestamp(last_used),
                        "inactive_days": age,
                    }
                )
        log.info(
            "Found %d IAM users inactive for more than %d days",
            len(inactive),
            max_inactive_days,
        )
        return inactive

    def delete_user(self, user_name, dry_run=True):
        if dry_run:
            log.info("[DRY RUN] Would delete IAM user: %s", user_name)
            return {"action": "dry_run", "user_name": user_name}
        log.warning("Deleting IAM user: %s", user_name)
        try:
            self._detach_user_policies(user_name)
            self._delete_user_access_keys(user_name)
            self.client.delete_login_profile(UserName=user_name)
        except self.client.exceptions.NoSuchEntityException:
            pass
        self.client.delete_user(UserName=user_name)
        return {"action": "deleted", "user_name": user_name}

    def _detach_user_policies(self, user_name):
        policies = self.client.list_attached_user_policies(UserName=user_name)
        for policy in policies.get("AttachedPolicies", []):
            self.client.detach_user_policy(
                UserName=user_name, PolicyArn=policy["PolicyArn"]
            )

    def _delete_user_access_keys(self, user_name):
        keys = self.client.list_access_keys(UserName=user_name)
        for key in keys.get("AccessKeyMetadata", []):
            self.client.delete_access_key(
                UserName=user_name, AccessKeyId=key["AccessKeyId"]
            )
