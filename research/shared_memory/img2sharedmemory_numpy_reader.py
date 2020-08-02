# In either the same shell or a new Python shell on the same machine

from multiprocessing import shared_memory
import numpy as np
import cv2
import time

t0_shm = time.time()
# Attach to the existing shared memory block
existing_shm = shared_memory.SharedMemory(name='my_shm_001')
t1_shm = time.time() - t0_shm
print('\nLatency [Attach to the existing shared memory block] in: (%.5fs)' % (t1_shm*1000))

t0_assign_shm = time.time()
# Note that a.shape is (6,) and a.dtype is np.int64 in this example
my_img = np.ndarray((1080, 1920, 3), dtype=np.uint8, buffer=existing_shm.buf)
# print(" --- my_img:", my_img)
t1_assign_shm = time.time() - t0_assign_shm
print('\nLatency [Assign variable] in: (%.5fs)' % (t1_assign_shm*1000))

########## SHM YOLO
t0_shm_yolo = time.time()
# Attach to the existing shared memory block
existing_shm_yolo = shared_memory.SharedMemory(name='yolo_shm_001')
t1_shm_yolo = time.time() - t0_shm_yolo
print('\nLatency [YOLO][Attach to the existing shared memory block] in: (%.5fs)' % (t1_shm_yolo*1000))

t0_assign_shm_yolo = time.time()
# Note that a.shape is (6,) and a.dtype is np.int64 in this example
my_img_yolo = np.ndarray((3, 480, 832), dtype=np.float32, buffer=existing_shm_yolo.buf)
# print(" --- my_img:", my_img)
t1_assign_shm_yolo = time.time() - t0_assign_shm_yolo
print('\nLatency [YOLO][Assign variable] in: (%.5fs)' % (t1_assign_shm_yolo*1000))
########## SHM YOLO

cv2.imshow('image', my_img)
# cv2.imshow('image', my_img_yolo)
cv2.waitKey(0)
cv2.destroyAllWindows()

# c[-1] = 888
# print(" --- c baru:", c)

# Clean up from within the second Python shell
existing_shm.close()
