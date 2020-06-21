import numpy as np
import cv2
import datetime


# Character Image

# Sources: https://pcrdfans.com/static/sprites/charas.png?t=20200610
# Sources: https://pcrdfans.com/static/sprites/charas_a.png?t=20200610
# Sources: https://pcrdfans.com/static/sprites/charas6x.png?t=20200610

# Sources: https://github.com/peterli110/pcrdfans.com/tree/master/static/sprites
character = {100:'似似花',101:'日和',102:'茉莉',103:'真步',104:'香織',105:'咲戀',106:'千歌',107:'步未',108:'珠希(夏日)',109:'尼諾(大江戶)',1010:'望(聖誕節)',
             110:'怜',111:'禊',112:'茜里',113:'璃乃',114:'伊緒',115:'望',116:'真琴',117:'流夏',118:'美冬(夏日)',119:'雷姆',1110:'伊莉亞(聖誕節)',
             120:'宮子',121:'雪',122:'杏奈',123:'初音',124:'美美',125:'尼諾',126:'伊莉亞',127:'吉塔',128:'忍(萬聖節)',129:'拉姆',1210:'可可羅(新年)',
             130:'七七香',131:'霞',132:'美里',133:'玲奈',134:'胡桃',135:'忍',136:'空花',137:'佩可',138:'宮子(萬聖節)',139:'艾蜜莉亞',1310:'凱留(新年)',
             140:'依里',141:'綾音',142:'鈴苺',143:'鈴',144:'惠理子',145:'秋乃',146:'朱希',147:'可可羅',148:'萬盛美咲',149:'玲奈(夏日)',1410:'鈴苺(新年)',
             150:'真陽',151:'優花梨',152:'鏡華',153:'智',154:'栞',155:'碧',156:'純',157:'凱留',158:'千歌(聖誕節)',159:'伊緒(夏日)',1510:'霞(魔法少女)',
             160:'美冬',161:'靜流',162:'美咲',163:'深月',164:'莉瑪',165:'莫尼卡',166:'紡希',167:'矛依未',168:'胡桃(聖誕節)',169:'咲戀(夏日)',1610:'栞(魔法少女)',
             170:'亞里莎',171:'嘉夜',172:'優依',173:'克莉絲緹娜',174:'佩可(夏日)',175:'可可羅(夏日)',176:'鈴苺(夏日)',177:'凱留(夏日)',178:'綾音(聖誕節)',179:'真琴(夏日)',1710:'卯月',
             180:'日和(新年)',181:'優依(新年)',182:'怜(新年)',183:'惠理子(情人節)',184:'靜流(情人節)',185:'安',186:'露',187:'古蕾婭',188:'空花(大江戶)',189:'香織(夏日)',1810:'凜',
             190:'真步(夏日)',191:'碧(插班生)',192:'克羅伊',193:'琪愛兒',194:'優妮',195:'鏡華(萬聖節)',196:'禊(萬聖節)',197:'美美(萬聖節)',198:'露娜',199:'克(聖誕節)',1910:'本田',
             1100:'鈴(巡者)',1101:'真陽(遊俠)',1102:'璃乃(奇幻)',1103:'步未(幻境)',1104:'公主佩可',1105:'公主可可羅',
             300:'優花梨(六星)',301:'日和(六星)',302:'璃乃(六星)',303:'美冬(六星)',
             310:'怜(六星)',311:'真布(六星)',312:'初音(六星)',313:'莉瑪(六星)',
             320:'伊緒(六星)',321:'優依(六星)',322:'朱希(六星)',323:'佩可(六星)',
             330:'可可羅(六星)',331:'凱留(六星)',}

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
        res = cv2.matchTemplate(charas,img,0)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if(min_val < min):
            index = i
            min = min_val
            loc = min_loc

    row = str(int(loc[1]/60))
    column = str(int(loc[0]/60))
    if index == 0 or index == 2:
        index = str(index+1)
    else:
        index = str(index)
    id = int(index + row + column)
    return id


# Battle Result
# Input: Record Image
# Output: Our Win or Lose
def battle_result(img):
    result = None
    template = cv2.imread('./icon/win.jpg', cv2.IMREAD_GRAYSCALE)
    res = cv2.matchTemplate(template, img, 0)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if min_loc[0] < int(img.shape[1]/3):
        result = True
    else:
        result = False
    return result


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


# Image Preprocessing
# Input: Record Image
# Output: Battle Results
def upload_battle_processing(img):

    x = 35
    y = 140
    # Width and Height of Cropped region
    w = 60
    h = 60
    result = battle_result(img)
    
    # Our team Character
    team = []
    for i in range(5):
        crop_img = img[y:y+h, x:x+w]
        team.append(get_id(crop_img))
        # cv2.imwrite('./test/our_' + str(i) +'.jpg', crop_img)
        x = x+w+7

    # Enemy team Character
    x += 62
    enemy = []
    for i in range(5):
        crop_img = img[y:y+h, x:x+w]
        enemy.append(get_id(crop_img))
        # cv2.imwrite('./test/enemy_' + str(i) +'.jpg', crop_img)
        x = x+w+7
        
    return team, enemy, result


# Image Preprocessing
# Input: Record Image
# Output: Battle Results
def search_battle_processing(img):

    x = 552
    y = 27
    # Width and Height of Cropped region
    w = 60
    h = 39

    # Enemy team Character
    enemy = []
    for i in range(5):
        crop_img = img[y:y+h, x:x+w]
        crop_img = cv2.resize(crop_img, (60, 60), interpolation=cv2.INTER_CUBIC)
        enemy.append(get_id(crop_img))
        # cv2.imwrite('./test/enemy_' + str(i) +'.jpg', crop_img)
        x = x+w+7
        
    return enemy


def get_record_msg(our, enemy, win):

    reply_msg = '我方隊伍: '
    for i in range(len(our)):
        reply_msg += character[our[i]] + ', '

    reply_msg += '\n\n敵方隊伍: '
    for i in range(len(enemy)):
        reply_msg += character[enemy[i]] + ', '
    
    reply_msg += '\n\n獲勝者: '
    if win == True:
        reply_msg += '我方'
    else:
        reply_msg += '敵方'

    reply_msg += '\n紀錄已為你儲存'

    # reply_msg = '競技場紀錄已為你儲存'

    return reply_msg

def confirm_record_success(our, enemy, mode):

    try:
        if mode == 'upload':
            for i in range(len(our)):
                print(character[our[i]])

        for i in range(len(enemy)):
            print(character[enemy[i]])
        # print(True)
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
            division = 0
            if icon > 1000:
                division = 1000
            else:
                division = 100
                
            index = int(icon/division)-1
            # print('index=%d' %(index))
            icon %= division
            division = int(division/10)
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