import os
import sqlite3

# Per pythonanywhere
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_PATH=os.path.join(BASE_DIR, "Konosuba.db")

def create_session(quest_id, day, hour, minute):
    conn=sqlite3.connect(DB_PATH)
    cursor=conn.cursor()
    query="INSERT INTO sessions (quest_id, day, hour, minute) VALUES (?,?,?,?)"
    cursor.execute(query, (quest_id, day, hour, minute))
    conn.commit()
    cursor.close()
    conn.close()

def get_all_session():
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    query="SELECT * FROM sessions"
    cursor.execute(query)
    all_session=cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return all_session

def get_session_of_quest(quest_id):
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    query="SELECT * FROM sessions WHERE quest_id=?"
    cursor.execute(query, (quest_id,))
    sessions=cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return sessions

def get_session_by_id(session_id):
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    query="SELECT * FROM sessions WHERE id=?"
    cursor.execute(query, (session_id,))
    session=cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return session