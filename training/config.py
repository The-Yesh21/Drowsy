"""
Configuration for the XGBoost Drowsiness Detection Training Pipeline.
All paths, hyperparameters, and constants.
"""

import os

# ── Paths ─────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
FEATURES_CSV = os.path.join(OUTPUT_DIR, "features.csv")
MODEL_PATH = os.path.join(OUTPUT_DIR, "model.json")
ONNX_PATH = os.path.join(OUTPUT_DIR, "model.onnx")
PLOTS_DIR = os.path.join(OUTPUT_DIR, "plots")

# ── MediaPipe Landmark Indices (same as Stage 1) ─────────────────
LEFT_EYE = [362, 385, 387, 263, 373, 380]
RIGHT_EYE = [33, 160, 158, 133, 153, 144]
MOUTH = [61, 291, 39, 181, 0, 17, 269, 405]
HEAD_POSE_POINTS = [1, 33, 263, 61, 291, 199]

# ── EAR threshold for blink detection ────────────────────────────
EAR_THRESHOLD = 0.22

# ── Preprocessing ────────────────────────────────────────────────
FRAME_SAMPLE_INTERVAL = 5       # sample every Nth frame (videos only)
EAR_ROLLING_WINDOW = 15         # frames for variance calculation
BLINK_HISTORY_SIZE = 90         # frames for blink rate estimation

# ── Image extensions recognised by preprocess.py ─────────────────
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".webp")
VIDEO_EXTENSIONS = (".avi", ".mp4", ".mkv", ".mov")

# ── XGBoost Hyperparameters ──────────────────────────────────────
XGB_PARAMS = {
    "n_estimators": 300,
    "max_depth": 6,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "use_label_encoder": False,
    "eval_metric": "logloss",  # binary classification 
    "random_state": 42,
}

# ── Labels ───────────────────────────────────────────────────────
# Supports both 2-class Kaggle datasets and 4-class NTHU-style datasets.
# The preprocess script auto-detects folder names and maps them here.
LABEL_MAP = {
    "alert": 0,         # also matches "non drowsy", "nonsleepy", "awake"
    "drowsy": 1,        # also matches "sleepy"
}

LABEL_NAMES = {v: k for k, v in LABEL_MAP.items()}

# ── Train / Test Split ───────────────────────────────────────────
TEST_SIZE = 0.2
RANDOM_STATE = 42
CV_FOLDS = 5

# ── Feature Columns ─────────────────────────────────────────────
FEATURE_COLUMNS = [
    "ear",
    "mar",
    "pitch",
    "yaw",
    "roll",
    "ear_variance",
    "mar_variance",
    "blink_rate",
    "left_ear",
    "right_ear",
]
