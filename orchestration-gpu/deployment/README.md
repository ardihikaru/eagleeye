
 # NCTU EagleEYEv1.5 Orchestration
This document serves as a guidance to deploy the NCTU's EagleEYEv1.5 by using Kubernetes.
- Document version: 20200921

NCTU EagleEYEv1.5 consists of 4 micro-services:
1. Database service (`mongo` and `redis`)
2. EagleEYE web service (`ews`)
3. EagleEYE scheduler service (`scheduler`)
4. EagleEYE detection service (`detection`)

We structure these micro-services like this:			
```
 /eagleeye
   /detection
	detection-configmap.yaml
	detection-deployment.yaml
	detection-persistent-volume-claim.yaml
	detection-persistent-volume.yaml
	kustomization.yaml
   detection.yaml
   /ews
	ews-configmap.yaml
	ews-deployment.yaml
	ews-dual-det-configmap.yaml
	ews-service.yaml
	kustomization.yaml
   ews.yaml
   /mongo
	kustomization.yaml
	mongo-deployment.yaml
	mongo-persistent-volume-claim.yaml
	mongo-persistent-volume.yaml
	mongo-service.yaml
   mongo.yaml
   /redis
	kustomization.yaml
	redis-deployment.yaml
	redis-persistent-volume-claim.yaml
	redis-persistent-volume.yaml
	redis-service.yaml
   redis.yaml
   /scheduler
	kustomization.yaml
	scheduler-configmap.yaml
	scheduler-deployment.yaml
	scheduler-persistent-volume-claim.yaml
	scheduler-persistent-volume.yaml
	scheduler-service.yaml
	scheduler-stream-service.yaml
   scheduler.yaml
   start-ee.yaml
```
- We separate the features that each micro-services uses and put them under a folder with the corresponding micro-service name.
- To generate the K8S yaml file, we use `kustomization`
	- Generate the yaml file by running the following command, e.g.: 
		- `$ kubectl kustomize build detection > detection.yaml`
	- To generate the final yaml file which is `start-ee.yaml`, we use the command:
		- `$ kubectl kustomize . > start-ee.yaml`
	- **Note that you have to generate a new yaml file every time a modification is made!!!**

## Requirements
#### OS
	- Ubuntu Server 18.04
#### Kubernetes (w/ a working NVIDIA GPU plugin)
	- Client: v1.18
	- Server: v1.18

## Deployment Steps
*Note that the deployment below should be done in this exact step!*

#### Login to the Docker Hub account

First, login to the dummy Docker Hub account so that we can download the image.
- `$ docker login` 
- **Username:** `crashdummydonny`
- **Password:** `@1zbDp9l@2J$zeFL`

#### Pull/Load the Docker images

Download the images from Docker Hub (*need login with the above credentials*):
- `$ docker pull timwilliam/eagleeye.scheduler:1.0`
- `$ docker pull timwilliam/eagleeye.redis:1.0`
- `$ docker pull timwilliam/eagleeye.webservice1.0`
- `$ docker pull timwilliam/eagleeye.detection:1.0`

Or you can also do `docker load` (*no need to docker login*):
- Download the saved docker images from this [Google Drive link](https://drive.google.com/drive/folders/1rKNg4dry7zVALIYYSordI8G3CE5iE4K0?usp=sharing).
	- You should be able to download 4 `*.tar` files namely `detection.tar`, `redis.tar`, `scheduler.tar`, and `webservice.tar`.
- **Remember to update the `*-deployment.yaml` file as necessary.**

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
	- `$ kubectl kustomize ./detection > detection.yaml`
	- `$ kubectl kustomize ./mongo > mongo.yaml`
	- `$ kubectl kustomize ./redis > redis.yaml`
	- `$ kubectl kustomize ./scheduler > scheduler.yaml`
	- `$ kubectl kustomize . > start-ee.yaml`
4. Deploy EagleEYEv1.5
	- `$ kubectl apply -f start-ee.yaml`

#### Notes
- At this moment, a successful deployment means that you will be able to see 4 pods running which is `detection`, `ews`, `redis`, and `mongo`.
- The `scheduler` pod is not running due to error, we are working on a solution right now.
- We will update you again with another deployment file that will be able to read an input and produce an output.

#### Kubernetes Features Used
- Deployment
- PersistentVolume, ConfigMap
- Service, NodePort (*we plan to replace this with Load Balancer in the future*)
- Probe
- Horizontal Pod Autoscaler (*we have not used HPA yet, but plan to use it in the future*)
- Kustomization


