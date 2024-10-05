from flask import Flask, jsonify, render_template 
from database import get_user_data, get_all_users  # Import necessary functions

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/<int:user_id>', methods=['GET'])
def user_data(user_id):
    user_data = get_user_data(user_id)
    if user_data:
        return jsonify({
            'user_id': user_data[0],
            'balance': user_data[1],
            'upi': user_data[2],
            'referrals': user_data[3],
            'is_subscribed': user_data[4],
            'joining_time': user_data[5],
            'online_status': user_data[6]
        })
    else:
        return jsonify(None)

@app.route('/users', methods=['GET'])
def all_users():
    users = get_all_users()
    return jsonify(users)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
