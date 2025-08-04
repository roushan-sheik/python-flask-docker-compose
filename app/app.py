from flask import Flask, jsonify, request
import mysql.connector
import os
from mysql.connector import Error

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'db',
    'database': 'application',
    'user': 'api',
    'password': 'api123'
}

def get_db_connection():
    """Get database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_database():
    """Initialize database with users table"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Create users table if it doesn't exist
            create_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                age INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_table_query)
            
            # Insert sample data if table is empty
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            
            if count == 0:
                sample_users = [
                    ('Alice', 25),
                    ('Bob', 29),
                    ('Charlie', 20)
                ]
                insert_query = "INSERT INTO users (name, age) VALUES (%s, %s)"
                cursor.executemany(insert_query, sample_users)
                connection.commit()
                print("Sample users inserted successfully")
            
            cursor.close()
            connection.close()
            print("Database initialized successfully")
            
        except Error as e:
            print(f"Error initializing database: {e}")
    else:
        print("Failed to connect to database")

@app.route('/')
def home():
    return jsonify({
        'message': 'Hello, Flask App is running with Docker Compose!',
        'endpoints': {
            'GET /users': 'Get all users',
            'GET /users/<id>': 'Get user by ID',
            'POST /users': 'Create new user',
            'PUT /users/<id>': 'Update user',
            'DELETE /users/<id>': 'Delete user'
        }
    })

@app.route('/users', methods=['GET'])
def get_users():
    """Get all users"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, name, age, created_at FROM users")
        users = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'data': users,
            'count': len(users)
        })
        
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, name, age, created_at FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if user:
            return jsonify({
                'success': True,
                'data': user
            })
        else:
            return jsonify({'error': 'User not found'}), 404
            
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/users', methods=['POST'])
def create_user():
    """Create new user"""
    if not request.json or 'name' not in request.json or 'age' not in request.json:
        return jsonify({'error': 'Missing required fields: name and age'}), 400
    
    name = request.json['name']
    age = request.json['age']
    
    if not isinstance(age, int) or age < 0:
        return jsonify({'error': 'Age must be a positive integer'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        insert_query = "INSERT INTO users (name, age) VALUES (%s, %s)"
        cursor.execute(insert_query, (name, age))
        connection.commit()
        
        user_id = cursor.lastrowid
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'data': {
                'id': user_id,
                'name': name,
                'age': age
            }
        }), 201
        
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user"""
    if not request.json:
        return jsonify({'error': 'No data provided'}), 400
    
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        # Check if user exists
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({'error': 'User not found'}), 404
        
        # Build update query dynamically
        update_fields = []
        values = []
        
        if 'name' in request.json:
            update_fields.append("name = %s")
            values.append(request.json['name'])
        
        if 'age' in request.json:
            if not isinstance(request.json['age'], int) or request.json['age'] < 0:
                return jsonify({'error': 'Age must be a positive integer'}), 400
            update_fields.append("age = %s")
            values.append(request.json['age'])
        
        if not update_fields:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        values.append(user_id)
        update_query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
        
        cursor.execute(update_query, values)
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'message': 'User updated successfully'
        })
        
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user"""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({'error': 'User not found'}), 404
        
        # Delete user
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'message': 'User deleted successfully'
        })
        
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    connection = get_db_connection()
    if connection:
        connection.close()
        return jsonify({
            'status': 'healthy',
            'database': 'connected'
        })
    else:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected'
        }), 500

if __name__ == '__main__':
    # Initialize database when app starts
    init_database()
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=True)