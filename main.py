"""
AWS AI Resource Cleanup - Main Entry Point
Author: Mithin Sagar S

Usage:
    python main.py --mode scan          Scan and list idle resources
    python main.py --mode cleanup       Run cleanup (dry run by default)
    python main.py --mode cleanup --live Execute actual deletions
    python main.py --mode dashboard     Launch the web dashboard
    python main.py --mode report        Generate a cleanup report
"""

import argparse
import sys

from config import (
    SETTINGS,
    CLEANUP_RULES,
    DRY_RUN,
    AWS_MAX_RETRY_ATTEMPTS,
    AWS_RETRY_MODE,
)
from aws.aws_session import AWSSession
from aws.ec2_manager import EC2Manager
from aws.ebs_manager import EBSManager
from aws.s3_manager import S3Manager
from aws.iam_manager import IAMManager
from aws.cloudwatch_manager import CloudWatchManager
from aws.rds_manager import RDSManager
from aws.dynamodb_manager import DynamoDBManager
from analyzer.idle_detector import IdleDetector
from analyzer.rule_engine import RuleEngine
from cleanup.cleanup_engine import CleanupEngine
from cleanup.ec2_cleanup import EC2Cleanup
from cleanup.ebs_cleanup import EBSCleanup
from cleanup.s3_cleanup import S3Cleanup
from cleanup.rds_cleanup import RDSCleanup
from cleanup.dynamodb_cleanup import DynamoDBCleanup
from cleanup.notification import NotificationService
from utils.logger import log
from utils.constants import PROJECT_NAME, VERSION


def build_services():
    session = AWSSession(
        profile_name=SETTINGS["aws"]["profile"],
        region_name=SETTINGS["aws"]["region"],
        max_attempts=AWS_MAX_RETRY_ATTEMPTS,
        retry_mode=AWS_RETRY_MODE,
    )
    return {
        "session": session,
        "ec2": EC2Manager(session),
        "ebs": EBSManager(session),
        "s3": S3Manager(session),
        "iam": IAMManager(session),
        "cloudwatch": CloudWatchManager(session),
        "rds": RDSManager(session),
        "dynamodb": DynamoDBManager(session),
    }


def run_scan(services):
    log.info("Running resource scan...")
    detector = IdleDetector(
        services["ec2"],
        services["ebs"],
        services["iam"],
        services["cloudwatch"],
        CLEANUP_RULES["rules"],
    )
    results = detector.detect_all()
    print(detector.summary(results))

    buckets = services["s3"].list_buckets()
    print(f"\n  S3 Buckets: {len(buckets)} total")
    for b in buckets:
        print(f"    - {b['name']} (created: {b['creation_date']})")

    tables = services["dynamodb"].list_tables()
    print(f"\n  DynamoDB Tables: {len(tables)} total")
    for t in tables:
        print(f"    - {t['table_name']} (items: {t['item_count']}, status: {t['status']})")

    return results


def run_cleanup(services, dry_run=True):
    log.info("Running cleanup (dry_run=%s)...", dry_run)
    thresholds = SETTINGS.get("thresholds", {})

    ec2_cleanup = EC2Cleanup(services["ec2"], thresholds.get("ec2_stopped_days", 90))
    ebs_cleanup = EBSCleanup(services["ebs"], thresholds.get("ebs_snapshot_days", 90))
    s3_cleanup = S3Cleanup(services["s3"])
    rds_cleanup = RDSCleanup(services["rds"])
    dynamodb_cleanup = DynamoDBCleanup(services["dynamodb"])

    engine = CleanupEngine(
        ec2_cleanup, ebs_cleanup, s3_cleanup, rds_cleanup, dynamodb_cleanup, dry_run
    )
    results = engine.run_full_cleanup()
    summary = engine.get_summary()

    notifier = NotificationService(services["session"])
    notifier.send_cleanup_summary(summary)

    return summary


def run_dashboard():
    log.info("Starting web dashboard...")
    from dashboard.app import app

    port = SETTINGS.get("dashboard", {}).get("port", 5000)
    debug = SETTINGS.get("dashboard", {}).get("debug", False)
    app.run(host="0.0.0.0", port=port, debug=debug)


def run_report(services):
    log.info("Generating cleanup report...")
    from reports.generate_report import ReportGenerator

    detector = IdleDetector(
        services["ec2"],
        services["ebs"],
        services["iam"],
        services["cloudwatch"],
        CLEANUP_RULES["rules"],
    )
    idle_results = detector.detect_all()
    generator = ReportGenerator()
    generator.generate(idle_results)


def main():
    parser = argparse.ArgumentParser(
        description=f"{PROJECT_NAME} v{VERSION} - by Mithin Sagar S"
    )
    parser.add_argument(
        "--mode",
        choices=["scan", "cleanup", "dashboard", "report"],
        default="scan",
        help="Operation mode (default: scan)",
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Execute actual deletions instead of dry run",
    )
    args = parser.parse_args()

    print(f"\n  {PROJECT_NAME} v{VERSION}")
    print(f"  Author: Mithin Sagar S")
    print(f"  Mode: {args.mode}")
    print(f"  {'=' * 42}\n")

    if args.mode == "dashboard":
        run_dashboard()
        return

    services = build_services()

    if args.mode == "scan":
        run_scan(services)
    elif args.mode == "cleanup":
        dry_run = not args.live
        run_cleanup(services, dry_run)
    elif args.mode == "report":
        run_report(services)


if __name__ == "__main__":
    main()
