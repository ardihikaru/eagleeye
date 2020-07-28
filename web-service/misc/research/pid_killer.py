import os
import signal

pid = 8266
os.kill(pid, signal.SIGTERM) # or signal.SIGKILL