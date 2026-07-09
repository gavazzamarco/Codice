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
    id=cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return id

def get_quest_by_id(id):
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    query="SELECT * FROM quests WHERE id=?"
    cursor.execute(query, (id,))
    quest=cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return quest

def get_all_quest():
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    query="SELECT * FROM quests"
    cursor.execute(query)
    all_quest=cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return all_quest

def get_filtered_quest(day, type, difficulty, role):
    # Da modificare per tenere traccia di role
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    if day is not None:
        query="SELECT DISTINCT quest_id FROM sessions WHERE day=?"
        cursor.execute(query, (day,))
        quests_id=cursor.fetchall()
        filtered_day_quests=[]
        for row in quests_id:
            filtered_day_quests.append(get_quest_by_id(row["quest_id"]))
    else:
        query="SELECT * FROM quests"
        cursor.execute(query)
        filtered_day_quests=cursor.fetchall()
    filtered_quests=[]
    for quest in filtered_day_quests:
        if type and quest['type']!=type:
            continue
        if difficulty and quest['difficulty']!=difficulty:
            continue    
        filtered_quests.append(quest)
    conn.commit()
    cursor.close()
    conn.close()
    return filtered_quests