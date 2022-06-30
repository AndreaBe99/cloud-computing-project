import pandas as pd
import pickle
import numpy as np
from df_Manipulation import * 

PATH = "https://raw.githubusercontent.com/AndreaBe99/cloud-computing-project/main/final_all_season.csv"


def dataset_manipulation(df):
    all_season = pd.read_csv(PATH, low_memory=False)
    print(all_season.head())

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




if __name__ == '__main__':
    # open a file, where you stored the pickled data
    file = open('lr_model.pkl', 'rb')
    # dump information to that file
    model = pickle.load(file)
    # close the file
    file.close()
    
    cols = ['season', 'Date', 'HomeTeam', 'AwayTeam', 'B365H', 'B365D', 'B365A']
    final = [2021, "02/02/2022", "Juventus", "Inter", 2.8, 3.4, 2.5]
    
    data_unseen = pd.DataFrame([final], columns = cols)
    df = dataset_manipulation(data_unseen)
    #saving data
    df.to_csv('one_line.csv', index = False)
    print(df)
