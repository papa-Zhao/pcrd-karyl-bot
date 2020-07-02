from linebot import (
    LineBotApi, WebhookHandler
)

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)

from datetime import datetime
from bs4 import BeautifulSoup
import requests
import configparser


import sys
sys.path.append('../')

config = configparser.ConfigParser()
config.read('config.ini')
# config.read('test_config.ini')
# Channel Access Token
line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
# Channel Secret
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

def scrape_pcrd_cygame():
    cygame_url = "https://priconne-redive.jp"
    response = requests.get(cygame_url + '/news')
    soup = BeautifulSoup(response.text, "html.parser")

    new_info = soup.find("div", {"class": "news-list-contents"}).findAll("div", {"class": "article_box"})
    
    time = []
    url = []
    content = []
    
    num = len(new_info)
    # print(new_info)
    for i in range(num):
        # print(new_info[i].time)
        time.append(new_info[i].time.text)
        # print(new_info[i].a['href'])
        url.append(new_info[i].a['href'])
        # print(new_info[i].h4)
        content.append(new_info[i].h4.text)
        
    # print(url)

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
            # print(content[i])
            
    if news:
        return msg
    else:
        return '今日日服無新消息'


if __name__ == "__main__":
    msg = scrape_pcrd_cygame()
    if msg != '今日日服無新消息':
        line_bot_api.push_message('C423cd7dee7263b3a2db0e06ae06d095e', TextSendMessage(text=msg))