import cv2
import time
root_path = "/home/s010132/devel/eagleeye/data/out1.png"
# root_path = "test.png"
image = cv2.imread(root_path)

img_1d = image.reshape(1, -1)

#%%
import numpy as np
# data = [('Ardi', img_1d)]
data = [('Ardi', False, time.time(), img_1d)]
print(data)
table = np.array(data,
                 dtype=[('id', 'U10'),
                        ('store_enabled', '?'),
                        ('timestamp', 'f'),
                        ('image', [('pixel', 'i')], (1, 6220800))
                        ]
                 )

print(table.shape)
print(table.shape)
print(table["id"])
print(table["store_enabled"])
print(table["timestamp"])
print(table["image"].shape)
print(table["image"]["pixel"][0].shape)
img_ori = table["image"]["pixel"][0].reshape(1080, 1920, 3)
print(img_ori.shape)

#%%
# Coba to bytes
bytes_table = table.tobytes()
print("SHAPE:", table.shape)
print(type(bytes_table))

#%%
# balikin ...
deserialized_bytes = np.frombuffer(bytes_table,
                                   dtype=[('id', 'U10'),
                                          ('store_enabled', '?'),
                                          ('timestamp', 'f'),
                                          ('image', [('pixel', 'i')], (1, 6220800))
                                          ])
print(type(deserialized_bytes))
# print(deserialized_bytes.shape)

print(deserialized_bytes["id"][0])
print(deserialized_bytes["store_enabled"][0])
print(deserialized_bytes["timestamp"][0])
print(deserialized_bytes["image"].shape)
print(deserialized_bytes["image"]["pixel"][0].shape)
img_ori = deserialized_bytes["image"]["pixel"][0].reshape(1080, 1920, 3)

# print(deserialized_bytes)
# deserialized_img = np.reshape(deserialized_bytes, newshape=(1080, 1920, 3))

import matplotlib.pyplot as plt
import cv2

b,g,r = cv2.split(img_ori)           # get b, g, r
rgb_img1 = cv2.merge([r,g,b])     # switch it to r, g, b

plt.imshow(rgb_img1)
