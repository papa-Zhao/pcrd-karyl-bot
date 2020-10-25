from linebot import (
    LineBotApi, WebhookHandler
)

from app import *
from clan_sheet import *
from cloud_firestore import *
from scrape_sonet import *
from scrape_cygame import *

from dateutil import tz
from dateutil.tz import tzlocal
from datetime import datetime, timedelta

import redis
import redis_lock
import sys
sys.path.append('./bin')
import time

r = redis.from_url(os.environ['REDIS_URL'], decode_responses=True)
# r = redis.StrictRedis(decode_responses=True)

number_list = ['一', '二', '三', '四', '五']
boss_list = ['一王', '二王', '三王', '四王', '五王']
boss_blood_list = [[600, 600, 700, 1500], [800, 800, 900, 1600], [1000, 1000, 1300, 1800], [1200, 1200, 1500, 1900], [1500, 1500, 2000, 2000]]
boss_cycle_list = [1, 4, 11, 35]


def clan_time_start():

    ISOTIMEFORMAT = "%Y-%m-%d %H:%M:%S"
    start = datetime.strptime("2020-10-25 21:00:00", ISOTIMEFORMAT)

    return start

def clan_time_end():

    ISOTIMEFORMAT = "%Y-%m-%d %H:%M:%S"
    end = datetime.strptime("2020-10-30 16:00:00", ISOTIMEFORMAT)

    return end

def get_clan_days():

    ISOTIMEFORMAT = "%Y-%m-%d %H:%M:%S"
    clan_start = clan_time_start()
    now = datetime.now().strftime(ISOTIMEFORMAT)
    now = datetime.strptime(now, ISOTIMEFORMAT)
    day = (now-clan_start).days + 1
    return day

def clan_period():
    
    return True
    ISOTIMEFORMAT = "%Y-%m-%d %H:%M:%S"
    
    clan_start = clan_time_start()
    clan_end = clan_time_end()
    now = datetime.now().strftime(ISOTIMEFORMAT)
    now = datetime.strptime(now, ISOTIMEFORMAT)

    if clan_end > now and now > clan_start:
        return True
    else:
        return False
    

def initial_atk_list(sh):
    
    reply_msg = '已將所有成員刀表重置'
    ws = sh.worksheet_by_title('刀表')

    for boss in boss_list:
        index = ws.find(boss, matchCase=True)
        index = index[0]
        length = len(ws.get_col(index.col+1))
        ws.update_col(index.col+1, values=['']*length, row_offset=1)
        
    return reply_msg

def initial_sign_up_list(sh):
    
    reply_msg = '已將報刀表格重置'

    ws = sh.worksheet_by_title('報刀')
    ws.update_value('B1', 1)
    ws.update_value('B2', '一王')
    ws.update_value('B3', '6000000')
    ws.update_value('E1', 90)
    ws.update_value('E2', 0)
    del_row = ws.rows-4
    if del_row > 0:
        ws.delete_rows(5, number=del_row)

    return reply_msg


def set_atk_list(sh, name, msg):

    ws = sh.worksheet_by_title('刀表')
    
    msg = msg.replace('回報刀表 ', '')
    msg = msg.split(' ')
    boss_dict = {'一王':2, '二王':4, '三王':6, '四王':8, '五王':10}
    
    name_index = ws.find(name, matchCase=True)
    if name_index:
        for i in range(len(name_index)):
            if name == name_index[i].value:
                name_index = name_index[i]
                break
        row = name_index.row
        ws.clear(start=(row, 2), end=(row, 11))
        reply_msg = name + ', 已更改你的刀表'
    else:
        index = ws.get_col(1).index('')
        row = index+1
        ws.update_value((row, 1), name)
        reply_msg = name + ', 你的刀表已經回報'

    for m in msg:
        if ':' in m:
            m = m.split(':')
        else:
            reply_msg = '指令錯誤，王與刀之間請輸入:'
            break
        col = boss_dict.get(m[0], -1)
        if col == -1:
            reply_msg = '指令錯誤，你並未輸入刀表，請重新嘗試'
            return reply_msg
        else:
            ws.update_value((row, col), m[1])
    
    return reply_msg


def set_atk_time(sh, name, msg):
    
    ws = sh.worksheet_by_title('出刀時間')
    msg = msg.replace('出刀時間 ', '')
    msg = msg.split(' ')
    time_dict = {'早上':2, '下午':3, '晚上':4}
    
    name_index = ws.find(name, matchCase=True)
    if name_index:
        for i in range(len(name_index)):
            if name == name_index[i].value:
                name_index = name_index[i]
                break
        row = name_index.row
        if '早上' in msg or '下午' in msg or '晚上' in msg:
            ws.clear(start=(row, 2), end=(row, 4))
        reply_msg = name + ', 已更新你出刀時間'
    else:
        index = ws.get_col(1).index('')
        row = index+1
        ws.update_value((row, 1), name)
        reply_msg = name + ', 你的出刀時間已經回報'

    for t in msg:
        col = time_dict.get(t, -1)
        if col == -1:
            reply_msg = '指令錯誤，你並未輸入時段，請重新嘗試'
            break
        else:
            ws.update_value((row, col), True)

    return reply_msg


def clan_user_str_processing(user_id, msg):
    
    reply_msg = '指令錯誤，請再輸入一次！'

    sh = initial_worksheet()
    profile = line_bot_api.get_profile(user_id)
    name = profile.display_name

    if '回報刀表' in msg:
        reply_msg = set_atk_list(sh, name, msg)

    # if '出刀時間' in msg:
    #     reply_msg = set_atk_time(sh, name, msg)

    return reply_msg


def get_clan_atk_times(sh, status):

    ws = sh.worksheet_by_title('出刀次數')
    ISOTIMEFORMAT = "%Y-%m-%d %H:%M:%S"
    clan_start = clan_time_start()
    now = datetime.now().strftime(ISOTIMEFORMAT)
    now = datetime.strptime(now, ISOTIMEFORMAT)
    day = (now-clan_start).days + 1

    name = ws.get_col(1)

    reply_msg = ''
    if status == '完整刀':
        info = ws.get_col(day+1)
        reply_msg = '完整刀狀態(剩下幾刀):'
    else:
        col = ws.find('補償刀', matchCase=True)[0].col
        info = ws.get_col(col)
        reply_msg = '補償刀狀態:'
        
    for i in range(1, len(name)-1):
        if int(info[i]) < 3:
            if status == '完整刀':
                reply_msg += '\n' + name[i] + ': ' + str((3 - int(info[i])))
            if status == '補償刀' and int(info[i]):
                reply_msg += '\n' + name[i]

    # print(reply_msg)
    return reply_msg


def get_clan_boss_sign_up(sh, boss):

    ws = sh.worksheet_by_title('報刀')
    rows = ws.rows
    name_list = []

    for row in range(5, rows + 1):
        user_info = ws.get_row(row)
        if user_info[3] == boss:
            name_list.append([user_info[0], user_info[5]])
    
    if len(name_list) == 0:
        reply_msg = '目前無人報名' + boss
    else:
        reply_msg = '目前報名' + boss + '的成員為:'
        for name, atk in name_list:
            reply_msg += '\n' + name + ': ' + atk

    return reply_msg


def myAlign(string, length=0):
	if length == 0:
		return string
	slen = len(string)
	re = string
	if isinstance(string, str):
		placeholder = ' '
	else:
		placeholder = u'　'
	while slen < length:
		re += placeholder
		slen += 1
	return re


def clan_group_find_str_processing(group_id, user_id, user_name, msg):
    # print('clan_group_find_str_processing')

    ############ Other Group function ############

    find = False
    
    # if '開啟戰隊戰功能' in msg:
    
    ############ Our Group function ############
    reply_msg = '指令錯誤，請再輸入一次！'

    sh = initial_worksheet()
    ws = sh.worksheet_by_title('報刀')

    if msg == '台聞':
        reply_msg = scrape_pcrd_sonet()

    if msg == '日聞':
        reply_msg = scrape_pcrd_cygame()

    if msg == '報名查詢            ': ###### Depreciated ######
        try:
            tplt = '{0:{5}^6}\t{1:^6}\t{2:{5}^6}\t{3:{5}^6}\t{4:{5}^6}'
            reply_msg = tplt.format("報名者", "周目", "boss", '傷害', '刀種', chr(12288))

            ws = sh.worksheet_by_title('報刀')
            rows = ws.rows
            for row in range(5, rows + 1):
                user_info = ws.get_row(row)
                # print(user_info)
                reply_msg += '\n'
                reply_msg += tplt.format(user_info[0], user_info[2], user_info[3], user_info[4], user_info[5], chr(12288))
        except IndexError:
            reply_msg = '目前沒有報名紀錄。'

    if msg == '我的報名':
        try:
            ws = sh.worksheet_by_title('報刀')
            index = ws.find(user_name, matchCase=True)[0].row
            user_info = ws.get_row(index)
            # print(user_info)
            reply_msg = user_name + '，你的報名紀錄:'
            reply_msg += '\n報名時間: ' + str(user_info[1]) 
            reply_msg += '\n報名周目: ' + str(user_info[2]) 
            reply_msg += '\n報名boss: ' + user_info[3]
            reply_msg += '\n報名刀種: ' + user_info[5]
        except IndexError:
            reply_msg = user_name + '，你目前沒有報名紀錄。'

    if msg == '戰隊戰加入':
        reply_msg = update_line_group(group_id, user_id, user_name)

    if msg == '戰隊成員':
        group_member = get_group_member(group_id)
        num = len(group_member.keys())
        reply_msg = '目前戰隊成員有' + str(num) + '位'
        reply_msg += '\n名單: '
        for name in group_member.keys():
            reply_msg += name + ', '
            # print(name)

    if msg == '指令':
        reply_msg = '指令查詢網址:https://docs.google.com/document/d/1Ba6H2ppgacKxicyB7y9xEaYRktuAuIPyI0mbW5wutsA/edit#'

    if msg == 'URL' or msg == 'url':
        url = sh.url
        reply_msg = '戰隊表格網址: ' + url

    if msg == '周目':
        cycle = ws.get_value('B1')
        reply_msg = '當前周目為: ' + str(cycle)

    if msg == 'boss' or msg == 'BOSS':
        boss = ws.get_value('B2')
        boss_blood = ws.get_value('B3')
        reply_msg = '當前boss為: ' + boss
        reply_msg += '\nboss血量: ' + boss_blood

    if msg == '完整刀':
        reply_msg = get_clan_atk_times(sh, '完整刀')

    if msg == '補償刀':
        reply_msg = get_clan_atk_times(sh, '補償刀')

    if msg == '剩刀':
        remainder = ws.get_value('E1')
        remainder_compensate = ws.get_value('E2')
        reply_msg = '剩餘刀數: ' + remainder
        reply_msg += '\n剩餘補償刀: ' + remainder_compensate

    if msg == '戰隊戰':
        cycle = ws.get_value('B1')
        boss = ws.get_value('B2')
        boss_blood = ws.get_value('B3')
        remainder = ws.get_value('E1')
        remainder_compensate = ws.get_value('E2')
        reply_msg = '當前周目: ' + cycle
        reply_msg += '\n當前boss: ' + boss
        reply_msg += '\nboss血量: ' + boss_blood 
        reply_msg += '\n剩餘刀數: ' + remainder
        reply_msg += '\n剩餘補償刀: ' + remainder_compensate

    if msg == '查樹':
        tree = ws.find('掛樹',  matchCase=True)
        find = False
        people = []
        for i in tree:
            find = True
            people.append(ws.get_value((i.row, 1)))
        if find == True:
            reply_msg = '目前掛樹人員為:'
            for i in people:
                reply_msg += '\n' + i
        else:
            reply_msg = '目前無人掛樹'
        # print(reply_msg)

    if '查' in msg:
        msg = msg.replace('查', '')
        try:
            if msg in number_list:
                boss_idx = number_list.index(msg)
                msg = boss_list[boss_idx]
            boss_list.index(msg)
            reply_msg = get_clan_boss_sign_up(sh, msg)
        except ValueError:
            reply_msg = user_name + '，輸入boss錯誤，查詢失敗！'

    """
    if '查刀' in msg:
        msg = msg.replace('查刀 ', '')
        try:
            boss_list.index(msg)
            ws = sh.worksheet_by_title('刀表')
            index_boss = ws.find(msg, matchCase=True)[0].col
            
            name_list = []
            
            name_index = ws.get_col(1)
            atk= ws.get_col(index_boss)
            status = ws.get_col(index_boss+1)
            # print(atk)
            for i in range(1, ws.rows):
                if atk[i] != '' and status[i] == '':
                    name_list.append(name_index[i])
            
            name_list = '%s，'*len(name_list) % tuple(name_list)  
            reply_msg = '目前還有' + msg + '刀的成員為:\n' + name_list
        except ValueError:
            reply_msg = user_name + '，輸入boss錯誤，查詢失敗！'
    """

    return reply_msg 

def search_user_permission(user):

    admin = ['Uc2d23ed107e40a72c3416ff90e4a9bd7', 'U28de6cdccf72c0078b78de1400a2ca2c',
                'U13fc4e6b8fa1ddbba5dd2acdc5489e32', 'U6baf0b50d8eb1d67f43be074d959d282', 
             'U782b1f50739f0de272b0ee23eb10ffde',
             'U03c9c9314f7e87c3976ea999b988b98d', 'U91103dadf5e53122210dc0fe407cce7c',]

    try:
        admin.index(user)
        return True
    except ValueError:
        return False


def clan_group_set_str_processing(group_id, user_id, user_name, msg):
    # print('clan_group_set_str_processing')
    reply_msg = '指令錯誤，請再輸入一次！'

    sh = initial_worksheet()
    
    """
    permission = search_user_permission(user_id)
    admin_instruction = ['發送訊息:', '刪刀', '代刀', '代報名', '代取消', '設定周目', '設定boss', '設定BOSS', '設定完整刀', '設定補償刀', '出刀刀表重置', '報名刀表重置']
    if permission == False:
        for i in range(len(admin_instruction)):
            if admin_instruction[i] in msg:
                reply_msg = user_name + '，你權限不符，無法使用此指令。'
                return reply_msg
    """

    if '發送訊息:' in msg:   ###### Depreciated ######
        msg = msg.replace('發送訊息:', '')
        # multicast_group_to_user_info(group_id, msg)
        reply_msg = ''
        return reply_msg

    if '刪刀' in msg:
        try:
            msg = msg.replace('刪刀 ','')
            no_id = int(msg)
            name, cycle, boss, damage, complete, kill = get_clan_record_info(sh, no_id)
            reply_msg = delete_clan_record(sh, no_id, name, cycle, boss, damage, complete, kill)
        except ValueError:
            reply_msg = '刪刀格式錯誤，請重新輸入。'
            return reply_msg

    if '代刀' in msg:
        try:
            msg = msg.replace('代刀 ','')
            user_name = msg[1:msg.index('王出刀')-2]
            msg = msg.replace('@' + user_name + ' ', '')
        except ValueError:
            reply_msg = '代刀格式錯誤，請重新輸入。'
            return reply_msg

    if '代報名' in msg:
        try:
            msg = msg.replace('代報名 ','')
            user_name = msg[1:msg.index('報名')-1]
            msg = msg.replace('@' + user_name + ' ', '')
        except ValueError:
            reply_msg = '代報名格式錯誤，請重新輸入。'
            return reply_msg

    if '代取消' in msg:
        try:
            msg = msg.replace('代取消 ','')
            user_name = msg[1:msg.index('取消')-1]
            msg = msg.replace('@' + user_name + ' ', '')
        except ValueError:
            reply_msg = '代取消格式錯誤，請重新輸入。'
            return reply_msg

    if '設定周目' in msg:
        ws = sh.worksheet_by_title('報刀')
        find = False
        cycle = ws.cell('B1')
        msg = msg.split(' ')
        for num in msg:
            if num.isdigit():
                find = True
                cycle.value = int(num)
                break
        
        if find == True:
            reply_msg = '已更改周目: ' + str(cycle.value)
        else:
            reply_msg = '設定失敗，周目請輸入整數!'

    if '設定boss' in msg or '設定BOSS' in msg:
        ws = sh.worksheet_by_title('報刀')
        msg = msg.split(' ')

        if len(msg) == 3:
            ws.update_value('B2', msg[1])
            ws.update_value('B3', msg[2])
            reply_msg = '已更改boss狀態'


    if '設定完整刀' in msg:
        ws = sh.worksheet_by_title('報刀')
        find = False
        remainder = ws.cell('E1')
        msg = msg.split(' ')
        for i in msg:
            if i.isdigit():
                find = True
                remainder.value = int(i)

        if find == True:
            reply_msg = '已更改完整刀數量: ' + str(remainder.value)
        else:
            reply_msg = '設定失敗，數量請輸入整數!'

    if '設定補償刀' in msg:
        ws = sh.worksheet_by_title('報刀')
        find = False
        remainder = ws.cell('E2')
        msg = msg.split(' ')
        for i in msg:
            if i.isdigit():
                find = True
                remainder.value = int(i)

        if find == True:
            reply_msg = '已更改補償刀數量: ' + str(remainder.value)
        else:
            reply_msg = '設定失敗，數量請輸入整數!'
    
    if '出刀刀表重置' == msg:
        reply_msg = initial_atk_list(sh)
        #print('出刀刀表重置')
    elif '出刀' in msg:
        try:
            msg = msg.replace('出刀', '')
            msg = msg.split(' ')
            boss = msg[0]
            damage = msg[1]
            if not damage.isdigit():
                reply_msg = '傷害請輸入數字'
                return reply_msg
            msg = '出刀'
            reply_msg = update_clan_sign_up(sh, group_id, msg, user_name, boss=boss, damage=damage, status = '出刀')
        except IndexError:
            reply_msg = '出刀格式錯誤，請再輸入一次！'

    if '掛樹' == msg:
        reply_msg = update_clan_sign_up(sh, group_id, msg, user_name, status = '掛樹')

    if '取消報名' in msg:
        msg = '取消'
        reply_msg = update_clan_sign_up(sh, group_id, msg, user_name)

    if '報名刀表重置' == msg:
        reply_msg = initial_sign_up_list(sh)
        #print('報名刀表重置')
    elif '報名' in msg:
        msg, cycle, boss, complete, damage = get_clan_sign_up_info(sh, msg)
        if msg == '':
            reply_msg = user_name + '，指令格式錯誤，報名失敗。'
            return reply_msg
        confirm = confirm_atk_info(sh, user_name, complete)

        if msg == '報名' and confirm == '成功':
            reply_msg = update_clan_sign_up(sh, group_id, msg, user_name, cycle, boss, complete, damage, '等待')
        elif msg != '報名':
            reply_msg = user_name + msg
        else:
            reply_msg = user_name + confirm
        # if len(msg.split(' ')) != 3:
        #     reply_msg = '報名失敗，資料填寫不完全'

    return reply_msg

def multicast_group_to_user_info(group_id, msg):

    user_id_tree = []
    group_member = get_group_member(group_id)
    for i in group_member.values():
        user_id_tree.append(i)

    line_bot_api.multicast(user_id_tree, TextSendMessage(text= msg))

def multicast_user_id(sh, group_id, name_list, boss, status):

    user_id_tree = []
    group_member = get_group_member(group_id)
    for index in range(len(name_list)):
        name = name_list[index]
        try:
            user_id_tree.append(group_member[name])
        except KeyError:
            print('not found')

    print('multicast_user_id = ', user_id_tree)
    sys.stdout.flush()
    if len(user_id_tree) > 0 :
        if status == '下樹':
            line_bot_api.multicast(user_id_tree, TextSendMessage(text= boss + '倒了，可以下樹摟!'))
        elif status == '呼叫':
            line_bot_api.multicast(user_id_tree, TextSendMessage(text= '目前' + boss + '卡住了，你有時間幫忙出刀嗎!?'))
        elif status == '王倒下':
            line_bot_api.multicast(user_id_tree, TextSendMessage(text= '目前到' + boss + '了，請準備出刀！'))
        

def call_next_boss_attacker(sh, group_id, cycle, boss):

    ws = sh.worksheet_by_title('報刀')

    row = ws.rows
    name_tree = []

    for i in reversed(range(5, row+1)):
        info = ws.get_row(i)
        if cycle == info[2] and boss == info[3]:
            name_tree.append(info[0])

    print('call_next_boss_attacker = ', name_tree)
    sys.stdout.flush()
    if len(name_tree) > 0:
        multicast_user_id(sh, group_id, name_tree, boss, '王倒下')


def update_tree_status(sh, group_id, cycle, boss, status):

    ws = sh.worksheet_by_title('報刀')

    row = ws.rows
    name_tree = []

    for i in reversed(range(5, row+1)):
        # print('row = ', i)
        info = ws.get_row(i)
        if cycle == info[2] and boss == info[3]:
            ws.delete_rows(i)
            if '掛樹' == info[6]:
                name_tree.append(info[0])

    # print("掛樹成員: ", name_tree)
    # if len(name_tree) > 0:
    #     multicast_user_id(sh, group_id, name_tree, boss, '下樹')
    


def update_boss_status(sh, cycle, boss, complete):

    ws = sh.worksheet_by_title('報刀')

    ########## Updated Cycle ##########
    if boss == '五王':
        cycle = int(cycle)+1
        ws.update_value('B1', int(cycle))

    ########## Updated Boss ##########
    boss_index = (boss_list.index(boss) + 1) %len(boss_list)

    ws.update_value('B2', boss_list[boss_index])

    # print(boss_list[boss_index])

    ########## Updated Boss Blood ##########

    stages_index = 0

    for i in range(len(boss_cycle_list)):
        if int(cycle) >= boss_cycle_list[i]:
            stages_index = i

    ws.update_value('B3', boss_blood_list[boss_index][stages_index] * 1e4)


    ########## Updated ATK Remainder ##########

    if '完整' in complete:
        val = ws.get_value('E2')
        ws.update_value('E2', int(val)+1)


def confirm_atk_info(sh, name, complete):

    reply_msg = '成功'

    ws = sh.worksheet_by_title('出刀次數')
    name_index = ws.find(name, matchCase=True)

    if name_index:
        for i in range(len(name_index)):
            if name == name_index[i].value:
                name_index = name_index[i]
                break
        row = name_index.row
    else:
        index = ws.get_col(1).index('')
        row = index+1
        ws.update_value((row, 1), name)

    col = ws.find('補償刀', matchCase=True)[0].col
    remain_val = ws.get_value((row, col))

    if int(remain_val) > 0 and '完整' in complete:
        reply_msg = '，你還有補償刀未出，報名失敗！'
        return reply_msg

    if int(remain_val) == 0 and '補償' in complete:
        reply_msg = '，你並未有補償刀，報名失敗！'
        return reply_msg

    ISOTIMEFORMAT = "%Y-%m-%d %H:%M:%S"
    clan_start = clan_time_start()
    now = datetime.now().strftime(ISOTIMEFORMAT)
    now = datetime.strptime(now, ISOTIMEFORMAT)
    day = (now-clan_start).days + 1
    val = ws.get_value((row, day+1))

    if int(val) > 2 and int(remain_val) == 0:
        reply_msg = '，你今日已經出完三刀，報名失敗！'
        return reply_msg

    return reply_msg

def get_clan_sign_up_info(sh, text):

    msg = ''
    cycle = ''
    boss = ''
    complete = ''
    damage = ''

    ws = sh.worksheet_by_title('報刀')
    msg = '報名'
    
    if '下輪' in text:
        text = text.replace('報名下輪', '')
        cycle = int(ws.get_value((1, 2)))+1
    else:
        text = text.replace('報名', '')
        cycle = int(ws.get_value((1, 2)))

    text = text.split(' ')

    if len(text) < 2:
        msg = ''
        return msg, cycle, boss, complete, damage
    
    try:
        if text[0] in boss_list:
            boss = text[0]
        else:
            msg = '報名失敗，boss格式錯誤，請輸入欲報名哪王！'

        now_boss = ws.get_value((2, 2))
        if boss_list.index(boss) < boss_list.index(now_boss):
            cycle += 1
    except ValueError:
        msg = '報名失敗，boss格式錯誤，請輸入欲報名哪王！'


    if '補償' in text[1]:
        complete = text[1]
    else:
        complete = text[1] + '完整刀'

    if len(text) > 2:
        damage = text[2]
            
    return msg, cycle, boss, complete, damage
    
def get_clan_record_info(sh, no_id):

    ws = sh.worksheet_by_title('出刀傷害表')
    info = ws.get_row(no_id)
    name, cycle, boss, damage, complete, kill = info[1], info[2], info[3], info[4], info[5], info[6]
    print(name, cycle, boss, damage, complete, kill)
    return name, cycle, boss, damage, complete, kill

def delete_clan_record(sh, no_id, name, cycle, boss, damage, complete, kill):

    reply_msg = '刪刀失敗，請再輸入一次！'

    ################  報刀表格  ################

    ws = sh.worksheet_by_title('報刀')
    ws.update_value('B1', int(cycle))
    ws.update_value('B2', boss)

    if complete == 'TRUE':
        val = ws.get_value('E1')
        ws.update_value('E1', int(val) + 1)
    else:
        val = ws.get_value('E2')
        ws.update_value('E2', int(val) + 1)
    
    if kill == 'TRUE':
        ws.update_value('B3', damage)
        index = None
        if complete == 'TRUE':
            val = ws.get_value('E2')
            ws.update_value('E2', int(val) - 1)
    else:
        boss_blood = ws.get_value('B3')
        ws.update_value('B3', int(boss_blood) + int(damage))
    

    ################  出刀次數表格  ################

    ws = sh.worksheet_by_title('出刀次數')
    name_index = ws.find(name, matchCase=True)
    for i in range(len(name_index)):
        if name == name_index[i].value:
            name_index = name_index[i]
            break

    if name_index:
        row = name_index.row
        if complete == 'TRUE':
            day_index = get_clan_days() + 1
        else:
            day_index = ws.find('補償刀', matchCase=True)[0].col
        print('出刀次數表格 day_index=', day_index)
        val = ws.get_value((row, day_index))
        ws.update_value((row, day_index), int(val) + 1)

    if kill == 'TRUE':
        day_index = ws.find('補償刀', matchCase=True)[0].col
        val = ws.get_value((row, day_index))
        ws.update_value((row, day_index), int(val) + 1)

    ################  刀表表格  ################

    if complete == 'TRUE':
        ws = sh.worksheet_by_title('刀表')
        name_index = ws.find(name, matchCase=True)
        for i in range(len(name_index)):
            if name == name_index[i].value:
                name_index = name_index[i]
                break

        if name_index:
            row = name_index.row 
            boss_index = ws.find(boss, matchCase=True)
            boss_index = boss_index[0]
            col = boss_index.col
            ws.update_value((row, col+1), '')


    ################  出刀傷害表格  ################
        
    ws = sh.worksheet_by_title('出刀傷害表')
    ws.delete_rows(no_id)

    ################  回報訊息格式  ################

    reply_msg = '出刀者:' + name
    reply_msg += '\n周目:' + cycle
    reply_msg += '\nboss:' + boss
    reply_msg += '\ndamage:' + damage
    reply_msg += '\n完整刀:' + complete
    reply_msg += '\n已為你刪除此刀。'

    return reply_msg

def update_clan_sign_up(sh, group_id, msg, name, cycle=0, boss='', complete='', damage='', status=''):

    find = False
    ws = sh.worksheet_by_title('報刀')
    cell_id = ws.find(name, matchCase=True)
    for i in range(len(cell_id)):
        if name == cell_id[i].value:
            find = True
            cell_id = cell_id[i]
            break

    reply_msg = '更新失敗，請再輸入一次！'

    if msg == '報名':

        reply_msg = '報名失敗，請再輸入一次！'
        if find == True:
            val = ws.get_value((cell_id.row, 4))
            
            if val == boss:
                reply_msg = '報名失敗，你重複報名' + boss
            else:
                reply_msg = '報名失敗，你已經報名過' + val
        else:
            reply_msg = name + '，你已經成功報名!\n' 
            reply_msg += '報名周目: ' + str(cycle) + '周\n' 
            reply_msg += '報名boss: ' + boss + '\n'
            reply_msg += '出刀類型: ' + complete + '\n'
            reply_msg += '預估傷害: ' + damage

            ws.add_rows(1)
            row = ws.rows
            # print('row=', row)
            ISOTIMEFORMAT = "%H:%M"
            now = (datetime.now() + timedelta(hours=8))
            now = now.strftime(ISOTIMEFORMAT)
            # now = datetime.now().strftime(ISOTIMEFORMAT) + timedelta(hours=8)
            # print(name, now, cycle, boss, damage, complete, '等待')
            sign_up = [name, now, cycle, boss, damage, complete, '等待']
            ws.update_row(row, values = sign_up)

            # ws.update_values((row, 1), values=[sign_up], )
    
    elif msg == '取消':
        reply_msg = '取消報名失敗，請再輸入一次！'
        if cell_id:
            ws.delete_rows(cell_id.row, number=1)
            # ws.add_rows(1)
            reply_msg = name + '，已為你取消報名'
        else:
            reply_msg = '取消報名失敗，' + name + '你並未報名過。'

    elif msg == '掛樹':
        reply_msg = '更新狀態失敗，請再輸入一次！'
        if cell_id:
            row = cell_id.row
            info = ws.get_row(row)
            cycle = ws.get_value('B1')
            boss = ws.get_value('B2')
            if cycle != info[2]:
                reply_msg = name + '，更新狀態失敗，報名周目錯誤!'
            elif boss != info[3]:
                reply_msg = name + '，更新狀態失敗，報名boss錯誤!'
            elif status == info[6]:
                reply_msg = name + '，更新狀態失敗，你的狀態已經是掛樹!'
            else:
                ws.update_value((cell_id.row, 7), status)
                reply_msg = '回報成功！\n'
                reply_msg += name + '你的狀態已更新為: ' + status
        else:
            reply_msg = name + '，你並未報名過。' 


    elif msg == '出刀':

        reply_msg = '出刀更新狀態失敗，請再輸入一次！'

        ################  報刀表格  ################

        ws = sh.worksheet_by_title('報刀')
        name_index = ws.find(name, matchCase=True)
        for i in range(len(name_index)):
            if name == name_index[i].value:
                name_index = name_index[i]
                break

        if name_index:
            row = name_index.row
            info = ws.get_row(row)
            cycle = info[2]
            complete = info[5]
        else:
            reply_msg = name + '你並未報名，請你報名後再出刀。\n'
            return reply_msg

        if boss not in info[3]:
                reply_msg ='出刀失敗!'
                reply_msg += '\n出刀boss: ' + boss
                reply_msg += '\n報名boss: ' + info[3]
                return reply_msg
        
        now_boss = ws.get_value('B2')
        if boss not in now_boss:
                reply_msg ='出刀失敗!'
                reply_msg += '\n出刀boss: ' + boss
                reply_msg += '\n目前boss: ' + now_boss
                return reply_msg

        if '完整' in complete:
            index = 'E1'
            # print('完整刀')
        else:
            index = 'E2'
            # print('補償刀')
        val = ws.get_value(index)
        ws.update_value(index, int(val)-1)

        boss_blood = ws.get_value('B3')

        if int(boss_blood) > int(damage):
            boss_blood = int(boss_blood) - int(damage)
            ws.update_value('B3', boss_blood)
            ws.delete_rows(name_index.row)
        else:
            damage = boss_blood
            boss_blood = int(boss_blood) - int(damage)
            update_boss_status(sh, cycle, boss, complete)
            update_tree_status(sh, group_id, cycle, boss, status)

        # next_cycle = cycle
        # boss_index = boss_list.index(boss)
        # if boss_index == 4:
        #     next_cycle = str(int(cycle)+1)
        # boss_index = (boss_index+1) % 5
        # next_boss = boss_list[boss_index]
        # call_next_boss_attacker(sh, group_id, next_cycle, next_boss)



        ################  出刀次數表格  ################

        ws = sh.worksheet_by_title('出刀次數')
        name_index = ws.find(name, matchCase=True)
        for i in range(len(name_index)):
            if name == name_index[i].value:
                name_index = name_index[i]
                break
  
        if name_index:
            row = name_index.row
        else:
            index = ws.get_col(1).index('')
            row = index+1
            ws.update_value((row, 1), name)

        # print(row)

        if '完整' in complete:
            ISOTIMEFORMAT = "%Y-%m-%d %H:%M:%S"
            clan_start = clan_time_start()
            now = datetime.now().strftime(ISOTIMEFORMAT)
            now = datetime.strptime(now, ISOTIMEFORMAT)
            day = (now-clan_start).days + 1
            val = ws.get_value((row, day+1))
            ws.update_value((row, day+1), int(val)+1)
            
            # print('damage = %d ,boss_blood = %d' %(int(damage), int(boss_blood)))
            if int(boss_blood) == 0:
                day_index = ws.find('補償刀', matchCase=True)[0].col
                # print('day_index= ', day_index)
                val = ws.get_value((row, day_index))
                ws.update_value((row, day_index), int(val)+1)
                
        else:
            day_index = ws.find('補償刀', matchCase=True)[0].col
            val = ws.get_value((row, day_index))
            ws.update_value((row, day_index), int(val)-1)

        # print('day= ', day)
            
        ################  刀表表格  ################

        if '完整' in complete:
            ws = sh.worksheet_by_title('刀表')
            name_index = ws.find(name, matchCase=True)
            for i in range(len(name_index)):
                if name == name_index[i].value:
                    name_index = name_index[i]
                    break

            if name_index:
                row = name_index.row
            else:
                index = ws.get_col(1).index('')
                row = index+1
                ws.update_value((row, 1), name)
                
            boss_index = ws.find(boss, matchCase=True)
            boss_index = boss_index[0]
            col = boss_index.col

            ws.update_value((row, col+1), True)

        ################  出刀傷害表格  ################
        
        ws = sh.worksheet_by_title('出刀傷害表')
        ws.add_rows(1)
        row = ws.rows
        no_id = ws.rows

        # sign_up = [name, cycle, boss, complete, damage]
        if '完整刀' in complete:
            complete = True
        else:
            complete = False
        
        if int(boss_blood) == 0:
            kill = True
        else:
            kill = False

        sign_up = [row, name, cycle, boss, damage, complete, kill]
        ws.update_row(row, values = sign_up)

        ################  回報訊息格式  ################

        reply_msg = name + '，你的出刀回報成功！\n'
        reply_msg += '出刀編號: ' + str(no_id) + '\n'
        if boss_blood > 0:
            reply_msg += boss + '剩餘血量為: ' + str(boss_blood)
        else:
            reply_msg += name + '已經擊殺了' + boss + '\n'
            boss_index = (boss_list.index(boss) + 1) %len(boss_list)
            if boss == '五王':
                cycle = str(int(cycle)+1)
            reply_msg += '目前目標為' + cycle + '周，' + boss_list[boss_index]

    return reply_msg