from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return 'Hello, Flask App is running By Docker compose'

@app.route('/users')
def get_users():
    users = [
        {'id': 1, 'name': 'Alice', 'age':25},
        {'id': 2, 'name': 'Bob', 'age':29},
        {'id': 3, 'name': 'Charlie', 'age':20}
    ]
    return jsonify(users)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',  use_reloader=True)
