from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)

import requests
import configparser
import sys
sys.path.append('../')

from datetime import datetime
from bs4 import BeautifulSoup

from cloud_firestore import *

config = configparser.ConfigParser()
config.read('config.ini')
# Channel Access Token
line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
# Channel Secret
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))


def lineNotifyMessage(token, msg):
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    payload = {'message': msg}
    r = requests.post(
        "https://notify-api.line.me/api/notify",
        headers=headers, 
        params=payload)
    return r.status_code


def scrape_pcrd_sonet():

    sonet_url = "http://www.princessconnect.so-net.tw"
    response = requests.get(sonet_url + '/news')
    soup = BeautifulSoup(response.text, "html.parser")

    new_info = soup.find("article", {"class": "news_con"}).find("dl")
    #print(new_info.findAll('dt'))

    info = []
    status = []
    url = []
    content = []

    for i in new_info.findAll('dt'):
        info.append(i.text.strip())
        status.append(i.span.text)

    for i in new_info.findAll('dd'):
        content.append(i.text.strip())
        url.append(i.a['href'])

    num = len(info)

    ISOTIMEFORMAT = '%Y-%m-%d'
    todayTime = datetime.now()

    news = False
    msg = '今日台服最新消息:\n'
    for i in range(num):
        new_time = info[i].replace(status[i], '')
        newTime = datetime.strptime(new_time, "%Y.%m.%d")
        if todayTime.month == newTime.month and todayTime.day == newTime.day:
            news = True
            msg += content[i] + '\n'
            msg += sonet_url + url[i] + '\n'
    
    if news:
        return msg
    else:
        return '今日台服無新消息'


if __name__ == "__main__":
    msg = scrape_pcrd_sonet()
    if msg != '今日台服無新消息':
        users = get_all_subscriber()
        for user in users.values():
            result = lineNotifyMessage(user, msg)
        # line_bot_api.push_message('C423cd7dee7263b3a2db0e06ae06d095e', TextSendMessage(text=msg))