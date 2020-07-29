from subprocess import Popen
import os
import signal
import time

pid = os.getpid()
print(" --- THIS PID", pid)

for i in range(1, 3):
	print(" --- i:", i)
	process = Popen('python detection.py -c etc/detection.conf', shell=True)
	print(" --- CHILD ID", process.pid)
	time.sleep(5)

	os.kill(process.pid, signal.SIGTERM)  # or signal.SIGKILL
	print(" --- killed [PID=%s] after 5 seconds" % str(process.pid))

# time.sleep(40)

print(" ---- ENDED ..")
