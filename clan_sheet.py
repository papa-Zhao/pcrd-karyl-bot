import numpy as np
import pandas as pd
import pygsheets

from dateutil import tz
from dateutil.tz import tzlocal
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

def initial_worksheet():
    gc = pygsheets.authorize(service_file='./key/google_key.json')
    url = '1mf3P9MQ5NgNd-ByXk-Z3TqqF0zY5ctLdpmZmdkFpbC8'
    sh = gc.open_by_key(url)
    # ws = sh.worksheet_by_title('clan_may')
    return sh

def create_worksheet():
    group_name = '凱留水球噠噠噠'
    gc = pygsheets.authorize(service_file='./key/google_key.json')
    sh = gc.create(group_name + '戰隊戰表格')
    print(sh.url)
    sh.share('', role='writer', type='anyone')
    return sh.url

def set_clan_worksheet(ws, total):
    ws.clear()
    box = []
    
    round = []
    for i in range(5*total):
        if i%5 == 0:
            cycle = int(i/5+1)
            round.append(str(cycle))
        else:
            round.append('')
    box.append(round)
    
    boss_round = []
    boss = ['一王', '二王', '三王', '四王', '五王']
    for i in range(total):
        for j in range(5):
            boss_round.append(boss[j%5])
    box.append(boss_round)

    df = pd.DataFrame(box)
    
    #print(df)
    try:
        print(df)
        # ws.set_dataframe(df, 'B1', copy_index=False, copy_head=False, nan='')
    except gspread.exceptions.RequestError:
        print('Not Success')


def get_time(time):
    timestamp = time/1000
    print('timestamp=', timestamp)
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('CST')
    dt = datetime.utcfromtimestamp(timestamp)
    utc = datetime.utcnow()
    utc = dt.replace(tzinfo=from_zone)
    local = utc.astimezone(to_zone)
    get_time = datetime.strftime(local, "%m-%d %H:%M:%S")
    # print(get_time)
    return get_time