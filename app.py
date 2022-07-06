import os
import jinja2
import pandas as pd

from flask import Flask, request, url_for, redirect, render_template, jsonify
from pycaret.classification import *
from df_manipulation import *
import config


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
    # int_features = [x for x in request.form.values()]

    final = []
    for i, x in enumerate(request.form.values()):
        if i == 1 or i == 2 or i == 3:
            final.append(str(x))
        elif i == 4 or i == 5 or i == 6:
            final.append(float(x))
        else:
            final.append(int(x))

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
