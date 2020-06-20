import configparser
from imgurpython import ImgurClient
import random
import cv2

config = configparser.ConfigParser()
config.read('config.ini')
client_id = config.get('imgur', 'client_id')
client_secret = config.get('imgur', 'client_secret')
access_token = config.get('imgur', 'access_token')
refresh_token = config.get('imgur', 'refresh_token')

client = ImgurClient(client_id, client_secret, access_token, refresh_token)



album = {'開車':'RlsqLO5', '表情包':'pLG8EmZ', '聯盟戰':'Ft0fvCO',
         '街頭霸王':'7ZXTizY', '可愛':'Bj9sXk4', '抽卡':'mMhngog', '吸貓':'j8bEjwz'}


def get_album_image(key):

    images = client.get_album_images(album[key])
    num = random.randint(0,len(images)-1)
    url = images[num].link
    return url



def upload_album_image(image):
    
    path = './image/search.jpg'
    cv2.imwrite(path,image)
    url = client.upload_from_path(path)['link']
    return url
