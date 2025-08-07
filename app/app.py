# app.py
from flask import Flask, render_template
import requests

app = Flask(__name__)
INTERNAL_API_BASE = "https://fastart-demo.loca.lt"  # или твой URL к internal_api

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
