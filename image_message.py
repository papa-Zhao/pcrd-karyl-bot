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
# Channel Access Token
line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
# Channel Secret
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

r = redis.from_url(os.environ['REDIS_URL'], decode_responses=True)
# r = redis.StrictRedis(decode_responses=True)


def content_to_image(content):

    # Convert to base64 encoding
    img_as_text = base64.b64encode(content)

    # Convert back to binary
    img_original = base64.b64decode(img_as_text)
    img_as_np = np.frombuffer(img_original, dtype=np.uint8)
    img = cv2.imdecode(img_as_np, flags=1)

    return img


def determine_arena_img(img):

    if img.shape[0] > img.shape[1]:
        return False
    else:
        return True


def get_user_image_msg_info(event):

    msg_id = event.message.id
    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)
    user_name = profile.display_name

    return msg_id, user_id, user_name 


def handle_user_image_message(event):

    reply_msg = ''
    msg_id, user_id, name = get_user_image_msg_info(event)

    message_content = line_bot_api.get_message_content(msg_id)
    content = message_content.content
    img = content_to_image(content)
    
    corrtect = determine_arena_img(img)
    if corrtect == False:
        reply_msg = ''
        return reply_msg

    mode, pre_img = preprocessing(img)
    # print('mode=', mode)
    if mode == 'not record':
        return reply_msg

    if mode == 'upload' or mode == 'friend_upload':
        region = decide_where(pre_img)
        our, enemy, win = upload_battle_processing(pre_img, region, mode)
        if mode == 'friend_upload':
            our, enemy = sort_character_loc(our, enemy)

        status = confirm_record_success(our, enemy, mode)
        if status == True:
            if mode == 'friend_upload':
                find_status = find_arena_record(our, enemy, win, user_id)
                if find_status == 'repeated':
                    reply_msg = '上傳失敗，此對戰紀錄您已上傳過。'
                    return reply_msg

                reply_msg = get_record_msg(our, enemy, win, find_status)
            else:
                key = user_id
                r.delete(key + "our")
                r.delete(key + "enemy")
                r.delete(key + "win")
                
                # print('win = ', str(win))
                for i in range(len(our)):
                    r.rpush(key + "our", our[i])
                for i in range(len(our)):
                    r.rpush(key + "enemy", enemy[i])
                r.expire(key + "our", time=10)
                r.expire(key + "enemy", time=10)
                r.set(key + 'win', str(win), ex=10)
                r.set(key + 'status', 'True', ex=10)

                with open('./reply_template/atk_quick_reply.json', newline='') as jsonfile:
                    data = json.load(jsonfile)
                text_message = TextSendMessage(text= '請問您是哪一方？1(進攻)，0(防守)' , quick_reply = data)
                line_bot_api.reply_message(event.reply_token, text_message)
    else:
        # print('search')
        enemy = search_battle_processing(pre_img)
        status = confirm_record_success([], enemy, mode)
        if status == True:
            record, good, bad = search_arena_record(enemy, user_id)
            record, good, bad = sort_arena_record(record, good, bad)
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


def handle_group_image_message(event):

    reply_msg = ''
    msg_id = event.message.id
    group_id = event.source.group_id
    user_id = event.source.user_id
    print('group_id = ', group_id)

    message_content = line_bot_api.get_message_content(msg_id)
    content = message_content.content
    img = content_to_image(content)
    corrtect = determine_arena_img(img)

    if corrtect == False:
        return reply_msg

    mode, pre_img = preprocessing(img)
    if mode == 'not record':
        return reply_msg

    if mode == 'upload' or mode == 'friend_upload':
        region = decide_where(pre_img)
        our, enemy, win = upload_battle_processing(pre_img, region, mode)
        if mode == 'friend_upload':
            our, enemy = sort_character_loc(our, enemy)

        status = confirm_record_success(our, enemy, mode)
        if status == True:
            if mode == 'friend_upload':
                find_status = find_group_arena_record(our, enemy, win, group_id)
                if find_status == 'success':
                    reply_msg = get_record_msg(our, enemy, win, find_status)
                    return reply_msg
            else:
                key = group_id + user_id
                r.delete(key + "our")
                r.delete(key + "enemy")
                r.delete(key + "win")
                
                for i in range(len(our)):
                    r.rpush(key + "our", our[i])
                for i in range(len(our)):
                    r.rpush(key + "enemy", enemy[i])
                r.expire(key + "our", time=10)
                r.expire(key + "enemy", time=10)
                r.set(key + 'win', str(win), ex=10)

                text_message = TextSendMessage(text= '請問您是哪一方？1(進攻)，0(防守)')
                line_bot_api.reply_message(event.reply_token, text_message)
    else:
        enemy = search_battle_processing(pre_img)
        status = confirm_record_success([], enemy, mode)
        if status == True:
            record, good, bad = search_group_arena_record(enemy, group_id)
            record, good, bad = sort_arena_record(record, good, bad)
            if len(record) > 0:
                reply_img = create_record_img(record, good, bad)
                url = upload_album_image(reply_img)
                return url
            else:
                reply_msg = '此對戰紀錄不存在'
                return reply_msg

    return reply_msg