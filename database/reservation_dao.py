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

def get_detailed_adventurer_quests(user_id):
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    query="""
        SELECT 
            q.id AS quest_id, q.title, q.location, q.type, q.difficulty, q.duration, q.description, q.illustration,
            s.id AS session_id, s.day, s.hour, s.minute,
            r.id AS reservation_id, r.role, r.total_people
        FROM reservations r
        JOIN sessions s ON r.session_id = s.id
        JOIN quests q ON s.quest_id = q.id
        WHERE r.user_id = ?"""
    cursor.execute(query, (user_id,))
    rows=cursor.fetchall()
    quests_dict={}
    for row in rows:
        query="SELECT username FROM companions WHERE reservation_id = ?"
        cursor.execute(query, (row['reservation_id'],))
        companions=[c_row['username'] for c_row in cursor.fetchall()]
        quest_id=row['quest_id']
        if quest_id not in quests_dict:
            quests_dict[quest_id]={
                'id':row['quest_id'],
                'title':row['title'],
                'location': row['location'],
                'type':row['type'],
                'difficulty': row['difficulty'],
                'duration':row['duration'],
                'description':row['description'],
                'illustration':row['illustration'],
                'sessions':[]
            } 
        quests_dict[quest_id]['sessions'].append({
            'session_id': row['session_id'],
            'day':row['day'],
            'hour':row['hour'],
            'minute': row['minute'],
            'role':row['role'],
            'total_people':row['total_people'],
            'companions':companions
        })
    cursor.close()
    conn.close()
    return list(quests_dict.values())

def get_reservation_by_session_for_user(user_id, session_id):
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    query="SELECT * FROM reservations WHERE user_id=? and session_id=?"
    cursor.execute(query, (user_id, session_id))
    reservation=cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return reservation

def delete_reservation(reservation_id):
    conn=sqlite3.connect(DB_PATH)
    cursor=conn.cursor()
    query="DELETE FROM companions WHERE reservation_id=?"
    cursor.execute(query, (reservation_id,))
    query="DELETE FROM reservations WHERE id=?"
    cursor.execute(query, (reservation_id,))
    conn.commit()
    cursor.close()
    conn.close()