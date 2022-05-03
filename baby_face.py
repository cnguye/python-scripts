from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import requests

from dotenv import load_dotenv
import os

load_dotenv()

# telegram keys
telegram_chat_key = os.getenv("TELEGRAM_CHAT_KEY")
bf_api_key = os.getenv("BF_STANDO")

stocks = {} #dict to stock of the product

# get HTML using request
url = os.getenv("PI_STOCKER")
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(req).read()

# find elements
soup = BeautifulSoup(webpage, 'html.parser')

# get pi table
table = soup.find('table', attrs={'id': 'prodTable'})
table_body = table.find('tbody')

# get each row
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

    if col_head in stocks:
        stocks[col_head].append(col_data)
    else:
        stocks[col_head] = [col_data]

selected_skus = ["RPI3-MODAP"]


for sku in stocks:
    if sku in selected_skus:
        message =   "<b><u>{}</u></b> IS IN STOCK ({})!\n".format(stocks[sku][0]['desc'], len(stocks[sku]))
        row_message = ""
        for row in stocks[sku]:
            temp_message = (
                "<b>Price:</b> {} ({})\n"
                "<b>Link:</b> <a href='{}'>{}</a>\n"
            ).format(row['price'], row['currency'], row['link'], row['vendor'])
            row_message += temp_message + "\n"
        message += row_message
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