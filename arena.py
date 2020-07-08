import numpy as np
import cv2
from collections import Counter

# Character Image
# redive.estertion.win
# Sources: https://pcrdfans.com/static/sprites/charas.png?t=20200630
# Sources: https://pcrdfans.com/static/sprites/charas_a.png?t=20200630
# Sources: https://pcrdfans.com/static/sprites/charas6x.png?t=20200630

# Sources: https://github.com/peterli110/pcrdfans.com/tree/master/static/sprites
character = {10000:'似似花',10001:'日和',10002:'茉莉',10003:'真步',10004:'香織',10005:'咲戀',10006:'千歌',10007:'步未',10008:'珠希(夏日)',10009:'尼諾(大江戶)',10010:'望(聖誕節)',
             10100:'怜',10101:'禊',10102:'茜里',10103:'璃乃',10104:'伊緒',10105:'望',10106:'真琴',10107:'流夏',10108:'美冬(夏日)',10109:'雷姆',10110:'伊莉亞(聖誕節)',
             10200:'宮子',10201:'雪',10202:'杏奈',10203:'初音',10204:'美美',10205:'尼諾',10206:'伊莉亞',10207:'吉塔',10208:'忍(萬聖節)',10209:'拉姆',10210:'可可羅(新年)',
             10300:'七七香',10301:'霞',10302:'美里',10303:'玲奈',10304:'胡桃',10305:'忍',10306:'空花',10307:'佩可',10308:'宮子(萬聖節)',10309:'艾蜜莉亞',10310:'凱留(新年)',
             10400:'依里',10401:'綾音',10402:'鈴苺',10403:'鈴',10404:'惠理子',10405:'秋乃',10406:'朱希',10407:'可可羅',10408:'萬盛美咲',10409:'玲奈(夏日)',10410:'鈴苺(新年)',
             10500:'真陽',10501:'優花梨',10502:'鏡華',10503:'智',10504:'栞',10505:'碧',10506:'純',10507:'凱留',10508:'千歌(聖誕節)',10509:'伊緒(夏日)',10510:'霞(魔法少女)',
             10600:'美冬',10601:'靜流',10602:'美咲',10603:'深月',10604:'莉瑪',10605:'莫尼卡',10606:'紡希',10607:'矛依未',10608:'胡桃(聖誕節)',10609:'咲戀(夏日)',10610:'栞(魔法少女)',
             10700:'亞里莎',10701:'嘉夜',10702:'優依',10703:'克莉絲緹娜',10704:'佩可(夏日)',10705:'可可羅(夏日)',10706:'鈴苺(夏日)',10707:'凱留(夏日)',10708:'綾音(聖誕節)',10709:'真琴(夏日)',10710:'卯月',
             10800:'日和(新年)',10801:'優依(新年)',10802:'怜(新年)',10803:'惠理子(情人節)',10804:'靜流(情人節)',10805:'安',10806:'露',10807:'古蕾婭',10808:'空花(大江戶)',10809:'香織(夏日)',10810:'凜',
             10900:'真步(夏日)',10901:'碧(插班生)',10902:'克羅伊',10903:'琪愛兒',10904:'優妮',10905:'鏡華(萬聖節)',10906:'禊(萬聖節)',10907:'美美(萬聖節)',10908:'露娜',10909:'克(聖誕節)',10910:'本田',
             11000:'鈴(巡者)',11001:'真陽(遊俠)',11002:'璃乃(奇幻)',11003:'步未(幻境)',11004:'佩可(公主型態)',11005:'可可羅(公主型態)',11006:'祈梨',11007:'優依(公主型態)',11008:'杏奈(夏日)',
             30000:'優花梨(六星)',30001:'日和(六星)',30002:'璃乃(六星)',30003:'美冬(六星)',
             30100:'怜(六星)',30101:'真布(六星)',30102:'初音(六星)',30103:'莉瑪(六星)',
             30200:'伊緒(六星)',30201:'優依(六星)',30202:'朱希(六星)',30203:'佩可(六星)',
             30300:'可可羅(六星)',30301:'凱留(六星)',}

# Get Character ID
# Input: Cropped Character Image
# Output: Character ID
def get_id(img):
    charas_all = ['./icon/charas_a_gray.png', './icon/charas_gray.png', './icon/charas6x_gray.png']
    min = 1e10
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
    if min > 2e6:
        return 0
    
    row = int(loc[1]/60)
    col = int(loc[0]/60)

    if index == 0 or index == 2:
        index = str(index+1)
    else:
        index = str(index)
    
    if row < 10:
        row = '0' + str(row)
    else:
        row = str(row)
        
    if col < 10:
        col = '0' + str(col)
    else:
        col = str(col)
            
    id = int(index + row + col)
    return id



# Battle Result
# Input: Record Image
# Output: Our Win or Lose
def battle_result(img):
    result = None
    win_template = cv2.imread('./icon/win.jpg', cv2.IMREAD_GRAYSCALE)
    lose_template = cv2.imread('./icon/lose.jpg', cv2.IMREAD_GRAYSCALE)
    win_res = cv2.matchTemplate(win_template, img, 0)
    lose_res = cv2.matchTemplate(lose_template, img, 0)
    min_val, max_val, win_min_loc, max_loc = cv2.minMaxLoc(win_res)
    min_val, max_val, lose_min_loc, max_loc = cv2.minMaxLoc(lose_res)
    if win_min_loc[0] < int(img.shape[1]/3):
        result = True
    else:
        result = False
    return win_min_loc, lose_min_loc, result

def decide_where(img):
    result = None
    china_template = cv2.imread('./icon/china.png', cv2.IMREAD_GRAYSCALE)
    taiwan_template = cv2.imread('./icon/taiwan.png', cv2.IMREAD_GRAYSCALE)
    china_res = cv2.matchTemplate(china_template, img, 0)
    taiwan_res = cv2.matchTemplate(taiwan_template, img, 0)
    china_min_val, china_max_val, china_min_loc, max_loc = cv2.minMaxLoc(china_res)
    taiwan_min_val, taiwan_max_val, taiwan_min_loc, max_loc = cv2.minMaxLoc(taiwan_res)
    if china_min_val < taiwan_min_val:
        return 'china'
    else:
        return 'taiwan'



# Image Preprocessing
# Input: Original Image
# Output: Record Image
def preprocessing(img):
    
    # BGR to Binary
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # BGR to Gray
    ret, binary = cv2.threshold(gray,150,255,cv2.THRESH_TOZERO) # Gray to Binary
     
    # Capture Record
    contours, hierarchy = cv2.findContours(binary,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    goal_index = 0
    status = 'upload'
    h_threshold = int(2*img.shape[0]/3)
    w_threshold = int(img.shape[1]/2)
    for i in range(len(contours)):
        w_min = contours[i].min(0)[0,0]
        w_max = contours[i].max(0)[0,0]
        if w_max - w_min > w_threshold:
            goal_index = i
            h_min = contours[i].min(0)[0,1]
            h_max = contours[i].max(0)[0,1]
            if h_max - h_min > h_threshold:
                status = 'search'
            break;

    
    h_min = contours[goal_index].min(0)[0,1]
    h_max = contours[goal_index].max(0)[0,1]
    w_min = contours[goal_index].min(0)[0,0]
    w_max = contours[goal_index].max(0)[0,0]
    
    if h_max == h_min or w_max == w_min:
        return 'not record', None

    record = gray[h_min:h_max, w_min:w_max]
    
    record =  cv2.resize(record, (900, 300), interpolation=cv2.INTER_CUBIC)
    return status, record


def upload_battle_processing_china(img):

    
    # result = None
    win_min_loc, lose_min_loc, result = battle_result(img)
    # print(win_min_loc)
    # print(lose_min_loc)
    if result == True:
        x = win_min_loc[0]+1
    else:
        x = lose_min_loc[0]+8
    y = 140
    # Width and Height of Cropped region
    w = 60
    h = 40
    border = 5
    
    # Our team Character
    team = []
    for i in range(5):
        crop_img = img[y:y+h, x+border:x+w-border]
        team.append(get_id(crop_img))
        x = x+w+7

    
    # Enemy team Character
    if result == True:
        x = lose_min_loc[0]+8
    else:
        x = win_min_loc[0]+1
    # x += 62
    enemy = []
    for i in range(5):
        crop_img = img[y:y+h, x+border:x+w-border]
        enemy.append(get_id(crop_img))
        x = x+w+7
        
    return team,enemy,result


# Image Preprocessing
# Input: Record Image
# Output: Battle Results
def upload_battle_processing(img):

    
    # result = None
    win_min_loc, lose_min_loc, result = battle_result(img)
    # print(win_min_loc)
    # print(lose_min_loc)
    if result == True:
        x = win_min_loc[0]+1
    else:
        x = lose_min_loc[0]+7
    y = 150
    # Width and Height of Cropped region
    w = 60
    h = 40
    border = 5
    
    
    # Our team Character
    team = []
    for i in range(5):
        crop_img = img[y:y+h, x+border:x+w-border]
        team.append(get_id(crop_img))
        x = x+w+7

    
    # Enemy team Character
    if result == True:
        x = lose_min_loc[0]+7
    else:
        x = win_min_loc[0]+1
    # x += 62
    enemy = []
    for i in range(5):
        crop_img = img[y:y+h, x+border:x+w-border]
        enemy.append(get_id(crop_img))
        x = x+w+7
        
    return team,enemy,result


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
        if mode == 'upload':
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