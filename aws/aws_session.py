"""
AWS session and client factory.
Author: Mithin Sagar S
"""

import boto3
from botocore.config import Config
from botocore.exceptions import ProfileNotFound, NoCredentialsError
from utils.logger import log


class AWSSession:
    def __init__(
        self,
        profile_name="default",
        region_name="us-east-1",
        max_attempts=5,
        retry_mode="standard",
    ):
        self.profile_name = profile_name
        self.region_name = region_name
        self._session = None
        self._client_config = Config(
            retries={"max_attempts": max_attempts, "mode": retry_mode}
        )

    def _create_session(self):
        try:
            self._session = boto3.Session(
                profile_name=self.profile_name,
                region_name=self.region_name,
            )
            log.info(
                "AWS session created (profile=%s, region=%s)",
                self.profile_name,
                self.region_name,
            )
        except ProfileNotFound:
            log.warning(
                "Profile '%s' not found, falling back to default credentials",
                self.profile_name,
            )
            self._session = boto3.Session(region_name=self.region_name)
        except NoCredentialsError:
            log.error("No AWS credentials found. Configure AWS CLI first.")
            raise

    @property
    def session(self):
        if self._session is None:
            self._create_session()
        return self._session

    def client(self, service_name):
        return self.session.client(service_name, config=self._client_config)

    def resource(self, service_name):
        return self.session.resource(service_name, config=self._client_config)
