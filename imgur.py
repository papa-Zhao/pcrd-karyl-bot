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
    num = random.randint(0,len(images)-1)
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


def test_kraken_image(image):

    path = './image/search.jpg'
    cv2.imwrite(path, image)

    api = Client('bd3b81ddac4b9cce4cb1e54e148fca1f', '386e40656e9207f53c379cf6c793e5449d71c1e6')

    data = {
        'wait': True
    }

    result = api.upload(path, data);

    if result.get('success'):
        print(result.get('kraked_url'))
        return result.get('kraked_url')