from flask import Flask, render_template, request, jsonify
import os
from database import init_db, get_balance, add_money, add_purchase, get_purchases,clear_purchases,reset_pot
app = Flask(__name__)

# Initialize database on startup
with app.app_context():
    init_db()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/balance', methods=['GET'])
def balance():
    bal = get_balance()
    return jsonify({"balance": bal})


@app.route('/api/add_money', methods=['POST'])
def deposit():
    data = request.get_json()
    amount = data.get('amount')

    if not amount or amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400

    add_money(amount)
    return jsonify({"message": "Money added!", "balance": get_balance()})


@app.route('/api/add_purchase', methods=['POST'])
def purchase():
    data = request.get_json()
    item = data.get('item')
    amount = data.get('amount')
    bought_by = data.get('bought_by')

    if not item or not amount or not bought_by:
        return jsonify({"error": "All fields required"}), 400

    if amount <= 0:
        return jsonify({"error": "Amount must be positive"}), 400

    if get_balance() < amount:
        return jsonify({"error": "Not enough money in pot!"}), 400

    add_purchase(item, amount, bought_by)
    return jsonify({"message": "Purchase added!", "balance": get_balance()})


@app.route('/api/purchases', methods=['GET'])
def purchases():
    history = get_purchases()
    return jsonify(history)

@app.route('/api/clear_history', methods=['DELETE'])
def clear_history():
    clear_purchases()
    return jsonify({"message": "Purchase history cleared!"})
    
@app.route('/api/reset_balance', methods=['PUT'])
def reset_balance():
    reset_pot()
    return jsonify({"message": "Balance reset!", "balance": 0})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)