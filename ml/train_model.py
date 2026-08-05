"""
Train the cleanup action prediction model.
Author: Mithin Sagar S
"""

import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report

from preprocess import preprocess_pipeline
from feature_engineering import add_derived_features

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")


def train(dataset_path=None):
    print("Loading and preprocessing data...")
    X, y = preprocess_pipeline(dataset_path)

    print("Engineering features...")
    X = add_derived_features(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1,
    )

    print("Training model...")
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    label_names = ["keep", "review", "delete"]
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=label_names))

    cv_scores = cross_val_score(model, X, y, cv=5, scoring="accuracy")
    print(f"Cross-validation accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

    return model


if __name__ == "__main__":
    train()
