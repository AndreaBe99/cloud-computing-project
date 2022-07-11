# cloud-computing-project

## 1 The Problem
The goal of the project is to provide a machine learning model and create a web application that communicates with it, allowing users to input data and receive predictions.
Our idea is to train a machine learning model to ”predict” the outcomes of football matches, in which a user can enter various data relating to the match(es) of interest (for example, which of the two teams plays at home, the date, the number of goals, etc.)
and the most likely outcomes of the matches will be provided in real time output [”Win - 1,” ”Draw - X,” ”Defeat - 2 ”). We also plan to test and measure key performance indicators such as latency, scalability, and cost-effectiveness, as well as adjust various components of the pipeline, such as the amount of data used, after the full pipeline has been constructed.

## 2 Technologies & Implementation
The development of the project will be divided into the following phases:
- the first phase involves training the machine learning model using the data-set Football Match Prediction, present on Kaggle, such procedure can be performed both locally and on the cloud. To simplify the development of this phase we intend to use PyCaret, which is a machine learning library used to train and deploy machine learning pipelines and models.
- the second phase involves the development of a Web-App that will connect to the trained machine learning model and the pipeline, in order to generate real-time forecasts based on user inputs. In fact, this application will be divided into two parts: front-end and back-end. The first will be developed in HTML and CSS, while for the development of the second we will use the Flask framework in Python.
- the last phase involves the implementation of the Machine Learning pipeline on Google Cloud Platform (GCP), in particular we will use Google Kubernetes Engine, that is an implementation of the open source Kubernetes framework on GCP, and Docker to upload the image in Google Container Registry.

## 3 Test & Validation
Finally, in terms of testing / validating the performance of our cloud service, we will use the following tools:
-  Google Cloud Console: we will use the Google Cloud Console monitoring tool (called Cloud Monitoring) to examine the system performance in relation to:
  – Load Users: we want to modify the number of users in order to stress our application, using Locust for the simulation.
  – Model (Time) Performance: The goal is to compare the training times of different Machine Learning algorithms on the same quantity of data. We’ll do tests on the quantity of data used to train the model once we’ve decided on the appropriate approach.
- Google Cloud Pricing Calculator: we will use this tool to predict the estimated costs necessary for the development of the project.

## Requirement
Per far girare flask:
  - avere python3 sulla propia macchina
  - installarlo con il comando: pip install flask
  - verificare l'installazione con: python -c "import flask; print(flask.__version__)"
  - per farlo girare usare il comando 'flask run' oppure 'python nomefile.py' da terminale dopodichè verificare corretta esecuzione all'indirizzo 127.0.0.1:5000/

Bisogna avere la seguente configurazione affinchè Flask giri correttamente:
  - cartella principale che contiene il file .py
  - sottocartella chiamata 'templates' che contiene il file html
  - sottocartella chiamata 'static', in questa cartella devono essere anche le (eventuali) immagini
    - sottocartella chiamata 'styles' che contiene il file CSS

## Lista Comandi GCP
1. Creare un progetto su google cloud

2. Eseguire i comandi: 
    - `export PROJECT_ID=bet-football-project`  (qui inserire l'id del proprio progetto)
    - `gcloud config set project $PROJECT_ID`
    - `gcloud auth configure-docker`
    - `gcloud services enable containerregistry.googleapis.com` 
    - `gcloud services enable container.googleapis.com`
   
   per ottenere le credenziali e su GCP nella sezione `API e servizi --> Credenziali --> Account di Servizio` cliccare sull'email. Dalla schermata che si apre andare in `Chiavi --> Aggiungi Chiave --> Crea Chiave --> Json`

3. Eseguire il notebook su colab (https://colab.research.google.com/drive/1JC7NXojjxu8R2VDC32thno5Bhets-IDx#scrollTo=XXDNis6ZAi1w) per creare un bucket nel progetto e così salvare il modello (è necessario modificare i nomi del progetto e eventualmente nel bucket all'interno di colab)

4. Eseguire la seguente lista di comandi per creare un docker container e un cluster:
    - `git clone https://github.com/AndreaBe99/cloud-computing-project.git`
    - `cd cloud-computing-project`
    - Modificare in `config.py`: `GOOGLE_APPLICATION_CREDENTIALS`, `PROJECT_NAME`, `BUCKET_NAME`
    - `docker build -t gcr.io/${PROJECT_ID}/bet-app:v1 .`
    - `docker images`
    - `docker push gcr.io/${PROJECT_ID}/bet-app:v1`
    - `gcloud config set compute/zone europe-west8-a`
    - `gcloud container clusters create football-bet-cluster --num-nodes=2`
    - `kubectl create deployment bet-app --image=gcr.io/${PROJECT_ID}/bet-app:v1`
    - `kubectl expose deployment bet-app --type=LoadBalancer --port 80 --target-port 8080`
    - `kubectl get pods`
    - `kubectl get service` (get EXTERNAL_IP and go to http://EXTERNAL_IP:80, in my case http://34.154.239.33:80)

5. Test:
    - `kubectl autoscale deployment bet-app --cpu-percent=80 --min=1 --max=30`

    - `gcloud services enable \cloudbuild.googleapis.com \ compute.googleapis.com \ container.googleapis.com \ containeranalysis.googleapis.com \ containerregistry.googleapis.com`
    - `git clone https://github.com/GoogleCloudPlatform/distributed-load-testing-using-kubernetes`
    - `cd distributed-load-testing-using-kubernetes`
    - Rename `.yaml.tpl` file in `.yaml`, and delete from `locust-master-service.yaml` rows 39 and 40, and add `pandas` to `requirements.txt`, and copy and paste `task.py`.
    - `REGION=europe-west8`
    - `ZONE=${REGION}-a`
    - `CLUSTER=football-bet-cluster`
    - `TARGET=http://34.154.239.33:80`
    - `gcloud builds submit --tag gcr.io/${PROJECT_ID}/locust-tasks:latest docker-image/.` 
    - `gcloud container images list` (update yaml file with docker image name and EXTERNAL_IP)
    - `kubectl apply -f kubernetes-config/locust-master-controller.yaml`
    - `kubectl apply -f kubernetes-config/locust-master-service.yaml`
    - `kubectl apply -f kubernetes-config/locust-worker-controller.yaml`
    - `kubectl get pods`
    - `kubectl get service` (get EXTERNAL_IP of `locust-master-web ` and go to http://EXTERNAL_IP:8089, in my case http://34.154.239.33:8089)


METODO DEL TUTORIAL CON DUE CLUSTER: 

4. Eseguire la seguente lista di comandi per creare un docker container e un cluster:
    - `export PROJECT_ID="$(gcloud config get-value project -q)"`
    - `git clone https://github.com/AndreaBe99/cloud-computing-project.git`
    - `cd cloud-computing-project`
    - Modificare in `config.py`: `GOOGLE_APPLICATION_CREDENTIALS`, `PROJECT_NAME`, `BUCKET_NAME` e aggiungere il .json della chiave.
    - `gcloud config set compute/zone europe-west8-a`
    - `gcloud beta container --project ${PROJECT_ID} clusters create football-bet-cluster --scopes https://www.googleapis.com/auth/compute,https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append --preemptible --num-nodes 3 --logging=NONE --monitoring=SYSTEM --enable-autoscaling --min-nodes 3 --max-nodes 7 --addons HorizontalPodAutoscaling,HttpLoadBalancing --enable-autorepair`
    - `gcloud container clusters get-credentials football-bet-cluster --zone europe-west8-a --project ${PROJECT_ID}`
    - `docker build -t gcr.io/${PROJECT_ID}/bet-app:v1 .`
    - `docker run --rm -p 8080:8080 gcr.io/${PROJECT_ID}/bet-app:v1` to test localy.
    - `gcloud docker -- push gcr.io/${PROJECT_ID}/bet-app:v1`
    - `kubectl create deployment bet-app --image=gcr.io/${PROJECT_ID}/bet-app:v1`
    - `kubectl expose deployment bet-app --type=LoadBalancer --port 80 --target-port 8080`,and run `kubectl get svc bet-app` to get IP (EXTERNAL_IP=http://34.139.102.238:80, wait some minute)



    - `gcloud beta container --project ${PROJECT_ID} clusters create "loadtesting" --zone europe-west8-a --scopes "https://www.googleapis.com/auth/compute","https://www.googleapis.com/auth/devstorage.read_only","https://www.googleapis.com/auth/logging.write","https://www.googleapis.com/auth/monitoring","https://www.googleapis.com/auth/servicecontrol","https://www.googleapis.com/auth/service.management.readonly","https://www.googleapis.com/auth/trace.append" --preemptible --num-nodes 3 --logging=NONE --monitoring=SYSTEM --enable-autoscaling --min-nodes 3 --max-nodes 7 --addons HorizontalPodAutoscaling,HttpLoadBalancing `
    - `gcloud container clusters get-credentials loadtesting --zone europe-west8-a --project ${PROJECT_ID}`
    - `cd locust`
    - `docker build -t gcr.io/${PROJECT_ID}/locust-task .`
    - `gcloud docker -- push gcr.io/${PROJECT_ID}/locust-task`
    - `docker images`
    - Modificare IP e image name nel file `loadtest-deployment.yaml`.
    - `kubectl create -f loadtest-deployment.yaml`