
#Names: Iliana Chevres and Avery Burke 
import requests 
import json
import sqlite3
import matplotlib

def call_apis(country):
    country_api_key = "https://newsapi.org/v2/top-headlines?country=&apiKey=API_KEY"
    news_api_key = "552f2cf7b2c444ca872c26be4c389a0d"

    #have to use different urls for the country api to access the different stuff?
    country_api_url = f"https://restcountries.com/v3.1/name/{country}"
    news_api_url = 'https://newsapi.org/v2/top-headlines'
    
    response_country = requests.get(country_api_url)
    response_news = requests.get(news_api_url, params={"country":country, "apiKey": news_api_key})
    
    return response_country.json(), response_news.json()

def get_headlines(country):
    data = call_apis(country)
    headlines = []
    for item in data[1:]:
        if 'articles' in item.keys():
            articles = item['articles']
            for article in articles:
                print(article['title'])
                headlines.append(article['title'])
    return headlines 

print(get_headlines("US"))

def get_country_status(country):
    data = call_apis(country)
    country_data = data[0]   # first element = REST Countries data

    if not isinstance(country_data, list) or len(country_data) == 0:
        return {"error": "No country data found"}

    info = country_data[0]

    status = {
        "name": info.get("name", {}).get("common"),
        "official_name": info.get("name", {}).get("official"),
        "capital": info.get("capital", [None])[0],
        "region": info.get("region"),
        "subregion": info.get("subregion"),
        "population": info.get("population"),
        "independent": info.get("independent"),
        "status": info.get("status"),
        "un_member": info.get("unMember")
    }
    return status

print(get_country_status("US"))

def store_headlines():
    pass 
def store_country_data():
    pass 
def count_headlines_by_month():
    pass 
def calculate_relationship_status():
    pass 
def join_headline_and_country_data():
    pass 
def create_scatter_plot():
    pass 
def create_boxplot():
    pass 

def main():
    pass

main()

#test cases 
