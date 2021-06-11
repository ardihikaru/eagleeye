import cv2

cap = cv2.VideoCapture(0)

window_title = "output-raw"
cv2.namedWindow(window_title, cv2.WND_PROP_FULLSCREEN)
# cv2.resizeWindow("Image", 1920, 1080)  # Enter your size
cv2.resizeWindow(window_title, 800, 550)  # Enter your size

while cap.isOpened():
	ret, frame = cap.read()

	if ret:
		# print(" >>> frame SHAPE:", frame.shape)
		cv2.imshow(window_title, frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

cap.release()
cv2.destroyAllWindows()
