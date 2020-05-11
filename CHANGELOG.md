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

