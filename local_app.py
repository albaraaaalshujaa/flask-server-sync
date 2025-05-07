import sqlite3
import requests
import os

LOCAL_DB = "local.db"
REMOTE_SYNC_UPLOAD = "https://flask-server-sync.onrender.com/api/sync"
REMOTE_SYNC_DOWNLOAD = "https://flask-server-sync.onrender.com/api/download"

def init_local_db():
    if not os.path.exists(LOCAL_DB):
        conn = sqlite3.connect(LOCAL_DB)
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password TEXT)")
        conn.commit()
        conn.close()

def sync_from_server():
    try:
        res = requests.get(REMOTE_SYNC_DOWNLOAD)
        if res.status_code == 200:
            users = res.json().get("users", [])
            conn = sqlite3.connect(LOCAL_DB)
            c = conn.cursor()
            for user in users:
                c.execute("INSERT OR IGNORE INTO users (email, password) VALUES (?, ?)", (user['email'], user['password']))
            conn.commit()
            conn.close()
            print(f"✅ Synchronized {len(users)} user(s) from the server.")
        else:
            print("⚠️ Failed to sync from server.")
    except Exception as e:
        print("⚠️ Error connecting to server:", e)

def sync_to_server(email, password):
    try:
        res = requests.post(REMOTE_SYNC_UPLOAD, json={"email": email, "password": password})
        print("🌐 Synced to server:", res.json().get("message"))
    except Exception as e:
        print("⚠️ Failed to sync to server:", e)

def register():
    email = input("Enter email: ")
    password = input("Enter password: ")

    conn = sqlite3.connect(LOCAL_DB)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        print("✅ Registered locally.")
        sync_to_server(email, password)
    except sqlite3.IntegrityError:
        print("❌ This email is already registered.")
    conn.close()

def login():
    email = input("Enter email: ")
    password = input("Enter password: ")

    conn = sqlite3.connect(LOCAL_DB)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = c.fetchone()
    conn.close()

    if user:
        print("✅ Login successful.")
    else:
        print("❌ Invalid email or password.")

if __name__ == "__main__":
    init_local_db()
    sync_from_server()
    while True:
        print("\n1. Login")
        print("2. Register")
        print("3. Exit")
        choice = input("Select an option: ")

        if choice == "1":
            login()
        elif choice == "2":
            register()
        elif choice == "3":
            break
        else:
            print("❌ Invalid choice.")
