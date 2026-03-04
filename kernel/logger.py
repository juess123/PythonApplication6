
import os
import time
import threading

_LOG_FILE = os.path.join(os.path.dirname(__file__), "clip.log")
_lock = threading.Lock()


def log(msg, *, tag="INFO"):
    return
    # ts = time.strftime("%Y-%m-%d %H:%M:%S")
    # line = f"[{ts}] [{tag}] {msg}\n"

    # try:
    #     with _lock:
    #         with open(_LOG_FILE, "a", encoding="utf-8") as f:
    #             f.write(line)
    # except Exception:
    #     pass