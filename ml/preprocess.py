"""
Data preprocessing for the cleanup prediction model.
Author: Mithin Sagar S
"""

import os
import pandas as pd
import numpy as np

DATA_DIR = os.path.dirname(__file__)
DATASET_PATH = os.path.join(DATA_DIR, "dataset.csv")


def load_dataset(path=None):
    path = path or DATASET_PATH
    df = pd.read_csv(path)
    print(f"Loaded {len(df)} records from {path}")
    return df


def clean_data(df):
    df = df.dropna(subset=["age_days", "action"])
    df["cpu_utilization"] = df["cpu_utilization"].fillna(0)
    df["network_in"] = df["network_in"].fillna(0)
    df["network_out"] = df["network_out"].fillna(0)
    df["disk_read"] = df["disk_read"].fillna(0)
    df["disk_write"] = df["disk_write"].fillna(0)
    df["is_stopped"] = df["is_stopped"].astype(int)
    df["has_tags"] = df["has_tags"].astype(int)
    print(f"Cleaned dataset: {len(df)} records remaining")
    return df


def encode_labels(df):
    label_map = {"keep": 0, "review": 1, "delete": 2}
    df["label"] = df["action"].map(label_map)
    return df


def get_features_and_labels(df):
    feature_cols = [
        "age_days",
        "cpu_utilization",
        "network_in",
        "network_out",
        "disk_read",
        "disk_write",
        "is_stopped",
        "has_tags",
    ]
    X = df[feature_cols].values
    y = df["label"].values
    return X, y


def preprocess_pipeline(path=None):
    df = load_dataset(path)
    df = clean_data(df)
    df = encode_labels(df)
    X, y = get_features_and_labels(df)
    print(f"Features shape: {X.shape}, Labels shape: {y.shape}")
    return X, y


if __name__ == "__main__":
    X, y = preprocess_pipeline()
    print("Label distribution:", dict(zip(*np.unique(y, return_counts=True))))
