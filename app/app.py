from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory storage
users = [
    {'id': 1, 'name': 'Alice', 'age': 25},
    {'id': 2, 'name': 'Bob', 'age': 29},
    {'id': 3, 'name': 'Charlie', 'age': 20}
]

@app.route('/')
def home():
    return 'Hello, Flask App is running By Docker compose'

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users)

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()

    if not data or 'name' not in data or 'age' not in data:
        return jsonify({'error': 'name and age are required'}), 400

    new_user = {
        'id': users[-1]['id'] + 1 if users else 1,
        'name': data['name'],
        'age': data['age']
    }
    users.append(new_user)
    return jsonify(new_user), 201

@app.route('/users/<int:user_id>', methods=['POST'])
def update_user(user_id):
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user.update({k: data[k] for k in ('name', 'age') if k in data})
    return jsonify(user), 200

@app.route('/users/search', methods=['POST'])
def search_users():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No search criteria provided'}), 400

    results = users

    if 'name' in data:
        results = [u for u in results if data['name'].lower() in u['name'].lower()]
    if 'age' in data:
        results = [u for u in results if u['age'] == data['age']]

    return jsonify(results), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', use_reloader=True)