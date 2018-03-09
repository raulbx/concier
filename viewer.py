from flask import Flask, request
import requests
import psycopg2
import sys
import os

app = Flask(__name__)

@app.route("/showtable", methods=['GET', 'POST'])
def showtable():
	DATABASE_URL = os.environ['DATABASE_URL']
	con = None
	con = psycopg2.connect(DATABASE_URL, sslmode='require')
	cur = con.cursor()
	cur = db.execute('SELECT * FROM Products')
    entries = cur.fetchall()
    return render_template('viewer.html', entries=entries)
