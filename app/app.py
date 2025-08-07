from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

INTERNAL_API = 'http://localhost:8080'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    promo_id = request.form.get('promo_id')
    if not promo_id:
        return jsonify({'error': 'Promo ID is required'}), 400

    try:
        response = requests.get(f'{INTERNAL_API}/fetch_and_store/{promo_id}', verify=False)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/products', methods=['GET'])
def products():
    try:
        response = requests.get(f'{INTERNAL_API}/products', verify=False)
        response.raise_for_status()
        return jsonify(response.json())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
