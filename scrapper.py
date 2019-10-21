import requests
import bs4
import time
import re
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import config



input_urls = config.input_urls
user_agent = {'user - agent': 'Mozilla / 5.0(X11; Linux x86_64) AppleWebKit / 537.36 (KHTML, like Gecko) Chrome / '
                              '77.0.3865.90 Safari / 537.36'}

data_for_export = []
sheet_name = 'scrapper_results'

def insert_data_to_sheet(sheet_name, data_for_export):
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets', ]
    creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
    client = gspread.authorize(creds)

    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sheet = client.open(sheet_name).sheet1
    index = 2

    if data_for_export:
        try:
            for row in data_for_export:
                sheet.insert_row(row, index)
        except Exception as err:
            print('Some error received: ', err)


def parse_urls(urls):
    data_for_export.clear()

    for url in urls:
        try:
            res = requests.get(url, headers=user_agent,)
            soup = bs4.BeautifulSoup(res.text, features="html.parser")

            price = soup.find("meta", itemprop="price")
            site = re.sub(r'(.*://)?([^/?]+).*', '\g<1>\g<2>', url)

            data_for_export.append([price["content"], time.ctime(), site])

        except Exception as err:
            print('Some error received: ', err)


while True:
    parse_urls(input_urls)
    insert_data_to_sheet(sheet_name, data_for_export)
    time.sleep(3600 + random.randint(1,360))
