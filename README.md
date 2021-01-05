![EagleEYE Logo Figure](https://lh3.googleusercontent.com/EFFTePzMeLxbZbsT_tShVsSgv2XC4E1-WiWWpMUCIXGr5O3Ea8Gd14sIHtXsY5x11Te433nboyC0zVSZgtVdf40Uq1qjYbmhIUGpK1oipFsuabgYGFP2N1Sx4kj-_6TCX9cKxbACFImEACGCc06-rl20zABZxv-nksYB5toz-x5BZq2zlCU5hb1_EqqdeA_iTrMRqVwoX_CMSB4QzS_yMC5N6W3pfW0YVZw4-8Qc1_XEicEej2C69YpcLAwQ75gtrfdZygxllIR-PbpduHA_6CGffZIJ1c7-lKT6eRkYEOnGlUDua1XX6YrZ7lONLpi2MREAWi-lhst8Tx1yqV4T5ooITRVMbM7rLvcj7MM8bQj3gjTYiJ8hOwq9_909vMwklqQ0MMmpBK1TDn4wQRcO3te2rkTA3SamP0u6kEolqCZeuQiCJ4yHcrYbvtGQGn39wCenU3G_xvLgg8Ixxo28ZlPxW3wwd0i_KxjSUOVOyyDnY2TMoeGBFbsMInrkHEbcGLY6Fyy0wMTWbwPEnkaE6hwBUCOS3A2khoe1Zx_j-3RD97fNVST2lQW1GaJdRr6ziIkxR-0GHOXgdve2AAmWWsvOrf25ih0qjWoBW3ocRAOlWAJI430HpRrJ-uOHYdNZeGeJbQhfAo21D53A_4v60IudEQDmjv8FKGyRJVGHy2MtNyq44CgjhNHVhQ52=w723-h255-no?authuser=1)
# Introduction

This repository contains the implementation of EagleEYE, a disaster relief system developed by [National Chiao Tung University](https://www.nctu.edu.tw/en) (NCTU) of Taiwan for the [5G-DIVE](https://5g-dive.eu/) project. The 5G-DIVE project is a collaborative project between partners from the European Union and Taiwan. Together, we aimed at proving the technical merits and business value proposition of 5G technologies in Autonomous Drone Scout (ADS) vertical pilot. 

# Description

### EagleEYE Overview
EagleEYE stands for A**e**ri**a**l Ed**g**e-enab**le**d Disaster Relief Respons**e** S**y**st**e**m. EagleEYE is a decentralized system designed to leverage pervasive edge computing infrastructures to support disaster relief teams. At its core, EagleEYE is designed to scale up/down depending on the processing workload.

### EagleEYE System Workflow

![EagleEYE System Workflow Figure](https://lh3.googleusercontent.com/ANO_-ETEpiAqDV1CdYv6Cx14SdddaQySoJeFmTuJJzcZzoxfmt1-0XrETkTeq_5TKDQrFRBlPsvpX4PwYpC2VF698coym26WV1yQwoWHAj4X0YDghezy761n3Rkcvf0eXsz_LOHI-r-wa6EHV03s8NL1ZsVUr2krQ1vFGzvjMNLS2TfbXqpJ1qW1bSGS5R_EABAgdwFSx5tX57A_ofbgUnfl4YHBS01J_j49k4taLr0vU41okdLsuLnzCCKdC1eCTAfrYm7X4kiI6YnXFkj6w3QRtgTeRq2VXrXxYvdU4VIWsi67BDkcBiQ_c0LkNONg8reIiRVmGxKGAp-BY6E_7gAgikqluUjbgxHm43qCGFDBumtP3TUZLXKtpYAR7mfLJ3xPpb7H42WUkqhwvhvHVUDzF2sAPlfR7rq61er7lgUjFU-DwUC1dSpx6t8ncPpXa1x1ZU_WuOnIFEwveYToC6YI7uQkyq5o0qkDWdzIGULmTGo6HENbAyst1wM3p5yqT20d_-HcRZ5qAZaJNfXALJOecUcE2zIf_9isBHkA6d-6CNBiIGtIPqH-EuJT0FQ0lkM3-gU5RnWi6GXzpAXxA68PtKWuVoiPqFzgay_gdunFiBW6opq8Yu5jtMJXC6Yms0OGJqzcf4kJt97QGD8q-xhizwYGpXP6gTI0Z7PRMqQZTqw6w186XsB-_tkw=w1920-h616-no?authuser=1)

The overview of EagleEYE system workflow are as follows:
 1. Drones are streaming video feed to EagleEYE via 4G/5G wireless communication. EagleEYE itself is deployed on OPTUNS Edge Data Center (EDC).
 2. EagleEYE processes the live video feed to detect for Person in need of help (PiH).
3.  Once a PiH is found, it's GPS location will be recorded and a waypoint trajectory will be calculated.
4. Based on the waypoint trajectory calculated in Step 3, drones will perform automatic trajectory update.

### The novelty of EagleEYE system is in the entirety of:
 - Using drone video and GPS data to identify an emergency situation in real-time.
 - Locating Person in need of Help (PiH) accurately.
 - Navigating drones to the emergency scene autonomously.
 - End-to-end system testing using drones, RAN, and EDC.

### EagleEYE Architecture for PiH Detection

Below is a short description on our architecture for PiH detection. For more details, please refer to our paper publication detailed in the next subsection.

![EagleEYE Architecture Figure](https://lh3.googleusercontent.com/QiCUd-OEAEvdQ_ungvgUF5rQ7VNpPxSKIvRoxbRn5rKlq1DXa5LAosvkgP4VTDB441SUe-oW-wYK7EtDU-Lj6y3P5qYTTCZTD0SZONBMaWCnjndVqKVEE3c_65unzeWxiSamgwWitsD6wrCwckcb5zfLQ3GjrOUaCgSmh_tY9UUH02Xp01v0n6wOjhpYogoO-jI4RmE83XUnda_2iNzgabRs1f-I_0t1pUBReGYGuRrK9I_xnPDwLe_TXPN5matgYJ-hFwHF5p3Fw8vuZfiPrrn5d2deXYw54k9qS-4kQ84nT8uGfD4FVmMaWiw_g9DuEOZkxUCA0i2VeBR62z4oMsEJb90w2CHO3klIa3D25oOUswE6IroqpiewEksCQPZRU4fgehxtWWsWUmV9qAhfZ63mW_WCxngxn1-RdpJZH6OtKcYyufu5eEHSjCrRsc223EKVwZCSl490V-tDeU03RHM_1oCTc7CbKwrxmqIdipTXI8tNnInmm31MC4MU9eAFDs0xjqHvo9poEJO6k6SnM8Xx3C3KSm2vWGWqaMTiYfStkNslx6WkRtdB2CMtg3xnEqXzAgT1-5WPHVAegqTYG9WnIkBfv_l9x6-9RaeDQWoVSvEfCiyhpcPhfImUtHIUALBnc7iEoic5kYzozy2gZz1R2BAzIbNHUmL6jVa8rahBegPmXoi55Z-KRnYk=w1125-h409-no?authuser=1)

- **Dual Object Detection:** CNN-based algorithm to detect ’*person*’ & ‘*flag*’ objects.
- **PiH Candidate Selection:** heuristic algorithm to check if the correlation between ‘person’ & ‘flag’ objects meets a set of criteria.
- **PiH Persistence Validation:** Sliding window algorithm to determine if PiH object appear across a consecutive number of frames persistently.

### Publication & Video Demo
More details on EagleEYE system can be found in:
1. Our [2020 EUCNC](https://www.eucnc.eu/) paper publication. This contains the initial design of our EagleEYE system.
	  - Ardiansyah, M.F., William, T., Abdullaziz, O.I., Wang, L.C., Tien, P.L. and Yuang, M.C., 2020, June. EagleEYE: Aerial edge-enabled disaster relief response system. In _2020 European Conference on Networks and Communications (EuCNC)_ (pp. 321-325). IEEE.

2. An extended version of the paper is also under works. In this extended version, more details on our latest implementation and results will be presented.

Video demo links:
1. [EagleEYE Demo Video 1 for 5G-DIVE](https://youtu.be/yufPUupQbAo)
2. [EagleEYE Demo Video 2 for 5G-DIVE](https://youtu.be/GcccfPQ4QHg)

# Credits & Acknowledgements

Our work will not be possible without the resources provided by other entities and individuals. We would like to express our gratitude to all of you.

#### Our credits go to the following entities (in no particular order):
 - [1] [Joseph Redmon](https://pjreddie.com/) for YOLO ([https://pjreddie.com/darknet/](https://pjreddie.com/darknet/))
 - [2] [AlexeyAB](https://github.com/AlexeyAB) for YOLOv3/v4 implementation ([https://github.com/AlexeyAB/darknet](https://github.com/AlexeyAB/darknet))
 - [3] [ultralytics](https://github.com/ultralytics) for YOLOv3 implementation in PyTorch ([https://github.com/ultralytics/yolov3](https://github.com/ultralytics/yolov3))
 - [4] [EasyDarwin](https://github.com/EasyDarwin/EasyDarwin) team for Golang based RTSP server
 - [5] [Cartucho](https://github.com/Cartucho) for mAP calculator (https://github.com/Cartucho/mAP)
 - [6] [developer0hye](https://github.com/developer0hye) for YOLO Bounding Box labelling tool (https://github.com/developer0hye/Yolo_Label)
 - Various icons in the figures is made by [Freepik](https://www.flaticon.com/authors/freepik) from [www.flaticon.com](www.flaticon.com)
 - Background music in the demo video is provided by [Bensound.com](https://www.bensound.com/)

#### Additional details:
- Trained our object detection algorithm using the work of [1] and [2]. 
- Implemented EagleEYE on top of [3] work. We use [3] repository linked above as the base of our EagleEYE development.
- We used tools in [4], [5], and [6] during our development for testing and validation of our implementation.

#### OPTUNS Edge Data Center (EDC):
OPTUNS is an optical-switched EDC network architecture for 5G application. OPTUNS provides high-bandwidth, and ultralow latency communication for supporting time-critical edge application. More details on OPTUNS data center can be found in the following publication:
- Yuang, M., Tien, P.L., Ruan, W.Z., Lin, T.C., Wen, S.C., Tseng, P.J., Lin, C.C., Chen, C.N., Chen, C.T., Luo, Y.A. and Tsai, M.R., 2020. OPTUNS: Optical intra-data center network architecture and prototype testbed for a 5G edge cloud. Journal of Optical Communications and Networking, 12(1), pp.A28-A37.

#### Acknowledgements:
- This project has been partially funded by the H2020 EU/TW joint action 5G-DIVE (Grant #859881).

# Contributors

 - Muhammad Febrian Ardiansyah:
	 - GitHub: [https://github.com/ardihikaru](https://github.com/ardihikaru)
	 - Email: mfardiansyah.eed08g@nctu.edu.tw
 - Timothy William:
	 - GitHub: [https://github.com/timwilliam](https://github.com/timwilliam)
	 - Email: timothywilliam.cs06g@g2.nctu.edu.tw
 - Osamah Ibrahiem Abdullaziz
	 - GitHub: [https://github.com/oiasam](https://github.com/oiasam)
	 - Email: yabolahan.04g@g2.nctu.edu.tw

