from random import random

import psycopg2
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import sys
from concurrent.futures import ThreadPoolExecutor
import time
import json

def get_total():
    url = "https://www.listesdemots.net/touslesmots.htm"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    pagenumbers = soup.find_all(class_="pg")
    return int(pagenumbers[-1].text)

def collect_words():
    total = get_total()
    start_time = time.time()  # début du timer

    for i in range(1, total+1):
        if i == 1:
            url = "https://www.listesdemots.net/touslesmots.htm"
        else:
            url = "https://www.listesdemots.net/touslesmotspage" + str(i) + ".htm"

        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.find_all(class_="mt")
        listePage = []
        for item in items:
            listePage = item.text.split(" ")

        inserted_count = 0

        for elements in listePage:
            cursor.execute("INSERT INTO dictionnaire (word) VALUES (%s)", (elements,))
            inserted_count += 1

        progress_bar(i, total, start_time)

    conn.commit()
    print("\n✅ Terminé !")

def collect_definitions(word):
    #print("\nlooking for the definition of " + word + ".")
    #print(cursor.fetchall())

    url = "https://www.larousse.fr/dictionnaires/francais/" + word + "/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.find(class_="Definitions")

    informations = {"definitions": [], "synonymes": []}
    if items:
        ### Looking for all synonyms
        itemsSyn = items.find_all(class_="Synonymes")
        for synonym in itemsSyn:
            #print(f"{synonym} elements is {itemsSyn[synonym].text}")
            informations["synonymes"].append(synonym.text)

        ### Looking for all definitions (not taking the last if it's a synonym)
        itemsDef = items.find_all(class_="DivisionDefinition")
        for definitions in itemsDef:
            #print(f"{definitions.text}")
            if "Synonyme" not in definitions.text:
                informations["definitions"].append(definitions.text.replace("\xa0", " "))
    return informations


def progress_bar(i, tot, start_time):
    # --- Progress bar ---
    percentage = i / tot
    #print(f"\r Percentage : {percentage}%")
    bar_length = 140
    filled_length = int(bar_length * percentage)
    elapsed = int(time.time() - start_time)
    bar = "#" * filled_length + "-" * (bar_length - filled_length)
    sys.stdout.write(f"\rProgression : |{bar}| {int(percentage * 100)}% depuis {elapsed}s.")
    sys.stdout.flush()
    # --------------------


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

cursor.execute("DROP TABLE IF EXISTS dictionnaire")        # This line reset the database

cursor.execute("""
    CREATE TABLE IF NOT EXISTS dictionnaire(
    id SERIAL PRIMARY KEY,
    word TEXT,
    definition JSONB
    )
""")

conn.commit()

collect_words()

cursor.execute("SELECT COUNT(*) FROM dictionnaire;")
total_length = cursor.fetchone()[0]

print(total_length)



def multithread_definitions(cores, total_length):
    cursor.execute("SELECT * FROM dictionnaire;")
    start_time = time.time()  # début du timer
    rows = cursor.fetchall()
    def process_row(row):
        word_def = collect_definitions(row[1])
        return (json.dumps(word_def), row[0])

    with ThreadPoolExecutor(max_workers= cores) as executor: #Creation of a pool of #cores Threads
        for i, result in enumerate(executor.map(process_row, rows), 1): #repartition des mots sur les threads. Chaque thread exécute process_row sur un mot différent.
            cursor.execute("UPDATE dictionnaire SET definition = %s WHERE id = %s", result)
            progress_bar(i, total_length, start_time)
        time.sleep(random.random([i for i in range(1, 5)]))
    conn.commit()

multithread_definitions(100, total_length)


conn.close()

#collect_definitions()

