from libs.addons.streamer.FileVideoStream import FileVideoStream

# import the necessary packages
from imutils.video import FileVideoStream
from libs.addons.streamer.my_fps import MyFPS
import time
import cv2

print("[INFO] starting video file thread...")
video = "data/5g-dive/videos/customTest_MIRC-Roadside-20s.mp4"
fvs = FileVideoStream(video).start()
time.sleep(1.0)

cv2.namedWindow("Frame", cv2.WND_PROP_FULLSCREEN)
cv2.moveWindow("Frame", 0, 0)
cv2.resizeWindow("Frame", 1366, 786)

fps = MyFPS().start()
# loop over frames from the video file stream
while fvs.more():
    try:
        # grab the frame from the threaded video file stream, resize
        # it, and convert it to grayscale (while still retaining 3 channels)
        frame = fvs.read()

        # show the frame and update the FPS counter
        cv2.imshow("Frame", frame)
        cv2.waitKey(1)
        fps.update()
        print("[CURRENT INFO] approx. FPS: {:.2f}".format(fps.current_fps()))
    except Exception as e:
        print("error: ", e)
        pass

# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
# do a bit of cleanup
cv2.destroyAllWindows()
fvs.stop()
