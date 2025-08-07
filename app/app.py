# app.py (для Render)
from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__, template_folder='templates', static_folder='static')

# сюда поставить публичный адрес твоего localtunnel (или адрес internal_api, если развернёшь в облаке)
INTERNAL_API_BASE = os.environ.get('INTERNAL_API_BASE', 'https://fastart-demo.loca.lt')

REQUEST_TIMEOUT = 20

def call_internal(path):
    url = INTERNAL_API_BASE.rstrip('/') + path
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT, verify=False)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {'error': str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/promos', methods=['GET'])
def promos():
    res = call_internal('/promos')
    return jsonify(res)

@app.route('/search', methods=['POST'])
def search():
    promo_id = request.form.get('promo_id')
    if not promo_id:
        return jsonify({'error': 'Promo ID is required'}), 400
    res = call_internal(f'/fetch_and_store/{promo_id}')
    return jsonify(res)

@app.route('/products', methods=['GET'])
def products():
    res = call_internal('/products')
    return jsonify(res)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
