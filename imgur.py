import configparser
import cv2
import random2 as random

from imgurpython import ImgurClient
import base64
import requests

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
    num = random.randint(0, len(images) - 1)
    url = images[num].link
    return url


def upload_album_image(image):
    
    path = './image/search.jpg'
    cv2.imwrite(path,image)
    url = client.upload_from_path(path)['link']
    return url


def get_arena_solutions_image(image):

    path = './image/search.jpg'
    cv2.imwrite(path, image)
    with open(path, "rb") as file:
        url = 'https://api.imgbb.com/1/upload'
        payload = {
            'key': config.get('imgbb', 'key'),
            'image': base64.b64encode(file.read()),
        }
        res = requests.post(url, payload)

    # print(res)
    url = res.json()['data']['image'].get('url')
    # url = res.json()['data'].get('display_url')
    # url = res.json()['data']['thumb'].get('url')
    return url


def get_nacx_image(image):

    path = './image/search.jpg'
    cv2.imwrite(path, image)
    file = {'image':('image.jpg', open(path, 'rb'), "multipart/form-data")}
    request = requests.post('https://api.na.cx/upload', files=file)
    
    res = request.json()
    if res.get('status') == 200:
        return res.get('url')