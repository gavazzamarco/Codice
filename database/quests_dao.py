import os
import sqlite3

# Per pythonanywhere
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_PATH=os.path.join(BASE_DIR, "Konosuba.db")

def create_quest(title, duration, location, type, difficulty, description, illustration):
    conn=sqlite3.connect(DB_PATH)
    cursor=conn.cursor()
    query="INSERT INTO quests (title, duration, location, type, difficulty, description, illustration) VALUES (?,?,?,?,?,?,?)"
    cursor.execute(query, (title, duration, location, type, difficulty, description, illustration))
    id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return id

def create_session(quest_id, day, hour, minute):
    conn=sqlite3.connect(DB_PATH)
    cursor=conn.cursor()
    query="INSERT INTO sessions (quest_id, day, hour, minute) VALUES (?,?,?,?)"
    cursor.execute(query, (quest_id, day, hour, minute))
    conn.commit()
    cursor.close()
    conn.close()

def get_quest_by_id(id):
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    query = "SELECT * FROM quests WHERE id=?"
    cursor.execute(query, (id,))
    quest=cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return quest

def get_all_session():
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    query = "SELECT * FROM sessions"
    cursor.execute(query)
    all_session=cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return all_session