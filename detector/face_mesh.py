"""
MediaPipe FaceMesh setup and landmark extraction.

Initializes FaceMesh with refined landmarks and provides named groups
for eye, mouth, and head-pose landmark indices.
"""

import mediapipe as mp
import numpy as np

# ── Named landmark index groups ──────────────────────────────────
LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
MOUTH_INDICES = [61, 291, 39, 181, 0, 17, 269, 405]
HEAD_POSE_INDICES = [1, 33, 263, 61, 291, 199]

LANDMARK_GROUPS = {
    "left_eye": LEFT_EYE_INDICES,
    "right_eye": RIGHT_EYE_INDICES,
    "mouth": MOUTH_INDICES,
    "head_pose": HEAD_POSE_INDICES,
}


class FaceMeshDetector:
    """Wraps MediaPipe FaceMesh for per-frame landmark extraction."""

    def __init__(
        self,
        max_num_faces: int = 1,
        refine_landmarks: bool = True,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5,
    ):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=max_num_faces,
            refine_landmarks=refine_landmarks,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

    def process_frame(self, frame):
        """
        Run FaceMesh on a BGR frame.

        Parameters
        ----------
        frame : np.ndarray
            BGR image from OpenCV.

        Returns
        -------
        np.ndarray or None
            (478, 3) array of (x, y, z) normalised landmark coordinates,
            or None if no face detected.
        """
        import cv2

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self.face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            return None

        face_landmarks = results.multi_face_landmarks[0]
        landmarks = np.array(
            [(lm.x, lm.y, lm.z) for lm in face_landmarks.landmark],
            dtype=np.float64,
        )
        return landmarks

    def draw_landmarks(self, frame, landmarks_raw=None):
        """
        Draw the face mesh tessellation on *frame* in-place.

        If landmarks_raw is not available, re-run detection (less efficient).
        Uses the raw MediaPipe result for drawing.
        """
        import cv2

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self.face_mesh.process(rgb)

        if results.multi_face_landmarks:
            for face_lms in results.multi_face_landmarks:
                self.mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=face_lms,
                    connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=self.mp_drawing_styles.get_default_face_mesh_tesselation_style(),
                )

    def close(self):
        """Release MediaPipe resources."""
        self.face_mesh.close()
