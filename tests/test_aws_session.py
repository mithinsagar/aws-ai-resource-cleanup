"""
Unit tests for AWSSession retry configuration.
Author: Mithin Sagar S
"""

import unittest
from unittest.mock import MagicMock, patch


class TestAWSSessionRetries(unittest.TestCase):
    @patch("aws.aws_session.boto3.Session")
    def test_client_uses_configured_retry_settings(self, mock_boto3_session):
        from aws.aws_session import AWSSession

        mock_session_instance = MagicMock()
        mock_boto3_session.return_value = mock_session_instance

        session = AWSSession(max_attempts=7, retry_mode="adaptive")
        session.client("ec2")

        mock_session_instance.client.assert_called_once()
        _, kwargs = mock_session_instance.client.call_args
        retries = kwargs["config"].retries
        self.assertEqual(retries["max_attempts"], 7)
        self.assertEqual(retries["mode"], "adaptive")

    @patch("aws.aws_session.boto3.Session")
    def test_resource_uses_configured_retry_settings(self, mock_boto3_session):
        from aws.aws_session import AWSSession

        mock_session_instance = MagicMock()
        mock_boto3_session.return_value = mock_session_instance

        session = AWSSession()
        session.resource("s3")

        mock_session_instance.resource.assert_called_once()
        _, kwargs = mock_session_instance.resource.call_args
        retries = kwargs["config"].retries
        self.assertEqual(retries["max_attempts"], 5)
        self.assertEqual(retries["mode"], "standard")

    @patch("aws.aws_session.boto3.Session")
    def test_default_max_attempts_is_five(self, mock_boto3_session):
        from aws.aws_session import AWSSession

        session = AWSSession()
        self.assertEqual(session._client_config.retries["max_attempts"], 5)


if __name__ == "__main__":
    unittest.main()
