
![figure-introduction](https://lh3.googleusercontent.com/W8a0T3bP9-vIIweUohN16JLArutuJgYlFHF9DWhiZ6sXz1IZUPEEoH7VvkHo1b4bo-GWGHlKMtm-KplJBmPOdTcSUCnZaDNYqJGgUR_b-OWAyyyGOTk9SctM8FtXNQozwZn9pigzxuqQptk7vOCoEiZeNo91sQbKKoN3v6XwXbq7qbYXAMY0RTCeSqrtMG5SyoUA52I2ezu_fjDh3ZT-Q1Ms40nzvbrlaldNpqTCXAYrlRTqLO07RDaNvtmz_QNkjbwIQV9CdQr-R0BzqUr28Ic0rsv-oTn-v_1dL7_vhGZLRu9YUHQcPNN6SQPzg40CBxmINUDj-o95kedCwuPiPza5PhtpG-EfTBPfnNBQk5IMkKpJ1octwfen7-rM0gNVbVraMuFbKO-KV3cxnuZUwhHE7NUjg-0o4g82SxWxdLKRpZ8QH_qIND0UY931yM1aDf0kLq4bJ3FIcmuin7FlQ-6z1BpNyoCUmC7LeyGdYKw4yhEtXPjv8ub08PpG92aWrLiNgFsHZNzfHmCVZDp2IASoftgRJq7HgKSw8ZEKy1gu6s4bZ3EXn6KbiLv4quVdUetd9h6sot7HMFej-D_9y8XZy_D4g4mqyY8cgWcFuIHvSMbo3cerFJB8xSN9tzKFnTESSckHORdj21tlZP9X-sNqlTc6uTXo5IXkr9-bUBvEk6WoAzchNYnnUrOI=w893-h294-no?authuser=1)
# Introduction

This repository contains the implementation of EagleEYE system developed by [National Chiao Tung University](https://www.nctu.edu.tw/en) (NCTU) of Taiwan for the [5G-DIVE](https://5g-dive.eu/) project.

# Description

### EagleEYE Overview
EagleEYE stands for A**e**ri**a**l Ed**g**e-enab**le**d Disaster Relief Respons**e** S**y**st**e**m. EagleEYE is a decentralized system designed to leverage pervasive edge computing infrastructures to support disaster relief teams. At its core, EagleEYE is designed to scale up/down depending on the processing workload.

### EagleEYE System Workflow
The basic workflow of EagleEYE system are as follows:

 1. Capture video stream and GPS information from drone(s).
 2. Process information and allocate task to worker node(s).
 3. Perform parrallelized Person in need of Help (PiH) candidate detection.
 4. Perform PiH persistence detection to look for PiH.
 5. Acquire the GPS location and the current view of PiH surroundings.
 6. Monitor the PiH in real-time and adjust the drone(s) trajectory as necessary.

![figure-ealgeeye-system](https://lh3.googleusercontent.com/pw/ACtC-3cOXs2Zvy4PhHuwD8K7ZG53fIoMMhj9chknpeqsm3jR53cr1P3GMCcHhkVEI_yVSW3SAM_WMBDR8ef6aqS5MGf5YFX0We2vxkQcvcO95jxNFhyNhJCHV0DYkhaYnnzHehtwNWuarA3-YWkxaIEFRJvL=w1498-h563-no?authuser=0)

### The novelty of the EagleEYE is in the entirety of:
 - Using drone video and GPS data to identify an emergency situation in real-time.
 - Locating Person in need of Help (PiH) accurately.
 - Navigating drones to the emergency scene autonomously.

### Publication
More details on EagleEYE system can also be found in our [2020 EUCNC](https://www.eucnc.eu/) paper publication:
  - EagleEYE: Aerial Edge-enabled Disaster Relief Response System [IEEExplore]
  - List of Authors: Muhammad Febrian Ardiansyah, Timothy William, Osamah Ibrahiem Abdullaziz, Li-Chun Wang, Po-Lung Tien, Maria C. Yuang
```
  Template to be provided soon
  ```

# Credits & Acknowledgements

#### Our credit go to the following entities (in no particular order):
 - [1] [Joseph Redmon](https://pjreddie.com/) for YOLO ([https://pjreddie.com/darknet/](https://pjreddie.com/darknet/))
 - [2] [AlexeyAB](https://github.com/AlexeyAB) for YOLOv3/v4 implementation ([https://github.com/AlexeyAB/darknet](https://github.com/AlexeyAB/darknet))
 - [3] [ultralytics](https://github.com/ultralytics) for YOLOv3 implementation in PyTorch ([https://github.com/ultralytics/yolov3](https://github.com/ultralytics/yolov3))

#### In our implementation, we:
- Trained our object detection algorithm using the work of [1] and [2]. 
- Implemented EagleEYE on top of [3] work. We use [3] repository linked above as the base of our EagleEYE development.

### Acknowledgements
- This project has been partially funded by the H2020 EU/TW joint action 5G-DIVE (Grant #859881)

# Requirements
1. Ubuntu 18.04:
	- We were using [Ubuntu Server 18.04.4](http://cdimage.ubuntu.com/releases/18.04.4/release/ubuntu-18.04.4-server-amd64.list) in our testing.
2. CUDA 10.1:
	- If you are on Ubuntu 18.04, you could refer to [this](https://medium.com/@exesse/cuda-10-1-installation-on-ubuntu-18-04-lts-d04f89287130) medium post by [Vladislav Kulbatski](https://medium.com/@exesse?source=post_page-----d04f89287130----------------------) for installation step.
	- Or, you could also refer to NVIDIA official documentation [here](https://docs.nvidia.com/cuda/archive/10.1/).
3. cuDNN 7.6.5:
	- Note that you need to sign in to NVIDIA Developer website to be able to download the cuDNN library (e.g.: `cudnn-10.1-linux-x64-v7.6.5.32.tgz`).
	- Then, you could extract the archieve and copy the library into your CUDA installation directory:
	```
	$ tar -xzvf cudnn-10.1-linux-x64-v7.6.5.32
	$ sudo cp -P cuda/include/cudnn.h /usr/local/cuda-10.1/include
    $ sudo cp -P cuda/lib64/libcudnn* /usr/local/cuda-10.1/lib64/
    $ sudo chmod a+r /usr/local/cuda-10.1/lib64/libcudnn*
    ```
4. Clone the git repository
    `$ git clonegit@github.com:ardihikaru/eagleeye.git`
    `$ cd eagleye`
5. Python Environment (`virtualenv`):
    - Download and install Python virtualenv, you could refer to the [Hitchhiker's](https://docs.python-guide.org/) guide [here](https://docs.python-guide.org/dev/virtualenvs/).
    - Create new virtualenv called `venv` (for first time use; create once):
    `$ python3 -m venv venv`
    - Activate the `venv` virtualenv:
    `$ . venv/bin/activate.fish`
    - Install additional library:
    `$ pip install Cython numpy scipy imagezmq`
    - Install even more library from the `requirements.txt` file:
    `$ pip install -r requirements.txt`
6. [OPTIONAL] Python Environment (`conda`):
    - Download and install Anaconda, you could refer to the guide by [DigitalOcean](https://www.digitalocean.com/) [here](https://www.digitalocean.com/community/tutorials/how-to-install-anaconda-on-ubuntu-18-04-quickstart).
    - Create a new Conda environment: 
    `$ conda create -n 5g-dive python=3.7 -c conda-forge`
    - Cloning a Conda environment:
    `$ conda create --name 5g-dive --file req_conda.txt`
    - OR, Python 3.7 or later with all of the 
        `pip install -U -r requirements.txt` packages including:
        - `torch >= 1.3`
        - `opencv-python`
        - `Pillow`
    - **WARNING**: If you get Module not found for `Cython`, please do:
        `$ pip install Cython numpy scipy`

# Usage (Under work ...)
1. Activate environment (for Conda Env): `$ conda activate 5gdive-yolov3`
2. Create RAM-based Disk storage:
    ```
    $ sudo mkdir -p /media/ramdisk 
    $ sudo chmod -R 777 /media/ramdisk/
    $ sudo mount -t tmpfs -o size=1G tmpfs /media/ramdisk/
    Testing:
    $ dd if=/dev/zero of=/media/ramdisk/zero bs=4k count=10000  
    ```
3. Run YOLOv3 Workers, as the for example here, I setup **3 workers** by default (file `worker_yolov3.py`)
    - `$ python worker_yolov3.py --sub_channel 1`
    - `$ python worker_yolov3.py --sub_channel 2`
    - `$ python worker_yolov3.py --sub_channel 3`
4. Resize input and output image (**optional**):
5. Run video streaming reader: `$ python reading_video.py`
    - By default, I set `3 number of workers`. Please modify them accordingly.

#### All dependencies are included in the associated docker images. Docker requirements are: 
- `nvidia-docker`
- Nvidia Driver Version >= 440.44

# Replicate Our Results (Under work ...)

### Our Setup:
We ran all of the test results provided here in our OPTUNS 5G Edge Data Center in NCTU. The details of our data center hardware and architecture can be found in the OPTUNS paper publication [1].
- [1] Yuang, M., Tien, P.L., Ruan, W.Z., Lin, T.C., Wen, S.C., Tseng, P.J., Lin, C.C., Chen, C.N., Chen, C.T., Luo, Y.A. and Tsai, M.R., 2020. OPTUNS: Optical intra-data center network architecture and prototype testbed for a 5G edge cloud. _Journal of Optical Communications and Networking_, _12_(1), pp.A28-A37.

*Section under work ...*

# Contributors

 - Muhammad Febrian Ardiansyah:
	 - GitHub: [https://github.com/ardihikaru](https://github.com/ardihikaru)
	 - Email: mfardiansyah.eed08g@nctu.edu.tw
 - Timothy William:
	 - GitHub: [https://github.com/moipalamoi](https://github.com/moipalamoi)
	 - Email: timothywilliam.cs06g@g2.nctu.edu.tw
 - Osamah Ibrahiem Abdullaziz
	 - GitHub: [https://github.com/oiasam](https://github.com/oiasam)
	 - Email: yabolahan.04g@g2.nctu.edu.tw

<!--stackedit_data:
eyJoaXN0b3J5IjpbLTcyMDI3MTk1MywtMjAyMTQxMTM1LDE2MT
M2OTM3NzEsODc0MDMyODQ0LC03NTYyMjUwNDIsLTcwMzMzMzQ3
MywxNjQwMjM1Mjg1LC0yMTE5NDU4NTcxLDg3ODY3NzMzMywyMD
QwMDQ1MzI2LC04NTQwNTMxOTFdfQ==
-->