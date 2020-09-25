

 # NCTU EagleEYEv1.5 Orchestration
This document serves as a guidance to deploy the NCTU's EagleEYEv1.5 by using Kubernetes.
- *Document version: 20200925*

NCTU EagleEYEv1.5 consists of 4 micro-services:
1. Database service (`mongo` and `redis`)
2. EagleEYE web service (`ews`)
3. EagleEYE scheduler service (`scheduler`)
4. EagleEYE detection service (`detection`)

- To generate the K8S yaml file, we use `Kustomization`
	- Generate the yaml file by running the following command, e.g.: 
		- `$ kubectl kustomize ./detection > detection.yaml`
	- **Note that you have to generate a new yaml file every time a modification is made!!!**

## Requirements
#### OS
	- Ubuntu Server 18.04
#### Kubernetes (w/ a working NVIDIA GPU plugin)
	- Client: v1.18
	- Server: v1.18

## Deployment Steps
*Note that the deployment below should be done in this exact step!*

#### Deploy
 1. Download the extra files
	 - Detection Data
		 - Link: [Google Drive](https://drive.google.com/file/d/1YpczmyStbl0FYtiiXuJjkBeIxFdbQWSE/view?usp=sharing)
		 - Extract and then place the contents inside a folder called `/data`
	- Config Files
		 - Link: [Google Drive](https://drive.google.com/file/d/18M1WZhsh-dfqbJjB8HiN0r-yHG8CBOQU/view?usp=sharing)
		 - Extract and then place the contents inside a folder called `/config_files`
 2. Update the `PersistentVolume` mounting path
	 - For `detection` service (`detection-persistent-volume-claim.yaml`)
		 - Update the `hostPath` to use the current path of `/config_files` (*from step 1*) on your local machine
	 - For `mongo` service (`mongo-persistent-volume.yaml`)
		 - Create a directory for `mongo`
		 - Update the `hostPath` to use the current path of `mongo` directory
	 -  For `redis` service (`redis-persistent-volume.yaml`)
		 - Create a directory for `redis`
		 - Update the `hostPath` to use the current path of `redis` directory
	-  For `scheduler` service (`scheduler-persistent-volume.yaml`)
		 - Update the `hostPath` to use the current path of `/data` (*from step 1*) on your local machine
3. Update the yaml file
	- `$ sh kustomize-renew.sh`
4. Deploy EagleEYEv1.5 with the following order
	1. Create `Secret` to allow for image download from Docker Hub (optional):
		- `$ kubectl apply -f timwilliam-regcred.yaml`
	2. Create `Volume` and `VolumeClaim`:
		- `$ kubectl apply -f volume.yaml`
		- `$ kubectl apply -f volume-claim.yaml`
	3. Create `Service` to allow for communication between `Pods`:
		- `$ kubectl apply -f service.yaml`
	4. Create the `redis-reployment` and `mongo-deployment`
		- `$ kubectl apply -f redis.yaml`
		- `$ kubectl apply -f mongo.yaml`
	5. Create `ews-deployment` (Web Service):
		- `$ kubectl apply -f ews.yaml`
	6. Create `scheduler-deployment`:
		- `$ kubectl apply -f scheduler.yaml`
	7. Create `detection-deployment`:
		- `$ kubectl apply -f detection.yaml`
	8. Or you can also run this magic script to do all the above magically :)
		- `$ sh start-eagleeye.sh`
#### Restore the Docker images with `docker load`

- Download the saved docker images from this [Google Drive link](https://drive.google.com/drive/folders/1rKNg4dry7zVALIYYSordI8G3CE5iE4K0?usp=sharing).
	- You should be able to download 4 `*.tar` files namely `detection.tar`, `redis.tar`, `scheduler.tar`, and `webservice.tar`.
- **Remember to update the `*-deployment.yaml` file as necessary.**

#### Notes
- At this moment, a successful deployment means that you will be able to see 4 pods running which is `detection`, `ews`, `redis`, and `mongo`.
- The `scheduler` pod is not running due to error, we are working on a solution right now.
- We will update you again with another deployment file that will be able to read an input and produce an output.

#### Kubernetes Features Used
- Deployment
- PersistentVolume
- ConfigMap, Secret
- Service, NodePort (*we plan to replace this with Load Balancer in the future*)
- Probe
- Horizontal Pod Autoscaler (*we have not used HPA yet, but plan to use it in the future*)
- Kustomization