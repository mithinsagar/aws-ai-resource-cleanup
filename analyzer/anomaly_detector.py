"""
Anomaly detection for unusual resource usage patterns.
Author: Mithin Sagar S
"""

import numpy as np
from utils.logger import log


class AnomalyDetector:
    def __init__(self, threshold_std=2.0):
        self.threshold_std = threshold_std

    def detect(self, values, labels=None):
        if len(values) < 3:
            log.warning("Not enough data points for anomaly detection")
            return []

        arr = np.array(values, dtype=float)
        mean = np.mean(arr)
        std = np.std(arr)

        if std == 0:
            return []

        anomalies = []
        for i, val in enumerate(arr):
            z_score = abs(val - mean) / std
            if z_score > self.threshold_std:
                anomalies.append(
                    {
                        "index": i,
                        "label": labels[i] if labels else f"point_{i}",
                        "value": float(val),
                        "z_score": round(float(z_score), 3),
                        "mean": round(float(mean), 3),
                        "std": round(float(std), 3),
                    }
                )

        log.info(
            "Anomaly detection complete: %d anomalies found in %d data points",
            len(anomalies),
            len(values),
        )
        return anomalies

    def detect_cost_anomalies(self, cost_data):
        values = [entry["cost"] for entry in cost_data]
        labels = [entry.get("start", f"period_{i}") for i, entry in enumerate(cost_data)]
        return self.detect(values, labels)
