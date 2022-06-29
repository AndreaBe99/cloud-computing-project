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
