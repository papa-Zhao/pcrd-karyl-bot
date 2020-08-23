# -*- coding: utf-8 -*
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, JoinEvent, LeaveEvent, MemberJoinedEvent, MemberLeftEvent, FollowEvent, UnfollowEvent, PostbackEvent,
    TextMessage, ImageMessage, LocationMessage, 
    TextSendMessage, ImageSendMessage, TemplateSendMessage, FlexSendMessage, 
    MessageAction, DatetimePickerAction, PostbackAction, URIAction, CameraAction, CameraRollAction, LocationAction,
    QuickReply, QuickReplyButton, 
    ButtonsTemplate,
)

import configparser
import copy
import json
import os
import redis
import requests
from flask import abort, Flask, jsonify, request

from cloud_firestore import *
from image_message import *
from imgur import *
from paper import *
from text_message import *


app = Flask(__name__)

config = configparser.ConfigParser()
config.read('config.ini')
# Channel Access Token
line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
# Channel Secret
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

@app.route("/callback", methods=['POST'])
def callback():

    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@app.route('/notify', methods=['GET'])
def notify():

    token = request.args.get('code')
    user_id = request.args.get('state')
    response = get_line_notify_token(token, user_id)

    if response['status'] == 200:
        reply_msg = jsonify({'id': user_id, 'token': response['access_token']})
    else:
        reply_msg = jsonify({'message': response['message']})

    return reply_msg


def is_reply_img_url(reply_msg):
    
    if not reply_msg:
        return False
    if '' == reply_msg:
        return False
    if 'https:' == reply_msg[0:6]:
        return True
    return False


@handler.add(PostbackEvent)
def handle_follow(event):
    print('msg = ', event.postback.data)


@handler.add(FollowEvent)
def handle_follow(event):

    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)
    name = profile.display_name

    create_line_user(name, '', user_id)

    reply_msg = name + '你啊，不要若無其事地向我搭話啦!畢竟又不是朋友，什麼都不是啊！'
    line_bot_api.reply_message(event.reply_token, TextMessage(text=reply_msg))
    print('新加入者: %s , user_id: %s' % (name, user_id))


@handler.add(UnfollowEvent)
def handle_follow(event):

    user_id = event.source.user_id
    print('使用者已刪除好友, user_id: %s' % (user_id))
    delete_line_user(user_id)


def get_group_summary(group_id):

    headers = {"content-type": "application/json; charset=UTF-8",'Authorization':'Bearer {}'.format(config.get('line-bot', 'channel_access_token'))}
    url = 'https://api.line.me/v2/bot/group/' + group_id + '/summary'
    response = requests.get(url, headers=headers)
    response = response.json()

    return response # Get groupId, groupName, pictureUrl


@handler.add(JoinEvent)
def handle_join(event):

    group_id = event.source.group_id
    response = get_group_summary(group_id)
    print('group_id = ', group_id)

    group_name = response['groupName']
    create_line_group(group_name, group_id)

    reply_msg = '真拿你們沒辦法 只有你們太不可靠了 我也加入' + group_name + '吧！要好好感謝我喔☆'
    line_bot_api.reply_message(event.reply_token, TextMessage(text = reply_msg))


@handler.add(MemberJoinedEvent)
def handle_join(event):

    # print(event.joined.members)
    user_id = event.joined.members[0].user_id
    group_id = event.source.group_id
    group_profile = line_bot_api.get_group_member_profile(group_id, user_id)
    name = group_profile.display_name

    reply_msg = name + "，你就是我新的身體嗎?"
    line_bot_api.reply_message(event.reply_token, TextMessage(text = reply_msg))


@handler.add(MemberLeftEvent)
def handle_join(event):

    group_id = event.source.group_id
    user_id_list = []
    for i in range(len(event.left.members)):
        user_id_list.append(event.left.members[i].user_id)
    for i in range(len(user_id_list)):
        delete_line_group_member(group_id, user_id_list[i])

    # print('group = ', event.source.group_id)
    # print('left member = ', event.left.members[0])
    # reply_msg = "我的身體怎麼不見了....?"
    # line_bot_api.push_message(group_id, TextSendMessage(text = reply_msg))
    # print("JoinEvent =", MemberLeftEvent)


@handler.add(LeaveEvent)
def handle_leave(event):

    group_id = event.source.group_id
    delete_line_group(group_id)
    print("leave Event =", event)
    print('群組踢除: ', event.source.group_id)


@handler.add(MessageEvent, message=LocationMessage)
def handle_message(event):

    address = event.message.address
    latitude = event.message.latitude
    longitude = event.message.longitude

    bank_info = get_bank_info(latitude, longitude)    
    data = {}
    with open('./reply_template/map_flex_message.json', newline='') as jsonfile:
        data = json.load(jsonfile)

    template = data.pop('contents')[0]
    data['contents'] = []
    for i in range(5):
        bank = copy.deepcopy(template)
        info = bank['body']['contents']
        index = bank_info[i][0].index('(')
        info[0]['text'] = bank_info[i][0][:index] # Name
        info[1]['text'] = bank_info[i][0][index:]
        info[2]['contents'][0]['text'] = '郵局地址: ' + bank_info[i][1] # Address
        info[2]['contents'][1]['text'] = '營業時間: ' + bank_info[i][2] # Time
        info[2]['contents'][2]['text'] = '剩餘數量: ' + bank_info[i][4] # Count

        index = bank_info[i][0].index('(')
        print(bank_info[i][0][:index])
        url = 'https://www.google.com/maps/dir/' + str(latitude) + ',+' + str(longitude) + '/' + str(bank_info[i][5]) + ',+' + str(bank_info[i][6])
        # url = 'https://www.google.com/maps/dir/' + str(latitude) + ',+' + str(longitude) + '/' + bank_info[i][0][:index]
        # print(url)
        bank['footer']['contents'][0]['action']['uri'] = url
        data['contents'].append(bank)

    send_msg = FlexSendMessage(alt_text = '振興三倍券', contents = data)
    line_bot_api.reply_message(event.reply_token, send_msg)

    # send_msg = TextSendMessage(text= reply_msg )
    # line_bot_api.reply_message(event.reply_token, send_msg)


@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):

    msg_source = event.source.type
    reply_msg = ''
    if msg_source == 'group':
        reply_msg = handle_group_image_message(event)
    elif msg_source == 'user':
        reply_msg = handle_user_image_message(event)

    if is_reply_img_url(reply_msg):
        send_msg = ImageSendMessage(original_content_url = reply_msg, preview_image_url = reply_msg)
        line_bot_api.reply_message(event.reply_token, send_msg)
    elif reply_msg != '':
        send_msg = TextSendMessage(text= reply_msg )
        line_bot_api.reply_message(event.reply_token, send_msg)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    reply_msg = ''
    msg_source = event.source.type
    user_id = event.source.user_id

    if msg_source == 'group':
        reply_msg = handle_group_text_message(event)
    elif msg_source == 'user':
        reply_msg = handle_user_text_message(event)
    else:
        reply_msg = handle_room_text_message(event)

    if is_reply_img_url(reply_msg):
        send_msg = ImageSendMessage(original_content_url = reply_msg, preview_image_url = reply_msg)
        line_bot_api.reply_message(event.reply_token, send_msg)
    elif reply_msg != '':
        send_msg = TextSendMessage(text= reply_msg )
        line_bot_api.reply_message(event.reply_token, send_msg)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port = port)
    # app.debug = True
    # app.run()