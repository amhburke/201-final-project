#Names: Iliana Chevres and Avery Burke 
import requests 
import json
import sqlite3
import matplotlib
def call_apis(country):
    country_api_key = "https://newsapi.org/v2/top-headlines?country=us&apiKey=API_KEY"
    news_api_key = "552f2cf7b2c444ca872c26be4c389a0d"
    
    country_api_url = " https://restcountries.com/v3.1/all"
    news_api_url = 'https://newsapi.org/v2/top-headlines'
    
    response_country = requests.get(country_api_url)
    response_news = requests.get(news_api_url, params={"country":country, "apiKey": news_api_key})
    
    return response_country.json(), response_news.json()

def get_headlines(country):
    data = call_apis(country)
    headlines = []
    for item in data.items():
        headlines.append(data['title'])
    return headlines 

def get_country_status():
    pass 
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