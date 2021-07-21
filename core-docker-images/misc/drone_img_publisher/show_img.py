import cv2

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

window_title = "output-raw"
cv2.namedWindow(window_title, cv2.WND_PROP_FULLSCREEN)
# cv2.resizeWindow("Image", 1920, 1080)  # Enter your size
cv2.resizeWindow(window_title, 800, 550)  # Enter your size

while cap.isOpened():
	ret, frame = cap.read()

	if ret:
		print(" ## Img SHAPE:", frame.shape)
		cv2.imshow(window_title, frame)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

cap.release()
cv2.destroyAllWindows()
