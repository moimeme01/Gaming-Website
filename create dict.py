import psycopg2
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import sys
from tqdm import tqdm
import time


load_dotenv()
# Connect to your PostgreSQL database
conn = psycopg2.connect(
    host=os.environ["DB_HOST"],
    port=int(os.environ.get("POSTGRES_PORT", 5432)),
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    dbname=os.environ["DB_NAME"]
)

cursor = conn.cursor()

# Read SQL file
cursor.execute("DROP TABLE IF EXISTS dictionnaire")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS dictionnaire(
    id SERIAL PRIMARY KEY,
    word TEXT,
    definition TEXT
    )
""")

url = "https://www.listesdemots.net/touslesmots.htm"

# Send GET request
response = requests.get(url)

def collect_words():
    total = 1549
    start_time = time.time()  # début du timer

    for i in range(1, 1549):
        if i == 1:
            url = "https://www.listesdemots.net/touslesmots.htm"
        else:
            url = "https://www.listesdemots.net/touslesmotspage" + str(i) + ".htm"

        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.find_all(class_="mt")
        listePage = []
        for item in items:
            listePage = (item.text.split(" "))

        inserted_count = 0

        for elements in listePage:
            cursor.execute("INSERT INTO dictionnaire (word) VALUES (%s)", (elements,))
            inserted_count += 1

            # Affichage d’un palier
            if inserted_count % 100000 == 0:
                elapsed = int(time.time() - start_time)
                print(f"\n✅ Palier atteint : {inserted_count} mots insérés ",
                      f"(temps écoulé = {elapsed}s)")

            # --- Progress bar ---
        percentage = i / total
        bar_length = 100
        filled_length = int(bar_length * percentage)
        bar = "#" * filled_length + "-" * (bar_length - filled_length)
        sys.stdout.write(f"\rProgression : |{bar}| {int(percentage * 100)}%")
        sys.stdout.flush()
        # --------------------

    conn.commit()
    conn.close()
    print("\n✅ Terminé !")

collect_words()

conn = psycopg2.connect(
    host=os.environ["DB_HOST"],
    port=int(os.environ.get("POSTGRES_PORT", 5432)),
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    dbname=os.environ["DB_NAME"]
)

cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM dictionnaire;")
row_count = cursor.fetchone()[0]

print(f"\nThe table has {row_count} rows.")


def collect_definitions():
    cursor.execute("SELECT * FROM dictionnaire")
    #print("running")
    #print(cursor.fetchall())
    for row in cursor:
        word = str(row[1])
        print(word)
        url = "https://www.larousse.fr/dictionnaires/francais/" + word + "/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

#print(collect_definitions())
