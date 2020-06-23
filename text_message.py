from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)

import configparser
import random


from clan import *
from clan_sheet import *

from cloud_firestore import *
from keyword_reply import *
from imgur import *


config = configparser.ConfigParser()
config.read('config.ini')
# config.read('test_config.ini')
# Channel Access Token
line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
# Channel Secret
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

def strQ2B(text):
    ss = []
    for s in text:
        string = ""
        for uchar in s:
            inside_code = ord(uchar)
            if inside_code == 12288:  # transfer fullwidth space to halfwidth space
                inside_code = 32
            elif (inside_code >= 65281 and inside_code <= 65374):  # transfer fullwidth string to halfwidth string except space
                inside_code -= 65248
            string += chr(inside_code)
        ss.append(string)
    return ''.join(ss)


def handle_user_text_message(event):

    reply_msg = ''

    msg = event.message.text
    user_id = event.source.user_id

    msg = strQ2B(msg)
    
    if '#' == msg:
        msg = msg.replace('#', '')
        reply_msg = clan_user_str_processing(user_id, msg)
    else:
        handle_key_message(event) 


    return reply_msg


def handle_group_text_message(event):

    reply_msg = ''

    msg = event.message.text
    group_id = event.source.group_id
    user_id = event.source.user_id
    group_profile = line_bot_api.get_group_member_profile(group_id, user_id)
    user_name = group_profile.display_name
    
    msg = strQ2B(msg)

    if '!' == msg[0]:
        msg = msg.replace('!', '')
        reply_msg = clan_group_find_str_processing(group_id, user_id, user_name, msg)
    elif '#' == msg[0]:
        group_member = get_group_member(group_id)
        try:
            group_member[user_name]
            if clan_period():
                msg = msg.replace('#', '')
                reply_msg = clan_group_set_str_processing(group_id, user_id, user_name, msg)
            else:
                reply_msg = '非戰隊戰期間，不開放此功能'
        except KeyError:
            reply_msg = user_name + '，你非戰隊成員，請先加入戰隊戰。'
    else:
        handle_key_message(event) 

    return reply_msg


def handle_key_message(event):

    # print(event.reply_token)
    msg = event.message.text
    key = ['街頭霸王', '開車', '表情包', '聯盟戰', '可愛', '抽卡', '吸貓']
    reply_msg = ''


    ##########  Image reply  ##########
    for i in range(len(key)):
        if key[i] in msg:
            print('關鍵字: %s' %(key[i]))
            # url = get_url(key[i])
            url = get_album_image(key[i])
            send_msg = ImageSendMessage(url, url)
            line_bot_api.reply_message(event.reply_token, send_msg)

    ##########  Text reply  ##########
    if '凱留' in msg:
        user_id = event.source.user_id
        profile = line_bot_api.get_profile(user_id)
        name = profile.display_name
        reply_msg = get_key_msg(msg, name)
        send_msg = TextSendMessage(text= reply_msg )
        line_bot_api.reply_message(event.reply_token, send_msg)
