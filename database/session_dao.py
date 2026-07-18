import os
import sqlite3

# Calcola la cartella in cui si trova il file DAO corrente (esame/database/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Unisce la cartella al nome del file del database
DB_PATH = os.path.join(BASE_DIR, "Konosuba.db")

# Creazione della sessione
def create_session(quest_id, location, day, hour, minute):
    conn=sqlite3.connect(DB_PATH)
    cursor=conn.cursor()
    query="INSERT INTO sessions (quest_id, location, day, hour, minute) VALUES (?,?,?,?,?)"
    cursor.execute(query, (quest_id, location, day, hour, minute))
    conn.commit()
    cursor.close()
    conn.close()

# Ottengo tutte sessioni (e relative informazioni contenute nella tabella
# sessions (come session_id, quest_id, location, day, hour, minute))
# presenti nel database ed ordinate in base a data/ora di partenza crescente
def get_all_session():
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    query="SELECT * FROM sessions GROUP BY id ORDER BY IFNULL(MIN(day*1440+hour*60+minute), 99999) ASC"
    cursor.execute(query)
    all_session=cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return all_session

# Ottengo tutte sessioni (e relative informazioni contenute nella tabella
# sessions (come session_id, quest_id, location, day, hour, minute))
# relative ad una certa sessione, quindi con uno specifico quest_id,
#  ed ordinate in base a data/ora di partenza crescente
def get_sessions_of_quest(quest_id):
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    query="SELECT * FROM sessions WHERE quest_id=? GROUP BY id ORDER BY IFNULL(MIN(day*1440+hour*60+minute), 99999) ASC"
    cursor.execute(query, (quest_id,))
    sessions=cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return sessions

# Ottengo le info di una specifica sessione (e relative informazioni contenute 
# nella tabella sessions (come session_id, quest_id, location, day, hour, minute))
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

# Cancello, tramite delete, una certa sessione con uno specifico database
def delete_session(session_id):
    conn=sqlite3.connect(DB_PATH)
    cursor=conn.cursor()
    query="DELETE FROM sessions WHERE id=?"
    cursor.execute(query, (session_id,))
    conn.commit()
    cursor.close()
    conn.close()