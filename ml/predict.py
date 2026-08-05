"""
Load trained model and predict cleanup actions.
Author: Mithin Sagar S
"""

import os
import joblib
import numpy as np
from feature_engineering import add_derived_features

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
ACTION_MAP = {0: "keep", 1: "review", 2: "delete"}


def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}. Run train_model.py first."
        )
    return joblib.load(MODEL_PATH)


def predict_single(model, features_dict):
    raw = np.array(
        [
            [
                features_dict.get("age_days", 0),
                features_dict.get("cpu_utilization", 0),
                features_dict.get("network_in", 0),
                features_dict.get("network_out", 0),
                features_dict.get("disk_read", 0),
                features_dict.get("disk_write", 0),
                features_dict.get("is_stopped", 0),
                features_dict.get("has_tags", 0),
            ]
        ]
    )
    enhanced = add_derived_features(raw)
    prediction = model.predict(enhanced)[0]
    probabilities = model.predict_proba(enhanced)[0]
    return {
        "action": ACTION_MAP.get(prediction, "review"),
        "confidence": round(float(max(probabilities)), 3),
        "probabilities": {
            ACTION_MAP[i]: round(float(p), 3) for i, p in enumerate(probabilities)
        },
    }


if __name__ == "__main__":
    model = load_model()
    sample = {
        "age_days": 120,
        "cpu_utilization": 2.5,
        "network_in": 100,
        "network_out": 50,
        "disk_read": 10,
        "disk_write": 5,
        "is_stopped": 1,
        "has_tags": 0,
    }
    result = predict_single(model, sample)
    print(f"Prediction: {result['action']} (confidence: {result['confidence']})")
    print(f"Probabilities: {result['probabilities']}")
