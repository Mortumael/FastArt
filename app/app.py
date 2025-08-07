from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Базовый URL без конкретных методов
INTERNAL_API_BASE = "https://fastart-demo.loca.lt"

def fetch_promo_data(promo_id):
    url = f"{INTERNAL_API_BASE}/fetch_and_store/{promo_id}"
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {'error': str(e)}

def fetch_products():
    url = f"{INTERNAL_API_BASE}/products"
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {'error': str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    promo_id = request.form.get('promo_id')
    if not promo_id:
        return jsonify({'error': 'Promo ID is required'}), 400
    return jsonify(fetch_promo_data(promo_id))

@app.route('/products', methods=['GET'])
def products():
    return jsonify(fetch_products())

if __name__ == '__main__':
    app.run(debug=True)
