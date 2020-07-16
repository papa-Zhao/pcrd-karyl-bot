import requests
from bs4 import BeautifulSoup
import requests
from datetime import datetime


def get_pay_info():
    response = requests.get("https://3000.gov.tw/News_Photo.aspx?n=26&sms=9054&page=1&PageSize=20")
    soup = BeautifulSoup(response.text, "html.parser")

    pay = soup.find("div", {"class": "group-list page-block"}).findAll('li')
    print(pay)