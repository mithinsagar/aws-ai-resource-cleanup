"""
DynamoDB table discovery and management.
Author: Mithin Sagar S
"""

from utils.logger import log


class DynamoDBManager:
    def __init__(self, aws_session):
        self.client = aws_session.client("dynamodb")

    def list_tables(self):
        log.info("Fetching DynamoDB tables...")
        table_names = []
        paginator = self.client.get_paginator("list_tables")
        for page in paginator.paginate():
            table_names.extend(page["TableNames"])
        log.info("Found %d DynamoDB tables", len(table_names))
        return [self.describe_table(name) for name in table_names]

    def describe_table(self, table_name):
        table = self.client.describe_table(TableName=table_name)["Table"]
        return {
            "table_name": table["TableName"],
            "status": table["TableStatus"],
            "item_count": table.get("ItemCount", 0),
            "size_bytes": table.get("TableSizeBytes", 0),
            "billing_mode": table.get("BillingModeSummary", {}).get(
                "BillingMode", "PROVISIONED"
            ),
        }

    def list_empty_tables(self):
        """Tables DynamoDB currently reports as having zero items.

        ItemCount comes from DescribeTable, which DynamoDB only refreshes on
        roughly a 6-hour cycle, so a table created or emptied recently may
        still show a stale non-zero count for a while. Treat this as a
        candidate list to review, not a live count.
        """
        tables = self.list_tables()
        empty = [t for t in tables if t["item_count"] == 0]
        log.info("Found %d empty DynamoDB tables", len(empty))
        return empty

    def delete_table(self, table_name, dry_run=True):
        if dry_run:
            log.info("[DRY RUN] Would delete DynamoDB table: %s", table_name)
            return {"action": "dry_run", "table_name": table_name}
        log.warning("Deleting DynamoDB table: %s", table_name)
        self.client.delete_table(TableName=table_name)
        return {"action": "deleted", "table_name": table_name}
