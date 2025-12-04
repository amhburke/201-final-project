#Data visualizations and calculations file 
#Iliana Chevres and Avery Burke 
import requests 
import json
import sqlite3
import pandas as pd 
import matplotlib.pyplot as plt 
import sys 

sys.stdout.reconfigure(encoding = 'utf-8')

#Joining Data 
def join_headline_and_country_data():

    conn = sqlite3.connect("countrynews.db")
    
    
    
    df = pd.read_sql_query("""
            SELECT h.country_code, h.country_id, c.name, c.independent, c.region, COUNT(h.id) AS headline_count
                           FROM headlines h 
                           JOIN country_status c 
                           ON h.country_id = c.country_id
                           GROUP BY h.country_id, h.country_code, c.independent, c.region
                           """, conn)

    conn.close()
    return df 

def headlines_per_reigon(): 
    conn = sqlite3.connect("countrynews.db")
    cur = conn.cursor()

    cur.execute("""
        SELECT c.region, COUNT(h.country_id) AS total_headlines
        FROM headlines h
        JOIN country_status c
            ON h.country_id = c.country_id
        GROUP BY c.region
    """)

    rows = cur.fetchall()
    conn.close()

    region_counts = {}

    for row in rows:
        region = row[0]
        count = row[1]

        if region is not None:
            region_counts[region] = count

    print("Headlines per region:")
    for region in region_counts:
        print(region + ":", region_counts[region])

    with open("headlines_per_region.json", "w", encoding="utf-8") as f:
        json.dump(region_counts, f, indent=4)

    return region_counts

headlines_per_reigon()

#GRAPHS 
def create_bar_chart(df):
    df_limited = df.sort_values(by='headline_count').head(5)
   
    #all returning as 10s, make it based on country?
    plt.figure(figsize=(8,6))
    plt.bar(df_limited["name"], df_limited["headline_count"])
    plt.title("Barchart of Headline Count by Country")
    plt.xlabel("Country")
    plt.ylabel("Number of Headlines")
    plt.show()

def create_boxplot(df):
    df.boxplot(column="headline_count", by="region")
    plt.title(f"Boxplot of Headlines by Region")
    plt.xlabel("Country's Region")
    plt.ylabel("Number of Headlines")
    plt.show()


def main():

    print("\n -- ANALYSIS -- ")
    df = join_headline_and_country_data()
    print(df)

    print("\n -- GRAPHS --")
    create_boxplot(df)
    create_bar_chart(df)

main()