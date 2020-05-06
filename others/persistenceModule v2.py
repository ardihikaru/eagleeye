# Persistence Module v1
# 	Compiled:	05 May 2020

# Sliding Window implementation: https://github.com/imravishar/sliding_window
from window_slider import Slider
import numpy as np

#PERSISTENCE_WINDOW = 45 # 1.5s for a 30FPS video
#TOLERANCE_LIMIT = 15 # 0.5s for a 30FPS video

# e.g. make it 5 seconds
PERSISTENCE_WINDOW = 3
TOLERANCE_LIMIT = 1

def getPersistenceBatch():
	#checkBatch = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
	#checkBatch = np.array([1, 2, 3, 4, 4, 6, 7, 8, 9, 10])
	#checkBatch = np.array([1, 2, 3, 4, 4, 4, 7, 8, 9, 10])
	checkBatch = np.array([1, 4, 99])
	print("[DBG] Original checkBatch: %s" % str(checkBatch))
	return checkBatch

# Check for persistence of a batch
def persistenceModule(checkBatch):
	persistenceCount = 0
	toleranceCount = 0

	# Get endFrameID
	endFrameID = checkBatch[PERSISTENCE_WINDOW - 1]

	while persistenceCount < PERSISTENCE_WINDOW - 1:
		currentFrameID = checkBatch[persistenceCount]
		nextFrameID = checkBatch[persistenceCount + 1]

		# Check next frame to see whether 'Flag' object is stil detected
		if (currentFrameID + 1) != nextFrameID:
			toleranceCount += 1
		
		persistenceCount += 1

	persistenceCount += 1 # Since the first frameID contributes to a count

	if toleranceCount <= TOLERANCE_LIMIT:
		print("[DBG] 	PiH Detected! Send frameID ", endFrameID)
		#sendFrameID(endFrameID)
		
		print("[DBG] 	persistenceCount=%d; toleranceCount=%d" % (persistenceCount, toleranceCount))
	else:
		print("[DBG] 	PiH not detected!")
		print("[DBG] 	persistenceCount=%d; toleranceCount=%d" % (persistenceCount, toleranceCount))

# Sliding window implementation of persistenceModule
def persistenceModuleWindow():
	# Get checkBatch
	checkBatch = getPersistenceBatch()

	# window_slider parameter
	bucket_size = PERSISTENCE_WINDOW
	overlap_count = PERSISTENCE_WINDOW - TOLERANCE_LIMIT

	# Sliding Window
	slider = Slider(bucket_size, overlap_count)
	slider.fit(checkBatch)

	while True:
		window_data = slider.slide()

		# Stop if the window_data does not have enough data
		if window_data.shape[0] < PERSISTENCE_WINDOW:
			break

		print("[DBG]  window_data: %s" % str(window_data))
		persistenceModule(window_data)
		
		if slider.reached_end_of_list():
			break

if __name__ == '__main__':
	persistenceModuleWindow()