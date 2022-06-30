from flask import Flask,request, url_for, redirect, render_template, jsonify
from pycaret.regression import *
import pandas as pd
import pickle
import numpy as np

PATH = "https://raw.githubusercontent.com/AndreaBe99/cloud-computing-project/main/final_all_season.csv"

app = Flask(__name__)

model = pickle.load('../lr_model.pkl')
cols = ['season', 'Date', 'HomeTeam', 'AwayTeam', 'B365H', 'B365D', 'B365A']

@app.route('/')
def home():
   return render_template('home.html')

def dataset_manipulation(df):
    all_season = pd.read_csv(PATH, low_memory=False)

    # Get Rank of current season
    df['ht_rank'] = np.where(all_season['HomeTeam'] == df['HomeTeam'][0] & all_season['season'] == df['season'][0], all_season['ht_rank'][0])
    df['at_rank'] = np.where(all_season['AwayTeam'] == df['AwayTeam'][0] & all_season['season'] == df['season'][0], all_season['at_rank'][0])

    # Get Rank of last season
    df['ht_ls_rank'] = np.where(all_season['HomeTeam'] == df['HomeTeam'][0] & all_season['season'] == df['season'][0], all_season['ht_ls_rank'][0])
    df['at_ls_rank'] = np.where(all_season['AwayTeam'] == df['AwayTeam'][0] & all_season['season'] == df['season'][0], all_season['at_ls_rank'][0])  

    # Get amount of days since last match
    last_date = all_season[(all_season['Date'] < df['Date']) & (all_season['season'] == df['season']) & ( (all_season["HomeTeam"] == df['HomeTeam']) | (all_season["AwayTeam"] == df['HomeTeam']) ) ].Date.max()
    days = (df['Date'] - last_date)/np.timedelta64(1,'D')
    df['ht_days_ls_match'] = days

    last_date = all_season[(all_season['Date'] < df['Date']) & (all_season['season'] == df['season']) & ( (all_season["HomeTeam"] == df['AwayTeam']) | (all_season["AwayTeam"] == df['AwayTeam']) ) ].Date.max()
    days = (df['Date'] - last_date)/np.timedelta64(1,'D')
    df['at_days_ls_match'] = days

    


    # Convert Date Column to Datetime
    df['Date'] = pd.to_datetime(df.Date)

@app.route('/predict',methods=['POST'])
def predict():
    int_features = [x for x in request.form.values()]
    final = np.array(int_features)
    data_unseen = pd.DataFrame([final], columns = cols)
    prediction = predict_model(model, data=data_unseen, round = 0)
    prediction = int(prediction.Label[0])
    return render_template('home.html',pred='Expected Bill will be {}'.format(prediction))

@app.route('/predict_api',methods=['POST'])
def predict_api():
    data = request.get_json(force=True)
    data_unseen = pd.DataFrame([data])
    prediction = predict_model(model, data=data_unseen)
    output = prediction.Label[0]
    return jsonify(output)

if __name__ == '__main__':
   app.run()