"""
Unit tests for EC2 manager and cleanup.
Author: Mithin Sagar S
"""

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone, timedelta


class TestEC2Manager(unittest.TestCase):
    def setUp(self):
        self.mock_session = MagicMock()
        self.mock_client = MagicMock()
        self.mock_session.client.return_value = self.mock_client

    def test_list_stopped_instances_returns_old_instances(self):
        from aws.ec2_manager import EC2Manager

        old_date = datetime.now(timezone.utc) - timedelta(days=120)
        self.mock_client.get_paginator.return_value.paginate.return_value = [
            {
                "Reservations": [
                    {
                        "Instances": [
                            {
                                "InstanceId": "i-test123",
                                "State": {"Name": "stopped"},
                                "LaunchTime": old_date,
                                "InstanceType": "t2.micro",
                                "Tags": [],
                            }
                        ]
                    }
                ]
            }
        ]

        mgr = EC2Manager(self.mock_session)
        result = mgr.list_stopped_instances(max_age_days=90)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["instance_id"], "i-test123")
        self.assertGreaterEqual(result[0]["age_days"], 120)

    def test_list_stopped_instances_skips_recent(self):
        from aws.ec2_manager import EC2Manager

        recent_date = datetime.now(timezone.utc) - timedelta(days=10)
        self.mock_client.get_paginator.return_value.paginate.return_value = [
            {
                "Reservations": [
                    {
                        "Instances": [
                            {
                                "InstanceId": "i-recent",
                                "State": {"Name": "stopped"},
                                "LaunchTime": recent_date,
                                "InstanceType": "t2.micro",
                                "Tags": [],
                            }
                        ]
                    }
                ]
            }
        ]

        mgr = EC2Manager(self.mock_session)
        result = mgr.list_stopped_instances(max_age_days=90)
        self.assertEqual(len(result), 0)

    def test_terminate_dry_run(self):
        from aws.ec2_manager import EC2Manager

        mgr = EC2Manager(self.mock_session)
        result = mgr.terminate_instance("i-test123", dry_run=True)

        self.assertEqual(result["action"], "dry_run")
        self.mock_client.terminate_instances.assert_not_called()

    def test_terminate_live(self):
        from aws.ec2_manager import EC2Manager

        self.mock_client.terminate_instances.return_value = {"TerminatingInstances": []}
        mgr = EC2Manager(self.mock_session)
        mgr.terminate_instance("i-test123", dry_run=False)

        self.mock_client.terminate_instances.assert_called_once_with(
            InstanceIds=["i-test123"]
        )


if __name__ == "__main__":
    unittest.main()
