from subprocess import call
from subprocess import Popen
import os
import time

pid = os.getpid()
print(" --- THIS PID", pid)

for i in range(1, 3):
	print(" --- i:", i)
	# process = Popen('python sample_worker.py --node %s' % str(i), shell=True)
	process = Popen('python misc/research/sample_worker.py --node %s' % str(i), shell=True)

	print(" --- CHILD ID", process.pid)

time.sleep(40)

print(" ---- ENDED ..")
