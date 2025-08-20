from random import random
import threading
import psycopg2
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import sys
from concurrent.futures import ThreadPoolExecutor
import random, time
import json
import requests
from requests.adapters import HTTPAdapter, Retry


def get_total():
    url = "https://www.listesdemots.net/touslesmots.htm"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    pagenumbers = soup.find_all(class_="pg")
    return int(pagenumbers[-1].text)

def collect_words(i):
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
    return listePage

session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))

def safe_get(url):
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Erreur sur {url}: {e}")
        return None

def collect_definitions(word):
    #print("\nlooking for the definition of " + word + ".")
    #print(cursor.fetchall())

    url = "https://www.larousse.fr/dictionnaires/francais/" + word + "/"
    response = safe_get(url)
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

#cursor.execute("DROP TABLE IF EXISTS dictionnaire")        # This line reset the database

cursor.execute("""
    CREATE TABLE IF NOT EXISTS dictionnaire(
    id SERIAL PRIMARY KEY,
    word TEXT,
    definition JSONB
    )
""")

conn.commit()

def multithread_get_words(cores):
    total = get_total()
    start_time = time.time()  # début du timer
    page_numbers = list(range(1, total + 1))
    def process_page(i):
        words = collect_words(i)
        for word in words:
            cursor.execute("INSERT INTO dictionnaire (word) VALUES (%s)", (word,))
        return len(words)

    with ThreadPoolExecutor(max_workers= cores) as executor: #Creation of a pool of #cores Threads
        for i, result in enumerate(executor.map(process_page, page_numbers), 1):
            progress_bar(i, total, start_time)

    conn.commit()
    print("\n✅ Terminé !")

_progress = 0
_progress_lock = threading.Lock()

def _progress_updater(total, refresh_interval=0.1):
    """Thread qui met à jour la barre de progression en temps réel."""
    start_time = time.time()
    while True:
        with _progress_lock:
            current = _progress
        progress_bar(current, total, start_time)
        if current >= total:
            break
        time.sleep(refresh_interval)
    # dernière mise à jour pour s'assurer que la barre est à 100%
    progress_bar(total, total, start_time)
    print("\n✅ Terminé !")


def multithread_definitions(cores, total_length):
    global _progress
    _process = 0
    cursor.execute("SELECT * FROM dictionnaire;")
    start_time = time.time()  # début du timer
    rows = cursor.fetchall()

    def process_row(row):
        local_cursor = conn.cursor()
        word_def = collect_definitions(row[1])
        local_cursor.execute("UPDATE dictionnaire SET definition = %s WHERE id = %s", (json.dumps(word_def), row[0]))
        conn.commit()
        local_cursor.close()
        with _progress_lock:
            global _progress
            _progress += 1
        return (json.dumps(word_def), row[0])

    progress_thread = threading.Thread(target=_progress_updater, args=(total_length,))
    progress_thread.start()
    time.sleep(random.uniform(0.2, 1.0))
    with ThreadPoolExecutor(max_workers=cores) as executor:
        list(executor.map(process_row, rows))
    conn.commit()

#multithread_get_words(100)

cursor.execute("SELECT COUNT(*) FROM dictionnaire;")
total_length = cursor.fetchone()[0]

print(total_length)

multithread_definitions(100, total_length)
conn.close()

#collect_definitions()

