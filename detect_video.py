import cv2 as cv


if __name__ == "__main__":
    # Ardi: Use video instead
    print("\nReading video:")
    # cap = cv.VideoCapture("data/5g-dive/customTest_MIRC-Roadside-5s.mp4")
    cap = cv.VideoCapture("http://140.113.86.92:10000/drone-3.flv")
    cv.namedWindow("Image", cv.WND_PROP_FULLSCREEN)
    cv.resizeWindow("Image", 1366, 768) # Enter your size
    while (cap.isOpened()):
        # ret = a boolean return value from getting the frame, frame = the current frame being projected in the video
        try:
            ret, frame = cap.read()

            cv.imshow("Image", frame)
        except:
            print("No more frame to show.")
            break

        if cv.waitKey(10) & 0xFF == ord('q'):
            break
    # The following frees up resources and closes all windows
    cap.release()
    cv.destroyAllWindows()
