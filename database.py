"""SQLite user storage for Lab 5. sqlite3 is included with Python."""
import os
import sqlite3
from contextlib import closing
from pathlib import Path

DATABASE = os.environ.get('LAB5_DATABASE', str(Path(__file__).with_name('database.db')))
FIELDS = ('name', 'email', 'phone', 'address', 'country')

def connect_to_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_db_table():
    with closing(connect_to_db()) as conn, conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY NOT NULL,
            name TEXT NOT NULL, email TEXT NOT NULL, phone TEXT NOT NULL,
            address TEXT NOT NULL, country TEXT NOT NULL
        )''')

def insert_user(user):
    with closing(connect_to_db()) as conn, conn:
        cur = conn.execute('INSERT INTO users (name,email,phone,address,country) VALUES (?,?,?,?,?)',
                           tuple(user[field] for field in FIELDS))
        row = conn.execute('SELECT * FROM users WHERE user_id=?', (cur.lastrowid,)).fetchone()
        return dict(row)

def get_users():
    with closing(connect_to_db()) as conn:
        return [dict(row) for row in conn.execute('SELECT * FROM users ORDER BY user_id')]

def get_user_by_id(user_id):
    with closing(connect_to_db()) as conn:
        row = conn.execute('SELECT * FROM users WHERE user_id=?', (user_id,)).fetchone()
        return dict(row) if row else None

def update_user(user):
    with closing(connect_to_db()) as conn, conn:
        cur = conn.execute('UPDATE users SET name=?,email=?,phone=?,address=?,country=? WHERE user_id=?',
                           tuple(user[field] for field in FIELDS) + (user['user_id'],))
        if not cur.rowcount:
            return None
        return dict(conn.execute('SELECT * FROM users WHERE user_id=?', (user['user_id'],)).fetchone())

def delete_user(user_id):
    with closing(connect_to_db()) as conn, conn:
        return conn.execute('DELETE FROM users WHERE user_id=?', (user_id,)).rowcount > 0

if __name__ == '__main__':
    create_db_table()
    print('User table created successfully')
