from io import BytesIO
import cv2 as cv

img_path = "data/out1.png"
frame = cv.imread(img_path)

imagefile = BytesIO()
frame.save(imagefile, format='PNG')
imagedata = imagefile.getvalue()
print("img data: ", imagedata)
