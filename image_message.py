from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)

import configparser
import cv2
import numpy as np
import pybase64 as base64
import random2 as random
import redis
import redis_lock

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


def is_arena_img(img):

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

    if not is_arena_img(img):
        reply_msg = ''
        return reply_msg

    mode, pre_img = preprocessing(img)
    print('mode=', mode)
    if mode == 'not record':
        return reply_msg

    if mode == 'upload' or mode == 'friend_upload':
        region = decide_where(pre_img)
        our, enemy, win = upload_battle_processing(pre_img, region, mode)
        # print(our, enemy, win)
        status = confirm_record_success(our, enemy, mode)
        if status == True:
            if mode == 'friend_upload':
                our = sort_character_loc(our)
                enemy = sort_character_loc(enemy)
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

                for i in range(len(our)):
                    r.rpush(key + "our", our[i])
                for i in range(len(our)):
                    r.rpush(key + "enemy", enemy[i])
                r.expire(key + "our", time=10)
                r.expire(key + "enemy", time=10)
                r.set(key + 'win', str(win), ex=10)
                r.set(key + 'status', 'True')

                with open('./reply_template/atk_quick_reply.json', newline='') as jsonfile:
                    data = json.load(jsonfile)
                text_message = TextSendMessage(text= '請問您是哪一方？1(進攻)，0(防守)' , quick_reply = data)
                line_bot_api.reply_message(event.reply_token, text_message)
        
        return reply_msg
    
    if mode == '3v3':
        our, enemy, win = upload_3v3_battle_processing(pre_img)
        reply_msg = get_3v3_record_msg(our, enemy, win)
    
    if mode == 'search':
        reply_msg = '查詢失敗，圖片讀取錯誤。'
        enemy = search_battle_processing(pre_img)
        status = confirm_record_success([], enemy, mode)
        if status == True:
            reply_msg = get_user_search_record(enemy, user_id)
        
        return reply_msg

    return reply_msg


def handle_group_image_message(event):

    reply_msg = ''
    msg_id = event.message.id
    group_id = event.source.group_id
    user_id = event.source.user_id
    # print('')
    message_content = line_bot_api.get_message_content(msg_id)
    content = message_content.content
    img = content_to_image(content)
    
    if not is_arena_img(img):
        return reply_msg

    mode, pre_img = preprocessing(img)
    if mode == 'not record':
        return reply_msg

    if mode == 'upload' or mode == 'friend_upload':
        region = decide_where(pre_img)
        our, enemy, win = upload_battle_processing(pre_img, region, mode)
        # print('our = ', our)
        # print('enemy = ', enemy)
        status = get_group_arena_utmost_star(group_id)
        if status == True:
            our = change_character_to_6x(our)
            enemy = change_character_to_6x(enemy)
            # print('our = ', our)
            # print('enemy = ', enemy)
            
        status = confirm_record_success(our, enemy, mode)
        if status == True:
            if mode == 'friend_upload':
                our = sort_character_loc(our)
                enemy = sort_character_loc(enemy)
                find_status = find_group_arena_record(our, enemy, win, group_id)
                if find_status == 'success':
                    reply_msg = get_group_record_msg(our, enemy, win, find_status)
                    return reply_msg
            if mode == 'upload':
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
                r.set(key + 'status', 'True')
                r.set(key + 'mode', 'Upload')

                text_message = TextSendMessage(text= '請問您是哪一方？1(進攻)，0(防守)')
                line_bot_api.reply_message(event.reply_token, text_message)
    
    if mode == '3v3':
        our, enemy, win = upload_3v3_battle_processing(pre_img)
        reply_msg = get_3v3_record_msg(our, enemy, win)

        status = get_group_arena_utmost_star(group_id)
        if status == True:
            for num in range(len(our)):
                # print(our[num])
                # print(enemy[num])
                our[num] = change_character_to_6x(our[num])
                enemy[num] = change_character_to_6x(enemy[num])
                # print(our[num])
                # print(enemy[num])

        status = False
        for num in range(len(our)):
            status = confirm_record_success(our[num], enemy[num], mode)
            if status == False:
                reply_msg = ''
                break
        
        if status == True:
            key = group_id + user_id
            r.delete(key + 'our')
            r.delete(key + 'enemy')
            r.delete(key + 'win')
            
            for record in range(len(our)):
                for character in range(len(our[record])):
                    r.rpush(key + "our" + str(record), our[record][character])
                    r.expire(key + "our" + str(record), time = 10)
            for record in range(len(enemy)):
                for character in range(len(enemy[record])):
                    r.rpush(key + "enemy" + str(record), enemy[record][character])
                    r.expire(key + "enemy" + str(record), time = 10)
            for record in range(len(win)):
                r.set(key + 'win' + str(record), str(win[record]), ex=10)

            r.set(key + 'status', 'True')
            r.set(key + 'mode', '3v3')
            r.set(key + 'count', str(len(win)), ex = 10)

            text_message = TextSendMessage(text= '請問您是哪一方？1(進攻)，0(防守)')
            line_bot_api.reply_message(event.reply_token, text_message)
            reply_msg = ''
            return reply_msg
    
    if mode == 'search':
        enemy = search_battle_processing(pre_img)
        # print('enemy = ', enemy)
        status = get_group_arena_utmost_star(group_id)
        if status == True:
            enemy = change_character_to_6x(enemy)
            # print('enemy = ', enemy)

        status = confirm_record_success([], enemy, mode)
        if status == True:
            record, good, bad = search_group_arena_record(enemy, group_id)
            record, good, bad = sort_arena_record(record, good, bad)
            if len(record) > 0:
                reply_img = create_group_record_img(record, good, bad)
                # url = upload_album_image(reply_img)
                # url = get_arena_solutions_image(reply_img)
                url = get_nacx_image(reply_img)
                return url
            else:
                reply_msg = '此對戰紀錄不存在'
                return reply_msg

    return reply_msg