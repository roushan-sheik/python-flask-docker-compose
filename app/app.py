from flask import Flask, jsonify, request
import re

app = Flask(__name__)

# In-memory storage
users = [
    {'id': 1, 'name': 'Alice', 'age': 25},
    {'id': 2, 'name': 'Bob', 'age': 29},
    {'id': 3, 'name': 'Charlie', 'age': 20}
]

# ── Constants ──────────────────────────────────────────
MAX_NAME_LENGTH = 50
MIN_AGE = 0
MAX_AGE = 150
NAME_PATTERN = re.compile(r"^[A-Za-z\s\-']+$")


# ── Helpers ────────────────────────────────────────────
def validate_user_input(data: dict) -> tuple[bool, str]:
    """Validate and sanitize user input to prevent injection attacks."""
    if 'name' in data:
        name = data.get('name')
        if not isinstance(name, str):
            return False, 'Name must be a string'
        if len(name) > MAX_NAME_LENGTH:
            return False, f'Name must not exceed {MAX_NAME_LENGTH} characters'
        if not NAME_PATTERN.match(name):
            return False, 'Name contains invalid characters'

    if 'age' in data:
        age = data.get('age')
        if not isinstance(age, int) or isinstance(age, bool):
            return False, 'Age must be an integer'
        if not (MIN_AGE <= age <= MAX_AGE):
            return False, f'Age must be between {MIN_AGE} and {MAX_AGE}'

    return True, ''


def sanitize_string(value: str) -> str:
    """Strip and escape potentially dangerous characters."""
    return value.strip()


def get_next_id() -> int:
    return max((u['id'] for u in users), default=0) + 1


def find_user(user_id: int):
    return next((u for u in users if u['id'] == user_id), None)


# ── Routes ─────────────────────────────────────────────
@app.route('/')
def home():
    return 'Hello, Flask App is running By Docker Compose'


@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users), 200


@app.route('/users', methods=['POST'])
def create_user():
    # Prevent content-type bypass
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 415

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid or empty JSON body'}), 400

    # Require fields
    if 'name' not in data or 'age' not in data:
        return jsonify({'error': 'name and age are required'}), 400

    # Whitelist — reject unknown fields
    allowed_fields = {'name', 'age'}
    if not set(data.keys()).issubset(allowed_fields):
        return jsonify({'error': 'Unexpected fields in request'}), 400

    valid, msg = validate_user_input(data)
    if not valid:
        return jsonify({'error': msg}), 422

    new_user = {
        'id': get_next_id(),
        'name': sanitize_string(data['name']),
        'age': data['age']
    }
    users.append(new_user)
    return jsonify(new_user), 201


@app.route('/users/<int:user_id>', methods=['POST'])
def update_user(user_id):
    # user_id is typed as int by Flask — no string injection possible
    if user_id <= 0:
        return jsonify({'error': 'Invalid user ID'}), 400

    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 415

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid or empty JSON body'}), 400

    # Whitelist
    allowed_fields = {'name', 'age'}
    if not set(data.keys()).issubset(allowed_fields):
        return jsonify({'error': 'Unexpected fields in request'}), 400

    valid, msg = validate_user_input(data)
    if not valid:
        return jsonify({'error': msg}), 422

    user = find_user(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if 'name' in data:
        user['name'] = sanitize_string(data['name'])
    if 'age' in data:
        user['age'] = data['age']

    return jsonify(user), 200


@app.route('/users/search', methods=['POST'])
def search_users():
    if not request.is_json:
        return jsonify({'error': 'Content-Type must be application/json'}), 415

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid or empty JSON body'}), 400

    # Whitelist
    allowed_fields = {'name', 'age'}
    if not set(data.keys()).issubset(allowed_fields):
        return jsonify({'error': 'Unexpected fields in request'}), 400

    valid, msg = validate_user_input(data)
    if not valid:
        return jsonify({'error': msg}), 422

    results = users

    if 'name' in data:
        # Safe: plain string comparison, no eval/exec/query
        needle = sanitize_string(data['name']).lower()
        results = [u for u in results if needle in u['name'].lower()]

    if 'age' in data:
        results = [u for u in results if u['age'] == data['age']]

    return jsonify(results), 200


# ── Error handlers ─────────────────────────────────────
@app.errorhandler(400)
def bad_request(e):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', use_reloader=True)