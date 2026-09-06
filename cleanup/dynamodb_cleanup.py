"""
DynamoDB table cleanup execution.
Author: Mithin Sagar S
"""

from utils.logger import log


class DynamoDBCleanup:
    def __init__(self, dynamodb_manager):
        self.dynamodb = dynamodb_manager

    def execute(self, dry_run=True):
        log.info("Running DynamoDB cleanup (dry_run=%s)...", dry_run)
        empty_tables = self.dynamodb.list_empty_tables()
        results = []

        for table in empty_tables:
            name = table["table_name"]
            result = self.dynamodb.delete_table(name, dry_run=dry_run)
            result["service"] = "dynamodb"
            result["resource_type"] = "table"
            results.append(result)

        log.info("DynamoDB cleanup: %d empty tables processed", len(results))
        return results
