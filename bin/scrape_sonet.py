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
    # print(info)
    # print(status)

    for i in new_info.findAll('dd'):
        content.append(i.text.strip())
        url.append(i.a['href'])
    # print(content)
    #print(url)

    num = len(info)

    ISOTIMEFORMAT = '%Y-%m-%d'
    todayTime = datetime.now()

    msg = '今日最新消息:\n'
    for i in range(num):
        new_time = info[i].replace(status[i], '')
        newTime = datetime.strptime(new_time, "%Y.%m.%d")
        if todayTime.month == newTime.month and todayTime.day == newTime.day:
            msg += content[i] + '\n'
            msg += sonet_url + url[i] + '\n'
            # print(content[i])
    
    return msg


if __name__ == "__main__":
    msg = scrape_pcrd_sonet()
    line_bot_api.push_message('C423cd7dee7263b3a2db0e06ae06d095e', TextSendMessage(text=msg))