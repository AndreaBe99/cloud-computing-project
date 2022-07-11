from os import environ as env
import multiprocessing

PORT = int(env.get("PORT", 8080))
DEBUG_MODE = int(env.get("DEBUG_MODE", 1))

# GCP Credentials
PROJECT_NAME = 'cc-project-football-bet'
BUCKET_NAME = 'cc-project-football-bet-bucket-model'
GOOGLE_APPLICATION_CREDENTIALS = 'cc-project-football-bet-key.json'

# Dataset Github Path
PATH_DATASET = "https://raw.githubusercontent.com/AndreaBe99/cloud-computing-project/main/datasets/"
DATASET = PATH_DATASET + "final_all_season.csv"

# Model Name
RF_MODEL = "cloud_project_rf_tuned"

# Column Name
COLS_DF = ['_rank', '_ls_rank', '_days_ls_match', '_points',
           '_l_points', '_l_wavg_points', '_goals', '_l_goals', '_l_wavg_goals',
           '_goals_sf', '_l_goals_sf', '_l_wavg_goals_sf', '_wins', '_draws',
           '_losses', '_win_streak', '_loss_streak', '_draw_streak']

COLS_URL = ['season', 'Date', 'HomeTeam', 'AwayTeam']

# Gunicorn config
bind = ":" + str(PORT)
workers = multiprocessing.cpu_count() * 2 + 1
threads = 2 * multiprocessing.cpu_count()
