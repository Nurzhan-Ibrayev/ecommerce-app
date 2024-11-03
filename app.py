from flask import Flask, jsonify, request, render_template, redirect, url_for, make_response, session
from pymongo import MongoClient
import bcrypt
import uuid
from bson import ObjectId

app = Flask(__name__)
app.secret_key = 'your_secret_key'

client = MongoClient('mongodb://localhost:27017/')
db = client['ecommerce_db']
users_collection = db['users']
products_collection = db['products']

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)

@app.route('/api/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if users_collection.find_one({'email': email}):
            return jsonify({'error': 'Email already exists'}), 400
        
        user = {
            'email': email,
            'password': hash_password(password),
            'session_token': str(uuid.uuid4()),
            'cart': []
        }
        users_collection.insert_one(user)
        
        response = make_response(redirect(url_for('login')))
        return response
        
    return render_template('register.html')

@app.route('/api/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = users_collection.find_one({'email': email})
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session_token = str(uuid.uuid4())
            users_collection.update_one(
                {'_id': user['_id']},
                {'$set': {'session_token': session_token}}
            )
            
            response = make_response(redirect(url_for('index')))
            response.set_cookie('session_token', session_token)
            return response
            
        return jsonify({'error': 'Invalid credentials'}), 401
        
    return render_template('login.html')

@app.route('/')
def index():
    session_token = request.cookies.get('session_token')
    if not session_token:
        return redirect(url_for('login'))
    
    products = list(products_collection.find())
    for product in products:
        product['_id'] = str(product['_id'])
    
    user = users_collection.find_one({'session_token': session_token})
    return render_template('index.html', products=products, user=user)

@app.route('/api/logout')
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

# Product management routes
@app.route('/api/products', methods=['GET', 'POST'])
def manage_products():
    if request.method == 'POST':
        new_product = {
            'name': request.form.get('name'),
            'description': request.form.get('description'),
            'price': float(request.form.get('price')),
            'category': request.form.get('category'),
            'stock': int(request.form.get('stock', 0))
        }
        products_collection.insert_one(new_product)
        return redirect(url_for('index'))
    
    products = list(products_collection.find())
    return jsonify(products)

@app.route('/product/<product_id>')
def product_detail(product_id):
    product = products_collection.find_one({'_id': ObjectId(product_id)})
    if product:
        product['_id'] = str(product['_id'])
        return render_template('product.html', product=product)
    return redirect(url_for('index'))

# Cart management (updated with session handling)
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

    # Check if the product is already in the user's cart
    existing_item = next((item for item in user.get('cart', []) if str(item['product_id']) == product_id), None)

    if existing_item:
        # If the product already exists in the cart, update the quantity
        users_collection.update_one(
            {'_id': user['_id'], 'cart.product_id': ObjectId(product_id)},
            {'$inc': {'cart.$.quantity': quantity}}
        )
    else:
        # If the product is not in the cart, add it
        users_collection.update_one(
            {'_id': user['_id']},
            {'$push': {'cart': {'product_id': ObjectId(product_id), 'quantity': quantity}}}
        )

    return redirect(url_for('index'))  # Redirect back to the product listing

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    session_token = request.cookies.get('session_token')
    if not session_token:
        return redirect(url_for('login'))

    user = users_collection.find_one({'session_token': session_token})
    if not user:
        return redirect(url_for('login'))

    product_id = request.form.get('product_id')

    # Check if product_id is valid before trying to remove
    if product_id and len(product_id) == 24:
        # Remove the product from the user's cart by matching the product_id
        result = users_collection.update_one(
            {'_id': user['_id']},
            {'$pull': {'cart': {'product_id': ObjectId(product_id)}}}
        )

        # Check if any documents were modified
        if result.modified_count == 0:
            print("No product was removed, please check the product_id.")

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
        {'$set': {'cart': []}}  # Set the cart to an empty list
    )

    return redirect(url_for('view_cart'))  # Redirect back to the cart view
from datetime import datetime

@app.route('/purchase', methods=['POST'])
def purchase():
    session_token = request.cookies.get('session_token')
    if not session_token:
        return redirect(url_for('login'))

    user = users_collection.find_one({'session_token': session_token})
    if not user:
        return redirect(url_for('login'))

    # Get the cart items
    cart = user.get('cart', [])

    if not cart:
        return redirect(url_for('view_cart'))  # Redirect if cart is empty

    # Process each item in the cart
    for item in cart:
        product_id = item['product_id']
        quantity = item['quantity']

        # Add to purchase history
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
                    'cart': {'product_id': ObjectId(product_id)}  # Remove item from cart
                }
            }
        )

    return redirect(url_for('view_cart'))  # Redirect back to cart
@app.route('/purchase_history')
def purchase_history():
    session_token = request.cookies.get('session_token')
    if not session_token:
        return redirect(url_for('login'))

    user = users_collection.find_one({'session_token': session_token})
    if not user:
        return redirect(url_for('login'))

    # Get purchase history from the user document
    purchases = user.get('purchase_history', [])
    
    # Fetch all products to display their names
    products = list(products_collection.find())
    
    # Convert ObjectId to string for better usability in templates
    for product in products:
        product['_id'] = str(product['_id'])

    return render_template('purchase_history.html', purchases=purchases, products=products)


if __name__ == '__main__':
    app.run(debug=True)