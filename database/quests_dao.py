import os
import sqlite3
from database import reservation_dao, session_dao, users_dao

LIMITS={"Warrior": 4,  "Mage":3, "Healer":2}
DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Per pythonanywhere
BASE_DIR=os.path.dirname(os.path.abspath(__file__))
DB_PATH=os.path.join(BASE_DIR, "Konosuba.db")

def create_quest(title, duration, type, difficulty, description, illustration):
    conn=sqlite3.connect(DB_PATH)
    cursor=conn.cursor()
    query="INSERT INTO quests (title, duration, type, difficulty, description, illustration) VALUES (?,?,?,?,?,?)"
    cursor.execute(query, (title, duration, type, difficulty, description, illustration))
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
    query="""
        SELECT q.* FROM quests q
        LEFT JOIN sessions s ON q.id = s.quest_id
        GROUP BY q.id
        ORDER BY MIN(s.day*1440 + s.hour*60 + s.minute) ASC"""
    cursor.execute(query)
    all_quest=cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return all_quest

def get_filtered_quest(day, type, difficulty, role):
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    filtered_quests=[]
    for quest in get_all_quest():
        if type and quest['type']!=type:
            continue
        if difficulty and quest['difficulty']!=difficulty:
            continue
        if day is not None:
            query="SELECT * FROM sessions WHERE quest_id=? AND day=?"
            cursor.execute(query, (quest["id"], day))
            sessions_to_check=cursor.fetchall()
        else:
            query="SELECT * FROM sessions WHERE quest_id=?"
            cursor.execute(query, (quest["id"],))
            sessions_to_check=cursor.fetchall()
        if not sessions_to_check:
            continue
        if role:
            has_available_session=False
            for session in sessions_to_check:
                query="SELECT SUM(total_people) AS totale FROM reservations WHERE session_id=? AND role=?"
                cursor.execute(query, (session["id"], role))
                result=cursor.fetchone()
                count=result['totale'] if (result and result['totale'] is not None) else 0
                if count<LIMITS[role]:
                    has_available_session=True
                    break
            if not has_available_session:
                continue
        filtered_quests.append(quest)
    conn.commit()
    cursor.close()
    conn.close()
    return filtered_quests

def get_all_info_of_all_quests():
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    quests=[dict(row) for row in get_all_quest()]
    for quest in quests:
        quest["sessions"]=[]
        sessions=[dict(session) for session in session_dao.get_sessions_of_quest(quest["id"])]
        for session in sessions:
            session["day"]=DAYS_OF_WEEK[session["day"]]
            session["adventurers"]=[]
            reservations=reservation_dao.get_reservations_for_session(session["id"])
            total_booked=0
            role_counts={"Warrior": 0, "Mage": 0, "Healer": 0}
            for reservation in reservations:
                user=users_dao.get_user_by_id(reservation["user_id"])
                session["adventurers"].append({
                    "username":user["username"],"name":user["name"], "surname":user["surname"], "role":reservation["role"],
                    "companions":[comp_row['username'] for comp_row in reservation_dao.get_companions_for_reservation(reservation["id"])]})
                total_booked+=reservation["total_people"]
                role_counts[reservation["role"]]+=reservation["total_people"]
            session["total_booked"]=total_booked
            for role in LIMITS:
                session[role]=LIMITS[role]-role_counts[role]
                # AGGIUNERE MOST REQUEST ROLe
            quest["sessions"].append(session)
    conn.commit()
    cursor.close()
    conn.close()
    return quests