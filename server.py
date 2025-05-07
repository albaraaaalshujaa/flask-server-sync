from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
DB_NAME = 'central.db'

def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT NOT NULL UNIQUE, password TEXT NOT NULL)")
        conn.commit()
        conn.close()

@app.route('/api/sync', methods=['POST'])
def sync():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"status": "error", "message": "Missing email or password"}), 400

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        return jsonify({"status": "success", "message": "User synced"})
    except sqlite3.IntegrityError:
        return jsonify({"status": "duplicate", "message": "User already exists"})
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)