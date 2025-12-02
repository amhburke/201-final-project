
#Names: Iliana Chevres and Avery Burke 
import requests 
import json
import sqlite3
import matplotlib as plt 
import unittest 

def call_apis(country):
    #country_api_key = "https://newsapi.org/v2/top-headlines?country=&apiKey=API_KEY"
    news_api_key = "552f2cf7b2c444ca872c26be4c389a0d"

    #have to use different urls for the country api to access the different stuff?
    country_api_url = f"https://restcountries.com/v3.1/alpha/{country}"
    news_api_url = 'https://newsapi.org/v2/top-headlines'
    
    response_country = requests.get(country_api_url)
    response_news = requests.get(news_api_url, params={"country":country, "apiKey": news_api_key})
    
    return response_country.json(), response_news.json()

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

def get_country_status(country):
    data = call_apis(country)
    country_data = data[0]  

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

def store_headlines(country):
    headlines = get_headlines(country)
    conn = sqlite3.connect('countrynews.db')
    cur = conn.cursor()
    #can remove later 
    cur.execute("DROP TABLE IF EXISTS headlines")

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
    
    print("Database 'countrynews.db'' and 'headlines' table created.") 


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

data = get_country_status("US")
store_country_data("US", data)


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