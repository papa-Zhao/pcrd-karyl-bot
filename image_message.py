from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)

import configparser
import random2 as random
import pybase64 as base64
import cv2
import numpy as np

from imgur import *
from app import *
from arena import *
from cloud_firestore import *


config = configparser.ConfigParser()
config.read('config.ini')
# config.read('test_config.ini')
# Channel Access Token
line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
# Channel Secret
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))


def get_image():
    image = None
    return image

def content_to_image(content):

    # Convert to base64 encoding
    img_as_text = base64.b64encode(content)

    # Convert back to binary
    img_original = base64.b64decode(img_as_text)
    img_as_np = np.frombuffer(img_original, dtype=np.uint8)
    img = cv2.imdecode(img_as_np, flags=1)

    return img



def handle_user_image_message(event):

    reply_msg = '此圖片非競技場圖片'
    msg_id = event.message.id
    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)
    name = profile.display_name

    message_content = line_bot_api.get_message_content(msg_id)
    content = message_content.content
    img = content_to_image(content)
    mode, pre_img = preprocessing(img)
    
    if mode == 'not record':
        return reply_msg

    print('圖片mode = ', mode)
    if mode == 'upload':
        our, enemy, win = upload_battle_processing(pre_img)
        print('our = %s' %(our))
        print('enemy = %s' %(enemy))
        status = confirm_record_success(our, enemy, mode)
        if status == True:
            find_status = find_arena_record(our, enemy, win, user_id)
            # print('find_status = %s' %(find_status))
            if find_status == 'repeat':
                reply_msg = '上傳失敗，此對戰紀錄你已上傳過。'
                return reply_msg
            reply_msg = get_record_msg(our, enemy, win)
        else:
            reply_msg = '上傳失敗，圖片讀取錯誤。'
    else:
        enemy = search_battle_processing(pre_img)
        status = confirm_record_success(enemy, enemy, mode)
        if status == True:
            record, good, bad = search_arena_record(enemy)
            if len(record) > 0:
                reply_img = create_record_img(record, good, bad)
                url = upload_album_image(reply_img)
                return url
            else:
                reply_msg = '此對戰紀錄不存在'
                return reply_msg
        else:
            reply_msg = '查詢失敗，圖片讀取錯誤。'

    return reply_msg