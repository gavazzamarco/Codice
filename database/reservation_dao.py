from database import quests_dao, session_dao
import os
import sqlite3

# Calcola la cartella in cui si trova il file DAO corrente (esame/database/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Unisce la cartella al nome del file del database
DB_PATH = os.path.join(BASE_DIR, "Konosuba.db")

# Creo una prenotazione e restituisco l'id della prenotazione appena creata
def create_reservation(user_id, session_id, role, total_people):
    conn=sqlite3.connect(DB_PATH)
    cursor=conn.cursor()
    query="INSERT INTO reservations (user_id, session_id, role, total_people) VALUES (?,?,?,?)"
    cursor.execute(query, (user_id, session_id, role, total_people))
    id=cursor.lastrowid # ottengo l'id della prenotazione appena creata
    conn.commit()
    cursor.close()
    conn.close()
    return id

# Estraggo tutte le informazioni contenute nella tabella reservation
# (cioè id della prenotazione, id della sessione, id dell'utente che ha fatto
# la prenotazione, ruolo scelto per la sessione e numero totale di persone 
# legate a tale prenotazione (cioè avventuriero + eventuale compagno))
# relative ad una determinata sessione, ossia tutte le info delle
# prenotazioni fatte per una certa sessione
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

# Estraggo tutte le informazioni contenute nella tabella reservation
# (cioè id della prenotazione, id della sessione, id dell'utente che ha fatto
# la prenotazione, ruolo scelto per la sessione e numero totale di persone 
# legate a tale prenotazione (cioè avventuriero + eventuale compagno))
# relative alle prenotazione fatte da un certo utente registrato
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

# Inserisco nella tabella companions il compagno di viaggio
# scelto da un certo utente e per una certa sessione
# Le info contenute nella tabelal reservation sono l'id auto-incrementale
# e poi solo l'id della prenotazione e l'username dell'accompagnatore
def add_companions(reservation_id, username):
    conn=sqlite3.connect(DB_PATH)
    cursor=conn.cursor()
    query="INSERT INTO companions (reservation_id, username) VALUES (?,?)"
    cursor.execute(query, (reservation_id, username))
    conn.commit()
    cursor.close()
    conn.close()

# Seleziono tutte le informazioni presenti nella tabella
# (cioè id della prenotazione, id della sessione, id dell'utente che ha fatto
# la prenotazione, ruolo scelto per la sessione e numero totale di persone 
# legate a tale prenotazione (cioè avventuriero + eventuale compagno))
# relative ad una determinata prenotazione con un certo id
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

# Informazioni dettagliate relative ad ogni prenotazione fatta da un avventuriero
def get_detailed_adventurer_quests(user_id):
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    # Seleziono gli id (NON duplicati) relativi a tutte le quest
    # per le quali l'utente corrente ha effettuato prenotazioni ad
    # almeno una delle loro sessioni
    query="""SELECT DISTINCT q.id FROM quests q
        JOIN sessions s ON q.id=s.quest_id JOIN reservations r ON s.id=r.session_id
        WHERE r.user_id=?"""
    
    cursor.execute(query, (user_id,))
    adventurer_quests=[]
    
    # Scanidsco i singoli id trovati tramite la query sopra
    for quest_id in [row["id"] for row in cursor.fetchall()]:
        # Estraggo le informazioni relative alla quest con l'id attualmente considerato
        quest=dict(quests_dao.get_quest_by_id(quest_id))

        # CAZZATA, prima prendo tutte le sessioni della quest corrente e poi
        # verifico se è presente una prenotazione da parte dell'utente corrente
        # per tale sessione
        quest["sessions"]=[]
        sessions=session_dao.get_sessions_of_quest(quest_id)
        for session in sessions:
            reservation=get_reservation_by_session_for_user(user_id, session["id"])
            
            # Se l'utente ha effettivamente una prenotazione attiva per tale sessione
            # allora aggiungo alla lista di sessioni a cui è iscritto l'utente
            # corrente tale sessione arricchita di informazioni come id della sessione,
            # luogo, giorno, ora, minuto, ruolo scelto per tale sessione, numero totale
            # di persone incluse in tale prenotazione e insieme dei compagni aggiunti
            # Inizialmente pensavo che ogni avventuriero potesse portare con sè più
            # accompagnatori e questo è ancora presente qui nella logica
            if reservation:
                companions=[companion["username"] for companion in get_companions_for_reservation(reservation["id"])]
                quest["sessions"].append({ "session_id":session["id"], "location":session["location"], "day":session["day"], "hour":session["hour"],
                    "minute":session["minute"], "role":reservation["role"], "total_people":reservation["total_people"], "companions":companions })
        
        # Siccome ho una lista di quest dove ogni quest contiene sia le
        # informazioni relative alla quest (come id, titolo, durata, tipo, difficoltà
        # illustrazione e difficoltà) e poi per ogni quest è presenta la lista di
        # sessioni di tale quest a cui l'utente considerato è prenotato
        adventurer_quests.append(quest)
    conn.commit()
    cursor.close()
    conn.close()    
    return adventurer_quests

# Ottengo tutte le informazioni presenti nella tabella reservations
# (cioè id della prenotazione, id della sessione, id dell'utente che ha fatto
# la prenotazione, ruolo scelto per la sessione e numero totale di persone 
# legate a tale prenotazione (cioè avventuriero + eventuale compagno))
# relative ad una determinata sessione
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

# Quando cancello una prenotazione, cancello anche dalla tabella
# companions i compagni che sono legati a quella prenotazione
# siccome tanto non ha senso che questi continuino ad esistere
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