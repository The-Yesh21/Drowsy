"""
Alert management — persistence tracking, cooldowns, severity levels, and logging.
"""

import time
from dataclasses import dataclass, field
from typing import List, Optional

from config import CONSECUTIVE_FRAMES, ALERT_COOLDOWN_SECONDS


@dataclass
class AlertRecord:
    timestamp: float
    state: str
    ear: float
    mar: float
    head_pitch: float

    def __str__(self):
        t = time.strftime("%H:%M:%S", time.localtime(self.timestamp))
        return f"[{t}] {self.state}  EAR={self.ear:.3f} MAR={self.mar:.3f} Pitch={self.head_pitch:.1f}°"


ALERT_CONFIG = {
    "MILD": {
        "color": (0, 255, 255),
        "label": "⚠ MILD DROWSINESS",
        "beep": False,
    },
    "DROWSY": {
        "color": (0, 165, 255),
        "label": "⚠ DROWSY — STAY ALERT!",
        "beep": True,
    },
    "CRITICAL": {
        "color": (0, 0, 255),
        "label": "🚨 CRITICAL — PULL OVER!",
        "beep": True,
    },
}


class AlertManager:
    def __init__(
        self,
        consecutive_threshold: int = CONSECUTIVE_FRAMES,
        cooldown_seconds: float = ALERT_COOLDOWN_SECONDS,
    ):
        self.consecutive_threshold = consecutive_threshold
        self.cooldown_seconds = cooldown_seconds
        self._current_state: str = "ALERT"
        self._frame_count: int = 0
        self._last_alert_time: float = 0.0
        self.alert_log: List[AlertRecord] = []
        self._active_alert: Optional[str] = None

    def update(self, state: str, ear: float, mar: float, head_pitch: float):
        now = time.time()

        if state == self._current_state:
            self._frame_count += 1
        else:
            self._current_state = state
            self._frame_count = 1

        if state == "ALERT":
            self._active_alert = None
            return None

        if self._frame_count < self.consecutive_threshold:
            if self._active_alert and self._active_alert == state:
                return ALERT_CONFIG.get(state)
            return None

        if (now - self._last_alert_time) < self.cooldown_seconds:
            if self._active_alert:
                cfg = ALERT_CONFIG.get(state, {}).copy()
                cfg["beep"] = False
                return cfg
            return None

        self._last_alert_time = now
        self._active_alert = state
        record = AlertRecord(now, state, ear, mar, head_pitch)
        self.alert_log.append(record)
        print(f"ALERT: {record}")
        return ALERT_CONFIG.get(state)
