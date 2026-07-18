import os
import sqlite3

# Calcola la cartella in cui si trova il file DAO corrente (esame/database/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Unisce la cartella al nome del file del database
DB_PATH = os.path.join(BASE_DIR, "Konosuba.db")

# Seleziono tutte le informazioni (come user_id, username, name, surname
# password, role, illustration, profile_img, bio) di uno specifico utente
def get_user_by_id(user_id):
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    query="SELECT * FROM users WHERE users.id=?"
    cursor.execute(query, (user_id,))
    db_user=cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return db_user

# Creo un utente con uno specifico ruolo [il fatto che il ruolo vari è
# dovuto al fatto che inizialmente pensavo che anche il master, la prima
# volta, dovesso registrarsi al sito come "normale" utente]
def create_user(name, surname, username, password, role, profile_img, bio):
    conn=sqlite3.connect(DB_PATH)
    cursor=conn.cursor()
    query="INSERT INTO users (name, surname, username, password, role, profile_img, bio) VALUES (?,?,?,?,?,?,?)"
    cursor.execute(query, (name, surname, username, password, role, profile_img, bio))
    conn.commit()
    cursor.close()
    conn.close()

# Ottengo tutte le informazioni relative ad un utente con uno specifico username
# Mi serve solo in fase di creazione di un account (per controllare che NON 
# esista già un utente con tale username) o in fase di validazione per il login
# (per verificare che esista un utente con tale username e le password coincidano)
def get_user_by_username(username):
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    query="SELECT * FROM users WHERE users.username=?"
    cursor.execute(query, (username,))
    db_user=cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return db_user

# Prendo dal database solo gli avventurieri e per ognuno di
# essi restituisco le informazioni presenti nella tabella user (come
# user_id, username, name, surname, password, illustration, bio e role)
# più il numero di prenotazioni che quell'utente ha fatto [e quindi
# il numero di sessioni a cui attualmente intende prendere parte]
def get_adventures_with_number_of_participation():
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    query="""SELECT u.*, COUNT(r.id) AS participations_count
        FROM users u
        LEFT JOIN reservations r ON u.id=r.user_id
        WHERE u.role='adventurer'
        GROUP BY u.id"""
    cursor.execute(query)
    # Inutile questa conversione. La scusa: dico che in un primo 
    # momento oltre al numero di sessioni andavo anche a prendere
    # tutte le altre informazioni relative alla sessione
    # stessa ma anche alla quest di appartenenza (come titolo, durata, ..)
    adventurers=[dict(row) for row in cursor.fetchall()]
    conn.commit()
    cursor.close()
    conn.close()
    return adventurers