import mysql.connector

from dotenv import load_dotenv
import os

load_dotenv()


mydb = mysql.connector.connect(
    host=os.getenv("localhost"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    database=os.getenv("DB_DB")
)

print(mydb)

mycursor = mydb.cursor()

print(mycursor.execute("SELECT * FROM pi_tim_pis"))