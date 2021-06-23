from zenoh_lib.zenoh_net_publisher import ZenohNetPublisher
import sys
import time
from datetime import datetime
import numpy as np
import cv2
import simplejson as json
from enum import Enum
import logging
import argparse
from extras.functions import humanbytes as fsize

# FullHD Format; fixed value, as per required in 5G-DIVE Project
FULLHD_WIDTH = 1920
FULLHD_HEIGHT = 1024

# Encoding parameter
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]  # The default value for IMWRITE_JPEG_QUALITY is 95

# --- [START] Command line argument parsing --- --- --- --- --- ---
parser = argparse.ArgumentParser(
	description='Zenoh Publisher example')
parser.add_argument('--peer', '-e', dest='peer',  # e.g. 140.113.193.134 (Little Boy)
                    metavar='LOCATOR',
                    action='append',
                    type=str,
                    help='Peer locators used to initiate the zenoh session.')
parser.add_argument('--path', '-p', dest='path',
                    default='/eagleeye/svc/zenoh-python-pub',
                    type=str,
                    help='The name of the resource to publish.')
parser.add_argument('--video', '-v', dest='video',
                    default="0",
                    type=str,
                    help='The name of the resource to publish.')
parser.add_argument('--pwidth', dest='pwidth', default=1920, type=int, help='Target width to publish')
parser.add_argument('--pheight', dest='pheight', default=1080, type=int, help='Target height to publish')
parser.add_argument('--cvout', dest='cvout', action='store_true', help="Use CV Out")
parser.add_argument('--resize', dest='resize', action='store_true', help="Force resize to FullHD")
parser.set_defaults(cvout=False)
parser.set_defaults(resize=False)

args = parser.parse_args()
print(args)
# --- [END] Command line argument parsing --- --- --- --- --- ---

###

L = logging.getLogger(__name__)


###

def encrypt_str(str_val, byteorder="little"):
	encrypted_bytes = str_val.encode('utf-8')
	encrypted_val = int.from_bytes(encrypted_bytes, byteorder)  # `byteorder` must be either 'little' or 'big'
	return encrypted_val  # max 19 digit


peer = args.peer
if peer is not None:
	peer = ",".join(args.peer)

video_path = args.video
if video_path == "0":
	video_path = int(video_path)

# Enable / disable cvout
_enable_cv_out = args.cvout

# configure zenoh service
path = args.path
z_svc = ZenohNetPublisher(
	_path=path, _session_type="PUBLISHER", _peer=peer
)
z_svc.init_connection()

# register and collect publisher object
z_svc.register()
publisher = z_svc.get_publisher()

#########################
# Zenoh related variables

window_title = "img-data-publisher"

published_height, published_weight = args.pheight, args.pwidth  # target width and height
cam_weight, cam_height = None, None  # default detected width and height

cap = cv2.VideoCapture(video_path)

# change the image property
# use `$ v4l2-ctl --list-formats-ext` to check the available format!
# install first (if not yet): `$ sudo apt install v4l-utils`
cap.set(cv2.CAP_PROP_FRAME_WIDTH, published_weight)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, published_height)

if _enable_cv_out:
	cv2.namedWindow(window_title, cv2.WND_PROP_FULLSCREEN)
	# cv2.resizeWindow("Image", 1920, 1080)  # Enter your size
	cv2.resizeWindow(window_title, 800, 550)  # Enter your size
_frame_id = 0

# Extra information (to be tagged into the frame)
int_drone_id = encrypt_str("1")  # contains 1 extra slot
extra_len = 8  # contains 1 extra slot; another one slot is from `tagged_data_len` variable

while cap.isOpened():
	_frame_id += 1

	# generate encrypted frame_id
	eframe_id = encrypt_str(str(_frame_id))

	# ret = a boolean return value from getting the frame, frame = the current frame being projected in the video
	try:
		ret, frame = cap.read()

		# do it ONCE
		# detect width and height
		if cam_weight is None:
			cam_height, cam_weight, _ = frame.shape

		print(" ## Initial image SHAPE:", frame.shape)

		t0_decoding = time.time()
		# resize the frame; Default VGA (640 x 480) for Laptop camera
		if cam_weight != FULLHD_WIDTH and args.resize:
			frame = cv2.resize(frame, (FULLHD_WIDTH, FULLHD_HEIGHT))

		print(" ## Final image SHAPE:", frame.shape)
		# compress image
		# NEW encoding method
		encoder_format = None  # disable custom encoder
		itype = 4  # new type specially for compressed image
		t0_img_compression = time.time()
		_, compressed_img = cv2.imencode('.jpg', frame, encode_param)
		compressed_img_len, _ = compressed_img.shape
		t1_img_compression = (time.time() - t0_img_compression) * 1000
		t1_img_compression = round(t1_img_compression, 3)
		print(('[%s] Latency Image Compression (%.3f ms) ' % (
			datetime.now().strftime("%H:%M:%S"), t1_img_compression)))
		tagged_data_len = compressed_img_len + extra_len  # `tagged_data_len` itself contains 1 extra slot

		# create t0
		t0_array = str(time.time()).split(".")  # contains 2 extra slots

		# generate img compression latency
		img_compr_lat_arr = str(t1_img_compression).split(".")  # contains 2 extra slots

		# generate encrypted frame_id
		eframe_id = encrypt_str(str(_frame_id))

		# vertically tag this frame with an extra inforamtion
		t0_tag_extraction = time.time()
		tagged_info = [
			[int_drone_id],
			[int(t0_array[0])],
			[int(t0_array[1])],
			[eframe_id],
			[int(img_compr_lat_arr[0])],
			[int(img_compr_lat_arr[1])],
			[extra_len],
			[tagged_data_len],
		]
		val = np.vstack([compressed_img, tagged_info])
		t1_tag_extraction = (time.time() - t0_tag_extraction) * 1000
		print(('[%s] Latency Image Taging (%.3f ms) ' % (datetime.now().strftime("%H:%M:%S"), t1_tag_extraction)))

		# publish data
		z_svc.publish(
			_val=val,
			_itype=itype,
		)

		if _enable_cv_out:
			cv2.imshow(window_title, frame)
		print()
	except Exception as e:
		print("No more frame to show: `{}`".format(e))
		break

	if _enable_cv_out:
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

if _enable_cv_out:
	# The following frees up resources and closes all windows
	cap.release()
	cv2.destroyAllWindows()
#########################

# closing Zenoh publisher & session
z_svc.close_connection(publisher)
