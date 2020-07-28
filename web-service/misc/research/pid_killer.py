import os
import signal

pid = 1107
os.kill(pid, signal.SIGTERM) #or signal.SIGKILL