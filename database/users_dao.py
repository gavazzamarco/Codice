import os
import sqlite3

# Per pythonanywhere
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_PATH=os.path.join(BASE_DIR, "Konosuba.db")

def get_user_by_id(user_id):
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    query="SELECT * FROM users WHERE users.id=?"
    cursor.execute(query, (user_id,))
    db_user=cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return db_user

def create_user(name, surname, username, password, role, profile_img, bio):
    conn=sqlite3.connect(DB_PATH)
    cursor=conn.cursor()
    query="INSERT INTO users (name, surname, username, password, role, profile_img, bio) VALUES (?,?,?,?,?,?,?)"
    cursor.execute(query, (name, surname, username, password, role, profile_img, bio))
    conn.commit()
    cursor.close()
    conn.close()

def get_user_by_username(username):
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    query="SELECT * FROM users WHERE users.username=?"
    cursor.execute(query, (username,))
    db_user=cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return db_user

def get_master():
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    query="SELECT * FROM users WHERE users.role='master'"
    cursor.execute(query)
    db_user=cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return db_user

def get_all_users_for_role(role):
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    query="SELECT * FROM users WHERE role=?"
    cursor.execute(query, (role,))
    db_users=cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return db_users