from flask import Flask, jsonify, request, render_template, redirect, url_for, make_response, session
from pymongo import MongoClient
import bcrypt
import uuid
from bson import ObjectId
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],  # Разрешить запросы от React-приложения
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
app.secret_key = 'your_secret_key'

client = MongoClient('mongodb://localhost:27017/')
db = client['ecommerce_db']
users_collection = db['users']
products_collection = db['products']

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)
@app.route('/setup_test_data')
def setup_test_data():
    products_collection.delete_many({})
    
 
    test_products = [
    {
        "name": "Predator Gaming Laptop",
        "description": "High performance gaming laptop with RGB keyboard",
        "price": 1299.99,
        "category": "electronics",
        "stock": 10,
        "image_url": "https://th.bing.com/th/id/R.c3cd4911a07125516be51b24a64e8be5?rik=0Y%2ffxPZezlI2Jw&pid=ImgRaw&r=0"
    },
    {
        "name": "iPhone 15",
        "description": "Latest model with high-res camera",
        "price": 799.99,
        "category": "electronics",
        "stock": 15,
        "image_url": "https://th.bing.com/th/id/OIP.Ghsb6CTDu5V1e6M0C5pxAwHaHa?rs=1&pid=ImgDetMain"
    },
    {
        "name": "Nike Running Shoes",
        "description": "Comfortable athletic shoes for running",
        "price": 89.99,
        "category": "sports",
        "stock": 20,
        "image_url": "https://m.media-amazon.com/images/I/71oUxUS0q9L._AC_UL1500_.jpg"
    },
    {
        "name": "Yoga Mat",
        "description": "Non-slip exercise yoga mat",
        "price": 29.99,
        "category": "sports",
        "stock": 30,
        "image_url": "https://th.bing.com/th/id/OIP.C4MWif4v7eIHCXywEzg45wAAAA?w=240&h=240&rs=1&pid=ImgDetMain"
    },
    {
        "name": "Coffee Maker",
        "description": "Automatic coffee maker with timer",
        "price": 49.99,
        "category": "home",
        "stock": 8,
        "image_url": "https://th.bing.com/th/id/OIP.v7ORILVh4Fl0C88CzQDN9QHaHa?rs=1&pid=ImgDetMain"
    },
    {
        "name": "Desk Lamp",
        "description": "LED desk lamp with adjustable brightness",
        "price": 34.99,
        "category": "home",
        "stock": 15,
        "image_url": "https://i5.walmartimages.com/asr/c9bba4aa-da0f-47fb-a567-587fffb0eebe_1.54d35c0a2193493f2f3b6161282a87cf.jpeg"
    },
    {
        "name": "Xiaomi Backpack",
        "description": "Waterproof laptop backpack",
        "price": 39.99,
        "category": "accessories",
        "stock": 25,
        "image_url": "https://th.bing.com/th/id/OIP.zSdmtnurQMAq64REptPq3QHaHa?rs=1&pid=ImgDetMain"
    },
    {
        "name": "AquaFina Water Bottle",
        "description": "Insulated stainless steel bottle",
        "price": 24.99,
        "category": "accessories",
        "stock": 40,
        "image_url": "https://th.bing.com/th/id/OIP.kPO_4gK2ANR_uEhPsRWORAHaHa?rs=1&pid=ImgDetMain"
    },
    {
        "name": "Samsung Wireless Earbuds",
        "description": "Bluetooth earbuds with noise cancellation",
        "price": 159.99,
        "category": "electronics",
        "stock": 12,
        "image_url": "https://th.bing.com/th/id/OIP.QVrIEkcjncEeXqcuNGqFKwHaHa?rs=1&pid=ImgDetMain"
    },
    {
        "name": "Huawei Smart Watch",
        "description": "Fitness tracking smartwatch",
        "price": 199.99,
        "category": "electronics",
        "stock": 18,
        "image_url": "https://th.bing.com/th/id/OIP.umTGTxijZaEW4jLpz8rFWwHaJA?rs=1&pid=ImgDetMain"
    }
]

    

    products_collection.insert_many(test_products)
    
    return "Test products added successfully! <a href='/'>Go to homepage</a>"
@app.route('/register', methods=['POST'])
def register():
    if not request.is_json:  # Проверка, что данные в формате JSON
        return jsonify({'error': 'Content-Type must be application/json'}), 400

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    if users_collection.find_one({'email': email}):
        return jsonify({'error': 'Email already exists'}), 400

    hashed_password = hash_password(password)
    user = {
        'email': email,
        'password': hashed_password,
        'session_token': str(uuid.uuid4()),
        'cart': []
    }
    users_collection.insert_one(user)

    return jsonify({'message': 'Registration successful'}), 201

@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 400

    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = users_collection.find_one({'email': email})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        print('succes')
        session_token = str(uuid.uuid4())
        users_collection.update_one(
            {'_id': user['_id']},
            {'$set': {'session_token': session_token}}
        )

        response = make_response(jsonify({'message': 'Login successful'}))
        response.set_cookie(
            'session_token', session_token, 
            httponly=True, samesite='Lax'  # 🛠️ Возможно, нужно `SameSite=None; Secure`
        )
        return response

    return jsonify({'error': 'Invalid credentials'}), 401
@app.route('/check-auth', methods=['GET'])
def check_auth():
    session_token = request.cookies.get('session_token')
    if session_token and users_collection.find_one({'session_token': session_token}):
        return jsonify({'authenticated': True}), 200
    return jsonify({'authenticated': False}), 401

@app.route('/')
def index():
    session_token = request.cookies.get('session_token')
    if not session_token:
        return redirect(url_for('login'))

    user = users_collection.find_one({'session_token': session_token})
    if not user:
        return redirect(url_for('login'))


    recommended_products = get_recommendations(user['_id'])
    recommended_product_ids = [p['_id'] for p in recommended_products]

    category = request.args.get('category')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)

    query = {}
    

    if category:
        query['category'] = category
    if min_price is not None:
        query['price'] = {'$gte': min_price}
    if max_price is not None:
        if 'price' in query:
            query['price']['$lte'] = max_price
        else:
            query['price'] = {'$lte': max_price}

    products = list(products_collection.find(query))


    for product in products:
        product['_id'] = str(product['_id'])
    for recommended_product in recommended_products:
        recommended_product['_id'] = str(recommended_product['_id'])

    categories = products_collection.distinct('category')

    return render_template(
        'index.html',
        products=products,
        recommended_products=recommended_products,
        categories=categories,
        user=user
    )



@app.route('/logout')
def logout():
    session_token = request.cookies.get('session_token')
    if session_token:
        users_collection.update_one(
            {'session_token': session_token},
            {'$set': {'session_token': None}}
        )
    
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('session_token')
    return response

@app.route('/products', methods=['GET', 'POST'])
def manage_products():
    if request.method == 'POST':
        new_product = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'price': float(request.form.get('price')),
            'category': request.form.get('category'),
            'stock': int(request.form.get('stock', 0)),
            'img': request.form.get('img')  # Добавляем URL картинки
        }
        products_collection.insert_one(new_product)
        return redirect(url_for('index'))
    
    products = list(products_collection.find({}, {"_id": 1, "name": 1, "price": 1, "category": 1, "img": 1}))
    
    for product in products:
        product['_id'] = str(product['_id'])  # Преобразуем ObjectId в строку

    categories = list(products_collection.distinct("category"))  # Получаем уникальные категории
    recommended_products = products[:3]  # Пример рекомендованных товаров

    return jsonify({
        "products": products,
        "recommended_products": recommended_products,
        "categories": categories
    })



@app.route('/product/<product_id>')
def product_detail(product_id):
    product = products_collection.find_one({'_id': ObjectId(product_id)})
    if product:
        product['_id'] = str(product['_id'])
        return render_template('product.html', product=product)
    return redirect(url_for('index'))


@app.route('/cart', methods=['GET'])
def view_cart():
    session_token = request.cookies.get('session_token')
    if not session_token:
        return redirect(url_for('login'))
    
    user = users_collection.find_one({'session_token': session_token})
    if not user:
        return redirect(url_for('login'))

    cart_items = []
    total = 0
    for item in user.get('cart', []):
        product = products_collection.find_one({'_id': item['product_id']})
        if product:
            product['_id'] = str(product['_id'])
            product['quantity'] = item['quantity']
            product['subtotal'] = item['quantity'] * product['price']
            total += product['subtotal']
            cart_items.append(product)

    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    session_token = request.cookies.get('session_token')
    if not session_token:
        return redirect(url_for('login'))

    user = users_collection.find_one({'session_token': session_token})
    if not user:
        return redirect(url_for('login'))

    product_id = request.form.get('product_id')
    quantity = int(request.form.get('quantity', 1))

    # Find the product and check its stock level
    product = products_collection.find_one({'_id': ObjectId(product_id)})
    if product['stock'] < quantity:
        return jsonify({'error': 'Not enough stock available'}), 400  # Or render a message on the template

    # Proceed to add to cart
    existing_item = next((item for item in user.get('cart', []) if str(item['product_id']) == product_id), None)

    if existing_item:
        users_collection.update_one(
            {'_id': user['_id'], 'cart.product_id': ObjectId(product_id)},
            {'$inc': {'cart.$.quantity': quantity}}
        )
    else:
        users_collection.update_one(
            {'_id': user['_id']},
            {'$push': {'cart': {'product_id': ObjectId(product_id), 'quantity': quantity}}}
        )

    # Decrease stock in the products collection
    products_collection.update_one(
        {'_id': ObjectId(product_id)},
        {'$inc': {'stock': -quantity}}
    )

    success_message = "Item added to your cart!"
    products = products_collection.find()

    recommended_products = get_recommendations(user['_id'])

    products = list(products_collection.find({
        '_id': {'$nin': [p['_id'] for p in recommended_products]}
    }))

    for product in products:
        product['_id'] = str(product['_id'])

    for recommended_product in recommended_products:
        recommended_product['_id'] = str(recommended_product['_id'])
    
    return render_template('index.html', products=products, recommended_products=recommended_products, success_message=success_message)

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    session_token = request.cookies.get('session_token')
    if not session_token:
        return redirect(url_for('login'))

    user = users_collection.find_one({'session_token': session_token})
    if not user:
        return redirect(url_for('login'))

    product_id = request.form.get('product_id')

    # Check if product_id is valid
    if product_id and len(product_id) == 24:
        existing_item = next((item for item in user.get('cart', []) if str(item['product_id']) == product_id), None)

        if existing_item:
            quantity_to_restore = existing_item['quantity'] if existing_item['quantity'] <= 1 else 1

            # Case 1: Reduce quantity in cart if greater than 1
            if existing_item['quantity'] > 1:
                users_collection.update_one(
                    {'_id': user['_id'], 'cart.product_id': ObjectId(product_id)},
                    {'$inc': {'cart.$.quantity': -1}}
                )
            else:
                # Case 2: Remove item from cart if quantity is 1
                users_collection.update_one(
                    {'_id': user['_id']},
                    {'$pull': {'cart': {'product_id': ObjectId(product_id)}}}
                )

            # Restore stock in products collection by the quantity removed from cart
            products_collection.update_one(
                {'_id': ObjectId(product_id)},
                {'$inc': {'stock': quantity_to_restore}}
            )

    return redirect(url_for('view_cart'))




@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    session_token = request.cookies.get('session_token')
    if not session_token:
        return redirect(url_for('login'))

    user = users_collection.find_one({'session_token': session_token})
    if not user:
        return redirect(url_for('login'))

    # Clear the user's cart
    users_collection.update_one(
        {'_id': user['_id']},
        {'$set': {'cart': []}}  
    )

    return redirect(url_for('view_cart'))  
from datetime import datetime

@app.route('/purchase', methods=['POST'])
def purchase():
    session_token = request.cookies.get('session_token')
    if not session_token:
        return redirect(url_for('login'))

    user = users_collection.find_one({'session_token': session_token})
    if not user:
        return redirect(url_for('login'))

    
    cart = user.get('cart', [])

    if not cart:
        return redirect(url_for('view_cart'))  

    
    for item in cart:
        product_id = item['product_id']
        quantity = item['quantity']

      
        users_collection.update_one(
            {'_id': user['_id']},
            {
                '$push': {
                    'purchase_history': {
                        'product_id': ObjectId(product_id),
                        'quantity': quantity,
                        'purchase_date': datetime.utcnow()
                    }
                },
                '$pull': {
                    'cart': {'product_id': ObjectId(product_id)}  
                }
            }
        )

    return redirect(url_for('view_cart'))  
@app.route('/purchase_history')
def purchase_history():
    session_token = request.cookies.get('session_token')
    if not session_token:
        return redirect(url_for('login'))

    user = users_collection.find_one({'session_token': session_token})
    if not user:
        return redirect(url_for('login'))


    purchases = user.get('purchase_history', [])
    
    for purchase in purchases:
        purchase['product_id'] = str(purchase['product_id'])

    products = list(products_collection.find())
    for product in products:
        product['_id'] = str(product['_id'])
    


    return render_template('purchase_history.html', purchases=purchases, products=products)
def get_recommendations(user_id, max_recommendations=5):
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    if not user or 'purchase_history' not in user:
        return []

    recommended_products = []

    for purchase in user['purchase_history']:
        product = products_collection.find_one({'_id': purchase['product_id']})
        if product:
            category = product['category']
            similar_products = list(products_collection.find({'category': category, '_id': {'$ne': purchase['product_id']}}).limit(max_recommendations))
            recommended_products.extend(similar_products)

    unique_recommendations = {str(p['_id']): p for p in recommended_products}.values()
    return list(unique_recommendations)[:max_recommendations]

@app.route('/search', methods=['GET'])
def search_products():
    query = request.args.get('query')
    if not query:
        return redirect(url_for('index'))  

    products = products_collection.find({
        '$or': [
            {'name': {'$regex': query, '$options': 'i'}},  
            {'category': {'$regex': query, '$options': 'i'}} 
        ]
    })

    products = list(products) 


    return render_template('index.html', products=products)

if __name__ == '__main__':
    app.run(debug=True)