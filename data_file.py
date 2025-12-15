#Names: Iliana Chevres and Avery Burke 
#Data fetching and storing file 

import requests 
import json
import sqlite3
import sys 

#scatterplot needs to show info from json - change to barchart  
#data fetching/storing one file and then visualizations and calculations in another 
#integer key thing to join function 
#dont call specific countries 
#join function should not be storing data, just making it temporarily so calculations can be called on it 

sys.stdout.reconfigure(encoding = 'utf-8')

def call_apis(country):
    #news_api_key = "e6dd185291d51a4ef822e45c5b359069" #iliana
    news_api_key = "ce61d3ddb5a4c64c22ff1b1ba85cd9d4" #avery

    country_api_url = f"https://restcountries.com/v3.1/alpha/{country}"
    news_api_url = f'https://gnews.io/api/v4/top-headlines?country={country.lower()}&apikey={news_api_key}'
    
    response_country = requests.get(country_api_url)
    response_news = requests.get(news_api_url)
    
    #print(response_country.json())
    return response_country.json(), response_news.json()

def get_headlines(country_code):
    country_data, news_data = call_apis(country_code)

    headlines = []
    #print(news_data)

    if "articles" in news_data: 
        for article in news_data["articles"]:
            headlines.append({
                "country" : country_code,
                "title": article.get("title"), 
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
            "region": info.get("region"),
            "independent": info.get("independent"),
            "un_member": info.get("unMember")
        }

        all_status[name] = status

    return all_status

all_data = get_country_status()
print(json.dumps(all_data, indent=4))
#print("Number of countries in all_data:", len(all_data))
#print("First 5 country names:", list(all_data.keys())[:5])

#https://restcountries.com/v3.1/independent?status=true 
def country_id_table():

    resp = requests.get("https://restcountries.com/v3.1/all?fields=name,cca2")
    if resp.status_code != 200:
        print("Error")
        return 
    
    countries = resp.json()

    conn = sqlite3.connect("countrynews.db")
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS country_ids")

    cur.execute("""
                CREATE TABLE IF NOT EXISTS country_ids (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                country_code TEXT UNIQUE, 
                country_name TEXT)
                """)

    for info in countries: 
    
        common_name = info["name"]["common"]
        country_code = info["cca2"].upper()

        cur.execute("""
                INSERT OR IGNORE INTO country_ids (country_code, country_name)
                    VALUES (?,?)
                    """, (country_code, common_name))

    conn.commit()
    conn.close()

    print("Created country id table.")

def get_country_ids():
    country_id_table()
    conn = sqlite3.connect("countrynews.db")
    cur = conn.cursor()

    cur.execute("SELECT country_name, id FROM country_ids")
    rows = cur.fetchall()

    conn.close()
    return {name: cid for name, cid in rows}

def store_headlines():
    #making country ids 
    ids = get_country_ids()
    #add &page=# to url call? 
    resp = requests.get("https://restcountries.com/v3.1/all?fields=name,cca2")
    if resp.status_code != 200:
        print("Error fetching country codes:", resp.status_code)
        return
    
    countries = resp.json()
    
    conn = sqlite3.connect('countrynews.db')
    cur = conn.cursor()
    
    #cur.execute("DROP TABLE IF EXISTS headlines")

    cur.execute('''
        CREATE TABLE IF NOT EXISTS headlines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER,
            country_code TEXT,
            title TEXT,
            url TEXT UNIQUE,
            FOREIGN KEY(country_id) REFERENCES country_ids(id)
        )
    ''')

    existing_countries = set()
    cur.execute("SELECT DISTINCT country_id FROM headlines")
    rows = cur.fetchall()
    for row in rows:
        existing_countries.add(row[0])

    limit = 25               
    new_headlines = 0        

    for info in countries:
        if new_headlines >= limit:
            break

        name_info = info.get("name", {})
        common_name = name_info.get("common")    
        code = info.get("cca2")
        id = ids[common_name]

        if not common_name or not code or not id:
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
            if new_headlines >= limit:
                break

            cur.execute("""
                INSERT OR IGNORE INTO headlines (country_id, country_code, title, url)
                VALUES (?, ?, ?, ?)
            """, (
                id,
                country_code,
                h["title"],
                h["url"]
            ))

            if cur.rowcount > 0:
                new_headlines += 1

        existing_countries.add(country_name)

    conn.commit()
    conn.close()


def store_country_data(all_data):

    ids = get_country_ids()

    conn = sqlite3.connect("countrynews.db")
    cur = conn.cursor()

    #cur.execute("DROP TABLE IF EXISTS country_status")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS country_status (
            country_id INTEGER,
            name TEXT PRIMARY KEY,
            official_name TEXT,
            region TEXT,
            independent INTEGER,
            un_member INTEGER, 
            FOREIGN KEY(country_id) REFERENCES country_ids(id)
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
        
        country_id = ids.get(country_name)
        if country_id is None:
            continue 

        independent_val = None
        if isinstance(info.get("independent"), bool):
            independent_val = int(info["independent"])

        un_member_val = None
        if isinstance(info.get("un_member"), bool):
            un_member_val = int(info["un_member"])

        cur.execute("""
            INSERT OR REPLACE INTO country_status
            (country_id, name, official_name, region,
             independent, un_member)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            country_id, 
            country_name,
            info.get("official_name"),
            info.get("region"),
            independent_val,
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



def main():
    country_id_table()
    store_headlines()
    all_data = get_country_status()      
    store_country_data(all_data)

main()