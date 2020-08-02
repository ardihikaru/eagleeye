import cv2
import numpy as np
import glob

fps = 30
img_array = []
imgs = sorted(glob.glob('video_frames/*.jpg'))
# print("max frames:", len(imgs))
size = None
for i in range (len(imgs)):
# for i in range (100):
    frame_id = i + 1
    filename = "video_frames/frame-" + str(frame_id) + ".jpg"
    print(" >> filename: ", filename)
# for filename in glob.glob('C:/New folder/Images/*.jpg'):
# for filename in imgs:
#     print(" filename: ", filename)
    img = cv2.imread(filename)
    height, width, layers = img.shape
    size = (width, height)
    img_array.append(img)
    # print(height, width, layers)

# out = cv2.VideoWriter('project.avi', cv2.VideoWriter_fourcc(*'DIVX'), 15, size)
out = cv2.VideoWriter('project.avi', cv2.VideoWriter_fourcc(*'DIVX'), fps, size)

for i in range(len(img_array)):
    out.write(img_array[i])
out.release()

print("DONE.")
