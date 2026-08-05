"""
Unit tests for AI recommender and anomaly detection.
Author: Mithin Sagar S
"""

import unittest
from analyzer.anomaly_detector import AnomalyDetector


class TestAnomalyDetector(unittest.TestCase):
    def test_detect_finds_outliers(self):
        detector = AnomalyDetector(threshold_std=2.0)
        values = [10, 12, 11, 13, 10, 11, 100, 12, 11]
        result = detector.detect(values)

        self.assertGreater(len(result), 0)
        outlier_values = [a["value"] for a in result]
        self.assertIn(100.0, outlier_values)

    def test_detect_no_anomalies(self):
        detector = AnomalyDetector(threshold_std=2.0)
        values = [10, 10, 10, 10, 10]
        result = detector.detect(values)
        self.assertEqual(len(result), 0)

    def test_detect_too_few_points(self):
        detector = AnomalyDetector(threshold_std=2.0)
        result = detector.detect([5, 10])
        self.assertEqual(len(result), 0)

    def test_cost_anomalies(self):
        detector = AnomalyDetector(threshold_std=2.0)
        cost_data = [
            {"start": "2024-01", "cost": 50},
            {"start": "2024-02", "cost": 55},
            {"start": "2024-03", "cost": 48},
            {"start": "2024-04", "cost": 300},
            {"start": "2024-05", "cost": 52},
        ]
        result = detector.detect_cost_anomalies(cost_data)
        self.assertGreater(len(result), 0)


class TestAIRecommenderFallback(unittest.TestCase):
    def test_rule_based_delete(self):
        from analyzer.ai_recommender import AIRecommender

        recommender = AIRecommender()
        result = recommender._rule_based_fallback(
            {"age_days": 120, "is_stopped": 1, "cpu_utilization": 0}
        )
        self.assertEqual(result["action"], "delete")

    def test_rule_based_keep(self):
        from analyzer.ai_recommender import AIRecommender

        recommender = AIRecommender()
        result = recommender._rule_based_fallback(
            {"age_days": 5, "is_stopped": 0, "cpu_utilization": 80}
        )
        self.assertEqual(result["action"], "keep")


if __name__ == "__main__":
    unittest.main()
