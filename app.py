from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)


def init_db():
    with sqlite3.connect('users.db') as conn:
        # Create table if not exists
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE,
                        age INTEGER NOT NULL
                    );''')
        
        # Insert default records if the table is empty
        cursor = conn.cursor()
        cursor.execute('''SELECT COUNT(*) FROM users''')
        count = cursor.fetchone()[0]
        
        if count == 0:  # Only insert default records if no records exist
            default_users = [
                ("John Doe", "john@example.com", 30),
                ("Jane Smith", "jane@example.com", 25),
                ("Alice Johnson", "alice@example.com", 28),
                ("Bob Brown", "bob@example.com", 35)
            ]
            cursor.executemany('''INSERT INTO users (name, email, age) VALUES (?, ?, ?)''', default_users)
            conn.commit()


@app.route('/api/create-user', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data['name']
    email = data['email']
    age = data['age']
    
    try:
        with sqlite3.connect('users.db') as conn:
            conn.execute('''INSERT INTO users (name, email, age) VALUES (?, ?, ?)''', (name, email, age))
            conn.commit()
        return jsonify({"message": "User created successfully!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 400


@app.route('/api/get-all-users', methods=['GET'])
def get_all_users():
    with sqlite3.connect('users.db') as conn:
        users = conn.execute('''SELECT * FROM users''').fetchall()
        users_list = [{"id": user[0], "name": user[1], "email": user[2], "age": user[3]} for user in users]
    return jsonify(users_list)


@app.route('/api/user/<int:id>', methods=['GET'])
def get_user(id):
    with sqlite3.connect('users.db') as conn:
        user = conn.execute('''SELECT * FROM users WHERE id = ?''', (id,)).fetchone()
        if user:
            return jsonify({"id": user[0], "name": user[1], "email": user[2], "age": user[3]})
        return jsonify({"error": "User not found"}), 404


@app.route('/api/user/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    age = data.get('age')
    
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM users WHERE id = ?''', (id,))
        user = cursor.fetchone()
        
        if user:
            if name:
                cursor.execute('''UPDATE users SET name = ? WHERE id = ?''', (name, id))
            if email:
                cursor.execute('''UPDATE users SET email = ? WHERE id = ?''', (email, id))
            if age:
                cursor.execute('''UPDATE users SET age = ? WHERE id = ?''', (age, id))
            conn.commit()
            return jsonify({"message": "User updated successfully!"})
        else:
            return jsonify({"error": "User not found"}), 404


@app.route('/api/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM users WHERE id = ?''', (id,))
        user = cursor.fetchone()
        
        if user:
            cursor.execute('''DELETE FROM users WHERE id = ?''', (id,))
            conn.commit()
            return jsonify({"message": "User deleted successfully!"})
        else:
            return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    init_db() 
    app.run(debug=True)
