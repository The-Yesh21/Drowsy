"""
Export trained XGBoost model to ONNX format.

Usage:
    python export_onnx.py
"""

import os
import sys

import numpy as np
import xgboost as xgb
from onnxmltools.convert import convert_xgboost
from onnxmltools.convert.common.data_types import FloatTensorType
import onnx

from config import MODEL_PATH, ONNX_PATH, OUTPUT_DIR, FEATURE_COLUMNS


def main():
    # ── Load model ───────────────────────────────────────────────
    if not os.path.isfile(MODEL_PATH):
        print(f"ERROR: {MODEL_PATH} not found. Run train.py first.")
        sys.exit(1)

    model = xgb.XGBClassifier()
    model.load_model(MODEL_PATH)
    print(f"Loaded XGBoost model from: {MODEL_PATH}")

    n_features = len(FEATURE_COLUMNS)

    # ── Convert to ONNX ─────────────────────────────────────────
    print(f"Converting to ONNX (input shape: [None, {n_features}])...")

    initial_type = [("features", FloatTensorType([None, n_features]))]

    onnx_model = convert_xgboost(
        model,
        initial_types=initial_type,
        target_opset=12,
    )

    # Rename outputs
    for output in onnx_model.graph.output:
        if output.name == "label":
            continue
        if "label" in output.name.lower():
            output.name = "label"
        elif "probabilities" in output.name.lower() or "proba" in output.name.lower():
            output.name = "probabilities"

    # Validate ONNX model
    onnx.checker.check_model(onnx_model)

    # ── Save ─────────────────────────────────────────────────────
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    onnx.save(onnx_model, ONNX_PATH)

    size_mb = os.path.getsize(ONNX_PATH) / (1024 * 1024)
    print(f"\nDONE: ONNX model saved to: {ONNX_PATH}")
    print(f"   File size: {size_mb:.2f} MB")
    print(f"   Input:  'features'       shape=[None, {n_features}]")
    print(f"   Outputs: {[o.name for o in onnx_model.graph.output]}")


if __name__ == "__main__":
    main()
