from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

from dotenv import load_dotenv
import os

load_dotenv()

countries = {}

url = 'https://www.scrapethissite.com/pages/simple/'
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
webpage = urlopen(req).read()

# find elements
soup = BeautifulSoup(webpage, 'html.parser')

# get country columns
countries = soup.find_all('div', attrs={'class': 'col-md-4 country'})
for country in countries:
    # c_name = country.find(class='country-name')
    # c_population = country.find('span', attr={'class': 'country-population'})
    # print(c_name + ' ' + c_population)
    print("NEXT COUNTRY:------------------------------------------------------")
  
    print(country.find('h3', attrs={'class': 'country-name'}).text.strip())


