import os
import jinja2
import pandas as pd
import random
from flask import Flask, request, request_tearing_down, url_for, redirect, render_template, jsonify
from pycaret.classification import *
from df_manipulation import *
import config
from datetime import datetime, date, timedelta
import logging

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config.GOOGLE_APPLICATION_CREDENTIALS

app = Flask(__name__)


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



@app.route('/predict', methods=['POST'])
def predict():

    # Load Model
    model = load_model(model_name=config.RF_MODEL, platform='gcp', authentication={'project': config.PROJECT_NAME, 'bucket': config.BUCKET_NAME})

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
    datetime_object = datetime.strptime(match_date, '%Y-%m-%d').date()
    today = date.today()
    if datetime_object < today:
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
    # - if month >  6 --> season = year
    # - if month <= 6 --> season = year - 1
    season = None
    if datetime_object.month > 6:
        season = datetime_object.year
    elif datetime_object.month <= 6:
        season = datetime_object.year - 1

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

    # Load Model
    model = load_model(model_name=config.RF_MODEL, platform='gcp', authentication={
                    'project': config.PROJECT_NAME, 'bucket': config.BUCKET_NAME})
    
    # request_data = request.json
    print("JSON: ")
    print(request.json)
    print("DATA: ")
    print(request.data)
    
    request_data = request.data
    logging.debug(request_data)

    match_date = request_data[0]
    home_team = request_data['home_team']
    away_team = request_data['away_team']

    # if not match_date or not home_team or not away_team:
    #    match_date, home_team, away_team = on_start()

    logging.debug('Date: %s, Home: %s, Away: %s', match_date, home_team, away_team)

    # Calculate the season
    # - if month >  6 --> season = year
    # - if month <= 6 --> season = year - 1
    season = None
    match_date = datetime.strptime(match_date, '%Y-%m-%d').date()
    if match_date.month > 6:
        season = match_date.year
    elif match_date.month <= 6:
        season = match_date.year - 1

    final = [season, match_date, home_team, away_team]

    data_unseen = pd.DataFrame([final], columns=config.COLS_URL)

    # Add usefull column
    data_unseen = dataset_manipulation(data_unseen)

    prediction = None
    prediction = predict_model(model, data=data_unseen, round=0)
    prediction = int(prediction.Label[0])

    # return jsonify(prediction)
    return '/predict_test - season: {}, match_date: {}, home_team: {}, away_team: {}, prediction: {}\n'.format(season, match_date, home_team, away_team, prediction)

# This method is used in case of error
def on_start():
    # Create a dataframe from the HTML form
    # Get tomorrow's date
    match_date = date.today() + timedelta(days=1)
    match_date = match_date.strftime("%Y-%m-%d")

    all_season = pd.read_csv(config.DATASET, low_memory=False)

    # Check Teams
    r = random.randint(0, all_season.HomeTeam.nunique() - 1)
    home_team = all_season.HomeTeam.unique()[r]

    all_away_team = all_season.AwayTeam.unique()
    all_away_team = all_away_team[all_away_team != home_team]
    r = random.randint(0, len(all_away_team) - 1)
    away_team = all_away_team[r]
    return match_date, home_team, away_team


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=config.PORT, debug=config.DEBUG_MODE)
