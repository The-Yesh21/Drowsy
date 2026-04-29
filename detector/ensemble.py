"""
Ensemble scoring — ONNX Model Integration.

Loads the trained XGBoost ONNX model and predicts drowsiness state
from 10 facial features.

Features expected (in order):
[ear, mar, pitch, yaw, roll, ear_variance, mar_variance, blink_rate, left_ear, right_ear]
"""

import numpy as np
import onnxruntime as ort
import sys

from config import ONNX_MODEL_PATH

# ── Initialize ONNX Session ──────────────────────────────────────
try:
    _session = ort.InferenceSession(ONNX_MODEL_PATH)
    _input_name = _session.get_inputs()[0].name
    print("OK: ONNX model loaded successfully")
except Exception as e:
    print(f"ERROR: Failed to load ONNX model from {ONNX_MODEL_PATH}")
    print(f"Details: {e}")
    sys.exit(1)


# ── State mapping ────────────────────────────────────────────────
# Model outputs 0 or 1. We map to 4 states based on probabilities
# to keep compatibility with the Stage 1 Alerter.
# Label 0 = Alert, Label 1 = Drowsy
STATE_LABELS = {
    0: "ALERT",
    1: "DROWSY"
}


def predict(
    ear: float,
    mar: float,
    pitch: float,
    yaw: float,
    roll: float,
    ear_variance: float,
    mar_variance: float,
    blink_rate: float,
    left_ear: float,
    right_ear: float,
):
    """
    Run inference through the ONNX model.

    Returns
    -------
    tuple[float, str, np.ndarray]
        (drowsiness_score (prob of class 1), state_string, probabilities)
    """
    # Pack features into shape (1, 10)
    features = np.array(
        [[ear, mar, pitch, yaw, roll, ear_variance, mar_variance, blink_rate, left_ear, right_ear]],
        dtype=np.float32,
    )

    # Run inference
    results = _session.run(None, {_input_name: features})

    # Parse output
    predicted_label = int(results[0][0])
    
    # Probabilities handling — depends on how skl2onnx exported it
    # usually it's a list of dicts for tree models: [{0: 0.1, 1: 0.9}]
    prob_output = results[1]
    
    if isinstance(prob_output, list) and isinstance(prob_output[0], dict):
        probs = np.array([prob_output[0].get(0, 0.0), prob_output[0].get(1, 0.0)])
    else:
        probs = np.array(prob_output[0])

    score = float(probs[1])  # probability of being drowsy

    # Map to legacy 4-state system using thresholds on the drowsy probability
    if score >= 0.75:
        state = "CRITICAL"
    elif score >= 0.5:
        state = "DROWSY"
    elif score >= 0.3:
        state = "MILD"
    else:
        state = "ALERT"

    return score, state, probs
