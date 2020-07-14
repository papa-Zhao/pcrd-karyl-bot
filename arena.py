import cv2
import enum
import numpy as np
import sys

from collections import Counter

# Character Image
# redive.estertion.win
# Sources: https://pcrdfans.com/static/sprites/charas.png?t=20200630
# Sources: https://pcrdfans.com/static/sprites/charas_a.png?t=20200630
# Sources: https://pcrdfans.com/static/sprites/charas6x.png?t=20200630

# Sources: https://github.com/peterli110/pcrdfans.com/tree/master/static/sprites
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
             30100:'怜(六星)',30101:'真布(六星)',30102:'初音(六星)',30103:'莉瑪(六星)',
             30200:'伊緒(六星)',30201:'優依(六星)',30202:'珠希(六星)',30203:'佩可(六星)',
             30300:'可可蘿(六星)',30301:'凱留(六星)', 30302:'靜流(六星)'}

character_loc = [10604, 30103, 10200, 10306, 10506, 10808, 10004, 10802, 10810, 10307, 
                 30203, 11004, 10107, 10210, 10105, 10607, 10106, 10701, 10800, 10009, 
                 10405, 10709, 10002, 10902, 10803, 10708, 10606, 11006, 10001, 30001, 
                 10101, 10401, 10906, 10406, 30202, 10503, 10903, 10008, 10404, 10704, 
                 10304, 10207, 10100, 30100, 10110, 11008, 10909, 10601, 30302, 10703, 10608, 
                 10204, 10305, 10907, 10710, 10804, 11001, 10500, 10501, 30000, 10605, 
                 10205, 10010, 10600, 30003, 11000, 10206, 10809, 10005, 10202, 10208, 
                 10108, 10407, 30300, 11003, 10007, 10807, 10705, 10109, 10209, 10403, 
                 11005, 10603, 10102, 10400, 10609, 10308, 10700, 10805, 10806, 10000, 
                 10901, 10310, 10910, 10103, 30002, 10303, 10409, 10504, 10610, 10104, 
                 30200, 10509, 10402, 10410, 10309, 10301, 10510, 11002, 10302, 10300, 
                 10801, 10507, 30301, 10203, 30102, 10602, 10908, 11007, 10508, 10706, 
                 10707, 10505, 10006, 10900, 10003, 30101, 10702, 30201, 10201, 10904, 
                 10502, 10408, 10905, ]

character_nickname = {'羊駝':10604, '六星羊駝':30103, '布丁':10200, '空花':10306, '黑騎':10506, '江空':10808, '狗拳':10004, '新怜':10802, '凜':10810, '飯糰':10307,
                      '六星飯糰':30203, '公佩':11004, '流夏':10107, '新可':10210, '小望':10105, '姆咪':10607, '月月':10106, '嘉夜':10701, '新日':10800, '江扇':10009,
                      '秋乃':10405, '泳月':10709, '茉莉':10002, '棒棒糖':10902, '情病':10803, '聖熊':10708, '紡希':10606, '祈梨':11006, '日和':10001, '六星日和':30001,
                      '炸彈人':10101, '熊槌':10401, '萬聖炸彈人':10906, '珠希':10406, '六星珠希':30202, '智':10503, '切嚕':10903, '泳貓':10008, '病嬌':10404, '泳飯':10704,
                      '鈴鐺':10304, '吉塔':10207, '怜':10100, '六星怜':30100, '聖伊':10110, '泳中二':11008, '聖克':10909, '靜流': 10601, '六星靜流': 30302, '克總':10703, '聖誕鈴鐺':10608, 
                      '美美':10204, '忍':10305, '萬美':10907, '卯月':10710, '情姊':10804, '自衛牛':11001, '真陽':10500, '酒鬼':10501, '六星酒鬼':30000, '莫妮卡':10605, 
                      '扇子':10205, '聖誕望':10010, '美冬':10600, '六星美冬':30003, '自衛鈴':11000, '伊莉亞':10206, '泳狗':10809, '咲戀':10005, '中二':10202, '萬聖忍':10208, 
                      '泳美冬':10108, '可蘿':10407, '六星可蘿':30300, '奇幻路人':11003, '路人':10007, '龍女':10807, '泳可':10705, '蕾姆':10109, '拉姆':10209, '鈴':10403, 
                      '公可':11005, '深月':10603, '妹法':10102, '姊法':10400, '泳咲':10609, '萬布丁':10308, '亞里莎':10700, '安':10805, '露':10806, '似似花':10000,
                      '插班碧':10901, '新黑':10310, '本田':10910, '妹弓':10103, '六星妹弓':30002, '爆弓':10303, '泳爆':10409, '病弓':10504, '魔弓':10610, '老師':10104, 
                      '六星老師':30200, '泳老師':10509, '女僕':10402, '新女僕':10410, 'EMT':10309, '霞':10301, '魔霞':10510 , '奇幻妹弓':11002, '美里':10302, '七七香':10300, 
                      '新優':10801, '黑貓':10507, '六星黑貓':30301, '初音':10203, '六星初音':30102, '美咲':10602, 'luna':10908, '公主優依':11007, '聖千':10508, '泳女僕':10706,
                      '泳黑':10707, '毒弓':10505, '千歌':10006, '泳真布':10900, '真布':10003, '六星真布':30101, '優依':10702, '六星優依':30201, '小雪':10201, '優妮':10904, 
                      '鏡華':10502, '萬美':10408, '萬八':10905, }


class Icon(enum.IntEnum):
    charas_1x = 0
    charas_3x = 1
    charas_6x = 2
    row_size = 10
    col_size = 10
    region = 60
    threshold = 2e6


# Get Character ID
# Input: Cropped Character Image
# Output: Character ID
def get_id(img):

    charas_all = ['./icon/charas_a_gray.png', './icon/charas_gray.png', './icon/charas6x_gray.png']
    min = sys.maxsize
    loc = None
    index = None
    
    for i in range(len(charas_all)):
        charas = cv2.imread(charas_all[i], cv2.IMREAD_GRAYSCALE)
        res = cv2.matchTemplate(charas,img, cv2.TM_SQDIFF)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if(min_val < min):
            index = i
            min = min_val
            loc = min_loc
    
    # print('min = ', min)
    if min > Icon.threshold:
        return 0

    col, row = int(loc[0]/Icon.region), int(loc[1]/Icon.region)
    if index == Icon.charas_1x or index == Icon.charas_6x:
        index = str(index+1)
    else:
        index = str(index)
    
    if row < Icon.row_size:
        row = '0' + str(row)
    else:
        row = str(row)
        
    if col < Icon.col_size:
        col = '0' + str(col)
    else:
        col = str(col)
            
    id = int(index + row + col)
    return id


# Battle Result
# Input: Record Image
# Output: Our Win or Lose
def battle_result(img, mode):

    result = None
    if mode == 'upload':
        win_template = cv2.imread('./icon/win.jpg', cv2.IMREAD_GRAYSCALE)
    else:
        win_template = cv2.imread('./icon/friend_win.jpg', cv2.IMREAD_GRAYSCALE)
    win_res = cv2.matchTemplate(win_template, img, cv2.TM_SQDIFF)
    min_val, max_val, win_min_loc, max_loc = cv2.minMaxLoc(win_res)

    if mode == 'upload':
        lose_template = cv2.imread('./icon/lose.jpg', cv2.IMREAD_GRAYSCALE)
    else:
        lose_template = cv2.imread('./icon/friend_lose.jpg', cv2.IMREAD_GRAYSCALE)
    lose_res = cv2.matchTemplate(lose_template, img, cv2.TM_SQDIFF)
    min_val, max_val, lose_min_loc, max_loc = cv2.minMaxLoc(lose_res)

    if win_min_loc[0] < int(img.shape[1]/3):
        result = True
    else:
        result = False
    return win_min_loc, lose_min_loc, result


def decide_where(img):
    
    result = None
    region_all = ['./icon/taiwan.png', './icon/china.png', './icon/japan.png']
    min = sys.maxsize
    loc = None
    index = None
    
    for i in range(len(region_all)):
        template = cv2.imread(region_all[i], cv2.IMREAD_GRAYSCALE)
        res = cv2.matchTemplate(template, img, 0)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        # print('min_val = ', min_val)
        if(min_val < min):
            index = i
            min = min_val

    region = ['taiwan', 'china', 'japan']
    return region[index]


# Image Preprocessing
# Input: Original Image
# Output: Record Image
def preprocessing(img):
    
    # BGR to Binary
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # BGR to Gray
    ret, binary = cv2.threshold(gray,127,255,cv2.THRESH_TOZERO) # Gray to Binary
     
    # Capture Record
    contours, hierarchy = cv2.findContours(binary,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    status = 'upload'
    h_threshold = int(2*img.shape[0]/3)
    w_threshold = int(2*img.shape[1]/3)
    for i in range(len(contours)):
        w_min, h_min = contours[i].min(0)[0,0], contours[i].min(0)[0,1]
        w_max, h_max = contours[i].max(0)[0,0], contours[i].max(0)[0,1]
        
        if w_max - w_min > w_threshold:
            goal_index = i
            if h_max - h_min > h_threshold:
                status = 'search'
            break  

        if h_max - h_min > h_threshold:
            goal_index = i
            status = 'friend_upload'
            break
    
    w_min, h_min = contours[goal_index].min(0)[0,0], contours[goal_index].min(0)[0,1]
    w_max, h_max = contours[goal_index].max(0)[0,0], contours[goal_index].max(0)[0,1]
    record = gray[h_min:h_max, w_min:w_max]
    
    if status == 'friend_upload':
        record =  cv2.resize(record, (630, 630), interpolation=cv2.INTER_CUBIC)
    else:
        record =  cv2.resize(record, (900, 300), interpolation=cv2.INTER_CUBIC)
    
    return status, record


# Image Preprocessing
# Input: Record Image
# Output: Battle Results
def upload_battle_processing(img, region, mode):
    
    # result = None
    win_min_loc, lose_min_loc, result = battle_result(img, mode)

    win_des = 1
    if region == 'china':
        lose_des = 8
        y = 140
    else:
        lose_des = 7
        y = 150

    # Width and Height of Cropped region
    w = 60
    h = 40
    border = 5
    
    # Our team Character
    if mode == 'friend_upload':
        y = 110
    if result == True:
        x = win_min_loc[0] + win_des
    else:
        x = lose_min_loc[0] + lose_des
        
    team = []
    for i in range(5):
        crop_img = img[y:y+h, x+border:x+w-border]
        team.append(get_id(crop_img))
        if mode == 'friend_upload':
            y = y+h+30
        else:
            x = x+w+7
    
    # Enemy team Character
    if mode == 'friend_upload':
        y = 110
    if result == True:
        x = lose_min_loc[0] + lose_des
    else:
        x = win_min_loc[0] + win_des

    enemy = []
    for i in range(5):
        crop_img = img[y:y+h, x+border:x+w-border]
        enemy.append(get_id(crop_img))
        if mode == 'friend_upload':
            y = y+h+30
        else:
            x = x+w+7
        
    return team, enemy, result


def sort_character_loc(our, enemy):
    
    loc_our = []
    loc_enemy = []
    for num in range(len(our)):
        index_our = character_loc.index(our[num])
        loc_our.append(index_our)
        
        index_enemy = character_loc.index(enemy[num])
        loc_enemy.append(index_enemy)
        
    sorted_our = sorted(range(len(loc_our)), key = lambda k : loc_our[k])
    sorted_enemy = sorted(range(len(loc_enemy)), key = lambda k : loc_enemy[k])
    
    for num in range(len(our)):
        order_our = sorted_our[num]
        index_our = loc_our[order_our]
        our[num] = character_loc[index_our]
        
        order_enemy = sorted_enemy[num]
        index_enemy = loc_enemy[order_enemy]
        enemy[num] = character_loc[index_enemy]
    
    return our, enemy


# Image Preprocessing
# Input: Record Image
# Output: Battle Results
def search_battle_processing(img):

    x = 552
    y = 27
    # Width and Height of Cropped region
    w = 60
    h = 37
    
    # Enemy team Character
    enemy = []
    for i in range(5):
        crop_img = img[y:y+h, x:x+w]
        crop_img = cv2.resize(crop_img, (60, 60), interpolation=cv2.INTER_CUBIC)
        crop_img = crop_img[15:50, 10:50]
        enemy.append(get_id(crop_img))
        x = x+w+7
    
    return enemy


def get_record_msg(our, enemy, win, status):

    reply_msg = '進攻隊伍: '
    for i in range(len(our)):
        reply_msg += character[our[i]] + ', '

    reply_msg += '\n\n防守隊伍: '
    for i in range(len(enemy)):
        reply_msg += character[enemy[i]] + ', '
    
    reply_msg += '\n\n獲勝者: '
    if win == True:
        reply_msg += '進攻'
    else:
        reply_msg += '防守'

    if status == 'success':
        reply_msg += '\n紀錄已為您儲存'
    else:
        reply_msg += '\n紀錄已為您更改'
    # reply_msg = '競技場紀錄已為您儲存'

    return reply_msg

def confirm_record_success(our, enemy, mode):

    try:
        if mode == 'upload' or mode == 'friend_upload':
            if len(our) == 0:
                return False
            count_our = Counter(our)
            test1 = count_our.most_common()
            for i in range(len(our)):
                character[our[i]]
                # print(character[our[i]])
                if test1[i][1] > 1:
                    return False

        if len(enemy) == 0:
            return False
        count_enemy = Counter(enemy)
        test2 = count_enemy.most_common()
        for i in range(len(enemy)):
            character[enemy[i]]
            # print(character[enemy[i]])
            # print(enemy[i])
            if test2[i][1] > 1:
                return False

        return True
    except KeyError:
        # print(False)
        return False


def create_record_img(record, good, bad):
    blank_image = np.zeros((len(record)*62, 530, 3), np.uint8)
    blank_image.fill(255)
    charas_all = ['./icon/charas.png', './icon/charas_a.png', './icon/charas6x.png']
    
    row = 0
    col = 0
    for i in range(len(record)):
        for j in range(len(record[0])):
            icon = record[i][j]
            division = 10000
                
            index = int(icon/division)-1
            icon %= division
            division = int(division/100)
            pic_row = int(icon/division)*62
            pic_col = int(icon%division)*62
            charas = cv2.imread(charas_all[index])
            char_pic = charas[pic_row:pic_row+60, pic_col:pic_col+60, :]

            blank_image[row:row+60, col:col+60] = char_pic
            col += 62

        col += 10
        row += 30
        like = cv2.imread('./icon/like.png')
        icon_size = like.shape[0]
        like = like[:icon_size, :icon_size, :]
        blank_image[row:row+icon_size, col:col+icon_size] = like

        cv2.putText(blank_image, str(good[i]), (col+40, row+20), cv2.FONT_ITALIC, 0.75, (0, 0, 0), 2)

        col += 100
        dislike = cv2.imread('./icon/dislike.png')
        icon_size = dislike.shape[0]
        dislike = dislike[:icon_size, :icon_size, :]
        blank_image[row:row+icon_size, col:col+icon_size] = dislike

        cv2.putText(blank_image, str(bad[i]), (col+40, row+20), cv2.FONT_ITALIC, 0.75, (0, 0, 0), 2)

        row += 32
        col = 0
    
    return blank_image