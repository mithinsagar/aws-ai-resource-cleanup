"""
Feature engineering for cleanup prediction.
Author: Mithin Sagar S
"""

import numpy as np


def add_derived_features(X):
    age = X[:, 0]
    cpu = X[:, 1]
    net_in = X[:, 2]
    net_out = X[:, 3]
    is_stopped = X[:, 6]

    total_network = (net_in + net_out).reshape(-1, 1)
    age_normalized = (age / (age.max() + 1e-8)).reshape(-1, 1)
    idle_score = ((1 - cpu / 100) * age_normalized.flatten()).reshape(-1, 1)
    stopped_age = (is_stopped * age).reshape(-1, 1)

    X_enhanced = np.hstack([X, total_network, age_normalized, idle_score, stopped_age])
    return X_enhanced


def get_feature_names():
    return [
        "age_days",
        "cpu_utilization",
        "network_in",
        "network_out",
        "disk_read",
        "disk_write",
        "is_stopped",
        "has_tags",
        "total_network",
        "age_normalized",
        "idle_score",
        "stopped_age",
    ]
