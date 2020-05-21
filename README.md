
![figure-introduction](https://lh3.googleusercontent.com/11Mn3a8IZSLZmsGSBEBfRZ4J7C3-OrBCPd3IvkXfm2AqVMMmmEY7hsNes7uMJHl-8dekqcUvEvoxjKomKc1deIJFVHHE6eEz_BhLAgNdVznCgtXwQf6IiJfz4zSp2axyeguOAunmZqM2YZtt9Peuu_CESgwWBFLgKiONgBvT-YNbWd9RhrqDbnjcntErknCarIodr1Yg-kd9fUVeGRsOgHzuJBAJJYnpKEKwsW_YrLyIi7L3cyIHqYJg7_4ynEEeIwaeXeY2heEMcrTp4NWSUPj3bVP4KFrLdwXwiwB1lyLz2LGHFftDA60s_ZcwxqTxv_-PUMPQ-WmgOtiXPpPfy_0Bv5dVef19tGZZN1nlrCKsjutZY28UFsbMvBpkkyWpwP0ldGIpR6c_G0zs_OxCi1HqRnNH2MZhxDzeWWi93fBlRhMfsNIIbICq7tKSDz1bH_yf11wgDQCJCbkfxwvyRGtufUf0KP5nzB37XMiRdJqMo5cebD7yI3MDnV7D4CudltKwhlOBDkWulHgv4xr_PlUygVOpfVnTjAl9HlUn-2YFE3wwc9PMVTalcT472GzwJlB9G1szB9Cq45uW8Dnmi6BEyyTLn1urt8V2JLihBWuO3fPvrHvU0nByMpzAIN_R99uIMvp3CHCaRcc5tdvWs1uU-vo49PyEYcGmDPm5mA5jWIdVvR7-x_dAKK1q=w893-h294-no?authuser=1)
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

#### Acknowledgements
- This project has been partially funded by the H2020 EU/TW joint action 5G-DIVE (Grant #859881).

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


 1. Activate the virtualenv by running this command below:
    - `$ cd eagleye # The location where eagleeye is cloned on your machine`
    - `$ . venv/bin/activate.fish # Assuming that you use fish`
 2.  For cleanup, run this delete_keys script:
     - `$ python delete_keys.py`
 3. Start the OpenCV visualizer:
	- `$ python main_visualizer.py --small --original --no-fps` (EagleEYE_Output_Stream)
	- `$ python main_visualizer.py --small # Eagle ` (Drone_Video_Feed)
 4. Start drone GPS dummy:
    - `$ python main_gps_collector.py`
 5. Start PiH Location Fetcher:
    - `$ python main_pih_location_fetcher.py`
 6. Start the woker nodes. Below show the example for the activation of 4 worker nodes:
    - `$ python main_yolov3_worker.py --node 1`
    - `$ python main_yolov3_worker.py --node 2`
    - `$ python main_yolov3_worker.py --node 3`
    - `$ python main_yolov3_worker.py --node 4`
 7. Start the Stream Reader module:
    - `$ python main_stream_reader.py --total_workers 4`


#### OLD Conda Environment
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

# Links and Documentation

-  [Single video streaming via HTTP using FFmpeg](https://github.com/ardihikaru/eagleeye/blob/feature/readme/docs/http-stream.md)
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
eyJoaXN0b3J5IjpbLTkxODIzNDAyMiwtMTYzNDQ4MDUzNiwxMz
kzMDAxNDQ3LC0xMjY3MDc1NTI1LDE2MDY4MDU0NzcsMjExODY2
MDEwLDE0MDM0ODQ2MywtNzIwMjcxOTUzLC0yMDIxNDExMzUsMT
YxMzY5Mzc3MSw4NzQwMzI4NDQsLTc1NjIyNTA0MiwtNzAzMzMz
NDczLDE2NDAyMzUyODUsLTIxMTk0NTg1NzEsODc4Njc3MzMzLD
IwNDAwNDUzMjYsLTg1NDA1MzE5MV19
-->
