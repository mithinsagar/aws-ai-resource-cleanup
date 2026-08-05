"""
AI-powered cleanup recommendations using a trained ML model.
Author: Mithin Sagar S
"""

import os
import numpy as np
from utils.logger import log

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "ml", "model.pkl"
)


class AIRecommender:
    def __init__(self):
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            import joblib

            if os.path.exists(MODEL_PATH):
                self.model = joblib.load(MODEL_PATH)
                log.info("AI recommendation model loaded successfully")
            else:
                log.warning(
                    "Model file not found at %s. Run ml/train_model.py first.",
                    MODEL_PATH,
                )
        except Exception as e:
            log.error("Failed to load AI model: %s", e)

    def predict_cleanup_action(self, resource_features):
        if self.model is None:
            log.warning("No model loaded, falling back to rule-based recommendation")
            return self._rule_based_fallback(resource_features)

        features = np.array(
            [
                [
                    resource_features.get("age_days", 0),
                    resource_features.get("cpu_utilization", 0),
                    resource_features.get("network_in", 0),
                    resource_features.get("network_out", 0),
                    resource_features.get("disk_read", 0),
                    resource_features.get("disk_write", 0),
                    resource_features.get("is_stopped", 0),
                    resource_features.get("has_tags", 0),
                ]
            ]
        )
        prediction = self.model.predict(features)[0]
        confidence = max(self.model.predict_proba(features)[0])

        actions = {0: "keep", 1: "review", 2: "delete"}
        return {
            "action": actions.get(prediction, "review"),
            "confidence": round(float(confidence), 3),
        }

    def _rule_based_fallback(self, features):
        age = features.get("age_days", 0)
        is_stopped = features.get("is_stopped", 0)
        cpu = features.get("cpu_utilization", 100)

        if is_stopped and age > 90:
            return {"action": "delete", "confidence": 0.85}
        if cpu < 5 and age > 60:
            return {"action": "review", "confidence": 0.7}
        return {"action": "keep", "confidence": 0.6}

    def batch_recommend(self, resources):
        recommendations = []
        for resource in resources:
            result = self.predict_cleanup_action(resource)
            result["resource_id"] = resource.get("resource_id", "unknown")
            recommendations.append(result)
        return recommendations
