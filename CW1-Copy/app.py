import re
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from models import db, Product, Order  
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Update the MySQL URI with the correct details
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flask_user:flask_password@ecommerce-db:3306/flask_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with the Flask app
db.init_app(app)

@app.route('/')
def index():
    # Query products from the database
    products = Product.query.all()  # Get all products from the database
    return render_template('index.html', products=products)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    # Fetch the product by ID from the database
    product = Product.query.get(product_id)
    if product:
        cart = session.get('cart', [])
        cart.append({'id': product.id, 'name': product.name, 'price': product.price})
        session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    total_price = sum([item['price'] for item in cart])
    return render_template('cart.html', cart=cart, total_price=total_price)

@app.route('/clear_cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])  
def checkout():
    cart = session.get('cart', [])
    total_price = sum([item['price'] for item in cart])
    
    if request.method == 'POST':
        customer_name = request.form.get('name')
        customer_address = request.form.get('address')
        credit_card_number = request.form.get('credit_card_number')
        expiry_date = request.form.get('expiry_date')
        cvv = request.form.get('cvv')

        # Server-side validation for payment details
        if not customer_name or not customer_address:
            return "Name and Address are required", 400
        
        if not re.match(r'^\d{16}$', credit_card_number):
            return "Invalid credit card number. It must be 16 digits.", 400
        
        if not re.match(r'^(0[1-9]|1[0-2])\/\d{2}$', expiry_date):
            return "Invalid expiry date format. Use MM/YY.", 400
        
        if not re.match(r'^\d{3}$', cvv):
            return "Invalid CVV. It must be 3 digits.", 400
        
        # Save order to database
        order = Order(
            customer_name=customer_name,
            customer_address=customer_address,
            total_price=total_price,
            items=json.dumps(cart)  # Convert list to JSON string
        )
        db.session.add(order)
        db.session.commit()

        # Clear cart after successful checkout
        session.pop('cart', None)

        return render_template('order_confirmation.html', name=customer_name, address=customer_address, total_price=total_price)
    
    return render_template('checkout.html', cart=cart, total_price=total_price)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
