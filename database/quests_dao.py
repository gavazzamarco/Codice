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
    conn.commit()
    cursor.close()
    conn.close()