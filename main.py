#import threading

#from flask import redirect
from flask.cli import load_dotenv
#from pyngrok import ngrok
import uvicorn
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
#from flask import Flask, render_template, request, jsonify
import os
import psycopg2 #This is the import for postgreSQL
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles
from dotenv import load_dotenv

# This is all necessary to launch the app.
# The app.mount is usefull for using all the elements in static files. In other words, usefull for using js file ect.

STATIC_DIR = Path("/Users/thibaultvanni/PycharmProjects/testingWebsite/static")
TEMPLATES_DIR = Path("/Users/thibaultvanni/PycharmProjects/testingWebsite/templates")


app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


def updateDB(hostname, ip_adress):
    """
    Updating the Database of all the users that visited the website
    :param hostname:
    :param ip_adress:
    :return: Updated DB
    """
    load_dotenv()

    conn = psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("POSTGRES_PORT", 5432)),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        dbname=os.environ["DB_NAME"]
    )
    cur = conn.cursor()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS visitorJournal (
        visitorNumber SERIAL PRIMARY KEY,
        ip VARCHAR(255) NOT NULL)
    """)

    cur.execute("INSERT INTO visitorJournal (ip) VALUES (%s)", (str(ip_adress),))

    cur.execute("SELECT * FROM visitorJournal WHERE ip = (%s)", (str(ip_adress),))

    result = cur.fetchall()

    if len(result) == 1:
        phrase = "Hello " + hostname +". Welcome on this incredible journey in the coding world"
    if len(result) > 1:
        phrase = "Welcome back " + hostname + ". Happy to see you again."

    conn.commit()
    conn.close()
    return(phrase, ip_adress)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    client_ip = request.client.host
    name = "TEST Name"
    updateDB(name, client_ip)
    return templates.TemplateResponse(
        "homepage.html", {"request": request, "ip": client_ip}
    )

@app.get("/waitingroom")
async def waitingroom(request: Request):
    return templates.TemplateResponse("waitingroom.html", {"request": request})

@app.get("/tusmo")
async def tusmo(request: Request):
    return templates.TemplateResponse("tusmo.html", {"request": request})

@app.get("/stats")
async def statisticsssfssdd(request: Request):
    return templates.TemplateResponse("stats.html", {"request": request})



#def start_ngrok():
#    print(f"🌍 Public URL: https://bear-smiling-gladly.ngrok-free.app")

if __name__ == "__main__":
#    threading.Thread(target=start_ngrok).start()
    # Lancer FastAPI
    uvicorn.run(app, host="localhost", port=8000)