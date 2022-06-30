from flask import Flask,request, url_for, redirect, render_template, jsonify
from pycaret.regression import *
import pandas as pd
import pickle
import numpy as np
from df_Manipulation import *

PATH = "https://raw.githubusercontent.com/AndreaBe99/cloud-computing-project/main/final_all_season.csv"

app = Flask(__name__)

# open a file, where you stored the pickled data
file = open('lr_model.pkl', 'rb')
# dump information to that file
model = pickle.load(file)
# close the file
file.close()
    
cols = ['season', 'Date', 'HomeTeam', 'AwayTeam', 'B365H', 'B365D', 'B365A']

@app.route('/')
def home():
   return render_template('home.html')

def dataset_manipulation(df):
    all_season = pd.read_csv(PATH, low_memory=False)

    # Convert Date Column to Datetime
    df['Date'] = pd.to_datetime(df.Date)
    all_season['Date'] = pd.to_datetime(all_season.Date)

    cols = ['_rank', '_ls_rank', '_days_ls_match', '_points',
        '_l_points', '_l_wavg_points', '_goals', '_l_goals', '_l_wavg_goals', 
        '_goals_sf', '_l_goals_sf', '_l_wavg_goals_sf','_wins', '_draws', 
        '_losses', '_win_streak', '_loss_streak', '_draw_streak']

    ht_cols = ['ht' + col for col in cols]
    at_cols = ['at' + col for col in cols]

    #gets main cols for home and away team
    df[ht_cols] = pd.DataFrame(df.apply(lambda x: create_main_cols(all_season, x, x.HomeTeam), axis=1).to_list(), index=df.index)
    df[at_cols] = pd.DataFrame(df.apply(lambda x: create_main_cols(all_season, x, x.AwayTeam), axis=1).to_list(), index=df.index)
    #result between last game of the teams
    df['ls_winner'] = df.apply(lambda x: get_ls_winner(all_season, x), axis = 1)

    return df

@app.route('/predict',methods=['POST'])
def predict():
    # Create a dataframe from the HTML form
    int_features = [x for x in request.form.values()]
    final = np.array(int_features)
    data_unseen = pd.DataFrame([final], columns = cols)

    # Add usefull column 
    data_unseen = dataset_manipulation(data_unseen)

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