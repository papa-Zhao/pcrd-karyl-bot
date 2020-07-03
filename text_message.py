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

import sys
sys.path.append('./bin')
from scrape_sonet import *


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

    if '#' in msg:
        if clan_period():
            info = get_user_info(user_id)
            try:
                karyl_group = ['C423cd7dee7263b3a2db0e06ae06d095e', 'C1f08f2cc641df24f803b133691e46e92']
                karyl_group.index(info['group_id'])
                msg = msg.replace('#', '')
                reply_msg = clan_user_str_processing(user_id, msg)
            except ValueError:
                reply_msg = '你不屬於凱留水球啵啵啵成員，無法使用此指令。'
        else:
            reply_msg = '非戰隊戰期間，不開放指令輸入。'
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

    try:

        karyl_group = ['C423cd7dee7263b3a2db0e06ae06d095e', 'C1f08f2cc641df24f803b133691e46e92']
        karyl_group.index(group_id)
    except ValueError:
        reply_msg = '此群組並非凱留水球啵啵啵群組，無法使用群組功能。'
        reply_msg += '\n若想使用群組功能請聯絡開發者 Email: r22742557@gmail.com'
        return reply_msg


    msg = strQ2B(msg)
    if '!' == msg[0]:
        msg = msg[1:]
        reply_msg = clan_group_find_str_processing(group_id, user_id, user_name, msg)
    elif '#' == msg[0]:
        group_member = get_group_member(group_id)
        try:
            group_member[user_name]
        except KeyError:
            reply_msg = user_name + '，你非戰隊成員，請先加入戰隊戰。'
        if clan_period():
            msg = msg[1:]
            reply_msg = clan_group_set_str_processing(group_id, user_id, user_name, msg)
        else:
            reply_msg = '非戰隊戰期間，不開放此功能'
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


    sticker_key = ['讚', '呼呼', '愛你', '哈哈', '早安', '失望', '累了', '餓', 
            '主人', '謝謝', '不愧是', '嗯?', '晚安', '不行唷!', '知道了', '請看',
            '拜託', '傲嬌', '不錯', '笨蛋', '掰掰', '有心就做得到', '隨便', '喵',
            '謝謝', '指教', '好厲害', 
            '死去', '放棄', '壞掉了', '奇怪的知識', '阿魯不搭', '怕', '可憐', '嚇到']

    for i in range(len(sticker_key)):
        if sticker_key[i] in msg:
            url = get_key_sticker(i)
            send_msg = ImageSendMessage(url, url)
            line_bot_api.reply_message(event.reply_token, send_msg)
            break
