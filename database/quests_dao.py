import sqlite3
from database import reservation_dao, session_dao, users_dao

LIMITS={"Warrior": 4,  "Mage":3, "Healer":2}
DAYS_OF_WEEK=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DB_PATH="database/Konosuba.db"

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
    query="""SELECT q.* FROM quests q
        LEFT JOIN sessions s ON q.id=s.quest_id
        GROUP BY q.id
        ORDER BY IFNULL(MIN(s.day*1440+s.hour*60+s.minute), 99999) ASC"""
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
        if (day is not None) or role:
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
                if has_available_session==False:
                    continue
        filtered_quests.append(quest)
    conn.commit()
    cursor.close()
    conn.close()
    return filtered_quests

def get_all_info_of_all_quests():
    quests=[dict(row) for row in get_all_quest()]
    for quest in quests:
        quest["sessions"]=[]
        sessions_of_quest=[dict(session) for session in session_dao.get_sessions_of_quest(quest["id"])]
        for session in sessions_of_quest:
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
            session["most_requested_roles"]=[]
            if total_booked>0:
                most_requested=[role for role, count in role_counts.items() if count==max(role_counts.values())]
                session["most_requested_roles"]=most_requested
            session["total_booked"]=total_booked
            for role in LIMITS:
                session[role]=LIMITS[role]-role_counts[role]
            quest["sessions"].append(session)
    return quests

def get_admin_stats():
    all_detailed_quests=get_all_info_of_all_quests()
    all_info={"total_adventurers":len(users_dao.get_adventures_with_number_of_participation()), "total_quests":len(all_detailed_quests), "total_sessions":0, "total_participations":0, "popular_types":[]}
    total_roles={"Warrior":0, "Mage":0, "Healer":0}
    total_types={"Combact":0, "Exploration":0, "Stealth":0, "Magic":0, "Survival":0}
    popular_sessions=[]
    max_popular_session=0
    for quest in all_detailed_quests:
        for session in quest["sessions"]:
            all_info["total_sessions"]+=1
            all_info["total_participations"]+=session["total_booked"]
            total_types[quest["type"]]+=session["total_booked"]
            if session["total_booked"]>max_popular_session:
                max_popular_session=session["total_booked"]
                popular_sessions=[{"id": session["id"], "total":session["total_booked"], 
                    "title":quest["title"], "location":session["location"], "day_name":session["day"], "hour":session["hour"], "minute":session["minute"]}]
            elif session["total_booked"]==max_popular_session and session["total_booked"]!=0:
                popular_sessions.append({"id": session["id"], "total":session["total_booked"], 
                    "title":quest["title"], "location":session["location"], "day_name":session["day"], "hour":session["hour"], "minute":session["minute"]})
            for adventurer in session["adventurers"]:
                total_roles[adventurer["role"]]+=(len(adventurer["companions"])+1)
    all_info["total_roles"]=total_roles
    for key, val in total_types.items():
        if max(total_types.values())>0 and val==max(total_types.values()):
            all_info["popular_types"].append(key)
    all_info["popular_sessions"]=popular_sessions
    return all_info