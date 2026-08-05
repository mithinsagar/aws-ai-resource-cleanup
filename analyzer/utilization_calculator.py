"""
Resource utilization calculation using CloudWatch metrics.
Author: Mithin Sagar S
"""

import datetime
from utils.logger import log


class UtilizationCalculator:
    def __init__(self, aws_session):
        self.cw_client = aws_session.client("cloudwatch")

    def get_ec2_cpu_utilization(self, instance_id, days=14):
        end = datetime.datetime.utcnow()
        start = end - datetime.timedelta(days=days)
        try:
            response = self.cw_client.get_metric_statistics(
                Namespace="AWS/EC2",
                MetricName="CPUUtilization",
                Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                StartTime=start,
                EndTime=end,
                Period=3600,
                Statistics=["Average"],
            )
            datapoints = response.get("Datapoints", [])
            if not datapoints:
                return {"average": 0, "datapoints": 0}

            avg = sum(d["Average"] for d in datapoints) / len(datapoints)
            return {
                "average": round(avg, 2),
                "datapoints": len(datapoints),
                "max": round(max(d["Average"] for d in datapoints), 2),
                "min": round(min(d["Average"] for d in datapoints), 2),
            }
        except Exception as e:
            log.error(
                "Error fetching CPU utilization for %s: %s", instance_id, e
            )
            return {"average": 0, "datapoints": 0}

    def get_ec2_network_io(self, instance_id, days=14):
        end = datetime.datetime.utcnow()
        start = end - datetime.timedelta(days=days)
        result = {}
        for metric in ["NetworkIn", "NetworkOut"]:
            try:
                response = self.cw_client.get_metric_statistics(
                    Namespace="AWS/EC2",
                    MetricName=metric,
                    Dimensions=[{"Name": "InstanceId", "Value": instance_id}],
                    StartTime=start,
                    EndTime=end,
                    Period=3600,
                    Statistics=["Sum"],
                )
                datapoints = response.get("Datapoints", [])
                total = sum(d["Sum"] for d in datapoints) if datapoints else 0
                result[metric.lower()] = round(total, 2)
            except Exception as e:
                log.error("Error fetching %s for %s: %s", metric, instance_id, e)
                result[metric.lower()] = 0
        return result

    def build_feature_vector(self, instance_id, age_days, is_stopped, has_tags):
        cpu = self.get_ec2_cpu_utilization(instance_id)
        network = self.get_ec2_network_io(instance_id)
        return {
            "resource_id": instance_id,
            "age_days": age_days,
            "cpu_utilization": cpu["average"],
            "network_in": network.get("networkin", 0),
            "network_out": network.get("networkout", 0),
            "disk_read": 0,
            "disk_write": 0,
            "is_stopped": int(is_stopped),
            "has_tags": int(has_tags),
        }
