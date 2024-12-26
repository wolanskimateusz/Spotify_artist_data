from requests import post, get
from dotenv import load_dotenv
import os
import base64
import json
import pyodbc
from datetime import datetime
import pandas as pd

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

server = "MATEUSZ\SQLEXPRESS"
database = "spotify_data"

connection_string = f""" 
DRIVER={{ODBC Driver 17 for SQL Server}};
SERVER={server};
DATABASE={database};
Trusted_Connection=yes;

"""
try:
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
except Exception as e:
    print("Error: ", e)


def get_auth_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization" : "Basic " + auth_base64,
        "Content-Type" : "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type" : "client_credentials"
    }
    
    result = post(url, headers = headers, data = data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization" : "Bearer " + token}
    
    
def get_artist_info(token, name):
    url = "https://api.spotify.com/v1/search"
    query = f"?q={name}&type=artist&limit=1"
    query_url = url + query
    current_date = datetime.now().date()
    headers = get_auth_header(token)
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    artist_name = json_result[0]["name"]
    artist_followers = json_result[0]["followers"]["total"]
    artist_popularity = json_result[0]["popularity"]
    artist_info = [artist_name, artist_followers, artist_popularity, current_date]
    print(artist_info)
    return artist_info

def save_artist_data(token, artists):
    for artist in artists:
        try:
            data = get_artist_info(token, artist)
            query = """
            INSERT INTO artists_stats (artist_name, followers, popularity, record_date)
            VALUES(?,?,?,?)
            """
            cursor.execute(query,data)
            conn.commit()
            
        except Exception as e:
            print("Error: ", e)
    print("Dane zapisane do bazy")

 
def get_artist_data():
    try:
        query = """
        SELECT * FROM artists_stats
        """
        df = pd.read_sql_query(query, conn)
        print(df)     
    except Exception as e:
        print("Error: ", e)

artists = ["Linkin Park", "Nirvana", "Dua lipa", "Szpaku", "kaz blagane", "the weeknd", "skolim", "taco Hemingway",
           "Modern talking", "Bambi", "Dżem", "Lady Pank", "Skillet", "Pitbull", "Flo rida", "Rihanna", "Britney Spears",
           "The Police", "Lady Gaga", "Scooter", "Hollywood Undead", "Sean Paul"]
token = get_auth_token()

save_artist_data(token, artists)
get_artist_data()
conn.close()