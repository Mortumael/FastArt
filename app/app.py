
# Подгружаем библиотеки!

from flask import Flask, render_template, request, jsonify
import sqlite3
import requests
from datetime import datetime

app = Flask(__name__)

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Таблица для кэширования акций
    c.execute('''CREATE TABLE IF NOT EXISTS promotions
                 (promoId INTEGER PRIMARY KEY, name TEXT)''')
    
    # Таблица для хранения результатов поиска
    c.execute('''CREATE TABLE IF NOT EXISTS search_results
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  articul INTEGER,
                  promo TEXT)''')
    
    conn.commit()
    conn.close()

# Получение списка акций из API Hoff
def get_promotions():
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
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJleHAiOjE3NTQ1ODU1MTIsImlzcyI6ImhvZmYucnUiLCJpYXQiOjE3NTQ1ODE5MTIsInN1YiI6Ik1PQkFQUCIsInR5cCI6IkJlYXJlciIsInNlcyI6InYzbWlvaXJrbGNvZWxobm91OXVhYTE1NmRzIiwicm9sZXMiOltdLCJjdXN0b21lciI6eyJpZCI6IjUwNDQxMmVhLTEzNzUtNDVmYy1hODYyLTM5ZmQ3NDllZjZlMCIsImZpbmdlcnByaW50IjoiYzIxZjk2OWI1ZjAzZDMzZDQzZTA0ZjhmMTM2ZTc2ODIifSwibW9iaWxlIjp7ImRldmljZUlkIjoiZGVmYXVsdCJ9LCJ1c2VyIjp7ImJpdHJpeElkIjoiMTkwMDcyMzMiLCJwaG9uZSI6Iis3ICg5MjYpIDg5Mi05MjM5IiwiZW1haWwiOiJyb21hbi51Y2h1dmF0a2luQGl0cWMucnUiLCJsb3lhbHR5Q2FyZCI6bnVsbCwibmFtZSI6Ilx1MDQyMFx1MDQzZVx1MDQzY1x1MDQzMFx1MDQzZCIsImxhc3ROYW1lIjoiXHUwNDIzXHUwNDQ3XHUwNDQzXHUwNDMyXHUwNDMwXHUwNDQyXHUwNDNhXHUwNDM4XHUwNDNkIiwic2Vjb25kTmFtZSI6Ilx1MDQxMlx1MDQ0Zlx1MDQ0N1x1MDQzNVx1MDQ0MVx1MDQzYlx1MDQzMFx1MDQzMlx1MDQzZVx1MDQzMlx1MDQzOFx1MDQ0NyJ9LCJob2ZmSWQiOiIrNyAoOTI2KSA4OTItOTIzOSJ9.AfqokvQeaxvLNLqq3CQieQkAoI6RGq7yHAuaKWbRA4Ff3Gt6riii524hF6v-9EAkFyAx_EZZnYFea_P-HGhVr00ocHOm_nFTrLf_Lot84H7DRm6nqq7Cvn3rCnYBuMt_CnE5s2KWTJdhlI1ZuNdovrNkGzv9cplN2pEUxUAjNVDj1rscz3d3wH4lPSYEHEJAI4rohbzAdKJw7NBktfGLj_KKTtV3k9x5z4f68HTYDQQzgsuX-hxNXC5DZh58114lYq2ff0qhc3NQuen6L5jCX0k_9gVNblhn39TIvqLsdSDm2Bf4VoFxeECdKL22FdI-C5V_m_n0HItBQhVvPNDv6Q'
    }
    
    try:
        print("Отправка запроса к API Hoff...")  # Отладочное сообщение
        response = requests.get(
            'https://apps.test-omni.hoff.ru/discount/v1/promo/2025',
            headers=headers
        )
        print(f"Статус ответа: {response.status_code}")  # Отладочное сообщение
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API: {e}")
        return None

def cache_promotions():
    print("Запуск cache_promotions()...")  # Отладочное сообщение
    promotions_data = get_promotions()
    
    if not promotions_data:
        print("Нет данных от API")  # Отладочное сообщение
        return []
    
    conn = None
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        print("Очистка старых данных...")  # Отладочное сообщение
        c.execute("DELETE FROM promotions")
        c.execute("DELETE FROM search_results")
        
        promotions = []
        articles = []
        
        promo_data = promotions_data.get('data', {}).get('promo', {})
        promo_id = promo_data.get('promoId')
        promo_name = promo_data.get('name')
        
        print(f"Обработка акции: ID={promo_id}, Name={promo_name}")  # Отладочное сообщение
        
        if promo_id and promo_name:
            # Сохраняем акцию
            print(f"Добавление акции в БД: {promo_name}")  # Отладочное сообщение
            c.execute("INSERT INTO promotions (promoId, name) VALUES (?, ?)", 
                     (promo_id, promo_name))
            promotions.append({'promoId': promo_id, 'name': promo_name})
            
            # Извлекаем товары
            groups = promo_data.get('group', [])
            print(f"Найдено групп товаров: {len(groups)}")  # Отладочное сообщение
            
            for group in groups:
                products = group.get('product', [])
                for product in products:
                    product_id = product.get('productId')
                    if product_id:
                        articles.append({
                            'articul': product_id,
                            'promo': promo_name
                        })
            
            print(f"Найдено товаров: {len(articles)}")  # Отладочное сообщение
            
            # Сохраняем товары
            for article in articles:
                c.execute("INSERT INTO search_results (articul, promo) VALUES (?, ?)",
                         (article['articul'], article['promo']))
            
            conn.commit()
            print("Данные успешно сохранены в БД")  # Отладочное сообщение
        else:
            print("Не удалось получить ID или название акции")  # Отладочное сообщение
        
        return promotions
        
    except sqlite3.Error as e:
        print(f"Ошибка SQLite: {e}")  # Отладочное сообщение
        return []
    finally:
        if conn:
            conn.close()

            
# Кэширование акций в БД
def cache_promotions():
    promotions_data = get_promotions()
    if not promotions_data:
        return []
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Очищаем старые данные
    c.execute("DELETE FROM promotions")
    
    # Сохраняем новые акции
    promotions = []
    
    # Обрабатываем ответ API
    # Предполагаем, что ответ содержит информацию об одной акции
    promo_id = promotions_data.get('promoId')  # или другой ключ, в зависимости от структуры ответа
    name = promotions_data.get('name')  # или другой ключ
    
    if promo_id and name:
        c.execute("INSERT INTO promotions (promoId, name) VALUES (?, ?)", 
                 (promo_id, name))
        promotions.append({'promoId': promo_id, 'name': name})
    
    conn.commit()
    conn.close()
    return promotions

# Поиск товаров по акции
def search_articles(promo_id, search_term):
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
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJleHAiOjE3NTA4NTIxMTIsImlzcyI6ImhvZmYucnUiLCJpYXQiOjE3NTA2ODAxMTIsInN1YiI6Ik1PQkFQUCIsInR5cCI6IkJlYXJlciIsInNlcyI6ImFqOTJ0bHZmc2p1Y2tvMmt2NnZjb2N2aGtnIiwicm9sZXMiOltdLCJjdXN0b21lciI6eyJpZCI6ImY3ODM2OTc3LTA0NGItNGI2Mi1hZWVkLWNlZmEzYWQ1NWFiMCIsImZpbmdlcnByaW50IjoiYzIxZjk2OWI1ZjAzZDMzZDQzZTA0ZjhmMTM2ZTc2ODIifSwiZ3Vlc3RpZCI6ImY3ODM2OTc3LTA0NGItNGI2Mi1hZWVkLWNlZmEzYWQ1NWFiMCIsIm1vYmlsZSI6eyJkZXZpY2VJZCI6ImRlZmF1bHQifSwidXNlciI6eyJiaXRyaXhJZCI6IjE5NjYxNDU1IiwicGhvbmUiOiIrNyAoOTAwKSAwMDAtMDAwMCIsImVtYWlsIjoiIiwibG95YWx0eUNhcmQiOiIxMTk5OTAwMDAwMDI1IiwibmFtZSI6Ilx1MDQxOFx1MDQzMlx1MDQzMFx1MDQzZCIsImxhc3ROYW1lIjoiXHUwNDE4XHUwNDMyXHUwNDMwXHUwNDNkXHUwNDNlXHUwNDMyIiwic2Vjb25kTmFtZSI6Ilx1MDQxOFx1MDQzMlx1MDQzMFx1MDQzZFx1MDQzZVx1MDQzMlx1MDQzOFx1MDQ0NyJ9LCJob2ZmSWQiOiIrNyAoOTAwKSAwMDAtMDAwMCJ9.fjzw6n-lOosY0Pwyt-iK0VvV4wyX4HYSc3dgFvqz0oZYcOQRM_URSOx5bikcBMJBbRxSGqJQNV_ofyI3f_OHAXr2lCJUF6h9ewQkI6ZZjvN1fYu_A2U3ZYQhHf3wWg-dnrHA4i0NSR7f-_7x8XPWAIR_U7O15RKd_ztqikIYLi7TLf6sfJIVwaoOXwfHmDzE6umccMIw0uYB1FwIOs7NqRmX-Ciq1a6Cys67z_v4GW_ohs-yFGseU5aIBb0yzxKozUmw13JY7MiBMPFe3YpxygisXufQ6ANTVFrXADWG4nEKL3PO49WFZhxUguD2li_ULpBO0YE2D0HMBGJsG0Ue1A'
    }
    
    data = {
        "filter": {
            "createAfterDT": "2023-01-01T00:00:00Z",
            "createBeforeDT": "2025-12-31T23:59:59Z",
            "startBeforeDT": "2025-12-31T23:59:59Z",
            "startAfterDT": "2023-01-01T00:00:00Z",
            "endBeforeDT": "3001-04-20T23:59:59Z",
            "endAfterDT": "2023-01-01T00:00:00Z",
            "promo": [{"promoId": str(promo_id)}],  # Используем выбранную акцию
            "name": search_term,  # Добавляем поисковый запрос
            "status": [{"status": "active"}]
        },
        "sort": {"by": "name", "order": "asc"},
        "offset": {"offset": 1, "pageSize": 100}  # Увеличим количество результатов
    }
    
    try:
        # Отправляем запрос к API
        response = requests.post(
            'http://apps.test-omni.hoff.ru/discount/v1/list',
            headers=headers,
            json=data
        )
        response.raise_for_status()  # Проверяем на ошибки
        
        # Обрабатываем результаты
        api_data = response.json()
        results = []
        
        # Проходим по всем акциям в ответе
        for promotion in api_data.get('promotions', []):
            # Проходим по всем товарам в акции
            for item in promotion.get('items', []):
                results.append({
                    'id': item.get('id'),
                    'articul': item.get('article'),  # Предполагаем, что артикул в поле article
                    'name': item.get('name'),
                    'promo': promo_id
                })
        
        # Сохраняем результаты в БД
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("DELETE FROM search_results")
        for result in results:
            c.execute("INSERT INTO search_results (articul, promo) VALUES (?, ?)",
                     (result['articul'], result['promo']))
        conn.commit()
        conn.close()
        
        return results
        
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API: {e}")
        return []

# Маршруты Flask
@app.route('/')
def index():
    # Получаем акции из кэша или API
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM promotions")
    promotions = [{'promoId': row[0], 'name': row[1]} for row in c.fetchall()]
    conn.close()
    
    if not promotions:
        promotions = cache_promotions()
    
    return render_template('index.html', promotions=promotions)

@app.route('/search', methods=['POST'])
def search():
    promo_id = request.form.get('promo')
    search_term = request.form.get('search_term')
    
    if not promo_id or not search_term:
        return jsonify({'error': 'Missing parameters'}), 400
    
    results = search_articles(promo_id, search_term)
    return jsonify(results)

@app.route('/results')
def results():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM search_results")
    results = [{'id': row[0], 'articul': row[1], 'promo': row[2]} for row in c.fetchall()]
    conn.close()
    
    return render_template('results.html', results=results)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)