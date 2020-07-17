from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)

import configparser
import requests
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


def scrape_pcrd_cygame():
    
    cygame_url = "https://priconne-redive.jp"
    response = requests.get(cygame_url + '/news')
    soup = BeautifulSoup(response.text, "html.parser")

    new_info = soup.find("div", {"class": "news-list-contents"}).findAll("div", {"class": "article_box"})
    
    time = []
    url = []
    content = []
    
    num = len(new_info)
    for i in range(num):
        time.append(new_info[i].time.text)
        url.append(new_info[i].a['href'])
        content.append(new_info[i].h4.text)

    ISOTIMEFORMAT = '%Y-%m-%d'
    todayTime = datetime.now()

    news = False
    msg = '今日日服最新消息:\n'
    for i in range(num):
        newTime = datetime.strptime(time[i], "%Y.%m.%d")
        if todayTime.month == newTime.month and todayTime.day == newTime.day:
            news = True
            msg += content[i] + '\n'
            msg += url[i] + '\n'
            
    if news:
        return msg
    else:
        return '今日日服無新消息'


if __name__ == "__main__":
    msg = scrape_pcrd_cygame()
    if msg != '今日日服無新消息':
        users = get_all_subscriber()
        for user in users.values():
            result = lineNotifyMessage(user, msg)

        # line_bot_api.push_message('C423cd7dee7263b3a2db0e06ae06d095e', TextSendMessage(text=msg))