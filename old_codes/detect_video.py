import cv2 as cv
from libs.addons.streamer.my_fps import MyFPS


if __name__ == "__main__":
    # Ardi: Use video instead
    print("\nReading video:")

    cv.namedWindow("Image", cv.WND_PROP_FULLSCREEN)
    cv.moveWindow("Image", 0, 0)
    cv.resizeWindow("Image", 1366, 768)  # Enter your size

    # cap = cv.VideoCapture("data/5g-dive/videos/customTest_MIRC-Roadside-5s.mp4")
    cap = cv.VideoCapture("data/5g-dive/videos/customTest_MIRC-Roadside-20s.mp4")
    # cap = cv.VideoCapture("http://140.113.86.92:10000/drone-3.flv")

    fps = MyFPS().start()
    while cap.isOpened():
        # ret = a boolean return value from getting the frame, frame = the current frame being projected in the video
        try:
            ret, frame = cap.read()

            cv.imshow("Image", frame)
            print("[CURRENT INFO] approx. FPS: {:.2f}".format(fps.current_fps()))
        except:
            print("No more frame to show.")
            break

        if cv.waitKey(1) & 0xFF == ord('q'):
            break
        fps.update()

    # stop the timer and display FPS information
    fps.stop()
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    # The following frees up resources and closes all windows
    cap.release()
    cv.destroyAllWindows()
