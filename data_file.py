#Names: Iliana Chevres and Avery Burke 
#Data fetching and storing file 

import requests 
import json
import sqlite3
import pandas as pd 
import matplotlib.pyplot as plt 
import sys 

#scatterplot needs to show info from json - change scatterplot 
#data fetching/storing one file and then visualizations and calculations in another 
#integer key thing to join function 
#dont call specific countries 
#join function should not be storing data, just making it temporarily so calculations can be called on it 

sys.stdout.reconfigure(encoding = 'utf-8')

def call_apis(country):
    news_api_key = "e6dd185291d51a4ef822e45c5b359069" #iliana
    #news_api_key = "ce61d3ddb5a4c64c22ff1b1ba85cd9d4" #avery

    country_api_url = f"https://restcountries.com/v3.1/alpha/{country}"
    news_api_url = f'https://gnews.io/api/v4/top-headlines?&apikey={news_api_key}'
    
    response_country = requests.get(country_api_url)
    response_news = requests.get(news_api_url)
    
    #print(response_country.json())
    return response_country.json(), response_news.json()

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
    #add &page=# to url call? 
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

    limit = 25               
    new_headlines = 0        

    for info in countries:
        if new_headlines >= limit:
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
            if new_headlines >= limit:
                break

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

            if cur.rowcount > 0:
                new_headlines += 1

        existing_countries.add(country_name)

    conn.commit()
    conn.close()
    
store_headlines()

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
    
    limit = 25 
    count_countries = 0 

    for info in countries: 
        if count_countries >= limit:
            break 
    
        common_name = info["name"]["common"]
        country_code = info["cca2"].upper()

        cur.execute("""
                INSERT OR IGNORE INTO country_ids (country_code, country_name)
                    VALUES (?,?)
                    """, (country_code, common_name))
        
        count_countries += 1 

    conn.commit()
    conn.close()

    print("Created country id table.")

country_id_table()

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



def main():
    pass

main()