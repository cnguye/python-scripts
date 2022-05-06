from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

import mysql.connector

from dotenv import load_dotenv
import os

load_dotenv()

scraped_pis = {} # dict for list of existing pis
currency_list = [] # array for existing currencies

# get HTML using request
url = os.getenv("PI_STOCKER_URL")
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(req).read()

# find elements
soup = BeautifulSoup(webpage, 'html.parser')

# get pi table
table = soup.find('table', attrs={'id': 'prodTable'})
table_body = table.find('tbody')

# get each row
rows = table_body.find_all('tr')

# insert selected SKUs
for row in rows:

    # get sku
    col_sku = row.th.find(text=True, recursive=False)
    
    # get all other info
    cols = row.find_all('td')
    cols = [ele.text.strip() for ele in cols]

    # get current currency
    currency = cols[6][1:4]
    # get current model
    pi_model = cols[0]

    if currency not in currency_list:
        currency_list.append(currency)
    if pi_model not in scraped_pis:
        scraped_pis[col_sku] = pi_model

# sort lists
sorted_scraped_pis = {k: scraped_pis[k] for k in sorted(scraped_pis)}
currency_list.sort()

# connect to DB
mydb = mysql.connector.connect(
    host=os.getenv("DB_LOCALHOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    database=os.getenv("DB_MAIN")
)

# # db query-ing
mycursor = mydb.cursor()

# get list of skus from database
mycursor.execute("SELECT sku FROM pi_tim_models")
db_skus = mycursor.fetchall()
# convert array of tuples into array
db_skus = [ele[0] for ele in db_skus]

# get list of currencies from database
mycursor.execute("SELECT currency FROM pi_tim_currencies")
db_currencies = mycursor.fetchall()
db_currencies = [ele[0] for ele in db_currencies]

# add nonexisting SKUs and Models to DB
for sku, model in sorted_scraped_pis.items():
    if(sku not in db_skus):
        # prepare to add to database
        sql = "INSERT INTO pi_tim_models (sku, models) VALUES (%s, %s);"
        adr = (sku, model)
        mycursor.execute(sql, adr)
        mydb.commit()
        print("added ", sku, " ", model, " to the pi_tim_models")

# add nonexisting currencies to DB
for currency in currency_list:
    if(currency not in db_currencies):
        # prepare to add to database
        sql = "INSERT INTO pi_tim_currencies (currency) VALUES (%s);"
        adr = (currency,)
        mycursor.execute(sql, adr)
        mydb.commit()
        print("added ", currency, " to the pi_tim_currencies")

# for db_sku in db_skus:
#     print(db_sku[0])

# for sku, model in sorted_scraped_pis.items():
#     print("SKU: ", sku, " MODEL: ", model)
