import pandas as pd
import pickle
import numpy as np

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


def create_main_cols(all_season, x, team):

    #get current and last delta (years) rank
    team_rank = get_rank(all_season, x, team, 0)
    ls_team_rank = get_rank(all_season, x, team, 1)

    #get main match stats
    total_points, total_l_points, total_l_w_avg_points, total_goals, total_l_goals, total_l_w_avg_goals, total_goals_sf, total_l_goals_sf, total_l_w_avg_goals_sf, total_wins, total_draws, total_losses, win_streak, loss_streak, draw_streak = get_match_stats(all_season, x)

    #get days since last match
    days = get_days_ls_match(all_season, x, team)

    return team_rank, ls_team_rank, days, total_points, total_l_points, total_l_w_avg_points, total_goals, total_l_goals, total_l_w_avg_goals, total_goals_sf, total_l_goals_sf, total_l_w_avg_goals_sf, total_wins, total_draws, total_losses, win_streak, loss_streak, draw_streak


def get_rank(all_season, x, team, delta_year):
    full_season_df = all_season[(
        all_season["season"] == (x["season"] - delta_year))]

    full_home_df = full_season_df.groupby(['HomeTeam']).sum()[['h_match_points', 'FTHG', 'FTAG']].reset_index()
    full_home_df.columns = ['team', 'points', 'goals', 'goals_sf']

    full_away_df = full_season_df.groupby(['AwayTeam']).sum()[['a_match_points', 'FTAG', 'FTHG']].reset_index()
    full_away_df.columns = ['team', 'points', 'goals', 'goals_sf']

    rank_df = pd.concat([full_home_df, full_away_df], ignore_index = True)
    rank_df['goals_df'] = rank_df.goals - rank_df.goals_sf
    rank_df = rank_df.groupby(['team']).sum().reset_index()
    rank_df = rank_df.sort_values(by = ['points', 'goals_df', 'goals'], ascending = False)
    rank_df['rank'] = rank_df.points.rank(method = 'first', ascending = False).astype(int)

    team_rank = rank_df[rank_df.team == team].min()['rank']

    return team_rank

def get_days_ls_match(all_season, x, team):

    #filtering last game of the team and getting date
    last_date = all_season[(all_season.Date < x.Date) & (all_season.season == x.season) & (
        (all_season["HomeTeam"] == team) | (all_season["AwayTeam"] == team))].Date.max()

    days = (x.Date - last_date)/np.timedelta64(1, 'D')

    return days

def get_match_stats(all_season, df):
    #home df filter
    home_df = all_season[(all_season.HomeTeam == df.HomeTeam) & (
        all_season.Date < df.Date) & (all_season.season == df.season)]

    #home df filter
    away_df = all_season[(all_season.AwayTeam == df.AwayTeam) & (
        all_season.Date < df.Date) & (all_season.season == df.season)]

    #points
    home_table = home_df.groupby(['Date']).sum(
        )[['h_match_points', 'FTHG', 'FTAG']].reset_index()
    
    home_table.columns = ['Date', 'points', 'goals', 'goals_sf']
    home_table['goals_df'] = home_table.goals - home_table.goals_sf
    home_table['host'] = 'home'


    away_table = away_df.groupby(['Date']).sum(
    )[['a_match_points', 'FTAG', 'FTHG']].reset_index()
    
    away_table.columns = ['date', 'points', 'goals', 'goals_sf']
    away_table['goals_df'] = away_table.goals - away_table.goals_sf
    away_table['host'] = 'away'

    full_table = pd.concat([home_table, away_table], ignore_index=True)
    full_table = full_table.sort_values('Date', ascending=True)

    #get streaks
    full_table['start_of_streak'] = full_table.points.ne(
        full_table.points.shift())
    full_table['streak_id'] = full_table['start_of_streak'].cumsum()
    full_table['streak_counter'] = full_table.groupby(
        'streak_id').cumcount() + 1

    #make exponentially weighted average
    full_table['w_avg_points'] = full_table.points.ewm(
        span=3, adjust=False).mean()
    full_table['w_avg_goals'] = full_table.goals.ewm(
        span=3, adjust=False).mean()
    full_table['w_avg_goals_sf'] = full_table.goals_sf.ewm(
        span=3, adjust=False).mean()

    streak_table = full_table[full_table.Date == full_table.Date.max()]

    if streak_table.points.min() == 3:
        win_streak = streak_table.streak_counter.sum()
        loss_streak = 0
        draw_streak = 0
    elif streak_table.points.min() == 0:
        win_streak = 0
        loss_streak = streak_table.streak_counter.sum()
        draw_streak = 0
    else:
        win_streak = 0
        loss_streak = 0
        draw_streak = streak_table.streak_counter.sum()

    home_points = home_table.points.sum()
    home_goals = home_table.goals.sum()
    home_goals_sf = home_table.goals_sf.sum()
    home_wins = len(home_table[home_table.points == 3])
    home_draws = len(home_table[home_table.points == 1])
    home_losses = len(home_table[home_table.points == 0])

    away_points = away_table.points.sum()
    away_goals = away_table.goals.sum()
    away_goals_sf = away_table.goals_sf.sum()
    away_wins = len(away_table[away_table.points == 3])
    away_draws = len(away_table[away_table.points == 1])
    away_losses = len(away_table[away_table.points == 0])

    #total points stats
    total_points = home_points + away_points
    total_goals = home_goals + away_goals
    total_goals_sf = home_goals_sf + away_goals_sf
    total_wins = home_wins + away_wins
    total_draws = home_draws + away_draws
    total_losses = home_losses + away_losses

    #getting data for a given delta
    full_table_delta = full_table[full_table.Date.isin(full_table.Date[-3:])]

    home_l_points = full_table_delta[full_table_delta.host == 'home'].points.sum()
    away_l_points = full_table_delta[full_table_delta.host == 'away'].points.sum()

    #total metric in given delta averaged
    total_l_points = (home_l_points + away_l_points)/3
    total_l_goals = (home_goals + away_goals)/3
    total_l_goals_sf = (home_goals_sf + away_goals)/3

    total_l_w_avg_points = full_table[full_table.Date.isin(
        full_table.Date[-1:])].w_avg_points.sum()
    total_l_w_avg_goals = full_table[full_table.Date.isin(
        full_table.Date[-1:])].w_avg_goals.sum()
    total_l_w_avg_goals_sf = full_table[full_table.Date.isin(
        full_table.Date[-1:])].w_avg_goals_sf.sum()

    return total_points, total_l_points, total_l_w_avg_points, total_goals, total_l_goals, total_l_w_avg_goals, total_goals_sf, total_l_goals_sf, total_l_w_avg_goals_sf, total_wins, total_draws, total_losses, win_streak, loss_streak, draw_streak

def get_ls_winner(all_season, x):
    temp_df = all_season[(all_season.Date < x.Date) & (((all_season.HomeTeam == x.HomeTeam) & (
        all_season.AwayTeam == x.AwayTeam)) | ((all_season.HomeTeam == x.AwayTeam) & (all_season.AwayTeam == x.HomeTeam)))]
    temp_df = temp_df[temp_df.Date == temp_df.Date.max()]

    #checking if there was a previous match
    if len(temp_df) == 0:
        result = None
    elif temp_df["FTR"].values[0] == 'D':
        result = 'D'
    elif temp_df.HomeTeam.all() == x.HomeTeam:
        result = temp_df["FTR"].values[0]
    else:
        if temp_df["FTR"].values[0] == 'H':
            result = 'H'
        else:
            result = 'A'
    return result

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
