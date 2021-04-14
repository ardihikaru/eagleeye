import time
from datetime import datetime
import logging
import simplejson as json

###

L = logging.getLogger(__name__)


###

# strg = 'user input'
t0_publish = time.time()
info = {
	"id": 1,
	"store_enabled": "False",
	"timestamp": time.time()
}
strg = json.dumps(info)
print(strg)
t1_publish = (time.time() - t0_publish) * 1000
L.warning(('\n[%s] Latency Dump (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_publish)))
# strg = str(time.time())

t0_publish = time.time()
i = int.from_bytes(strg.encode('utf-8'), byteorder='big')
t1_publish = (time.time() - t0_publish) * 1000
L.warning(('\n[%s] Latency Encrypt (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_publish)))

t0_publish = time.time()
s = int.to_bytes(i, length=len(strg), byteorder='big').decode('utf-8')
t1_publish = (time.time() - t0_publish) * 1000
L.warning(('\n[%s] Latency Decrypt (%.3f ms) \n' % (datetime.now().strftime("%H:%M:%S"), t1_publish)))

print(">>>> strg: ", strg)
print(">>>> i: ", i)
print(">>>> s: ", s)
