"""
Configuration constants for the Drowsiness Detection System.
Values can be overridden via environment variables in .env file.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def _env_float(key: str, default: float) -> float:
    """Read a float from environment, falling back to default."""
    val = os.getenv(key)
    return float(val) if val is not None else default


def _env_int(key: str, default: int) -> int:
    """Read an int from environment, falling back to default."""
    val = os.getenv(key)
    return int(val) if val is not None else default


# ── Eye Aspect Ratio ──────────────────────────────────────────────
EAR_THRESHOLD = _env_float("EAR_THRESHOLD", 0.22)

# ── Mouth Aspect Ratio ────────────────────────────────────────────
MAR_THRESHOLD = _env_float("MAR_THRESHOLD", 0.6)

# ── Head Pose (degrees) ──────────────────────────────────────────
PITCH_THRESHOLD = _env_float("PITCH_THRESHOLD", 15.0)

# ── Temporal Filtering ───────────────────────────────────────────
CONSECUTIVE_FRAMES = _env_int("CONSECUTIVE_FRAMES", 20)

# ── Alert Cooldown ───────────────────────────────────────────────
ALERT_COOLDOWN_SECONDS = _env_float("ALERT_COOLDOWN_SECONDS", 5.0)

# ── EAR History Buffer (frames) ─────────────────────────────────
EAR_HISTORY_SIZE = _env_int("EAR_HISTORY_SIZE", 90)

# ── ONNX Model ───────────────────────────────────────────────────
ONNX_MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "detector", "models", "model.onnx")

# ── Backend Integration (Stage 2) ───────────────────────────────
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
SESSION_ID = os.getenv("SESSION_ID", None)
DRIVER_ID = os.getenv("DRIVER_ID", None)
