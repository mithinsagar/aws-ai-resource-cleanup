"""
Notification system for cleanup alerts via SNS and email.
Author: Mithin Sagar S
"""

from utils.logger import log


class NotificationService:
    def __init__(self, aws_session, topic_arn=None):
        self.sns_client = aws_session.client("sns") if topic_arn else None
        self.topic_arn = topic_arn

    def send_cleanup_summary(self, summary):
        message = self._format_summary(summary)
        log.info("Cleanup notification:\n%s", message)

        if self.sns_client and self.topic_arn:
            try:
                self.sns_client.publish(
                    TopicArn=self.topic_arn,
                    Subject="AWS Resource Cleanup Report",
                    Message=message,
                )
                log.info("SNS notification sent to %s", self.topic_arn)
            except Exception as e:
                log.error("Failed to send SNS notification: %s", e)

        return message

    def _format_summary(self, summary):
        lines = [
            "AWS AI Resource Cleanup Report",
            "=" * 40,
            f"Timestamp: {summary.get('timestamp', 'N/A')}",
            f"Mode: {'DRY RUN' if summary.get('dry_run') else 'LIVE'}",
            f"Total Actions: {summary.get('total_actions', 0)}",
            "",
            "Breakdown by Service:",
        ]
        for service, count in summary.get("by_service", {}).items():
            lines.append(f"  {service}: {count} resource(s)")
        lines.append("=" * 40)
        return "\n".join(lines)
