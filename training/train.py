"""
XGBoost Training Script.

Loads features.csv, applies SMOTE oversampling, trains XGBoost with
stratified cross-validation, evaluates on a held-out test set, and
saves the model.

Usage:
    python train.py
"""

import os
import sys
import warnings

import numpy as np
import pandas as pd
import xgboost as xgb
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.metrics import accuracy_score, classification_report

from config import (
    FEATURES_CSV,
    MODEL_PATH,
    OUTPUT_DIR,
    XGB_PARAMS,
    FEATURE_COLUMNS,
    LABEL_MAP,
    LABEL_NAMES,
    TEST_SIZE,
    RANDOM_STATE,
    CV_FOLDS,
)

warnings.filterwarnings("ignore", category=UserWarning)


def main():
    # ── Load data ────────────────────────────────────────────────
    if not os.path.isfile(FEATURES_CSV):
        print(f"ERROR: {FEATURES_CSV} not found. Run preprocess.py first.")
        sys.exit(1)

    df = pd.read_csv(FEATURES_CSV)
    print(f"Loaded {len(df)} samples from {FEATURES_CSV}")

    # Drop NaN rows
    before = len(df)
    df.dropna(inplace=True)
    dropped = before - len(df)
    if dropped > 0:
        print(f"Dropped {dropped} rows with NaN values")

    # ── Class distribution check ─────────────────────────────────
    print("\nClass distribution:")
    for name, lid in LABEL_MAP.items():
        count = len(df[df["label"] == lid])
        flag = " ⚠ LOW" if count < 50 else ""
        print(f"  {name:10s}: {count:>6d}{flag}")
        if count < 50:
            print(f"    WARNING: '{name}' has fewer than 50 samples!")

    # ── Prepare features and labels ──────────────────────────────
    X = df[FEATURE_COLUMNS].values
    y = df["label"].values.astype(int)

    # ── Train / test split ───────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    print(f"\nTrain: {len(X_train)} | Test: {len(X_test)}")

    # ── SMOTE oversampling on training set ───────────────────────
    print("Applying SMOTE oversampling...")
    smote = SMOTE(random_state=RANDOM_STATE)
    try:
        X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
        print(f"After SMOTE: {len(X_train_res)} training samples")
        print("  Resampled class distribution:")
        unique, counts = np.unique(y_train_res, return_counts=True)
        for u, c in zip(unique, counts):
            print(f"    {LABEL_NAMES.get(u, str(u)):10s}: {c:>6d}")
    except ValueError as e:
        print(f"SMOTE failed ({e}), proceeding without oversampling.")
        X_train_res, y_train_res = X_train, y_train

    # ── Train XGBoost ────────────────────────────────────────────
    print("\nTraining XGBoost classifier...")
    model = xgb.XGBClassifier(**XGB_PARAMS)
    model.fit(
        X_train_res,
        y_train_res,
        eval_set=[(X_test, y_test)],
        verbose=False,
    )

    # ── Cross-validation ─────────────────────────────────────────
    print(f"\nRunning {CV_FOLDS}-fold stratified cross-validation...")
    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    cv_scores = cross_val_score(model, X_train_res, y_train_res, cv=cv, scoring="accuracy")
    print(f"  CV Accuracy: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # ── Test set evaluation ──────────────────────────────────────
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nTest Accuracy: {acc:.4f}")

    class_names = [LABEL_NAMES.get(i, str(i)) for i in sorted(LABEL_MAP.values())]
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=class_names, zero_division=0))

    # ── Feature importances ──────────────────────────────────────
    importances = model.feature_importances_
    sorted_idx = np.argsort(importances)[::-1]
    print("Feature Importances (ranked):")
    for i in sorted_idx:
        print(f"  {FEATURE_COLUMNS[i]:18s}: {importances[i]:.4f}")

    # ── Save model ───────────────────────────────────────────────
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    model.save_model(MODEL_PATH)
    print(f"\nModel saved to: {MODEL_PATH}")


if __name__ == "__main__":
    main()
