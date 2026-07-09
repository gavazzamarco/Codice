import os
import sqlite3

# Per pythonanywhere
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_PATH=os.path.join(BASE_DIR, "Konosuba.db")

def create_reservation(user_id, session_id, role, total_people):
    conn=sqlite3.connect(DB_PATH)
    cursor=conn.cursor()
    query="INSERT INTO reservations (user_id, session_id, role, total_people) VALUES (?,?,?,?)"
    cursor.execute(query, (user_id, session_id, role, total_people))
    id=cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return id

def get_reservations_for_session(session_id):
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    query="SELECT * FROM reservations WHERE session_id=?"
    cursor.execute(query, (session_id,))
    reservations=cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return reservations

def get_reservations_of_user(user_id):
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    query="SELECT * FROM reservations WHERE user_id=?"
    cursor.execute(query, (user_id,))
    reservations=cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return reservations

def add_companions(reservation_id, username):
    conn=sqlite3.connect(DB_PATH)
    cursor=conn.cursor()
    query="INSERT INTO companions (reservation_id, username) VALUES (?,?)"
    cursor.execute(query, (reservation_id, username))
    conn.commit()
    cursor.close()
    conn.close()