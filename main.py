#import threading
#from pyngrok import ngrok
import uvicorn
from fastapi import *
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
#from flask import Flask, render_template, request, jsonify
import os
#import psycopg2 #This is the import for postgreSQL
from starlette.staticfiles import StaticFiles

import psycopg2

print("psycopg2 loaded successfully")

# This is all necessary to launch the app.
# The app.mount is usefull for using all the elements in static files. In other words, usefull for using js file ect.

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def updateDB(hostname, ip_adress):
    """
    Updating the Database of all the users that visited the website
    :param hostname:
    :param ip_adress:
    :return: Updated DB
    """
    DATABASE_URL = "postgresql://admin:9Nunf4zluOKitXz6OCpwmsLJW3K0feaG@dpg-d2fq9p7diees73co83cg-a.frankfurt-postgres.render.com/visitorjournal"

    conn = psycopg2.connect(DATABASE_URL, sslmode='require')  # Render requires SSL

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


#def start_ngrok():
#    public_url = ngrok.connect(8000, bind_tls=True)
#    print(f"🌍 Public URL: {public_url}")

if __name__ == "__main__":
 #   threading.Thread(target=start_ngrok).start()
    # Lancer FastAPI
    uvicorn.run(app, host="0.0.0.0", port=8000)