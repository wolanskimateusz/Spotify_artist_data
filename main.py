from requests import post, get
from dotenv import load_dotenv
import os
import base64
import json
import pyodbc
from datetime import datetime
import pandas as pd 
import matplotlib.pyplot as plt

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
        return df     
    except Exception as e:
        print("Error: ", e)
        
# Funkcja do filtrowania danych dla wybranego artysty
def plot_artist(df, artist_name):
    # Filtruj dane dla danego artysty
    artist_data = df[df['artist_name'].str.lower() == artist_name.lower()]
    
    # Upewnij się, że dane są posortowane po dacie
    artist_data = artist_data.sort_values(by="record_date")
    
    fig, axs = plt.subplots(1, 2, figsize=(16, 6))
    
     # Wykres 1: Liczba obserwujących
    axs[0].plot(artist_data['record_date'], artist_data['followers'], marker='o', label="Obserwujący")
    axs[0].set_title(f"Zmiana liczby obserwujących: {artist_name}", fontsize=14)
    axs[0].set_xlabel("Data", fontsize=12)
    axs[0].set_ylabel("Liczba obserwujących", fontsize=12)
    axs[0].grid(alpha=0.5)
    axs[0].legend()

    # Wykres 2: Popularność
    axs[1].plot(artist_data['record_date'], artist_data['popularity'], marker='o', color='orange', label="Popularność")
    axs[1].set_title(f"Zmiana popularności: {artist_name}", fontsize=14)
    axs[1].set_xlabel("Data", fontsize=12)
    axs[1].set_ylabel("Popularność", fontsize=12)
    axs[1].grid(alpha=0.5)
    axs[1].legend()

    # Wyświetlenie wykresów
    plt.tight_layout()
    plt.show()


def plot_all_artists(df):
    # Pobierz unikalne nazwy artystów
    unique_artists = df['artist_name'].unique()
    
    for artist_name in unique_artists:
        # Filtruj dane dla danego artysty
        artist_data = df[df['artist_name'].str.lower() == artist_name.lower()]
        
        # Upewnij się, że dane są posortowane po dacie
        artist_data = artist_data.sort_values(by="record_date")
        
        # Tworzenie dwóch wykresów obok siebie
        fig, axs = plt.subplots(1, 2, figsize=(16, 6))
        
        # Wykres 1: Liczba obserwujących
        axs[0].plot(artist_data['record_date'], artist_data['followers'], marker='o', label="Obserwujący")
        axs[0].set_title(f"Zmiana liczby obserwujących: {artist_name}", fontsize=14)
        axs[0].set_xlabel("Data", fontsize=12)
        axs[0].set_ylabel("Liczba obserwujących", fontsize=12)
        axs[0].grid(alpha=0.5)
        axs[0].legend()

        # Wykres 2: Popularność
        axs[1].plot(artist_data['record_date'], artist_data['popularity'], marker='o', color='orange', label="Popularność")
        axs[1].set_title(f"Zmiana popularności: {artist_name}", fontsize=14)
        axs[1].set_xlabel("Data", fontsize=12)
        axs[1].set_ylabel("Popularność", fontsize=12)
        axs[1].grid(alpha=0.5)
        axs[1].legend()

        # Wyświetlenie wykresów
        plt.tight_layout()
        plt.show()
        
        
artists = ["Linkin Park", "Nirvana", "Dua lipa", "Szpaku", "kaz blagane", "the weeknd", "skolim", "taco Hemingway",
           "Modern talking", "Bambi", "Dżem", "Lady Pank", "Skillet", "Pitbull", "Flo rida", "Rihanna", "Britney Spears",
           "The Police", "Lady Gaga", "Scooter", "Hollywood Undead", "Sean Paul"]
token = get_auth_token()

#save_artist_data(token, artists)
df = get_artist_data()
#plot_artist(df, "Linkin Park")
plot_all_artists(df)
conn.close()