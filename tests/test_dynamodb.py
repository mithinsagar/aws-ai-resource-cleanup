"""
Unit tests for DynamoDB manager.
Author: Mithin Sagar S
"""

import unittest
from unittest.mock import MagicMock


class TestDynamoDBManager(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock()
        self.mock_client = MagicMock()
        self.mock_session.client.return_value = self.mock_client

    def test_list_tables(self):
        from aws.dynamodb_manager import DynamoDBManager

        paginator = MagicMock()
        paginator.paginate.return_value = [{"TableNames": ["orders", "sessions"]}]
        self.mock_client.get_paginator.return_value = paginator
        self.mock_client.describe_table.side_effect = [
            {"Table": {"TableName": "orders", "TableStatus": "ACTIVE", "ItemCount": 42, "TableSizeBytes": 1024}},
            {"Table": {"TableName": "sessions", "TableStatus": "ACTIVE", "ItemCount": 0, "TableSizeBytes": 0}},
        ]

        mgr = DynamoDBManager(self.mock_session)
        result = mgr.list_tables()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["table_name"], "orders")
        self.assertEqual(result[0]["item_count"], 42)
        self.assertEqual(result[1]["billing_mode"], "PROVISIONED")

    def test_list_empty_tables_filters_by_item_count(self):
        from aws.dynamodb_manager import DynamoDBManager

        paginator = MagicMock()
        paginator.paginate.return_value = [{"TableNames": ["orders", "sessions"]}]
        self.mock_client.get_paginator.return_value = paginator
        self.mock_client.describe_table.side_effect = [
            {"Table": {"TableName": "orders", "TableStatus": "ACTIVE", "ItemCount": 42}},
            {"Table": {"TableName": "sessions", "TableStatus": "ACTIVE", "ItemCount": 0}},
        ]

        mgr = DynamoDBManager(self.mock_session)
        empty = mgr.list_empty_tables()

        self.assertEqual(len(empty), 1)
        self.assertEqual(empty[0]["table_name"], "sessions")

    def test_delete_table_dry_run(self):
        from aws.dynamodb_manager import DynamoDBManager

        mgr = DynamoDBManager(self.mock_session)
        result = mgr.delete_table("sessions", dry_run=True)

        self.assertEqual(result["action"], "dry_run")
        self.mock_client.delete_table.assert_not_called()

    def test_delete_table_live(self):
        from aws.dynamodb_manager import DynamoDBManager

        mgr = DynamoDBManager(self.mock_session)
        result = mgr.delete_table("sessions", dry_run=False)

        self.assertEqual(result["action"], "deleted")
        self.mock_client.delete_table.assert_called_once_with(TableName="sessions")


class TestDynamoDBCleanup(unittest.TestCase):
    def test_execute_deletes_only_empty_tables(self):
        from cleanup.dynamodb_cleanup import DynamoDBCleanup

        mock_manager = MagicMock()
        mock_manager.list_empty_tables.return_value = [{"table_name": "sessions"}]
        mock_manager.delete_table.return_value = {"action": "dry_run", "table_name": "sessions"}

        cleanup = DynamoDBCleanup(mock_manager)
        results = cleanup.execute(dry_run=True)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["service"], "dynamodb")
        self.assertEqual(results[0]["resource_type"], "table")
        mock_manager.delete_table.assert_called_once_with("sessions", dry_run=True)


if __name__ == "__main__":
    unittest.main()
