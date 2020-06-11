## 2.0.3-mobileheroes2020 (June 11, 2020)
  - Merge branch 'feature/ads-integration' into develop
  - added results for mobileheroes2020 figures
  - added another experimental data
  - bug fixed
  - added graph generator
  - added another experimental data
  - added experimental data for worker=2
  - latency graph for EagleEYE v2
  - Added 1 sec delay for dummy data
  - Tested A-DNS new features
  - A-DNS: Automatically send the cur. GPS information
  - integration with A-DNS: Collect and Store GPS data
  - Merge branch 'release-2.0.2-video-demo' into develop

## 2.0.2-video-demo (June 04, 2020)
  - last changes only for video demo @ 9th June 2020
  - Merge branch 'release-2.0.1' into develop

## 2.0.1 (May 21, 2020)
  - Merge branch 'feature/readme' into develop
  - test
  - Merge branch 'release-2.0' into develop

## 2.0 (May 21, 2020)
  - Merge branch 'feature/readme' into develop
  - Updated readme to reflect the newest command to run
  - Merge branch 'feature/eagleeyev2.1' into develop
  - prioritize sending raw frames into YOLO network first, then, stream raw frames
  - change window name
  - bug fixed: window size and window position
  - change argparse name from `sub_channel` into `node`
  - standardize color of Person and Flag objects
  - disable confidence_score outputted into labels
  - added frame information
  - change original frame visualizer from SubProcess into normal process using pubsub to notify the visualizer app
  - Updated broken link in README
  - Added documentation for RTMP Server Setup
  - Added documentation for ffmpeg HTTP streaming
  - add new feature to disable FPS information
  - added waiting time limit to prevent PiH Location Fetcher for executing infinite loop due to waiting worker node's result
  - tested with weight TM-07
  - bug fixed: unable to feed frames into visualizer asynchronously
  - Added more content to various sections, updated figure
  - Updated the readme with figures
  - Updated README
  - added side-by-side with original input stream
  - added processing latency for each frame
  - resize the plotted GPS information
  - added visualizer side-by-side
  - added visualizer with original frame
  - Merge branch 'release-1.2' into develop

## 1.2.0 (May 15, 2020)
  - Merge branch 'feature/eagleeyev2' into develop
  - automate read number of collected drone data
  - update saved image path; update exported file path
  - disable log
  - update log information
  - bug fixed: infinite loop when waiting the bbox result from yolo network
  - fixed infinite loop when waiting available worker
  - moved and denoted as worker_finder() function
  - update logs;
  - updated logs in PiH location fetcher
  - revised logs in yolo worker
  - revised stored fps information; update log in visualizer
  - update log
  - updated FPS calculation
  - bug fixed: show GPS information; bug show in visualizer
  - Merge branch 'release-1.1' into develop

## 1.1.0 (May 12, 2020)
  - Merge branch 'feature/eagleeyev2' into develop
  - changed frame extractor into thread-based frame extractor
  - bug fixed: FPS calculation;
  - Set PiH label to the front
  - added information in each resulted frame
  - added latency exporter; added latency graph
  - default values
  - added latency information
  - remove unused vars
  - added testing code for reading video stream
  - clean up unused print and comments
  - added Visualizer component
  - fix fps calculation
  - bug fix: fps calculation
  - split functions of: PiH Location Fetcher, Monitoring (GUI)
  - tidy up printing informations
  - refactored printing information; changed `PiH Candidate` label into `FALSE PiH`
  - added latency information; FOUND bug: unable to work async
  - added persistence detection (v1) algorithm
  - Merge branch 'release-1.0' into develop

## 1.0 (May 06, 2020)
  - Merge branch 'feature/eagleeyev1' into develop
  - New feature: allow viewer to plot both YOLOv3 BBox and MBBox
  - finished development of EagleEYE_v1
  - changed export pih json format
  - remove comments
  - remove unused print and comments
  - bug fixed: show default BBox in CV Out
  - added new function: Get GPS Data
  - added GPS Data Collector
  - refactoring codes
  - bug fixed: - CV window position - export stored PiH coordinates - Store BBox and MBBox coordinates
  - added functional in result viewer v2
  - Merge branch 'feature/image-streamer' into develop
  - added viewer v2 core code
  - update storage configuration; update argparser
  - finished sending and reading image data through ZMQ TCP
  - tested send via TCP
  - fixed TCP send/recv; added PCA testing
  - playing with ZMQ
  - Merge branch 'feature/udp-data-transfer' into develop
  - finished testing image streaming
  - change info
  - finish testing.
  - changed tag
  - added redis dockerfile

## 0.1.0 (四月 14, 2020)
  - migrated codes from old repo @ yolov3/feature/modv2
  - Initial commit

