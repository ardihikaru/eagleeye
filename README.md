![EagleEYE Logo Figure](https://lh3.googleusercontent.com/XedEhHMwmtTq0IDwZDKeTrxNwRmr3zbGJwScBUD4192mg9Og9wDzAHRJTZ-sNsZ0YQaHVR-79XtDvm7wZGONiuTnHP9K-fiBdJV_D0f5BQ54kb5KocXW9NTg--DBDAmuBSAsgyRpUqVmK05xOzLCj9_8dcRRJyunSw8go6l9KRzZu9RkaWVn8_b0EF1QR8fxozLwW5oXkZGBQNni3NwDYZ0tb6FUMvni4aEErqeLTjY77lXM0hPAloj6lDc1ZDBhjdM_IUUpr_IDkBCfaBw30l2X6ztmA8ui9XhW_Ja0uckd303wI8YTzpzIdsJQW8l4kutvoyoMSQSwU60nliOytW8u0oBY5hLfrf1TvJ2Nac7334mx1YIsU-pyqoDKLQwEdmE2PfQWio2kn9Rs8_yJXzFe88UJsz-kIb_6og5y8bIAoA5AE4cvl7TEdB6rU2KRbfv33XycOO_VbOt_cVeCGj9UBSybhVdgxg1P8s8zCe88d_cQUMKgsDPTgNGHCjnNBX9gc6V3Zpe82GCrk2fuxocuIWa6-vxHi5w0VJQpnY6QegXc8krgGpY-dx2T_I2Hd6yZpVI4pQdJFixQ_UH85mN8dQ2zyYK0FxfSVgMxjLAtW694tegvNPP2WZOJz2_1ICH8rZYdHb8jGYf6AhhgMzEr2oSu_WRSCb2z5NUCEPv8M43rWv-pjcXyeqJc=w723-h255-no?authuser=1)
# Introduction

This repository contains the implementation of EagleEYE, a disaster relief system developed by [National Chiao Tung University](https://www.nctu.edu.tw/en) (NCTU) of Taiwan for the [5G-DIVE](https://5g-dive.eu/) project. The 5G-DIVE project is a collaborative project between partners from the European Union and Taiwan. Together, we aimed at proving the technical merits and business value proposition of 5G technologies in Autonomous Drone Scout (ADS) vertical pilot. 

# Description

### EagleEYE Overview
EagleEYE stands for A**e**ri**a**l Ed**g**e-enab**le**d Disaster Relief Respons**e** S**y**st**e**m. EagleEYE is a decentralized system designed to leverage pervasive edge computing infrastructures to support disaster relief teams. At its core, EagleEYE is designed to scale up/down depending on the processing workload.

### EagleEYE System Workflow

![EagleEYE System Workflow Figure](https://lh3.googleusercontent.com/HxfxRnprjTV5ESFrEP5eSJpkMMjwqmYM_JpYn_aCxV6A3YgQaLS4bcdYhmgfh7G_1Oirk4rcR2U0OsK14YuVPvKNX3afofW5S4orREV99i-NIHAYg4u_Y2biRsEIHHF1xb5K-2fvQwXIdV5PqexSj-JJrdApN0FVOYdRWaFqTh3npT7OMKij9OsATK1WikRKiV3voA8gpJHJzrjeW3zR1v-YSygle-wED3JbVDDWb7K5xnpdLqWHM5GtRZqnSQrq0x9yg8YLiVrPRAzrZy8kGwUbu8y64b77dqmQPgEb2z5gUwHAPXVHr7U6b7jNqcjs2KDi8UcSncz7n2kffWLS3F6UqA_tWgdOAAu4XLR2-rXagknodWotn-hlVqV2XwdBwAzIYRYnQ-cH5yv1-T01UeDQsopnLQms6RD8GPuRKk67jftowDa40Xy6DYbECDDqixQeMLyez9e--5CpjuFLZGrb9Fdupd3B2evBYCaQuT2GZEh5vdYd4ILyIV3gWA1DzH_Z1bm8sauMEqfh1gc_ZFeYl4YMkPPbJ79STWqsPePQBONw3u1Sx2NJPe-N2512--1AD_7s78GzFhXL-yxenfdVcF5PpinuJ5jDJkD6mB9fKSma-eupumr3_Nx-YFadxkcgkicNvh7PQBeTVK0FpkNDBXXLBlWUTbbeBRE0MiueE_M1seIgKYgMbqIO=w1560-h500-no?authuser=1)

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
### Publication
More details on EagleEYE system can be found in:
1. Our [2020 EUCNC](https://www.eucnc.eu/) paper publication. This contains the initial design of our EagleEYE system.
	  - Ardiansyah, M.F., William, T., Abdullaziz, O.I., Wang, L.C., Tien, P.L. and Yuang, M.C., 2020, June. EagleEYE: Aerial edge-enabled disaster relief response system. In _2020 European Conference on Networks and Communications (EuCNC)_ (pp. 321-325). IEEE.

2. An extended version of the paper is also under works. In this extended version, more details on our latest implementation and results will be presented.

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

#### In our implementation, we:
- Trained our object detection algorithm using the work of [1] and [2]. 
- Implemented EagleEYE on top of [3] work. We use [3] repository linked above as the base of our EagleEYE development.
- We used tools in [4], [5], and [6] during our development for testing and validation of our implementation.

#### Acknowledgements
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

