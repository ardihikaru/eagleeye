from multiprocessing import shared_memory
import numpy as np
import time
import cv2
# from utils.datasets import letterbox

# a = np.array([1, 1, 2, 3, 5, 8])  # Start with an existing NumPy array
img_size = 832
path = "../out1.png"
img = cv2.imread(path)
print(" --- img.shape:", img.shape)
print(" --- img.dtype:", img.dtype)

##############
# Padded resize
# t0_letterbox = time.time()
# yolo_img = letterbox(img, new_shape=img_size)[0]
# t1_letterbox = time.time() - t0_letterbox
# print('\nLatency [Letterbox] in: (%.5fs)' % (t1_letterbox*1000))
# print(" --- yolo_img.shape:", yolo_img.shape)
# print(" --- yolo_img.dtype:", yolo_img.dtype)

# Convert
# t0_convert = time.time()
# yolo_img = yolo_img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
# # yolo_img = np.ascontiguousarray(yolo_img, dtype=np.float16 if self.half else np.float32)  # uint8 to fp16/fp32
# yolo_img = np.ascontiguousarray(yolo_img, dtype=np.float32)  # uint8 to fp16/fp32
# yolo_img /= 255.0  # 0 - 255 to 0.0 - 1.0
# t1_convert = time.time() - t0_convert
# print('\nLatency [Convert] in: (%.5fs)' % (t1_convert*1000))

# print(" --- NEW yolo_img.shape:", yolo_img.shape)
# print(" --- NEW yolo_img.dtype:", yolo_img.dtype)
# print(" --- NEW yolo_img.nbytes:", yolo_img.nbytes)

# t0_shm = time.time()
# shm_yolo = shared_memory.SharedMemory(create=True, size=yolo_img.nbytes, name="yolo_shm_001")
# t1_shm = time.time() - t0_shm
# print('\nLatency [YOLO][Creating shm variable] in: (%.5fs)' % (t1_shm*1000))

# t0_assign_shm = time.time()
# copy_yolo_img = np.ndarray(yolo_img.shape, dtype=yolo_img.dtype, buffer=shm_yolo.buf)
# copy_yolo_img[:] = yolo_img[:]  # Copy the original data into shared memory
# t1_assign_shm = time.time() - t0_assign_shm
# print('\nLatency [YOLO][Assign img value into shm value] in: (%.5fs)' % (t1_assign_shm*1000))
#############

t0_shm = time.time()
shm = shared_memory.SharedMemory(create=True, size=img.nbytes, name="my_shm_001")
t1_shm = time.time() - t0_shm
print('\nLatency [Creating shm variable] in: (%.5fs)' % (t1_shm*1000))

t0_assign_shm = time.time()
# Now create a NumPy array backed by shared memory
b = np.ndarray(img.shape, dtype=img.dtype, buffer=shm.buf)
b[:] = img[:]  # Copy the original data into shared memory
t1_assign_shm = time.time() - t0_assign_shm
print('\nLatency [Assign img value into shm value] in: (%.5fs)' % (t1_assign_shm*1000))

# print(" --- b:", b)
print(" --- TYPE b:", type(b))
# print(" --- TYPE img:", type(img))
print(" --- shm.name:", shm.name)

# cv2.imshow('image', img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

time.sleep(20)
# time.sleep(2)

shm.close()
shm.unlink()
# shm_yolo.close()
# shm_yolo.unlink()
print(" --- closing app ..")