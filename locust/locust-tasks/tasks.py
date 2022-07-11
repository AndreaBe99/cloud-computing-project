#!/usr/bin/env python

# Copyright 2022 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import final

from datetime import timedelta, datetime, date
from locust import FastHttpUser, TaskSet, task

import pandas as pd
import random

# Dataset Github Path
PATH_DATASET = "https://raw.githubusercontent.com/AndreaBe99/cloud-computing-project/main/datasets/"
DATASET = PATH_DATASET + "final_all_season.csv"


# [START locust_test_task]

class MetricsTaskSet(TaskSet):
    _match_date = None
    _home_team = None
    _away_team = None

    def on_start(self):
        # Create a dataframe from the HTML form
        # Get tomorrow's date
        self._match_date = date.today() + timedelta(days=1)
        all_season = pd.read_csv(DATASET, low_memory=False)

        # Check Teams
        r = random.randint(0, all_season.HomeTeam.nunique() - 1)
        self._home_team = all_season.HomeTeam.unique()[r]

        all_away_team = all_season.AwayTeam.unique()
        all_away_team = all_away_team[all_away_team != self._home_team]
        r = random.randint(0, len(all_away_team) - 1)
        self._away_team = all_away_team[r]
        
    @task(1)
    def predict_test(self):
        myheaders = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        self.client.post(
            '/predict_test', {
                "match_date": self._match_date, 
                "home_team": self._home_team, 
                "away_team": self._away_team},
            headers=myheaders)

class MetricsLocust(FastHttpUser):
    tasks = {MetricsTaskSet}

# [END locust_test_task]
