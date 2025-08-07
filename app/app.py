from flask import Flask, render_template, request, jsonify
import sqlite3
import requests
import os

app = Flask(__name__)

# Инициализация БД
def init_db():
    db_exists = os.path.exists('database.db')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Проверяем существование таблицы
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='products'
    """)
    table_exists = cursor.fetchone()
    
    if not table_exists:
        cursor.execute('''
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                productId TEXT NOT NULL,
                promoId INTEGER NOT NULL,
                name TEXT NOT NULL
            )
        ''')
        print("Таблица 'products' создана")
    else:
        print("Таблица 'products' уже существует")
    
    conn.commit()
    conn.close()

# Вызываем инициализацию БД при старте
init_db()

# Функция для получения данных об акции
def fetch_promo_data(promo_id):
    url = f'https://apps.test-omni.hoff.ru/discount/v1/promo/{promo_id}'
    headers = {
        'Hoff-Business-Unit-Id': '799',
        'Content-Type': 'application/json',
        'traceparent': '00-26ece1a526f49cb7b45654d8253ccbc6-2ef0c451a304a1e5-01',
        'Hoff-UserType': 'legal',
        'Hoff-UserId': '19561435',
        'Hoff-GuestId': 'b64890e8-86d5-4a1a-90c6-633fc9bddb49',
        'Hoff-DeliveryZoneId': '5637179076',
        'Hoff-BusinessUnitId': '799',
        'Accept-Charset': 'UTF-8',
        'Authorization': 'Bearer'
    }

    # Прокси через VPN
    proxies = {
        'http': 'https://f33224e08083.ngrok-free.app',
        'https': 'https://f33224e08083.ngrok-free.app'
    }

    try:
        response = requests.get(url, headers=headers, proxies=proxies, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching promo data: {e}")
        return None

# Сохранение товаров в БД
def save_products_to_db(products):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Очищаем старые данные перед добавлением новых
    cursor.execute('DELETE FROM products')
    
    for product in products:
        cursor.execute('''
            INSERT INTO products (productId, promoId, name)
            VALUES (?, ?, ?)
        ''', (product['productId'], product['promoId'], product['name']))
    
    conn.commit()
    conn.close()

# Получение товаров из БД
def get_products_from_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, productId, promoId, name FROM products')
    products = cursor.fetchall()
    conn.close()
    
    return [{
        'id': row[0],
        'productId': row[1],
        'promoId': row[2],
        'name': row[3]
    } for row in products]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    promo_id = request.form.get('promo_id')
    if not promo_id:
        return jsonify({'error': 'Promo ID is required'}), 400
    
    promo_data = fetch_promo_data(promo_id)
    if not promo_data or 'data' not in promo_data:
        return jsonify({'error': 'Failed to fetch promo data'}), 500
    
    promo_info = promo_data['data']['promo']
    products = []
    
    # Извлекаем товары из групп
    for group in promo_info.get('group', []):
        for product in group.get('product', []):
            products.append({
                'productId': product['productId'],
                'promoId': promo_info['promoId'],
                'name': promo_info['name']
            })
    
    # Сохраняем товары в БД
    save_products_to_db(products)
    
    return jsonify({
        'success': True,
        'count': len(products)
    })

@app.route('/products', methods=['GET'])
def get_products():
    products = get_products_from_db()
    return jsonify(products)

if __name__ == '__main__':
    app.run(debug=True)
