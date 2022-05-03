import requests
import json

from dotenv import load_dotenv
import os #provides ways to access the Operating System and allows us to read the environment variables

load_dotenv()

lat = '34.053939'
lon = '-118.158953'
api_key = os.getenv("CURRENT_WEATHER")

#telegram keys
telegram_chat_key = os.getenv("TELEGRAM_CHAT_KEY")
#weather report API token
wr_api_key = os.getenv("WR_STANDO")

# connect to API
weather_response = requests.get('https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}&units=imperial'.format(lat, lon, api_key))
#print(weather_response.status_code)

# get the data from API
data = weather_response.text

# parse the data into JSON format
wr = json.loads(data)

# print
if(wr['cod'] != 200):
    send_weather_report = requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id={}&text=Error {}: {}'.format(wr_api_key, telegram_chat_key, wr['cod'], wr['message']))
else:
    #format string
    weather = wr['weather'][0]
    main = wr['main']
    temp = main['temp']
    temp_min = main['temp_min']
    temp_max = main['temp_max']

    message =   ("Mori mori mori mori!\n"
                "Mori-oh Cho, radioooo!\n\n"
                "Today's forcast is:\n"
                "{} <b>{}</b> ({})\n"
                "Min: <i>{}</i>\n"
                "Max: <i>{}</i>"
                ).format(weather['description'], temp, main['feels_like'], temp_min, temp_max)
    send_weather_report = requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id={}&parse_mode=HTML&text={}'.format(wr_api_key, telegram_chat_key, message))