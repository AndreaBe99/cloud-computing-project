# cloud-computing-project

## 1 The Problem
The aim of the project is to provide a machine learning model and create a web application that communicates with it, allowing users to input data and receive predictions about football matches. 
We supposed the following real scenario: a user enters a series of data about a football match such as the match date, the name of the home team and the away team. Once these parameters have been entered, they will be processed and a prediction on the final outcome of the match will be provided in the output, i.e. victory of the home team, draw or victory of the away team.

Our Presentation: [Cloud Computing Presentation](https://docs.google.com/presentation/d/1JdaCvFCW2jtfhTCZ9vC09MMd9lg4aHDTCxvhbHiF0T0/edit#slide=id.p)

## 2 Technologies
The tools we used for the development are:
  - **Flask**, for the creation of the web-app through the use of Python, HTML and CSS code.
  - **Docker**, for the creation of a containerized environment in which to run our application.
  - **Kubernetes**, for the management of containerized applications, or to completely manage their life cycle.The reason why we chose to use Kubernetes is because it allows you to balance the load, automatically distributing it among the containers, and to resize, that is, it allows you to automatically add or remove containers when it changes.
  - **Google Cloud Platform** (GCP), which provides Google Kubernetes Engine which is an implementation of the open source Kubernetes framework, as well as various cloud computing services. One of the reasons we chose to use GCP is that it allowed a free trial worth $ 300 for 90 days.
  - **Locust**, To monitor and stress our application.

## 3 Implementation
The development of the project will be divided into the following phases:
  1. the first phase involves training the machine learning model using the data-set Football Match Prediction, such procedure can be performed both locally and on the cloud.
  2. the second phase involves the development of a Web-App that will connect to the trained machine learning model and the pipeline, in order to generate real-time forecasts based on user inputs. In fact, this application will be divided into two parts: front-end and back-end. The first will be developed in HTML and CSS, while for the development of the second we will use the Flask framework in Python.
  3. the last phase involves the implementation of the Machine Learning pipeline on Google Cloud Platform (GCP), in particular we will use Google Kubernetes Engine, that is an implementation of the open source Kubernetes framework on GCP, and Docker to upload the image in Google Container Registry.

## 4 Test & Validation
Finally, in terms of testing / validating the performance of our cloud service, we will use the following tools:
  -  Google Cloud Console: we will use the Google Cloud Console monitoring tool (called Cloud Monitoring) to examine the system performance.
  - Locust: we want to modify the number of users in order to stress our application, using Locust for the simulation.
  - Google Cloud Pricing Calculator: we will use this tool to predict the estimated costs necessary for the development of the project.

## 5 Repository Organization
- Web-App: The Python files `app.py`,` config.py`, `df_manipulation.py` are necessary for the web application to work,` app.py` contains the Back-End logic with HTTP method management, while in `df_manipulation.py` there are a series of functions for extrapolating new features based on user input data. The `static` and` templates` folders contain the HTML, CSS files and the resources for displaying the application. Finally Dockerfile and requirement.txt are used for image build.

- The `src` folder contains all the resources used for development, such as datasets or model files.

- Locust: Finally, the `Locust` folder contains all the files needed to deploy the cluster for load tests. The most important file is `task.py` inside the` locust-task`, where the logic of the tester is developed.


## 6 Deploy Machine Learning Model on GKE
1. Create a project on Google Cloud Platform.

2. Run the following commands to set the project on which to operate and obtain credentials / API:
    - `export PROJECT_ID=circular-acumen-356407` (change project ID)
    - `gcloud config set project $PROJECT_ID`
    - `gcloud auth configure-docker`
    - `gcloud services enable containerregistry.googleapis.com` 
    - `gcloud services enable container.googleapis.com`
   
   To get the credentials go to GCP in the section `API and services -> Credentials -> Service Account` click on the email. From the screen that opens go to `Keys -> Add Key -> Create Key -> Json` and download the json.

3. Run the following list of commands to create a cluster and build the application image:
    - Football Bet App Cluster:
      - `git clone https://github.com/AndreaBe99/cloud-computing-project.git`
      - `cd cloud-computing-project`
      - Modify in `config.py`: `GOOGLE_APPLICATION_CREDENTIALS`, `PROJECT_NAME`, `BUCKET_NAME` and add the JSON file credential.
      - `gcloud config set compute/zone us-west1-a`
      - `gcloud beta container --project ${PROJECT_ID} clusters create football-bet-cluster --zone us-west1-a  --scopes https://www.googleapis.com/auth/compute,https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append --preemptible --num-nodes 3 --logging=NONE --monitoring=SYSTEM --enable-autoscaling --min-nodes 3 --max-nodes 7 --addons HorizontalPodAutoscaling,HttpLoadBalancing --enable-autorepair`
      - `gcloud container clusters get-credentials football-bet-cluster --zone us-west1-a --project ${PROJECT_ID}`
      - `docker build -t gcr.io/${PROJECT_ID}/bet-app:v1 .`
      - `docker run --rm -p 8080:8080 gcr.io/${PROJECT_ID}/bet-app:v1` to test localy.
      - `gcloud docker -- push gcr.io/${PROJECT_ID}/bet-app:v1`
      - `kubectl create deployment bet-app --image=gcr.io/${PROJECT_ID}/bet-app:v1`
      - `kubectl expose deployment bet-app --type=LoadBalancer --port 80 --target-port 8080`,and run `kubectl get svc bet-app` to get IP (http://34.168.77.128:80, wait some minute)
      - `kubectl autoscale deployment bet-app --cpu-percent=80 --min=1 --max=30`

    - Locust Cluster:
      - `gcloud beta container --project ${PROJECT_ID} clusters create "loadtesting" --zone us-central1-a --scopes "https://www.googleapis.com/auth/compute","https://www.googleapis.com/auth/devstorage.read_only","https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring","https://www.googleapis.com/auth/servicecontrol","https://www.googleapis.com/auth/service.management.readonly","https://www.googleapis.com/auth/trace.append" --preemptible --num-nodes 3 --logging=NONE --monitoring=SYSTEM --enable-autoscaling --min-nodes 3 --max-nodes 7 --addons HorizontalPodAutoscaling,HttpLoadBalancing `
      - `gcloud container clusters get-credentials loadtesting --zone us-central1-a --project ${PROJECT_ID}`
      - `cd locust`
      - `docker build -t gcr.io/${PROJECT_ID}/locust-task .`
      - `gcloud docker -- push gcr.io/${PROJECT_ID}/locust-task`
      - Modify IP and image project name nel file `loadtest-deployment.yaml`.
      - `kubectl create -f loadtest-deployment.yaml`
      - `kubectl get service` (get EXTERNAL_IP of locust-master-web and go to http://EXTERNAL_IP:8089, in my case http://34.154.185.168:8089)

      - add `limits: cpu: ?m   requests: cpu: ?m` in yaml file.