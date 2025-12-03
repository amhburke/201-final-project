#Names: Iliana Chevres and Avery Burke 
import requests 
import json
import sqlite3
import pandas as pd 
import matplotlib.pyplot as plt 
import unittest 
import sys 

sys.stdout.reconfigure(encoding = 'utf-8')

def call_apis(country):
    #news_api_key = "65bc8405516b8eeece5b4e5741ab6851"
    news_api_key = "05bf2fe9d109116a0c3c2acba93a6f39"

    country_api_url = f"https://restcountries.com/v3.1/alpha/{country}"
    news_api_url = f'https://gnews.io/api/v4/top-headlines?country={country.lower()}&apikey={news_api_key}'
    
    response_country = requests.get(country_api_url)
    response_news = requests.get(news_api_url)
    
    #print(response_country.json())
    return response_country.json(), response_news.json()

call_apis("US")

def get_headlines(country_code):
    country_data, news_data = call_apis(country_code)

    headlines = []

    if "articles" in news_data: 
        for article in news_data["articles"]:
            headlines.append({
                "country" : country_code,
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
#print("Number of countries in all_data:", len(all_data))
#print("First 5 country names:", list(all_data.keys())[:5])

#https://restcountries.com/v3.1/independent?status=true 

def store_headlines():
    resp = requests.get("https://restcountries.com/v3.1/all?fields=name,cca2")
    if resp.status_code != 200:
        print("Error fetching country codes:", resp.status_code)
        return
    
    countries = resp.json()
    
    conn = sqlite3.connect('countrynews.db')
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS headlines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country TEXT,
            title TEXT,
            source TEXT,
            publishedAt TEXT,
            url TEXT UNIQUE
        )
    ''')

    existing_countries = set()
    cur.execute("SELECT DISTINCT country FROM headlines")
    rows = cur.fetchall()
    for row in rows:
        existing_countries.add(row[0])

    limit = 10
    count_countries = 0

    for info in countries:
        if count_countries >= limit:
            break

        name_info = info.get("name", {})
        common_name = name_info.get("common")    
        code = info.get("cca2")

        if not common_name or not code:
            continue

        country_name = common_name
        country_code = code.upper()

        if country_name in existing_countries:
            continue

        print("Getting headlines for", country_name, "with code", country_code)

        headlines = get_headlines(country_code)

        if not headlines:
            print("No headlines found for", country_name)
            continue

        for h in headlines: 
            cur.execute("""
                INSERT OR IGNORE INTO headlines (country, title, source, publishedAt, url)
                VALUES (?, ?, ?, ?, ?)
            """, (
                country_name,
                h["title"],
                h["source"],
                h["publishedAt"],
                h["url"]
            ))
        existing_countries.add(country_name)
        count_countries += 1

    conn.commit()
    conn.close()
    
    print(f"{country_code} headlines added to 'headlines' table.") 

store_headlines()


#putting country data in the database 
#store_headlines("US")   # United States
#store_headlines("MX")   # Mexico
#store_headlines("AI")   # Anguilla
#store_headlines("FR")   # France


def store_country_data(all_data):
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
        )
    """)

    existing = set()
    cur.execute("SELECT name FROM country_status")
    rows = cur.fetchall()
    for row in rows:
        existing.add(row[0])

    rows_added = 0
    limit = 25

    for country_name, info in all_data.items():
        if country_name in existing:
            continue

        if rows_added >= limit:
            break

        independent_val = None
        if isinstance(info.get("independent"), bool):
            independent_val = int(info["independent"])

        un_member_val = None
        if isinstance(info.get("un_member"), bool):
            un_member_val = int(info["un_member"])

        cur.execute("""
            INSERT OR REPLACE INTO country_status
            (name, official_name, capital, region, subregion, population,
             independent, status, un_member)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            country_name,
            info.get("official_name"),
            info.get("capital"),
            info.get("region"),
            info.get("subregion"),
            info.get("population"),
            independent_val,
            info.get("status"),
            un_member_val
        ))

        rows_added += 1

    conn.commit()

    # check if worked
    cur.execute("SELECT COUNT(*) FROM country_status")
    total_rows = cur.fetchone()[0]
    print("\nAdded", rows_added, "new rows.")
    print("Database now contains", total_rows, "rows total.")

    conn.close()

all_data = get_country_status()      
store_country_data(all_data) 

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

def average_headlines_independent():
    pass

def join_headline_and_country_data():

    conn = sqlite3.connect("countrynews.db")
    
    df = pd.read_sql_query("""
            SELECT h.country, c.independent, c.region, COUNT(h.id) AS headline_count
                           FROM headlines h 
                           JOIN country_status c 
                           ON h.country = c.name 
                           GROUP BY h.country, c.independent, c.region
                           """, conn)
    
    conn.execute("""DROP TABLE IF EXISTS joined_data""")
    
    #saving data frame as a sql table 
    df.to_sql("joined_data", conn, index=False)
    
    conn.commit()
    conn.close()
    return df 

def create_scatter_plot(df):
    #pick something else besides independent 
    plt.scatter(df["independent"], df["headline_count"])
    plt.title("Scatterplot of Headlines by Independent Status")
    plt.xlabel("Country's Independence Status")
    plt.ylabel("Number of Headlines")
    plt.show()

def create_boxplot(df):
    df.boxplot(column="headline_count", by="independent")
    plt.title(f"Boxplot of Headlines by Independent Status")
    plt.xlabel("Country's Independence Status")
    plt.ylabel("Number of Headlines")
    plt.show()

def main():
    print("\n -- STORING DATA -- ")

    print("\n -- ANALYSIS -- ")
    df = join_headline_and_country_data()
    print(df)

    print("\n -- GRAPHS --")
    create_boxplot(df)
    create_scatter_plot(df)

main()


#test cases 
class TestCases(unittest.TestCase):
    #add in test cases for all functions 
    if __name__ == 'main':
        unittest.main()