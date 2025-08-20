import psycopg2
from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
import sys
from tqdm import tqdm
import time
import json
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

DB_CONFIG = {
    "host": os.environ["DB_HOST"],
    "port": int(os.environ.get("POSTGRES_PORT", 5432)),
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
    "dbname": os.environ["DB_NAME"]
}

# --- Connexion unique ---
conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS dictionnaire")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS dictionnaire(
        id SERIAL PRIMARY KEY,
        word TEXT,
        definition JSONB
    )
""")
conn.commit()

# --- Progress bar ---
def progress_bar(i, tot, start_time):
    percentage = i / tot
    bar_length = 100
    filled_length = int(bar_length * percentage)
    elapsed = int(time.time() - start_time)
    bar = "#" * filled_length + "-" * (bar_length - filled_length)
    sys.stdout.write(f"\rProgression : |{bar}| {int(percentage * 100)}% depuis {elapsed}s.")
    sys.stdout.flush()

# --- Collecte des mots ---
def collect_words(total_pages=40):
    session = requests.Session()
    all_words = []

    start_time = time.time()

    for i in range(1, total_pages + 1):
        url = f"https://www.listesdemots.net/touslesmots.htm" if i == 1 else f"https://www.listesdemots.net/touslesmotspage{i}.htm"
        response = session.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        items = soup.find_all(class_="mt")

        for item in items:
            words = item.text.split(" ")
            all_words.extend(words)

        progress_bar(i, total_pages, start_time)

    # Insertion en batch
    batch_size = 1000
    for j in range(0, len(all_words), batch_size):
        batch = all_words[j:j+batch_size]
        args_str = ",".join(cursor.mogrify("(%s)", (word,)).decode("utf-8") for word in batch)
        cursor.execute("INSERT INTO dictionnaire (word) VALUES " + args_str)
    conn.commit()
    print("\n✅ Terminé !")

# --- Collecte des définitions ---
def collect_definitions(word):
    url = f"https://www.larousse.fr/dictionnaires/francais/{word}/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.find(class_="Definitions")

    informations = {"definitions": [], "synonymes": []}
    if items:
        for synonym in items.find_all(class_="Synonymes"):
            informations["synonymes"].append(synonym.text)
        for definition in items.find_all(class_="DivisionDefinition"):
            if "Synonyme" not in definition.text:
                informations["definitions"].append(definition.text.replace("\xa0", " "))
    return informations

# --- Update définitions en parallèle ---
def update_definitions_parallel(max_workers=8):
    cursor.execute("SELECT id, word FROM dictionnaire")
    rows = cursor.fetchall()
    total_length = len(rows)
    start_time = time.time()

    def process_row(row):
        word_def = collect_definitions(row[1])
        return (json.dumps(word_def), row[0])

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i, result in enumerate(executor.map(process_row, rows), 1):
            cursor.execute("UPDATE dictionnaire SET definition = %s WHERE id = %s", result)
            progress_bar(i, total_length, start_time)
    conn.commit()
    print("\n✅ Définitions mises à jour !")

# --- Execution ---
collect_words()
update_definitions_parallel()
conn.close()