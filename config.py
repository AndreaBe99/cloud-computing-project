from os import environ as env
import multiprocessing

PORT = int(env.get("PORT", 8080))
DEBUG_MODE = int(env.get("DEBUG_MODE", 1))

# GCP Credentials
GOOGLE_APPLICATION_CREDENTIALS = 'cloud-355408-facb8fd85885.json'

# Dataset Github Path
PATH_DATASET = "https://raw.githubusercontent.com/AndreaBe99/cloud-computing-project/main/datasets/"
DATASET = PATH_DATASET + "final_all_season.csv"

# Model Name
RF_MODEL = "cloud_project_rf_tuned"

# Gunicorn config
bind = ":" + str(PORT)
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2 * multiprocessing.cpu_count()
