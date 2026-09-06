"""
Unit tests for the cleanup engine.
Author: Mithin Sagar S
"""

import unittest
from unittest.mock import MagicMock


class TestCleanupEngine(unittest.TestCase):
    def setUp(self):
        self.ec2_cleanup = MagicMock()
        self.ebs_cleanup = MagicMock()
        self.s3_cleanup = MagicMock()
        self.rds_cleanup = MagicMock()

    def test_full_cleanup_dry_run(self):
        from cleanup.cleanup_engine import CleanupEngine

        self.ec2_cleanup.execute.return_value = [
            {"action": "dry_run", "instance_id": "i-123", "service": "ec2"}
        ]
        self.ebs_cleanup.execute.return_value = []
        self.s3_cleanup.execute.return_value = []
        self.rds_cleanup.execute.return_value = []

        engine = CleanupEngine(
            self.ec2_cleanup, self.ebs_cleanup, self.s3_cleanup, self.rds_cleanup,
            dry_run=True,
        )
        results = engine.run_full_cleanup()

        self.assertEqual(len(results), 1)
        self.ec2_cleanup.execute.assert_called_once_with(dry_run=True)

    def test_get_summary(self):
        from cleanup.cleanup_engine import CleanupEngine

        self.ec2_cleanup.execute.return_value = [
            {"service": "ec2", "action": "dry_run"},
            {"service": "ec2", "action": "dry_run"},
        ]
        self.ebs_cleanup.execute.return_value = [
            {"service": "ebs", "action": "dry_run"},
        ]
        self.s3_cleanup.execute.return_value = []
        self.rds_cleanup.execute.return_value = []

        engine = CleanupEngine(
            self.ec2_cleanup, self.ebs_cleanup, self.s3_cleanup, self.rds_cleanup,
            dry_run=True,
        )
        engine.run_full_cleanup()
        summary = engine.get_summary()

        self.assertEqual(summary["total_actions"], 3)
        self.assertEqual(summary["by_service"]["ec2"], 2)
        self.assertEqual(summary["by_service"]["ebs"], 1)

    def test_full_cleanup_skips_dynamodb_when_not_provided(self):
        from cleanup.cleanup_engine import CleanupEngine

        self.ec2_cleanup.execute.return_value = []
        self.ebs_cleanup.execute.return_value = []
        self.s3_cleanup.execute.return_value = []
        self.rds_cleanup.execute.return_value = []

        engine = CleanupEngine(
            self.ec2_cleanup, self.ebs_cleanup, self.s3_cleanup, self.rds_cleanup,
            dry_run=True,
        )
        results = engine.run_full_cleanup()

        self.assertEqual(results, [])

    def test_full_cleanup_includes_dynamodb_when_provided(self):
        from cleanup.cleanup_engine import CleanupEngine

        self.ec2_cleanup.execute.return_value = []
        self.ebs_cleanup.execute.return_value = []
        self.s3_cleanup.execute.return_value = []
        self.rds_cleanup.execute.return_value = []
        dynamodb_cleanup = MagicMock()
        dynamodb_cleanup.execute.return_value = [
            {"service": "dynamodb", "action": "dry_run", "table_name": "sessions"}
        ]

        engine = CleanupEngine(
            self.ec2_cleanup, self.ebs_cleanup, self.s3_cleanup, self.rds_cleanup,
            dynamodb_cleanup=dynamodb_cleanup, dry_run=True,
        )
        results = engine.run_full_cleanup()

        self.assertEqual(len(results), 1)
        dynamodb_cleanup.execute.assert_called_once_with(dry_run=True)


if __name__ == "__main__":
    unittest.main()
