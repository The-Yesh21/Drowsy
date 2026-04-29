"""
Feature Extraction — supports both IMAGE FOLDERS and VIDEO datasets.

Image-folder layout (Kaggle style):
    data/raw/
    ├── Drowsy/         ← images of drowsy subjects
    │   ├── img001.jpg
    │   └── ...
    └── Non Drowsy/     ← images of alert subjects
        ├── img001.jpg
        └── ...

Video layout (NTHU style):
    data/raw/
    ├── 001/
    │   ├── sleepyCombination.avi
    │   └── nonsleepyCombination.avi
    └── ...

Usage:
    python preprocess.py
"""

import os
import sys
from collections import deque

import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
from tqdm import tqdm

from config import (
    DATA_DIR,
    OUTPUT_DIR,
    FEATURES_CSV,
    LEFT_EYE,
    RIGHT_EYE,
    MOUTH,
    HEAD_POSE_POINTS,
    EAR_THRESHOLD,
    FRAME_SAMPLE_INTERVAL,
    EAR_ROLLING_WINDOW,
    BLINK_HISTORY_SIZE,
    FEATURE_COLUMNS,
    LABEL_MAP,
    IMAGE_EXTENSIONS,
    VIDEO_EXTENSIONS,
)


# ═══════════════════════════════════════════════════════════════════
#  Metric helpers (self-contained — no Stage 1 dependency)
# ═══════════════════════════════════════════════════════════════════

def _dist(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))


def _calculate_ear(landmarks, eye_indices):
    pts = landmarks[eye_indices, :2]
    p1, p2, p3, p4, p5, p6 = pts
    vert1 = _dist(p2, p6)
    vert2 = _dist(p3, p5)
    horiz = _dist(p1, p4)
    return (vert1 + vert2) / (2.0 * horiz) if horiz != 0 else 0.0


def _calculate_mar(landmarks, mouth_indices):
    pts = landmarks[mouth_indices, :2]
    left, right = pts[0], pts[1]
    v1 = _dist(pts[2], pts[3])
    v2 = _dist(pts[4], pts[5])
    v3 = _dist(pts[6], pts[7])
    h = _dist(left, right)
    return (v1 + v2 + v3) / (3.0 * h) if h != 0 else 0.0


_MODEL_POINTS = np.array([
    (0.0, 0.0, 0.0),
    (-225.0, 170.0, -135.0),
    (225.0, 170.0, -135.0),
    (-150.0, -150.0, -125.0),
    (150.0, -150.0, -125.0),
    (0.0, -330.0, -65.0),
], dtype=np.float64)


def _calculate_head_pose(landmarks, h, w):
    image_pts = np.array(
        [(landmarks[i, 0] * w, landmarks[i, 1] * h) for i in HEAD_POSE_POINTS],
        dtype=np.float64,
    )
    focal = float(w)
    center = (w / 2.0, h / 2.0)
    cam_mat = np.array([
        [focal, 0, center[0]],
        [0, focal, center[1]],
        [0, 0, 1],
    ], dtype=np.float64)
    dist_coeffs = np.zeros((4, 1))
    ok, rvec, tvec = cv2.solvePnP(
        _MODEL_POINTS, image_pts, cam_mat, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
    )
    if not ok:
        return 0.0, 0.0, 0.0
    rmat, _ = cv2.Rodrigues(rvec)
    pose = cv2.hconcat([rmat, tvec])
    
    # decomposeProjectionMatrix expects a 3x4 projection matrix. 
    # cv2.hconcat([pose, np.array([[0, 0, 0, 1]], dtype=np.float64)]) was creating a 4x4,
    # but `pose` is already 3x4 (3x3 rmat concat with 3x1 tvec).
    # We can just pass `pose` directly if we pad it, but decomposeProjectionMatrix 
    # actually expects a 3x4 projection matrix directly!
    proj_matrix = pose
    _, _, _, _, _, _, euler = cv2.decomposeProjectionMatrix(proj_matrix)
    return float(euler[0, 0]), float(euler[1, 0]), float(euler[2, 0])


def _count_blinks(ear_history, fps):
    if len(ear_history) < 3 or fps <= 0:
        return 0.0
    count, below = 0, False
    for e in ear_history:
        if e < EAR_THRESHOLD:
            below = True
        elif below:
            count += 1
            below = False
    dur = len(ear_history) / fps
    return (count / dur) * 60.0 if dur > 0 else 0.0


# ═══════════════════════════════════════════════════════════════════
#  Label inference
# ═══════════════════════════════════════════════════════════════════

def infer_label(path: str):
    """
    Infer label from folder/file name.

    Matches common Kaggle naming (Drowsy, Non Drowsy) and NTHU naming.
    Returns label int or None if no match.
    """
    low = path.lower().replace("\\", "/").replace("_", " ")

    # Check "non drowsy" / "non sleepy" / "alert" first (before "drowsy"/"sleepy")
    if any(kw in low for kw in ("non drowsy", "nondrowsy", "nonsleepy", "non sleepy", "alert", "awake")):
        return LABEL_MAP.get("alert")
    if any(kw in low for kw in ("drowsy", "sleepy", "yawn", "nodding", "slow blink", "slowblink")):
        return LABEL_MAP.get("drowsy")

    return None


# ═══════════════════════════════════════════════════════════════════
#  Dataset discovery
# ═══════════════════════════════════════════════════════════════════

def discover_dataset(root_dir):
    """
    Walk root_dir and return two lists:
        image_groups : [(label_int, [path, path, ...]), ...]
        video_files  : [(label_int, path), ...]
    """
    image_groups = {}   # label → list of image paths
    video_files = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            ext = os.path.splitext(fn)[1].lower()

            if ext in IMAGE_EXTENSIONS:
                label = infer_label(dirpath)   # use FOLDER name
                if label is None:
                    continue
                image_groups.setdefault(label, []).append(full)

            elif ext in VIDEO_EXTENSIONS:
                label = infer_label(full)      # use full path
                if label is None:
                    print(f"  ⚠ Skipping video (no label match): {full}")
                    continue
                video_files.append((label, full))

    return image_groups, video_files


# ═══════════════════════════════════════════════════════════════════
#  Process IMAGES (one face per image, no temporal features)
# ═══════════════════════════════════════════════════════════════════

def process_images(image_paths, face_mesh, label):
    """Extract features from a list of images. Returns (rows, processed, skipped)."""
    rows = []
    processed = 0
    skipped = 0

    for img_path in tqdm(image_paths, desc=f"Images [label={label}]", leave=False, unit="img"):
        frame = cv2.imread(img_path)
        if frame is None:
            skipped += 1
            continue

        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            skipped += 1
            continue

        lm = results.multi_face_landmarks[0]
        landmarks = np.array([(p.x, p.y, p.z) for p in lm.landmark], dtype=np.float64)

        left_ear = _calculate_ear(landmarks, LEFT_EYE)
        right_ear = _calculate_ear(landmarks, RIGHT_EYE)
        ear = (left_ear + right_ear) / 2.0
        mar = _calculate_mar(landmarks, MOUTH)
        pitch, yaw, roll = _calculate_head_pose(landmarks, h, w)

        # Temporal features not available for single images → 0.0
        rows.append([
            ear, mar, pitch, yaw, roll,
            0.0,       # ear_variance
            0.0,       # mar_variance
            0.0,       # blink_rate
            left_ear, right_ear,
            label,
        ])
        processed += 1

    return rows, processed, skipped


# ═══════════════════════════════════════════════════════════════════
#  Process VIDEOS (temporal features via rolling buffers)
# ═══════════════════════════════════════════════════════════════════

def process_video(video_path, face_mesh, label):
    """Extract features from one video file. Returns (rows, processed, skipped)."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"  ⚠ Cannot open: {video_path}")
        return [], 0, 0

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    ear_buffer = deque(maxlen=BLINK_HISTORY_SIZE)
    mar_buffer = deque(maxlen=EAR_ROLLING_WINDOW)
    rows, processed, skipped, frame_idx = [], 0, 0, 0

    pbar = tqdm(total=total_frames, desc=os.path.basename(video_path), leave=False, unit="fr")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        pbar.update(1)
        frame_idx += 1

        if frame_idx % FRAME_SAMPLE_INTERVAL != 0:
            continue

        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = face_mesh.process(rgb)

        if not results.multi_face_landmarks:
            skipped += 1
            continue

        lm = results.multi_face_landmarks[0]
        landmarks = np.array([(p.x, p.y, p.z) for p in lm.landmark], dtype=np.float64)

        left_ear = _calculate_ear(landmarks, LEFT_EYE)
        right_ear = _calculate_ear(landmarks, RIGHT_EYE)
        ear = (left_ear + right_ear) / 2.0
        mar = _calculate_mar(landmarks, MOUTH)
        pitch, yaw, roll = _calculate_head_pose(landmarks, h, w)

        ear_buffer.append(ear)
        mar_buffer.append(mar)

        ear_var = float(np.var(list(ear_buffer))) if len(ear_buffer) >= 2 else 0.0
        mar_var = float(np.var(list(mar_buffer))) if len(mar_buffer) >= 2 else 0.0
        blink_rate = _count_blinks(list(ear_buffer), fps)

        rows.append([
            ear, mar, pitch, yaw, roll,
            ear_var, mar_var, blink_rate,
            left_ear, right_ear,
            label,
        ])
        processed += 1

    pbar.close()
    cap.release()
    return rows, processed, skipped


# ═══════════════════════════════════════════════════════════════════
#  Main
# ═══════════════════════════════════════════════════════════════════

def main():
    if not os.path.isdir(DATA_DIR):
        print(f"ERROR: Dataset directory not found: {DATA_DIR}")
        print("Place your dataset folders inside data/raw/ and try again.")
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Discover images and videos
    image_groups, video_files = discover_dataset(DATA_DIR)

    total_images = sum(len(v) for v in image_groups.values())
    total_videos = len(video_files)

    if total_images == 0 and total_videos == 0:
        print(f"ERROR: No images or videos found in {DATA_DIR}")
        print("Expected subfolders like 'Drowsy/' and 'Non Drowsy/' with images inside.")
        sys.exit(1)

    print(f"Dataset: {DATA_DIR}")
    print(f"  Images found : {total_images} across {len(image_groups)} class(es)")
    print(f"  Videos found : {total_videos}")
    print()

    # Init MediaPipe
    mp_face = mp.solutions.face_mesh
    face_mesh = mp_face.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    all_rows = []
    total_processed = 0
    total_skipped = 0

    # ── Process image folders ────────────────────────────────────
    label_names = {v: k for k, v in LABEL_MAP.items()}
    for label_id, paths in image_groups.items():
        name = label_names.get(label_id, str(label_id))
        print(f"Processing images [{name}]: {len(paths)} files")
        rows, proc, skip = process_images(paths, face_mesh, label_id)
        all_rows.extend(rows)
        total_processed += proc
        total_skipped += skip

    # ── Process video files ──────────────────────────────────────
    for label_id, vpath in video_files:
        name = label_names.get(label_id, str(label_id))
        print(f"Processing video [{name}]: {os.path.relpath(vpath, DATA_DIR)}")
        rows, proc, skip = process_video(vpath, face_mesh, label_id)
        all_rows.extend(rows)
        total_processed += proc
        total_skipped += skip

    face_mesh.close()

    if not all_rows:
        print("\nERROR: No features extracted. Check dataset structure.")
        sys.exit(1)

    # Save CSV
    columns = FEATURE_COLUMNS + ["label"]
    df = pd.DataFrame(all_rows, columns=columns)
    df.to_csv(FEATURES_CSV, index=False)

    # Summary
    print(f"\n{'='*55}")
    print(f"  Feature Extraction Complete")
    print(f"{'='*55}")
    print(f"  Frames/images processed : {total_processed}")
    print(f"  Frames/images skipped   : {total_skipped} (no face detected)")
    print(f"  Total samples           : {len(df)}")
    print(f"  Saved to                : {FEATURES_CSV}")
    print(f"\n  Class distribution:")
    for label_name, label_id in LABEL_MAP.items():
        count = len(df[df["label"] == label_id])
        print(f"    {label_name:10s}: {count:>6d}")
    print(f"{'='*55}")


if __name__ == "__main__":
    main()
