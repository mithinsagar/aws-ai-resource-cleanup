"""
AWS Cost Explorer integration for cost analysis.
Author: Mithin Sagar S
"""

import datetime
from utils.logger import log


class CostExplorer:
    def __init__(self, aws_session):
        self.client = aws_session.client("ce")

    def get_monthly_cost(self, months_back=3):
        log.info("Fetching cost data for the last %d months...", months_back)
        end = datetime.date.today().replace(day=1)
        start = end - datetime.timedelta(days=months_back * 30)
        try:
            response = self.client.get_cost_and_usage(
                TimePeriod={
                    "Start": start.strftime("%Y-%m-%d"),
                    "End": end.strftime("%Y-%m-%d"),
                },
                Granularity="MONTHLY",
                Metrics=["UnblendedCost"],
            )
            results = []
            for period in response.get("ResultsByTime", []):
                results.append(
                    {
                        "start": period["TimePeriod"]["Start"],
                        "end": period["TimePeriod"]["End"],
                        "cost": float(
                            period["Total"]["UnblendedCost"]["Amount"]
                        ),
                        "unit": period["Total"]["UnblendedCost"]["Unit"],
                    }
                )
            return results
        except Exception as e:
            log.error("Cost Explorer error: %s", e)
            return []

    def get_cost_by_service(self, days_back=30):
        log.info("Fetching cost breakdown by service...")
        end = datetime.date.today()
        start = end - datetime.timedelta(days=days_back)
        try:
            response = self.client.get_cost_and_usage(
                TimePeriod={
                    "Start": start.strftime("%Y-%m-%d"),
                    "End": end.strftime("%Y-%m-%d"),
                },
                Granularity="MONTHLY",
                Metrics=["UnblendedCost"],
                GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
            )
            services = {}
            for period in response.get("ResultsByTime", []):
                for group in period.get("Groups", []):
                    service = group["Keys"][0]
                    cost = float(group["Metrics"]["UnblendedCost"]["Amount"])
                    services[service] = services.get(service, 0) + cost
            return dict(sorted(services.items(), key=lambda x: x[1], reverse=True))
        except Exception as e:
            log.error("Cost Explorer error: %s", e)
            return {}
