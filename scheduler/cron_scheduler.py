"""
Local cron-style scheduler for running cleanup at fixed intervals.
Use this for on-premise or local execution instead of Lambda.
Author: Mithin Sagar S
"""

import sys
import os
import time
import schedule

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import SETTINGS, CLEANUP_RULES
from aws.aws_session import AWSSession
from aws.ec2_manager import EC2Manager
from aws.ebs_manager import EBSManager
from aws.s3_manager import S3Manager
from aws.rds_manager import RDSManager
from cleanup.cleanup_engine import CleanupEngine
from cleanup.ec2_cleanup import EC2Cleanup
from cleanup.ebs_cleanup import EBSCleanup
from cleanup.s3_cleanup import S3Cleanup
from cleanup.rds_cleanup import RDSCleanup
from cleanup.notification import NotificationService
from utils.logger import log


def run_scheduled_cleanup():
    log.info("Scheduled cleanup triggered")
    try:
        session = AWSSession(
            profile_name=SETTINGS["aws"]["profile"],
            region_name=SETTINGS["aws"]["region"],
        )
        thresholds = SETTINGS.get("thresholds", {})

        ec2_cleanup = EC2Cleanup(EC2Manager(session), thresholds.get("ec2_stopped_days", 90))
        ebs_cleanup = EBSCleanup(EBSManager(session), thresholds.get("ebs_snapshot_days", 90))
        s3_cleanup = S3Cleanup(S3Manager(session))
        rds_cleanup = RDSCleanup(RDSManager(session))

        dry_run = SETTINGS.get("cleanup", {}).get("dry_run", True)
        engine = CleanupEngine(ec2_cleanup, ebs_cleanup, s3_cleanup, rds_cleanup, dry_run)
        engine.run_full_cleanup()

        notifier = NotificationService(session)
        notifier.send_cleanup_summary(engine.get_summary())

    except Exception as e:
        log.error("Scheduled cleanup failed: %s", e)


def start_scheduler():
    interval = SETTINGS.get("scheduler", {}).get("interval_hours", 24)
    log.info("Starting scheduler (every %d hours)...", interval)

    schedule.every(interval).hours.do(run_scheduled_cleanup)

    run_scheduled_cleanup()

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    start_scheduler()
