import os
import jinja2
import pandas as pd

from flask import Flask, request, url_for, redirect, render_template, jsonify
from pycaret.classification import *
from df_manipulation import *
import config
from datetime import datetime, date

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
    model = load_model(model_name=config.RF_MODEL, platform='gcp', authentication={
        'project': config.PROJECT_NAME, 'bucket': config.BUCKET_NAME})

    # Create a dataframe from the HTML form
    match_date = str(request.form['match_date'])
    home_team = str(request.form['home_team'])
    away_team = str(request.form['away_team'])

    error = None

    # Check Missing Value
    if not match_date or not match_date.strip():
        error = 'Match Date is missing'
    if not home_team or not home_team.strip():
        error = 'Home Team is missing'
    if not away_team or not away_team.strip():
        error = 'Away Team is missing'
    
    if error:
        return render_template('home.html', error=error, match_date=match_date, home_team=home_team, away_team=away_team)

    # Check Date
    datetime_object = datetime.strptime(match_date, '%y-%m-%d').date()
    today = date.today()
    if datetime_object < today:
        error = 'The date you selected is in the past'
    
    # Check Teams
    all_season = pd.read_csv(config.DATASET, low_memory=False)
    if home_team not in all_season.HomeTeam.unique() and home_team not in all_season.AwayTeam.unique():
        error = 'The home team you selected is not in the dataset'
    if away_team not in all_season.HomeTeam.unique() and away_team not in all_season.AwayTeam.unique():
        error = 'The away team you selected is not in the dataset'
    
    if error:
        return render_template('home.html', error=error, match_date=match_date, home_team=home_team, away_team=away_team)

    # Calculate the season
    # - if month >  6 --> season = year
    # - if month <= 6 --> season = year - 1
    season = None
    if datetime_object.month > 6:
        season = datetime_object.year
    elif datetime_object.month <= 6:
        season = datetime_object.year - 1

    final = [season, match_date, home_team, away_team]

    # print("#############################################################")
    # print("Data: ", final)
    # print("#############################################################")

    data_unseen = pd.DataFrame([final], columns=config.COLS_URL)

    # Add usefull column
    data_unseen = dataset_manipulation(data_unseen)

    prediction = predict_model(model, data=data_unseen, round=0)
    prediction = int(prediction.Label[0])
    if prediction == 1:
        return render_template('home.html', pred='The Predicted Winner is {}'.format(final[2]))
    elif prediction == 2:
        return render_template('home.html', pred='The Predicted Winner is {}'.format(final[2]))
    else:
        return render_template('home.html', pred='The Predicted Result is a DRAW')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=config.PORT, debug=config.DEBUG_MODE)
