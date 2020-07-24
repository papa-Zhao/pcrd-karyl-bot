from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
)

import configparser
import enum
import random
import redis
import redis_lock
import sys
sys.path.append('./bin')
import time
from scrape_sonet import *
from scrape_cygame import *


from arena import *
from clan import *
from clan_sheet import *
from cloud_firestore import *
from imgur import *
from keyword_reply import *
from scrape_sonet import *
from subscribe import *

config = configparser.ConfigParser()
config.read('config.ini')
# Channel Access Token
line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
# Channel Secret
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

# r = redis.from_url(os.environ['REDIS_URL'], decode_responses=True)
r = redis.StrictRedis(decode_responses=True)


class StrEnum(str, enum.Enum):
     pass
class MsgType(StrEnum):
    Atk = '1'
    Def = '0'


def strQ2B(text):
    ss = []
    for s in text:
        string = ''
        for uchar in s:
            inside_code = ord(uchar)
            if inside_code == 12288:  # Transfer fullwidth space to halfwidth space
                inside_code = 32
            elif (inside_code >= 65281 and inside_code <= 65374):  # Transfer fullwidth string to halfwidth string except space
                inside_code -= 65248
            string += chr(inside_code)
        ss.append(string)
    return ''.join(ss)


def handle_user_arena_text_message(user_id, msg):

    key = user_id
    status = r.get(key + 'status')
    if status != 'True':
        reply_msg = ''
        return reply_msg

    our = r.lrange(key + "our", 0, -1)
    for i in range(len(our)):
        our[i] = int(our[i])
    enemy = r.lrange(key + "enemy", 0, -1)
    for i in range(len(enemy)):
        enemy[i] = int(enemy[i])

    win = r.get(key + 'win')
    if msg == '防守' or msg == MsgType.Def:

        if win == 'True':
            win = False
        else:
            win = True
        our, enemy = enemy, our

    elif msg == '進攻' or msg == MsgType.Atk:

        if win == 'True':
            win = True
        else:
            win = False

    reply_msg = 'atk:' + str(our)
    reply_msg += '\ndef:' + str(enemy)
    reply_msg += '\nwin:' + str(win)
    # print('reply_msg = ', reply_msg)

    if len(our) == 0 or len(enemy) == 0:
        reply_msg = '時效已到期'
    else:
        find_status = find_arena_record(our, enemy, win, user_id)
        if find_status == 'repeated':
            reply_msg = '上傳失敗，此對戰紀錄您已上傳過。'
        else:
            reply_msg = get_record_msg(our, enemy, win, find_status)
    
    
    return reply_msg


def get_user_text_msg_info(event):

    msg = event.message.text
    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)
    user_name = profile.display_name

    return msg, user_id, user_name 


character = {10000:'似似花',10001:'日和',10002:'茉莉',10003:'真步',10004:'香織',10005:'咲戀',10006:'千歌',10007:'步未',10008:'珠希(夏日)',10009:'尼諾(大江戶)',10010:'望(聖誕節)',
             10100:'怜',10101:'禊',10102:'茜里',10103:'璃乃',10104:'伊緒',10105:'望',10106:'真琴',10107:'流夏',10108:'美冬(夏日)',10109:'蕾姆',10110:'伊莉亞(聖誕節)',
             10200:'宮子',10201:'雪',10202:'杏奈',10203:'初音',10204:'美美',10205:'尼諾',10206:'伊莉亞',10207:'吉塔',10208:'忍(萬聖節)',10209:'拉姆',10210:'可可蘿(新年)',
             10300:'七七香',10301:'霞',10302:'美里',10303:'玲奈',10304:'胡桃',10305:'忍',10306:'空花',10307:'佩可',10308:'宮子(萬聖節)',10309:'艾蜜莉亞',10310:'凱留(新年)',
             10400:'依里',10401:'綾音',10402:'鈴苺',10403:'鈴',10404:'惠理子',10405:'秋乃',10406:'珠希',10407:'可可蘿',10408:'萬盛美咲',10409:'玲奈(夏日)',10410:'鈴苺(新年)',
             10500:'真陽',10501:'優花梨',10502:'鏡華',10503:'智',10504:'栞',10505:'碧',10506:'純',10507:'凱留',10508:'千歌(聖誕節)',10509:'伊緒(夏日)',10510:'霞(魔法少女)',
             10600:'美冬',10601:'靜流',10602:'美咲',10603:'深月',10604:'莉瑪',10605:'莫尼卡',10606:'紡希',10607:'矛依未',10608:'胡桃(聖誕節)',10609:'咲戀(夏日)',10610:'栞(魔法少女)',
             10700:'亞里莎',10701:'嘉夜',10702:'優依',10703:'克莉絲緹娜',10704:'佩可(夏日)',10705:'可可蘿(夏日)',10706:'鈴苺(夏日)',10707:'凱留(夏日)',10708:'綾音(聖誕節)',10709:'真琴(夏日)',10710:'卯月',
             10800:'日和(新年)',10801:'優依(新年)',10802:'怜(新年)',10803:'惠理子(情人節)',10804:'靜流(情人節)',10805:'安',10806:'露',10807:'古蕾婭',10808:'空花(大江戶)',10809:'香織(夏日)',10810:'凜',
             10900:'真步(夏日)',10901:'碧(插班生)',10902:'克羅伊',10903:'琪愛兒',10904:'優妮',10905:'鏡華(萬聖節)',10906:'禊(萬聖節)',10907:'美美(萬聖節)',10908:'露娜',10909:'克(聖誕節)',10910:'本田',
             11000:'鈴(巡者)',11001:'真陽(遊俠)',11002:'璃乃(奇幻)',11003:'步未(幻境)',11004:'佩可(公主型態)',11005:'可可蘿(公主型態)',11006:'祈梨',11007:'優依(公主型態)',11008:'杏奈(夏日)',
             30000:'優花梨(六星)',30001:'日和(六星)',30002:'璃乃(六星)',30003:'美冬(六星)',
             30100:'怜(六星)',30101:'真步(六星)',30102:'初音(六星)',30103:'莉瑪(六星)',
             30200:'伊緒(六星)',30201:'優依(六星)',30202:'珠希(六星)',30203:'佩可(六星)',
             30300:'可可蘿(六星)',30301:'凱留(六星)', 30302:'靜流(六星)'}

def user_find_str_processing(user_id, msg):

    reply_msg = '指令錯誤，請再輸入一次！'

    if msg == '台聞':
        reply_msg = scrape_pcrd_sonet()

    if msg == '日聞':
        reply_msg = scrape_pcrd_cygame()

    if '陣容: ' in msg:
        msg = msg.replace('陣容: ', '')
        reply_msg , enemy = nickname_search_arena_record(msg)
        if reply_msg == 'True':
            enemy = sort_character_loc(enemy)

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
            return reply_msg

    if '查詢方法' == msg:
        status = get_user_database(user_id)
        if status == True:
            method = '個人資料庫'
        else:
            method = '全體資料庫'
        reply_msg = '你目前作業查詢方法為: ' + method

    if '設定查詢:' in msg :
        msg = msg.replace('設定查詢:', '')
        print(msg)
        if msg == '個人':
            status = True
        elif msg == '全體':
            status = False
        else:
            reply_msg = '輸入格式錯誤，請重新輸入。'
            return reply_msg
        update_user_database(user_id, status)
        reply_msg = '已更改你的作業查詢方法為: ' + msg + '資料庫'

    return reply_msg


def handle_user_text_message(event):

    reply_msg = ''
    msg, user_id, user_name = get_user_text_msg_info(event)

    msg = strQ2B(msg)
    if msg == '進攻' or msg == MsgType.Atk or msg == '防守' or msg == MsgType.Def:
        reply_msg = handle_user_arena_text_message(user_id, msg)
        return reply_msg

    if '!' == msg[0]:
        msg = msg[1:]
        reply_msg = user_find_str_processing(user_id, msg)
    elif '#' in msg:
        if clan_period():
            info = get_user_info(user_id)
            try:
                karyl_group = ['C423cd7dee7263b3a2db0e06ae06d095e', 'C1f08f2cc641df24f803b133691e46e92']
                karyl_group.index(info['group_id'])
                msg = msg[1:]
                reply_msg = clan_user_str_processing(user_id, msg)
            except ValueError:
                reply_msg = '你不屬於凱留水球啵啵啵成員，無法使用此指令。'
        else:
            reply_msg = '非戰隊戰期間，不開放指令輸入。'
    elif '@' in msg:
        msg = msg[1:]
        reply_msg = subscribe_str_processing(msg, user_id)
        send_msg = TextSendMessage(text= reply_msg )
        line_bot_api.reply_message(event.reply_token, send_msg)
        reply_msg = ''
    else:
        handle_key_message(event) 

    return reply_msg


def handle_group_upload(group_id, user_id, msg):

    key = group_id + user_id
    redis_our = r.lrange(key + "our", 0, -1)
    redis_enemy = r.lrange(key + "enemy", 0, -1)
    win = r.get(key + 'win')

    our = [0] * len(redis_our)
    enemy = [0] * len(redis_enemy)
    if msg == '防守' or msg == MsgType.Def:

        for i in range(len(redis_our)):
            enemy[i] = int(redis_our[i])
        for i in range(len(redis_enemy)):
            our[i] = int(redis_enemy[i])

        if win == 'True':
            win = False
        else:
            win = True

    elif msg == '進攻' or msg == MsgType.Atk:

        for i in range(len(redis_our)):
            our[i] = int(redis_our[i])
        for i in range(len(redis_enemy)):
            enemy[i] = int(redis_enemy[i])

        if win == 'True':
            win = True
        else:
            win = False

    reply_msg = 'atk:' + str(our)
    reply_msg += '\ndef:' + str(enemy)
    reply_msg += '\nwin:' + str(win)
    # print('reply_msg = ', reply_msg)
    if our == [] or enemy == []:
        reply_msg = '時效已到期'
    else:
        find_status = find_group_arena_record(our, enemy, win, group_id)
        if find_status == 'success':
            reply_msg = get_group_record_msg(our, enemy, win, find_status)

    return reply_msg


def handle_group_3v3_upload(group_id, user_id, msg):
    
    key = group_id + user_id
    count = r.get(key + 'count')
    print('count=', count)
    
    for record in range(int(count)):
        print('record=', record)
        redis_our = r.lrange(key + 'our' + str(record), 0, -1)
        redis_enemy = r.lrange(key + 'enemy' + str(record), 0, -1)
        win = r.get(key + 'win' + str(record))
        print(redis_our)
        print(redis_enemy)
        print(win)
        
        our = [0] * len(redis_our)
        enemy = [0] * len(redis_enemy)
        if msg == '防守' or msg == MsgType.Def:

            for i in range(len(redis_our)):
                enemy[i] = int(redis_our[i])
            for i in range(len(redis_enemy)):
                our[i] = int(redis_enemy[i])

            if win == 'True':
                win = False
            else:
                win = True

        elif msg == '進攻' or msg == MsgType.Atk:

            for i in range(len(redis_our)):
                our[i] = int(redis_our[i])
            for i in range(len(redis_enemy)):
                enemy[i] = int(redis_enemy[i])

            if win == 'True':
                win = True
            else:
                win = False

        reply_msg = '\natk:' + str(our)
        reply_msg += '\ndef:' + str(enemy)
        reply_msg += '\nwin:' + str(win)
        print('reply_msg = ', reply_msg)
        if our == [] or enemy == []:
            reply_msg = '時效已到期'
        else:
            find_status = find_group_arena_record(our, enemy, win, group_id)
            if find_status == 'success':
                reply_msg = get_group_record_msg(our, enemy, win, find_status)


    return reply_msg
    


def handle_group_arena_text_message(group_id, user_id, msg):
    
    key = group_id + user_id
    status = r.get(key + 'status')
    if status != 'True':
        reply_msg = ''
        return reply_msg

    reply_msg = ''
    mode = r.get(key + 'mode')
    print('mode=',mode)
    if mode == 'Upload':
        reply_msg = handle_group_upload(group_id, user_id, msg)
    
    if mode == '3v3':
        reply_msg = handle_group_3v3_upload(group_id, user_id, msg)
    
    return reply_msg

def get_group_msg_info(event):

    msg = event.message.text
    group_id = event.source.group_id
    user_id = event.source.user_id
    group_profile = line_bot_api.get_group_member_profile(group_id, user_id)
    user_name = group_profile.display_name

    return msg, group_id, user_id, user_name 


def handle_group_text_search(group_id, msg):

    msg = msg.replace('陣容: ', '')
    reply_msg , enemy = nickname_search_arena_record(msg)
    if reply_msg == 'True':
        enemy = sort_character_loc(enemy)

        record, good, bad = search_group_arena_record(enemy, group_id)
        record, good, bad = sort_arena_record(record, good, bad)
        if len(record) > 0:
            reply_img = create_record_img(record, good, bad)
            url = test_nacx_image(reply_img)
            return url
        else:
            reply_msg = '此對戰紀錄不存在'
            return reply_msg
    else:
        return reply_msg


def handle_group_text_message(event):

    reply_msg = ''
    msg, group_id, user_id, user_name = get_group_msg_info(event)

    try:
        karyl_group = ['C423cd7dee7263b3a2db0e06ae06d095e', 'C1f08f2cc641df24f803b133691e46e92', 'C8c5635612e8d8b6856f805b7522a56f0', 'C6c42bc1911917f460609c6bfe5b2c6ff'
                    ,'Cdf1027c25ba50ddd3f71fef81ed5fb59']
        karyl_group.index(group_id)
    except ValueError:
        reply_msg = '此群組並非凱留水球啵啵啵群組，無法使用群組功能。'
        reply_msg += '\n若想使用群組功能請聯絡開發者 Email: rr06922013@gmail.com'
        return reply_msg

    msg = strQ2B(msg)

    if msg == '進攻' or msg == '1' or msg == '防守' or msg == '0':
        reply_msg = handle_group_arena_text_message(group_id, user_id, msg)
        return reply_msg

    if '!' == msg[0]:
        msg = msg[1:]
        if '陣容: ' in msg:
            reply_msg = handle_group_text_search(group_id, msg)
        else:
            try:
                karyl_group = ['C423cd7dee7263b3a2db0e06ae06d095e', 'C1f08f2cc641df24f803b133691e46e92']
                karyl_group.index(group_id)
            except ValueError:
                reply_msg = '此群組並非凱留水球啵啵啵群組，無法使用群組功能。'
                return reply_msg

            reply_msg = clan_group_find_str_processing(group_id, user_id, user_name, msg)

    elif '#' == msg[0]:
        try:
            karyl_group = ['C423cd7dee7263b3a2db0e06ae06d095e', 'C1f08f2cc641df24f803b133691e46e92']
            karyl_group.index(group_id)
        except ValueError:
            reply_msg = '此群組並非凱留水球啵啵啵群組，無法使用群組功能。'
            return reply_msg
        
        group_member = get_group_member(group_id)
        try:
            group_member[user_name]
            # redis_lock.reset_all(r)
            if clan_period():
                msg = msg[1:]
                reply_msg = clan_group_set_str_processing(group_id, user_id, user_name, msg)

            else:
                reply_msg = '非戰隊戰期間，不開放此功能'
        except KeyError:
            reply_msg = user_name + '，你非戰隊成員，請先加入戰隊戰。'
    else:
        try:
            karyl_group = ['C423cd7dee7263b3a2db0e06ae06d095e', 'C1f08f2cc641df24f803b133691e46e92', 'Cdf1027c25ba50ddd3f71fef81ed5fb59']
            karyl_group.index(group_id)
            handle_key_message(event) 
        except ValueError:
            print('')

    return reply_msg


def handle_room_text_message(event):
    
    handle_key_message(event)
    reply_msg = ''
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
