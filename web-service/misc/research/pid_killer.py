import os
import signal

pid = 71546
os.kill(pid, signal.SIGTERM)  # or signal.SIGKILL