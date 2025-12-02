
#Names: Iliana Chevres and Avery Burke 
import requests 
import json
import sqlite3
import matplotlib as plt 
import unittest 
import sys 
sys.stdout.reconfigure(encoding = 'utf-8')

def call_apis(country):
    news_api_key = "65bc8405516b8eeece5b4e5741ab6851"

    #have to use different urls for the country api to access the different stuff?
    country_api_url = f"https://restcountries.com/v3.1/name/{country}"
    news_api_url = f'https://gnews.io/api/v4/top-headlines?country = {country}&apikey={news_api_key}'
    
    response_country = requests.get(country_api_url, params = {"country": country})
    response_news = requests.get(news_api_url, params={"country": country.lower(), "apiKey": news_api_key})
    
    #print(response_country.json())
    return response_country.json(), response_news.json()

call_apis("US")

def get_headlines(country):
    country_data, news_data = call_apis(country)
    headlines = []

    if "articles" in news_data: 
        for article in news_data["articles"]:
            headlines.append({
                "title": article.get("title"), 
                "source": article.get("source", {}).get("name"),
                "publishedAt" : article.get("publishedAt"),
                "url" : article.get("url")})
    return headlines 

def get_country_status():
    url = "https://restcountries.com/v3.1/all?fields=name,capital,region,subregion,population,independent,status,unMember"
    response = requests.get(url)

    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return {}

    countries = response.json()
    all_status = {}

    for info in countries:
        name = info.get("name", {}).get("common")
        if not name:
            continue

        status = {
            "official_name": info.get("name", {}).get("official"),
            "capital": info.get("capital", [None])[0] if info.get("capital") else None,
            "region": info.get("region"),
            "subregion": info.get("subregion"),
            "population": info.get("population"),
            "independent": info.get("independent"),
            "status": info.get("status"),
            "un_member": info.get("unMember")
        }

        all_status[name] = status

    return all_status

all_data = get_country_status()
print(json.dumps(all_data, indent=4))

#https://restcountries.com/v3.1/independent?status=true 
def store_headlines(country):
    headlines = get_headlines(country)
    print(country, len(headlines))
    conn = sqlite3.connect('countrynews.db')
    cur = conn.cursor()
    #cur.execute('''  DROP TABLE IF EXISTS headlines''')
    cur.execute('''
                CREATE TABLE IF NOT EXISTS headlines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                country TEXT, 
                title TEXT, 
                source TEXT, 
                publishedAt TEXT, 
                url TEXT
                )
                ''')
    for h in headlines: 
        cur.execute("""
                INSERT INTO headlines (country, title, source, publishedAt, url)
                    VALUES (?,?,?,?,?)
                    """, (country, h["title"], h["source"], h["publishedAt"], h["url"]))
    conn.commit()
    conn.close()
    
    print(f"{country} headlines added to 'headlines' table and 'countrynews.db' created.") 

#putting country data in the database 
store_headlines("fr")
store_headlines("US")
store_headlines("ra")
store_headlines("mx")


def store_country_data(country_data, data_dict):
    conn = sqlite3.connect("countrynews.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS country_status (
            name TEXT PRIMARY KEY,
            official_name TEXT,
            capital TEXT,
            region TEXT,
            subregion TEXT,
            population INTEGER,
            independent INTEGER,
            status TEXT,
            un_member INTEGER
        );
    """)

    independent_val = None
    if isinstance(data_dict.get("independent"), bool):
        independent_val = int(data_dict["independent"])

    un_member_val = None
    if isinstance(data_dict.get("un_member"), bool):
        un_member_val = int(data_dict["un_member"])

    cur.execute("""
        INSERT OR REPLACE INTO country_status
        (name, official_name, capital, region, subregion, population,
         independent, status, un_member)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data_dict.get("name"),
        data_dict.get("official_name"),
        data_dict.get("capital"),
        data_dict.get("region"),
        data_dict.get("subregion"),
        data_dict.get("population"),
        independent_val,
        data_dict.get("status"),
        un_member_val
    ))

    conn.commit()
    conn.close()

def count_headlines_by_month(country, month):
    conn = sqlite3.connect("countrynews.db")
    cur = conn.cursor()

    cur.execute("""
                SELECT COUNT(*) FROM headlines 
                WHERE country = ? AND substr(publishedAt, 6, 2) = ?
                """, (country, month))
    
    count = cur.fetchone()[0]
    conn.close()
    return count 

def calculate_relationship_status():
    pass 

def join_headline_and_country_data():
    pass 

def create_scatter_plot():
    pass 

def create_boxplot(df):
    df.boxplot(column="headline_count", by="independent")
    plt.title(f"Boxplot of Headlines by Independent Status")
    plt.xlabel("Country's Independence Status")
    plt.ylabel("Number of Headlines")
    plt.show()

def main():
    pass

main()


#test cases 
class TestCases(unittest.TestCase):
    #add in test cases for all functions 
    if __name__ == 'main':
        unittest.main()