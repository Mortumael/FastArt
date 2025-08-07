
app = Flask(__name__)

INTERNAL_API = 'internal_api_url = f'https://fastart-demo.loca.lt/fetch_and_store/{promo_id}''
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
@@ -14,22 +33,11 @@ def search():
    promo_id = request.form.get('promo_id')
    if not promo_id:
        return jsonify({'error': 'Promo ID is required'}), 400

    try:
        response = requests.get(f'{INTERNAL_API}/fetch_and_store/{promo_id}', verify=False)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify(fetch_promo_data(promo_id))

@app.route('/products', methods=['GET'])
def products():
    try:
        response = requests.get(f'{INTERNAL_API}/products', verify=False)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify(fetch_products())

if __name__ == '__main__':
    app.run(debug=True)