from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

import json

# request for telegram  app
import requests
# mysql
import mysql.connector

from dotenv import load_dotenv
import os

load_dotenv()

# telegram keys
telegram_chat_key = os.getenv("TELEGRAM_CHAT_KEY")
bf_api_key = os.getenv("BF_STANDO")

# connect to DB
mydb = mysql.connector.connect(
    host=os.getenv("DB_LOCALHOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    database=os.getenv("DB_MAIN")
)

# # db query-ing
mycursor = mydb.cursor()

# variables
scraped_stock = {} #dict to stock of the product

# get user settings from db
sql = "SELECT user_settings FROM pi_tim_user_settings WHERE user_id=(%s)"
adr = (1,)
mycursor.execute(sql, adr)
#convert json to list
user_settings = json.loads(mycursor.fetchone()[0])

# get HTML using request
url = os.getenv("PI_STOCKER_URL")
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(req).read()

# find elements
soup = BeautifulSoup(webpage, 'html.parser')

# get pi table
table = soup.find('table', attrs={'id': 'prodTable'})
table_body = table.find('tbody')

# get each in-stock row of the table
rows = table_body.find_all('tr', attrs={'class': 'table-success'})

# insert selected SKUs
for row in rows:

    # get sku
    col_head = row.th.find(text=True, recursive=False)

    # get link
    link = row.a.get('href')
    
    # get all other info
    cols = row.find_all('td')
    cols = [ele.text.strip() for ele in cols]

    # print(cols)
    col_data = {
        'sku': col_head,
        'desc': cols[0],
        'link': link,
        'vendor': cols[3],
        'in_stock': cols[4],
        'last_stock': cols[5],
        'price': cols[6][6:],
        'currency': cols[6][1:4]
    }

    if col_head in scraped_stock:
        scraped_stock[col_head].append(col_data)
    else:
        scraped_stock[col_head] = [col_data]

message = ""
for user_selected_model in user_settings['watchlist']:
    if user_selected_model['sku'] in scraped_stock:
        notifierBlackList = []
        for user_blacklist_site in user_settings['blacklist']:
            for key, scraped_stock_item in scraped_stock.items():
                scraped_stock_link = scraped_stock_item[0]['link']
                if user_blacklist_site in scraped_stock_link:
                    notifierBlackList.append(scraped_stock_link)
                    break
        
        user_selected_currencies = user_selected_model['currencies']
        model_info = scraped_stock[user_selected_model['sku']]
        # get model_info currencies (of available in-stock currencies)
        model_info_currencies = []
        for row in model_info:
            model_info_currencies.append(row['currency'])

        # write message for ANY currency
        if user_selected_currencies[0] == "ALL":
            message += "<b><u>{}</u></b> IS IN STOCK ({})!\n".format(model_info[0]['desc'], (len(model_info) - len(notifierBlackList)))
            # begin message
            row_message = ""
            for row in model_info:
                if row['link'] in notifierBlackList: # ignore if site is blacklisted
                    continue
                temp_message = (
                    "<b>Price:</b> {} ({})\n"
                    "<b>Link:</b> <a href='{}'>{}</a>\n"
                ).format(row['price'], row['currency'], row['link'], row['vendor'])
                row_message += temp_message + "\n"
            message += row_message
        # write message for selected currencies
        elif any(x in model_info_currencies for x in user_selected_currencies):
            if (len(model_info_currencies) - len(notifierBlackList)) > 0:
                message += "<b><u>{}</u></b> IS IN STOCK (".format(model_info[0]['desc'])
                for model_info_data in model_info:
                    if model_info_data['link'] in notifierBlackList:
                        continue
                    if not model_info_data['currency'] in user_selected_currencies:
                        continue
                    # begin message
                    row_message = ""
                    if(message[-5:-2] != model_info_data['currency']):
                        message += "{}, ".format(model_info_data['currency'])
                    temp_message = (
                        "<b>Price:</b> {} ({})\n"
                        "<b>Link:</b> <a href='{}'>{}</a>\n"
                    ).format(model_info_data['price'], model_info_data['currency'], model_info_data['link'], model_info_data['vendor'])
                    row_message += temp_message + "\n"
                    message = message.rstrip(', ')
                    message += ")!\n{}".format(row_message)

if message:
    send_baby_face = requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id={}&parse_mode=HTML&text={}'.format(bf_api_key, telegram_chat_key, message))

# {
# 'RPI3-MODAP': 
#     [
#         {
#             'sku': 'RPI3-MODAP', 
#             'desc': 'RPi 3 Model A+ - 512MB RAM', 'link': '', 
#             'vendor': 'MC Hobby (BE)', 
#             'in_stock': 'Yes', 
#             'last_stock': '03-May-22', 
#             'price': '27.95', 'currency': 'EUR'
#         }, 
#         {
#             'sku': 'RPI3-MODAP', 
#             'desc': 'RPi 3 Model A+ - 512MB RAM', 'link': '', 
#             'vendor': 'Pimoroni (UK)', 
#             'in_stock': 'Yes', 
#             'last_stock': '03-May-22', 
#             'price': '23.40', 'currency': 'GBP'
#         }, 
#         {
#             'sku': 'RPI3-MODAP', 
#             'desc': 'RPi 3 Model A+ - 512MB RAM', 'link': '', 
#             'vendor': 'Reichelt (DE)', 
#             'in_stock': 'Yes', 
#             'last_stock': '03-May-22', 
#             'price': '33.60', 'currency': 'EUR'
#         }
#     ]
# }