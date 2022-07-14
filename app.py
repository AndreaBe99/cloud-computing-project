import os
import jinja2
import pandas as pd
import random
from flask import Flask, request, request_tearing_down, url_for, redirect, render_template, jsonify
from pycaret.classification import *
from df_manipulation import *
import config
from datetime import datetime, date, timedelta

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config.GOOGLE_APPLICATION_CREDENTIALS

app = Flask(__name__)

# Load Model
model = load_model(model_name=config.RF_MODEL, platform='gcp', authentication={'project': config.PROJECT_NAME, 'bucket': config.BUCKET_NAME})

@app.route('/')
def home():
    return render_template('home.html')

# Function to create usefull features
def dataset_manipulation(df):
    # Load Main Dataset
    all_season = pd.read_csv(config.DATASET, low_memory=False)

    # Convert Date Column to Datetime
    df['Date'] = pd.to_datetime(df.Date)
    all_season['Date'] = pd.to_datetime(all_season.Date)

    ht_cols = ['ht' + col for col in config.COLS_DF]
    at_cols = ['at' + col for col in config.COLS_DF]

    #gets main cols for home and away team
    df[ht_cols] = pd.DataFrame(df.apply(lambda x: create_main_cols(
        all_season, x, x.HomeTeam), axis=1).to_list(), index=df.index)
    df[at_cols] = pd.DataFrame(df.apply(lambda x: create_main_cols(
        all_season, x, x.AwayTeam), axis=1).to_list(), index=df.index)

    #result between last game of the teams
    df['ls_winner'] = df.apply(lambda x: get_ls_winner(all_season, x), axis=1)

    return df

# Calculate the season
def get_season(match_date):
    # - if month >  6 --> season = year
    # - if month <= 6 --> season = year - 1
    season = None
    if match_date.month > 6:
        season = match_date.year
    elif match_date.month <= 6:
        season = match_date.year - 1
    return season


@app.route('/predict', methods=['POST'])
def predict():
    # Create a dataframe from the HTML form
    match_date = str(request.form['match_date'])
    home_team = str(request.form['home_team'])
    away_team = str(request.form['away_team'])

    error = None

    # Check Missing Value
    if not match_date or not match_date.strip():
        error = 'Match Date is missing!'
    if not home_team or not home_team.strip():
        error = 'Home Team is missing!'
    if not away_team or not away_team.strip():
        error = 'Away Team is missing!'

    if error:
        return render_template('home.html', error="Ops! "+error, match_date=match_date, home_team=home_team, away_team=away_team)

    # Check Date
    match_date = datetime.strptime(match_date, '%Y-%m-%d').date()
    today = date.today()
    if match_date < today:
        error = 'The date you selected is in the past'

    # Check Teams
    all_season = pd.read_csv(config.DATASET, low_memory=False)
    if home_team not in all_season.HomeTeam.unique() and home_team not in all_season.AwayTeam.unique():
        error = 'The home team you selected is not in the dataset!'
    if away_team not in all_season.HomeTeam.unique() and away_team not in all_season.AwayTeam.unique():
        error = 'The away team you selected is not in the dataset!'

    if error:
        return render_template('home.html', error="Ops! "+error, match_date=match_date, home_team=home_team, away_team=away_team)

    # Calculate the season
    season = get_season(match_date)

    final = [season, match_date, home_team, away_team]

    # Teams Logo
    image_home_path = "static/image/team-logo/"+home_team+".png"
    image_away_path = "static/image/team-logo/"+away_team+".png"

    data_unseen = pd.DataFrame([final], columns=config.COLS_URL)

    # Add usefull column
    data_unseen = dataset_manipulation(data_unseen)

    prediction = None
    prediction = predict_model(model, data=data_unseen, round=0)
    prediction = int(prediction.Label[0])

    if prediction:
        return render_template('home.html', pred=prediction, match_date=match_date, home_team=home_team, away_team=away_team, image_home_path=image_home_path, image_away_path=image_away_path)
    else:
        return render_template('home.html', error="Ops! Something went wrong during the prediction.", match_date=match_date, home_team=home_team, away_team=away_team)


@app.route('/predict_test',  methods=['POST'])
def predict_test():   
    request_data = request.json

    match_date = request_data['match_date']
    home_team = request_data['home_team']
    away_team = request_data['away_team']

    # Calculate the season
    season = get_season(match_date)

    final = [season, match_date, home_team, away_team]

    data_unseen = pd.DataFrame([final], columns=config.COLS_URL)

    # Add usefull column
    data_unseen = dataset_manipulation(data_unseen)

    prediction = None
    prediction = predict_model(model, data=data_unseen, round=0)
    prediction = int(prediction.Label[0])

    # return jsonify(prediction)
    return '/predict_test - season: {}, match_date: {}, home_team: {}, away_team: {}, prediction: {}\n'.format(season, match_date, home_team, away_team, prediction)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=config.PORT, debug=config.DEBUG_MODE)
