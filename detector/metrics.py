"""
Drowsiness metric calculations.

Provides EAR, MAR, head-pose estimation, and blink-rate counting.
"""

import numpy as np
import cv2
from collections import deque
from config import EAR_THRESHOLD


# ── Helper ────────────────────────────────────────────────────────
def _distance(p1, p2):
    """Euclidean distance between two points (arrays of shape (2,) or (3,))."""
    return np.linalg.norm(np.array(p1) - np.array(p2))


def calculate_ear(landmarks, eye_indices):
    """Eye Aspect Ratio. Given 6 landmark indices."""
    pts = landmarks[eye_indices, :2]  # use x, y only
    p1, p2, p3, p4, p5, p6 = pts

    vertical_1 = _distance(p2, p6)
    vertical_2 = _distance(p3, p5)
    horizontal = _distance(p1, p4)

    if horizontal == 0:
        return 0.0

    ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
    return ear


def get_average_ear(landmarks, left_indices, right_indices):
    """Return the average EAR for both eyes."""
    left_ear = calculate_ear(landmarks, left_indices)
    right_ear = calculate_ear(landmarks, right_indices)
    return (left_ear + right_ear) / 2.0


def calculate_mar(landmarks, mouth_indices):
    """Mouth Aspect Ratio. Uses 8 mouth landmarks."""
    pts = landmarks[mouth_indices, :2]
    left_corner, right_corner = pts[0], pts[1]
    top1, bottom1 = pts[2], pts[3]
    top2, bottom2 = pts[4], pts[5]
    top3, bottom3 = pts[6], pts[7]

    vertical_1 = _distance(top1, bottom1)
    vertical_2 = _distance(top2, bottom2)
    vertical_3 = _distance(top3, bottom3)
    horizontal = _distance(left_corner, right_corner)

    if horizontal == 0:
        return 0.0

    mar = (vertical_1 + vertical_2 + vertical_3) / (3.0 * horizontal)
    return mar


# Standard 3D face model points
_MODEL_POINTS = np.array(
    [
        (0.0, 0.0, 0.0),        # Nose tip
        (-225.0, 170.0, -135.0), # Left eye left corner
        (225.0, 170.0, -135.0),  # Right eye right corner
        (-150.0, -150.0, -125.0),# Left mouth corner
        (150.0, -150.0, -125.0), # Right mouth corner
        (0.0, -330.0, -65.0),    # Chin
    ],
    dtype=np.float64,
)


def calculate_head_pose(landmarks, frame_shape):
    """Estimate head pitch, yaw, roll using cv2.solvePnP."""
    from detector.face_mesh import HEAD_POSE_INDICES

    h, w = frame_shape[:2]
    image_points = np.array(
        [(landmarks[idx, 0] * w, landmarks[idx, 1] * h) for idx in HEAD_POSE_INDICES],
        dtype=np.float64,
    )

    focal_length = w
    center = (w / 2.0, h / 2.0)
    camera_matrix = np.array(
        [
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1],
        ],
        dtype=np.float64,
    )
    dist_coeffs = np.zeros((4, 1))

    success, rotation_vec, translation_vec = cv2.solvePnP(
        _MODEL_POINTS,
        image_points,
        camera_matrix,
        dist_coeffs,
        flags=cv2.SOLVEPNP_ITERATIVE,
    )

    if not success:
        return 0.0, 0.0, 0.0

    rotation_mat, _ = cv2.Rodrigues(rotation_vec)
    pose = cv2.hconcat([rotation_mat, translation_vec])
    _, _, _, _, _, _, euler_angles = cv2.decomposeProjectionMatrix(
        pose
    )

    return float(euler_angles[0, 0]), float(euler_angles[1, 0]), float(euler_angles[2, 0])


class BlinkCounter:
    def __init__(self, ear_threshold=0.22, history_size=90):
        self.ear_threshold = ear_threshold
        self.history = deque(maxlen=history_size)
        self.eye_closed = False
        self.blink_frames = deque(maxlen=history_size)

    def update(self, ear, fps):
        self.history.append(ear)
        blinked = False

        if ear < self.ear_threshold:
            self.eye_closed = True
        else:
            if self.eye_closed:
                blinked = True
                self.eye_closed = False

        self.blink_frames.append(1 if blinked else 0)

        elapsed_seconds = len(self.blink_frames) / max(fps, 1)
        blink_rate = (sum(self.blink_frames) / elapsed_seconds) * 60 \
                     if elapsed_seconds > 0 else 0
        return blink_rate
