# Introduction

This repository contains the implementation of EagleEYE system developed by [National Chiao Tung University](https://www.nctu.edu.tw/en) of Taiwan for the [5G-DIVE](https://5g-dive.eu/) project.

# Description

#### EagleEYE Overview
EagleEYE stands for A**e**ri**a**l Ed**g**e-enab**le**d Disaster Relief Respons**e** S**y**st**e**m. EagleEYE is a decentralized system designed to leverage pervasive edge computing infrastructures to support disaster relief teams.

#### The novelty of the EagleEYE is in the entirety of:
 - Using drone video and GPS data to identify an emergency situation in real-time.
 - Locating Person in need of Help (PiH) accurately.
 - Navigating drones to the emergency scene autonomously.

At its core, EagleEYE is designed to scale up/down depending on the processing workload.

# Credits

 - [Joseph Redmon](https://pjreddie.com/) for YOLO ([https://pjreddie.com/darknet/](https://pjreddie.com/darknet/))
 - [AlexeyAB](https://github.com/AlexeyAB) for YOLOv3/v4 implementation ([https://github.com/AlexeyAB/darknet](https://github.com/AlexeyAB/darknet))
 - [ultralytics](https://github.com/ultralytics) for YOLOv3 implementation in PyTorch ([https://github.com/ultralytics/yolov3](https://github.com/ultralytics/yolov3))

# Requirements:
1. Ubuntu 18.04:
	- We were using [Ubuntu Server 18.04.4](http://cdimage.ubuntu.com/releases/18.04.4/release/ubuntu-18.04.4-server-amd64.list) in our testing.
2. CUDA 10.1:
	- If you are on Ubuntu 18.04, you could refer to [this](https://medium.com/@exesse/cuda-10-1-installation-on-ubuntu-18-04-lts-d04f89287130) medium post by [Vladislav Kulbatski](https://medium.com/@exesse?source=post_page-----d04f89287130----------------------) for installation step.
	- Or, you could also refer to NVIDIA official documentation [here](https://docs.nvidia.com/cuda/archive/10.1/).
3. cuDNN 7.6.5:
	- Note that you need to sign in to NVIDIA Developer website to be able to download the cuDNN library (e.g.: `cudnn-10.1-linux-x64-v7.6.5.32.tgz`).
	- Then, you could extract the archieve and copy the library into your CUDA installation directory:
	`$ tar -xzvf cudnn-10.1-linux-x64-v7.6.5.32`
	`$ sudo cp -P cuda/include/cudnn.h /usr/local/cuda-10.1/include`
    `$ sudo cp -P cuda/lib64/libcudnn* /usr/local/cuda-10.1/lib64/`
    `$ sudo chmod a+r /usr/local/cuda-10.1/lib64/libcudnn*`
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

## Usage (Section under work ...)
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

# Useful Links & Tutorials

* [GCP Quickstart](https://github.com/ultralytics/yolov3/wiki/GCP-Quickstart)
* [Transfer Learning](https://github.com/ultralytics/yolov3/wiki/Example:-Transfer-Learning)
* [Train Single Image](https://github.com/ultralytics/yolov3/wiki/Example:-Train-Single-Image)
* [Train Single Class](https://github.com/ultralytics/yolov3/wiki/Example:-Train-Single-Class)
* [Train Custom Data](https://github.com/ultralytics/yolov3/wiki/Train-Custom-Data)


# Reproduce Our Results

*Section under work ...*

# Citation

*Section under work ...*

# Contact

*Section under work ...*
