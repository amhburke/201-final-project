import requests 
import json
import sys 
import pprint

#scatterplot needs to show info from json 
#integer key thing to join function 
#delete table for join 

sys.stdout.reconfigure(encoding = 'utf-8')

news_api_key = "e6dd185291d51a4ef822e45c5b359069" #iliana
country = "GB"
country_api_url = f"https://restcountries.com/v3.1/alpha/{country}"
news_api_url = f'https://gnews.io/api/v4/top-headlines?country={country.lower()}&apikey={news_api_key}&page=1'
# news_api_url2 = f'https://gnews.io/api/v4/top-headlines?country={country.lower()}&apikey={news_api_key}&page=2'

resp = requests.get(news_api_url)
resp.encoding = 'utf-8'
countries = resp.json()

print("FIRST ONE")
pprint.pprint(countries)


# resp = requests.get(news_api_url2)
# resp.encoding = 'utf-8'
# countries = resp.json()

# print("SECOND ONE")
# pprint.pprint(countries)
# EXCLUSIVA: Crean nuevo consejo empresarial; lo '
#                         'integran Slim, Bernardo Gómez, Carlos Hank y otros 15 '
#                         'inversionistas'