#Names: Iliana Chevres and Avery Burke 
import requests 
import json
import sqlite3
import pandas as pd 
import matplotlib as plt 
import unittest 
import sys 

sys.stdout.reconfigure(encoding = 'utf-8')

def call_apis(country):
    # iliana news_api_key = "65bc8405516b8eeece5b4e5741ab6851"
    news_api_key = "3d234e0bcad1631cbd31fac995d6ac72"

    country_api_url = f"https://restcountries.com/v3.1/name/{country}"
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
    url = "https://restcountries.com/v3.1/all?fields=cca2,name,capital,region,subregion,population,independent,status,unMember"
    response = requests.get(url)

    if response.status_code != 200:
        print("Error:", response.status_code, response.text)
        return {}

    countries = response.json()
    all_status = {}

    for info in countries:
        code = info.get("cca2")
        #name = info.get("name", {}).get("common")
        #if not name:
           # continue

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

        all_status[code.upper()] = status

    return all_status

all_data = get_country_status()
print(json.dumps(all_data, indent=4))
#print("Number of countries in all_data:", len(all_data))
#print("First 5 country names:", list(all_data.keys())[:5])

#https://restcountries.com/v3.1/independent?status=true 

def store_headlines(country_code):
    country_name = country_code
    country_data, _ = call_apis(country_code)

    country_name = country_code 

    if isinstance(country_data, list) and len(country_data) > 0:
        first = country_data[0]
        name_info = first.get("name", {})
        common_name = name_info.get("common")
        if common_name:
            country_name = common_name

    headlines = get_headlines(country_code)
    #print(country, len(headlines))
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
        """, (
            country_name,           
            h["title"],
            h["source"],
            h["publishedAt"],
            h["url"]
        ))
    conn.commit()
    conn.close()

    print(f"{headlines_dict} for {country_code}")

#putting country data in the database 
store_headlines("US")   # United States
store_headlines("MX")   # Mexico
store_headlines("AI")   # Anguilla
store_headlines("FR")   # France


def store_country_data(all_data):

    conn = sqlite3.connect("countrynews.db")
    cur = conn.cursor()
    #cur.execute("""DROP TABLE IF EXISTS country_status""")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS country_status (
            country_code TEXT PRIMARY KEY,
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
    cur.execute("SELECT country_code FROM country_status")
    rows = cur.fetchall()
    for row in rows:
        existing.add(row[0])

    rows_added = 0
    limit = 25

    for code, info in all_data.items():
        code = code.upper()

        if code in existing: 
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
            (country_code, official_name, capital, region, subregion, population,
             independent, status, un_member)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            code,
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
    conn = sqlite3.connect("countrynews.db")
    cur = conn.cursor()

    cur.execute("SELECT country_code FROM country_status WHERE independent = 1")
    rows = cur.fetchall()

    independent_countries = []
    for row in rows:
        independent_countries.append(row[0])

    if len(independent_countries) == 0:
        conn.close()
        print("No independent countries found in database.")
        return 0.0

    total_headlines = 0
    num_countries = 0

    for country_name in independent_countries:

        simple_code = country_name.lower()[:2]     
        simple_code_upper = simple_code.upper()

        cur.execute("""
            SELECT COUNT(*) FROM headlines
            WHERE country = ? OR country = ? OR country = ?
        """, (country_name, simple_code, simple_code_upper))

        count = cur.fetchone()[0]

        total_headlines += count
        num_countries += 1

    if num_countries == 0:
        average = 0.0
    else:
        average = total_headlines / float(num_countries)

    conn.close()
    
    print("Average headlines per independent country:", average)
    return average

average_headlines_independent()

def join_headline_and_country_data():
    country_codes = {"us": "United States",
                     "fr": "France", 
                     "mx" : "Mexico",
                     "ca" : "Canada"}

    conn = sqlite3.connect("countrynews.db")
    
    df = pd.read_sql_query("""
            SELECT h.country, c.independent, COUNT(h.id) AS headline_count
                           FROM headlines h 
                           JOIN country_status c 
                           ON UPPER(h.country) = UPPER(c.country_code)
                           GROUP BY h.country
                           """, conn)
    
    conn.close()
    return df 

def create_scatter_plot():
    pass 

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

main()


#test cases 
class TestCases(unittest.TestCase):
    #add in test cases for all functions 
    if __name__ == 'main':
        unittest.main()