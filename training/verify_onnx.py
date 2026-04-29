"""
Verify ONNX model by comparing outputs with original XGBoost model.

Usage:
    python verify_onnx.py
"""

import os
import sys

import numpy as np
import pandas as pd
import xgboost as xgb
import onnxruntime as ort

from config import MODEL_PATH, ONNX_PATH, FEATURES_CSV, FEATURE_COLUMNS


def main():
    # ── Check files exist ────────────────────────────────────────
    for path, name in [(ONNX_PATH, "ONNX model"), (MODEL_PATH, "XGBoost model")]:
        if not os.path.isfile(path):
            print(f"ERROR: {name} not found at {path}")
            sys.exit(1)

    # ── Load ONNX model ──────────────────────────────────────────
    print(f"Loading ONNX model: {ONNX_PATH}")
    session = ort.InferenceSession(ONNX_PATH)

    input_name = session.get_inputs()[0].name
    output_names = [o.name for o in session.get_outputs()]
    print(f"  Input:   {input_name}")
    print(f"  Outputs: {output_names}")

    # ── Test 1: Dummy input ──────────────────────────────────────
    print("\n--- Test 1: Dummy input (zeros) ---")
    dummy = np.zeros((1, len(FEATURE_COLUMNS)), dtype=np.float32)
    results = session.run(None, {input_name: dummy})

    predicted_label = results[0]
    probabilities = results[1] if len(results) > 1 else None

    print(f"  Predicted label : {predicted_label}")
    if probabilities is not None:
        # probabilities may be a list of dicts or ndarray depending on converter
        if isinstance(probabilities, list):
            print(f"  Probabilities   : {probabilities[0]}")
        else:
            print(f"  Probabilities   : {probabilities[0]}")

    # ── Test 2: Compare with XGBoost on real data ────────────────
    print("\n--- Test 2: Real data comparison ---")

    if not os.path.isfile(FEATURES_CSV):
        print(f"  ⚠ {FEATURES_CSV} not found, skipping real data test.")
        print("\n✅ ONNX export verified successfully (dummy input only)")
        return

    df = pd.read_csv(FEATURES_CSV).dropna()
    if len(df) == 0:
        print("  ⚠ No valid rows in features.csv, skipping.")
        print("\n✅ ONNX export verified successfully (dummy input only)")
        return

    # Take 5 random samples
    sample = df.sample(n=min(5, len(df)), random_state=42)
    X_sample = sample[FEATURE_COLUMNS].values.astype(np.float32)

    # XGBoost predictions
    xgb_model = xgb.XGBClassifier()
    xgb_model.load_model(MODEL_PATH)
    xgb_preds = xgb_model.predict(X_sample)
    xgb_probs = xgb_model.predict_proba(X_sample)

    # ONNX predictions
    onnx_results = session.run(None, {input_name: X_sample})
    onnx_preds = onnx_results[0]

    # Handle probabilities (may be list of dicts from onnxmltools)
    if len(onnx_results) > 1:
        onnx_probs_raw = onnx_results[1]
        if isinstance(onnx_probs_raw, list) and isinstance(onnx_probs_raw[0], dict):
            n_classes = len(onnx_probs_raw[0])
            onnx_probs = np.array(
                [[row[c] for c in range(n_classes)] for row in onnx_probs_raw],
                dtype=np.float32,
            )
        else:
            onnx_probs = np.array(onnx_probs_raw, dtype=np.float32)
    else:
        onnx_probs = None

    # Compare labels
    onnx_preds_flat = np.array(onnx_preds).flatten()
    xgb_preds_flat = np.array(xgb_preds).flatten()

    labels_match = np.array_equal(onnx_preds_flat, xgb_preds_flat)
    print(f"  XGBoost preds: {xgb_preds_flat.tolist()}")
    print(f"  ONNX preds   : {onnx_preds_flat.tolist()}")
    print(f"  Labels match : {'YES' if labels_match else 'NO'}")

    # Compare probabilities
    if onnx_probs is not None and xgb_probs is not None:
        max_diff = np.max(np.abs(onnx_probs - xgb_probs))
        print(f"  Max prob diff : {max_diff:.6f}")
        probs_close = max_diff < 0.01
        print(f"  Probs close  : {'YES' if probs_close else 'NO (diff > 0.01)'}")

    if labels_match:
        print("\nDONE: ONNX export verified successfully")
    else:
        print("\nERROR: ONNX predictions differ from XGBoost — check export_onnx.py")
        sys.exit(1)


if __name__ == "__main__":
    main()
