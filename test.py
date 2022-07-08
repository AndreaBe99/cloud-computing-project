import pandas as pd
import config
import random
from datetime import timedelta, datetime, date

#datetime.now() + timedelta(days=1)

today = date.today()
tomorrow = today + timedelta(days=1)
#datetime_object = datetime.strptime(match_date, '%Y-%m-%d').date()
#print(today, tomorrow)

match_date = datetime.strptime(str(tomorrow), '%Y-%m-%d').date()
print(match_date)
