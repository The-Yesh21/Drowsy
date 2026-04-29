"""
Drowsiness Detection System — Entry Point (Stage 1c - ONNX)

Opens webcam, runs face mesh detection, computes drowsiness metrics,
runs ONNX inference, and renders an overlay with alerts.

Controls:
    q — Quit
    s — Save snapshot
"""

import sys
import os
import argparse
import time
from collections import deque
import queue
import threading
import asyncio
import httpx

import cv2
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import EAR_HISTORY_SIZE, EAR_THRESHOLD, BACKEND_URL, SESSION_ID, DRIVER_ID

parser = argparse.ArgumentParser(description="Run Drowsiness Detector")
parser.add_argument("--session-id", type=str, help="Override .env SESSION_ID")
parser.add_argument("--driver-id", type=str, help="Override .env DRIVER_ID")
args, unknown = parser.parse_known_args()

ACTIVE_SESSION_ID = args.session_id or SESSION_ID
ACTIVE_DRIVER_ID = args.driver_id or DRIVER_ID

from detector.face_mesh import (
    FaceMeshDetector,
    LEFT_EYE_INDICES,
    RIGHT_EYE_INDICES,
    MOUTH_INDICES,
)
from detector.metrics import (
    calculate_ear,
    calculate_mar,
    calculate_head_pose,
    BlinkCounter,
)
from detector.ensemble import predict
from detector.alerter import AlertManager

# ── Colours (BGR) ─────────────────────────────────────────────────
COLOR_GREEN = (0, 220, 0)
COLOR_YELLOW = (0, 255, 255)
COLOR_ORANGE = (0, 165, 255)
COLOR_RED = (0, 0, 255)
COLOR_WHITE = (255, 255, 255)
COLOR_DARK = (30, 30, 30)

STATE_COLORS = {
    "ALERT": COLOR_GREEN,
    "MILD": COLOR_YELLOW,
    "DROWSY": COLOR_ORANGE,
    "CRITICAL": COLOR_RED,
}

# ── API Background Worker ─────────────────────────────────────────
api_queue = queue.Queue()

def api_worker():
    """Background thread running an async loop to post events."""
    async def _process_queue():
        async with httpx.AsyncClient() as client:
            while True:
                event_data = api_queue.get()
                if event_data is None: 
                    break
                try:
                    await client.post(f"{BACKEND_URL}/events", json=event_data, timeout=3.0)
                except Exception as e:
                    print(f"Failed to post to backend: {e}")
                finally:
                    api_queue.task_done()
    
    # Run the event loop for this thread
    asyncio.run(_process_queue())

# Start telemetry background thread
threading.Thread(target=api_worker, daemon=True).start()

def draw_overlay(frame, ear, mar, pitch, blink_rate, score, state, alert_cfg, fps_val):
    """Draw metrics, state indicator, and drowsiness bar on the frame."""
    h, w = frame.shape[:2]

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 90), COLOR_DARK, -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, f"EAR: {ear:.3f}", (15, 25), font, 0.55, COLOR_WHITE, 1)
    cv2.putText(frame, f"MAR: {mar:.3f}", (15, 50), font, 0.55, COLOR_WHITE, 1)
    cv2.putText(frame, f"Pitch: {pitch:.1f} deg", (15, 75), font, 0.55, COLOR_WHITE, 1)
    cv2.putText(frame, f"Blink: {blink_rate:.0f} bpm", (200, 25), font, 0.55, COLOR_WHITE, 1)
    cv2.putText(frame, f"FPS: {fps_val:.0f}", (200, 50), font, 0.55, COLOR_WHITE, 1)

    state_color = STATE_COLORS.get(state, COLOR_WHITE)
    text_size = cv2.getTextSize(state, font, 0.9, 2)[0]
    tx = w - text_size[0] - 20
    cv2.putText(frame, state, (tx, 40), font, 0.9, state_color, 2)

    score_label = f"ONNX Prob: {score:.2f}"
    cv2.putText(frame, score_label, (tx - 40, 70), font, 0.55, state_color, 1)

    bar_h, bar_y, bar_x, bar_w = 18, h - 28, 15, w - 30
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), COLOR_DARK, -1)
    fill_w = int(bar_w * score)
    if fill_w > 0:
        ratio = min(score, 1.0)
        r, g = int(255 * ratio), int(220 * (1 - ratio))
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_w, bar_y + bar_h), (0, g, r), -1)
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), COLOR_WHITE, 1)
    cv2.putText(frame, "Drowsiness Prob", (bar_x, bar_y - 5), font, 0.45, COLOR_WHITE, 1)

    if alert_cfg is not None:
        cv2.rectangle(frame, (0, 95), (w, 135), alert_cfg.get("color", COLOR_RED), -1)
        cv2.putText(frame, alert_cfg.get("label", "ALERT"), (15, 125), font, 0.7, COLOR_WHITE, 2)
        if alert_cfg.get("beep", False):
            print("\a", end="", flush=True)


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Cannot open webcam.")
        sys.exit(1)

    detector = FaceMeshDetector()
    alert_manager = AlertManager()
    
    # Initialize once before the loop
    blink_counter = BlinkCounter(
        ear_threshold=EAR_THRESHOLD,
        history_size=EAR_HISTORY_SIZE
    )

    ear_history = deque(maxlen=EAR_HISTORY_SIZE)
    mar_history = deque(maxlen=15)
    ear_variance_history = deque(maxlen=15)

    prev_time = time.time()
    fps_val = 0.0
    fps_print_time = time.time()
    snapshot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snapshots")

    print("\nPress 'q' to quit, 's' to save snapshot.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]

            landmarks = detector.process_frame(frame)
            detector.draw_landmarks(frame)

            if landmarks is not None:
                # Core metrics
                left_ear = calculate_ear(landmarks, LEFT_EYE_INDICES)
                right_ear = calculate_ear(landmarks, RIGHT_EYE_INDICES)
                ear = (left_ear + right_ear) / 2.0
                mar = calculate_mar(landmarks, MOUTH_INDICES)
                pitch, yaw, roll = calculate_head_pose(landmarks, frame.shape)

                # Temporal buffers
                ear_history.append(ear)
                mar_history.append(mar)
                ear_variance_history.append(ear)

                # Derived temporal metrics
                ear_var = float(np.var(list(ear_variance_history))) if len(ear_variance_history) >= 2 else 0.0
                mar_var = float(np.var(list(mar_history))) if len(mar_history) >= 2 else 0.0
                blink_rate = blink_counter.update(ear, fps_val if fps_val > 0 else 30)

                # ONNX Inference
                score, state, _ = predict(
                    ear, mar, pitch, yaw, roll, 
                    ear_var, mar_var, blink_rate, 
                    left_ear, right_ear
                )

                # Alerts and Overlay
                alert_cfg = alert_manager.update(state, ear, mar, pitch)
                draw_overlay(frame, ear, mar, pitch, blink_rate, score, state, alert_cfg, fps_val)

                # Send telemetry
                if state in ["MILD", "DROWSY", "CRITICAL"] and ACTIVE_SESSION_ID and ACTIVE_DRIVER_ID:
                    api_queue.put({
                        "session_id": ACTIVE_SESSION_ID,
                        "driver_id": ACTIVE_DRIVER_ID,
                        "state": state,
                        "drowsiness_score": score,
                        "ear": float(ear),
                        "mar": float(mar),
                        "pitch": float(pitch),
                        "yaw": float(yaw),
                        "blink_rate": float(blink_rate)
                    })
            else:
                cv2.putText(frame, "No face detected", (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLOR_RED, 2)

            now = time.time()
            if (now - prev_time) > 0:
                fps_val = 1.0 / (now - prev_time)
            prev_time = now

            if now - fps_print_time >= 1.0:
                print(f"FPS: {fps_val:.1f}")
                fps_print_time = now

            cv2.imshow("Drowsiness Detection (ONNX)", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("s"):
                os.makedirs(snapshot_dir, exist_ok=True)
                fname = os.path.join(snapshot_dir, f"snapshot_{time.strftime('%Y%m%d_%H%M%S')}.jpg")
                cv2.imwrite(fname, frame)
                print(f"📸 Snapshot saved: {fname}")

    except KeyboardInterrupt:
        pass
    finally:
        detector.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
