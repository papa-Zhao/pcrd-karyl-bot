from cloud_firestore import *

from dateutil import tz
from dateutil.tz import tzlocal
from datetime import datetime, timedelta

from linebot import (
    LineBotApi, WebhookHandler
)

from app import *

import configparser
import sys
sys.path.append('./bin')
from scrape_sonet import *
from scrape_cygame import *

config = configparser.ConfigParser()
config.read('config.ini')
# Channel Access Token
line_notify_client_id = config.get('line-notify', 'client_id')
# Channel Secret
line_notify_client_secret = config.get('line-notify', 'client_secret')
line_notify_redirect_uri = config.get('line-notify', 'redirect_uri')


def subscribe_str_processing(msg):

    reply_msg = ''

    if msg == '訂閱凱留報報':
        reply_msg = 'https://notify-bot.line.me/oauth/authorize'
        reply_msg += '?response_type=code'
        reply_msg += '&client_id=' + line_notify_client_id
        reply_msg += '&redirect_uri=' + line_notify_redirect_uri
        reply_msg += '&scope=notify&state=1234'

    return reply_msg


def get_line_notify_token(code):

    print('type = ', type(code))
    client = {'grant_type': 'authorization_code', 'code': code, 'redirect_uri': line_notify_redirect_uri,
                    'client_id': line_notify_client_id, 'client_secret': line_notify_client_secret}
    r = requests.post(
        'https://notify-bot.line.me/oauth/token', data=client)

    req = json.loads(r.text)
    print('access_token = ', req['access_token'])
    insert_line_notify_subscriber(req['access_token'])

    return req