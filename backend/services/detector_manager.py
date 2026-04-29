import subprocess
import os
import logging
import psutil

log = logging.getLogger("uvicorn")

class DetectorManager:
    """Manages the lifecycle of the local webcam detector python subprocess"""
    
    def __init__(self):
        self.active_process = None
        self.script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "main.py")

    def start_detector(self, session_id: str, driver_id: str) -> bool:
        if self.active_process and self.active_process.poll() is None:
            log.warning("Detector is already running.")
            return False

        if not os.path.exists(self.script_path):
            log.error(f"Detector script not found at {self.script_path}")
            return False

        try:
            log.info(f"Starting detector subprocess for session {session_id} and driver {driver_id}")
            # Run the root directory main.py
            self.active_process = subprocess.Popen(
                ["python", self.script_path, "--session-id", session_id, "--driver-id", driver_id],
                cwd=os.path.dirname(self.script_path)
            )
            return True
        except Exception as e:
            log.error(f"Failed to start subprocess: {e}")
            self.active_process = None
            return False

    def stop_detector(self) -> bool:
        if not self.active_process or self.active_process.poll() is not None:
            return False

        try:
            pid = self.active_process.pid
            log.info(f"Terminating detector subprocess PID {pid}")
            
            # Use psutil to kill process and any children cleanly
            parent = psutil.Process(pid)
            for child in parent.children(recursive=True):
                child.terminate()
            parent.terminate()
            
            # Wait for clean exit, otherwise forcefully kill
            gone, still_alive = psutil.wait_procs(parent.children(recursive=True) + [parent], timeout=3)
            for p in still_alive:
                p.kill()
                
            self.active_process = None
            return True
        except psutil.NoSuchProcess:
            self.active_process = None
            return True
        except Exception as e:
            log.error(f"Failed to cleanly stop subprocess: {e}")
            return False

    def is_running(self) -> bool:
        return self.active_process is not None and self.active_process.poll() is None

# Singleton state
manager = DetectorManager()
