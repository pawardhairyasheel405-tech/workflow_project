import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("instance/workflow.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        filename TEXT,
        uploaded_by INTEGER,
        status TEXT DEFAULT 'Pending',
        current_role TEXT,
        FOREIGN KEY(uploaded_by) REFERENCES users(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id INTEGER,
        user_id INTEGER,
        comment TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(document_id) REFERENCES documents(id),
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)
DATABASE = "workflow.db"

def get_connection():
    return sqlite3.connect(DATABASE, check_same_thread=False)


def save_comment(role, comment):
    conn = get_connection()
    cur = conn.cursor()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        INSERT INTO comments (role, comment, timestamp)
        VALUES (?, ?, ?)
    """, (role, comment, timestamp))

    conn.commit()
    conn.close()

    return True
    





if __name__ == "__main__":
    init_db()
    print("Database initialized.")
