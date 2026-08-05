"""
Unit tests for S3 manager.
Author: Mithin Sagar S
"""

import unittest
from unittest.mock import MagicMock
from datetime import datetime, timezone


class TestS3Manager(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock()
        self.mock_client = MagicMock()
        self.mock_resource = MagicMock()
        self.mock_session.client.return_value = self.mock_client
        self.mock_session.resource.return_value = self.mock_resource

    def test_list_buckets(self):
        from aws.s3_manager import S3Manager

        self.mock_client.list_buckets.return_value = {
            "Buckets": [
                {"Name": "test-bucket", "CreationDate": datetime(2024, 1, 1, tzinfo=timezone.utc)},
                {"Name": "prod-bucket", "CreationDate": datetime(2023, 6, 15, tzinfo=timezone.utc)},
            ]
        }

        mgr = S3Manager(self.mock_session)
        result = mgr.list_buckets()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["name"], "test-bucket")

    def test_delete_bucket_dry_run(self):
        from aws.s3_manager import S3Manager

        mgr = S3Manager(self.mock_session)
        result = mgr.delete_bucket("test-bucket", dry_run=True)

        self.assertEqual(result["action"], "dry_run")


if __name__ == "__main__":
    unittest.main()
