import cv2
while True:
  im = cv2.imread("/app/misc/out1.png")
  im = cv2.resize(im, (256, 256))
  cv2.imshow("GoCoding", im)
  key = cv2.waitKey(10) & 0xFF
  if key == 27 or key == ord('q'):
    break
