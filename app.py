# -*- coding: utf-8 -*

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)

from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, JoinEvent, LeaveEvent, MemberJoinedEvent, MemberLeftEvent, FollowEvent, UnfollowEvent, PostbackEvent,
    TextMessage, ImageMessage,
    TextSendMessage, ImageSendMessage, TemplateSendMessage,
    MessageAction, DatetimePickerAction, PostbackAction, URIAction, CameraAction, CameraRollAction, LocationAction,
    QuickReply, QuickReplyButton, 
    ButtonsTemplate,
)

import configparser
import os

from cloud_firestore import *
from text_message import *
from image_message import *
import requests
from imgur import *


app = Flask(__name__)

config = configparser.ConfigParser()
config.read('config.ini')
# config.read('test_config.ini')
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

    # print(body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(PostbackEvent)
def handle_follow(event):
    print('msg = ', event.postback.data)


@handler.add(FollowEvent)
def handle_follow(event):

    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)
    name = profile.display_name
    print('新加入者: %s , user_id: %s' % (name, user_id))
    create_line_user(name, user_id)
    reply_msg = name + '你啊，不要若無其事地向我搭話啦!畢竟又不是朋友，什麼都不是啊！'
    line_bot_api.reply_message(event.reply_token, TextMessage(text=reply_msg))


@handler.add(UnfollowEvent)
def handle_follow(event):

    user_id = event.source.user_id
    # profile = line_bot_api.get_profile(user_id)
    # name = profile.display_name
    print('使用者已刪除好友, user_id: %s' % (user_id))
    delete_line_user(user_id)


@handler.add(JoinEvent)
def handle_join(event):

    group_id = event.source.group_id
    headers = {"content-type": "application/json; charset=UTF-8",'Authorization':'Bearer {}'.format(config.get('line-bot', 'channel_access_token'))}
    url = 'https://api.line.me/v2/bot/group/' + group_id + '/summary'
    response = requests.get(url, headers=headers)
    response = response.json()
    # print('response = %s' %(response))

    group_name = response['groupName']
    create_line_group(group_name, group_id)

    reply_msg = '真拿你們沒辦法 只有你們太不可靠了 我也加入' + group_name + '吧！要好好感謝我喔☆'
    line_bot_api.reply_message(event.reply_token, TextMessage(text=reply_msg))


@handler.add(MemberJoinedEvent)
def handle_join(event):

    # print(event.joined.members)

    user_id = event.joined.members[0].user_id
    group_id = event.source.group_id
    group_profile = line_bot_api.get_group_member_profile(group_id, user_id)
    name = group_profile.display_name

    # update_line_group(name, user_id, group_id)

    reply_msg = name + "，你就是我新的身體嗎?"
    line_bot_api.reply_message(event.reply_token, TextMessage(text=reply_msg))
    print("JoinEvent =", MemberJoinedEvent)


@handler.add(MemberLeftEvent)
def handle_join(event):

    reply_msg = "我的身體怎麼不見了....?"
    line_bot_api.reply_message(event.reply_token, TextMessage(text=reply_msg))
    # print("JoinEvent =", MemberLeftEvent)


@handler.add(LeaveEvent)
def handle_leave(event):

    group_id = event.source.group_id
    delete_line_group(group_id)
    print("leave Event =", event)
    print('群組踢除: ', event.source.group_id)


@handler.add(MessageEvent, message=ImageMessage)
def handle_message(event):

    msg_source = event.source.type

    reply_msg = ''
    if msg_source == 'user':
        reply_msg = handle_user_image_message(event)
        if 'https:' in reply_msg:
            send_msg = ImageSendMessage(original_content_url=reply_msg, preview_image_url=reply_msg)
            line_bot_api.reply_message(event.reply_token, send_msg)
        else:
            send_msg = TextSendMessage(text= reply_msg )
            line_bot_api.reply_message(event.reply_token, send_msg)


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    # user_id = event.source.user_id
    # line_bot_api.link_rich_menu_to_user(user_id, 'richmenu-36d5000e0e2bd620a04a7ec9facfcf1d')

    reply_msg = ''

    msg_source = event.source.type

    if msg_source == 'group':
        reply_msg = handle_group_text_message(event)
    else:
        reply_msg = handle_user_text_message(event)
   
    if reply_msg != '':
        send_msg = TextSendMessage(text= reply_msg )
        line_bot_api.reply_message(event.reply_token, send_msg)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    # app.debug = True
    # app.run()