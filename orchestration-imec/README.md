# EagleEYEv1.5 Orchestration

 1. Download the extra files
	 - Download the extra data
		 - Link: [Google Drive](https://drive.google.com/file/d/1YpczmyStbl0FYtiiXuJjkBeIxFdbQWSE/view?usp=sharing)
		 - Extract and then place the contents inside the `/data`
	 - Download the Object Detection model config data
		 - Link: [Google Drive](https://drive.google.com/file/d/18M1WZhsh-dfqbJjB8HiN0r-yHG8CBOQU/view?usp=sharing)
		 - Extract and then place the contents inside the `/config_files`
	
 2. Create ConfigMap
	 - Generate the ConfigMap by running the script with `$ sh generate-configmap.sh`
	 - Delete the ConfigMap by running the script with `$ delete-configmap.sh`
 3. Update the Deployment yaml file `ee-deploy.yaml` 
	 - Update the hostPath for the following Deployment:
		 - `redis` at line 28
		 - `mongo` at line 65
		 - `scheduler` at line 147 (the path to the `/data` dir)
		 - `detection` at line 192 (the path to the `/config_files` dir)
 4. Rollout the Deployement
	 -	`$ kubectl apply -f ee-deploy.yaml`
