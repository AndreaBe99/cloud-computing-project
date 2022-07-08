import pandas as pd
import config
import random

# Check Teams
all_season = pd.read_csv(config.DATASET, low_memory=False)

r = random.randint(0, all_season.HomeTeam.nunique() - 1)
home_team = all_season.HomeTeam.unique()[r]

all_away_team = all_season.AwayTeam.unique()
all_away_team = all_away_team[all_away_team != home_team]

r = random.randint(0, len(all_away_team) - 1)
away_team = all_away_team[r]

print(home_team, away_team)
