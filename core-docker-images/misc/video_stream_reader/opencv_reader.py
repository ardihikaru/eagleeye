import cv2 as cv

if __name__ == "__main__":
    # Ardi: Use video instead
    print("\nReading video:")
    window_title = "output-raw"
    # cap = cv.VideoCapture("rtsp://localhost/test")
    # cap = cv.VideoCapture("rtsp://192.168.42.1/live")
    # cap = cv.VideoCapture("rtsp://192.168.1.250/0137")
    cap = cv.VideoCapture("rtsp://192.168.1.250/output-raw")
    cv.namedWindow(window_title, cv.WND_PROP_FULLSCREEN)
    # cv.resizeWindow("Image", 1920, 1080)  # Enter your size
    cv.resizeWindow(window_title, 800, 550)  # Enter your size
    while (cap.isOpened()):
        # ret = a boolean return value from getting the frame, frame = the current frame being projected in the video
        try:
            ret, frame = cap.read()

            cv.imshow(window_title, frame)
        except:
            print("No more frame to show.")
            break

        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    # The following frees up resources and closes all windows
    cap.release()
    cv.destroyAllWindows()
