import sqlite3
from database import quests_dao, session_dao

DB_PATH="database/Konosuba.db"

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

def get_companions_for_reservation(reservation_id):
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    query="SELECT * FROM companions WHERE reservation_id=?"
    cursor.execute(query, (reservation_id,))
    reservations=cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return reservations

def get_detailed_adventurer_quests(user_id):
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    query="""SELECT DISTINCT q.id FROM quests q
        JOIN sessions s ON q.id=s.quest_id JOIN reservations r ON s.id=r.session_id
        WHERE r.user_id=?"""
    cursor.execute(query, (user_id,))
    adventurer_quests=[]
    for quest_id in [row["id"] for row in cursor.fetchall()]:
        quest=dict(quests_dao.get_quest_by_id(quest_id))
        quest["sessions"]=[]
        sessions=session_dao.get_sessions_of_quest(quest_id)
        for session in sessions:
            reservation=get_reservation_by_session_for_user(user_id, session["id"])
            if reservation:
                companions=[companion["username"] for companion in get_companions_for_reservation(reservation["id"])]
                quest["sessions"].append({ "session_id":session["id"], "location":session["location"], "day":session["day"], "hour":session["hour"],
                    "minute":session["minute"], "role":reservation["role"], "total_people":reservation["total_people"], "companions":companions })
        adventurer_quests.append(quest)
    conn.commit()
    cursor.close()
    conn.close()    
    return adventurer_quests

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
    query="DELETE FROM reservations WHERE id=?"
    cursor.execute(query, (reservation_id,))
    query="DELETE FROM companions WHERE reservation_id=?"
    cursor.execute(query, (reservation_id,))
    conn.commit()
    cursor.close()
    conn.close()