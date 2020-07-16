import requests

from math import radians, cos, sin, asin, sqrt
 

def haversine(lat1, lon1, lat2, lon2):
    p = 0.017453292519943295    # Math.PI/180
    c = cos
    a = 0.5 - c((lat2 - lat1) * p)/2 + c(lat1 * p) * c(lat2 * p) * (1 - c((lon2 - lon1) * p))/2

    return 12742 * asin(sqrt(a)) # C = 2 * R, R = 6371 km

def get_recently_bank(bank, distance):
    
    num = len(bank)
    sorted_s = sorted(range(num), key = lambda k : distance[k]) 
    info = []
    for i in range(5):
        index = sorted_s[i]
        # city = bank[index]['hsnNm']
        # town = bank[index]['townNm']
        name = bank[index]['storeNm']
        addr = bank[index]['addr']
        opentime = bank[index]['busiTime']
        opentime = opentime.replace('<br>', '\n')
        memo = bank[index]['busiMemo']
        total = bank[index]['total']
        lat = bank[index]['latitude']
        lon = bank[index]['longitude']
        if memo == None:
            info.append([name, addr, opentime, '', total, lat, lon])
            # print(name, addr, opentime, total)
        else:
            memo = memo.replace('<br>', '\n')
            info.append([name, addr, opentime, memo, total, lat, lon])
            # print(name, addr, opentime, memo, total)
    
    return info

def get_bank_info(user_lat, user_lon):
    
    city = ['臺北市', '新北市', '桃園市', '臺中市', '臺南市', '高雄市', '基隆市', '新竹市', '嘉義市',
       '新竹縣', '苗栗縣', '彰化縣', '南投縣', '雲林縣', '嘉義縣', '屏東縣', '宜蘭縣', '花蓮縣', '臺東縣', '澎湖縣', '金門縣', '連江縣']
    r = requests.get("https://3000.gov.tw/hpgapi-openmap/api/getPostData", verify=True)
    list_of_bank = r.json()

    num = len(list_of_bank)
    distance = []
    for i in range(num):
        lat = list_of_bank[i]['latitude']
        lon = list_of_bank[i]['longitude']
        distance.append(haversine(user_lat, user_lon, float(lat), float(lon)))

    bank = get_recently_bank(list_of_bank, distance)
    
    return bank
    
    msg = '振興三倍卷資訊:'
    for i in range(5):
        msg += '\n' + str(i+1) + '.名稱:' + bank[i][0]
        msg += '\n郵局地址:' + bank[i][1]
        msg += '\n營業時間:' + bank[i][2]
        if bank[i][3] != '':
            msg += '\n營業資訊:' + bank[i][3]
        msg += '\n剩餘數量:' + bank[i][4]
        msg += '\n'

    # for i in range(len(distance)):
    #     print(distance[i])

    return msg