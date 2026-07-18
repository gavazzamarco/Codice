from database import reservation_dao, session_dao, users_dao
import os
import sqlite3

# Calcola la cartella in cui si trova il file DAO corrente (esame/database/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Unisce la cartella al nome del file del database
DB_PATH = os.path.join(BASE_DIR, "Konosuba.db")

LIMITS={"Warrior": 4,  "Mage":3, "Healer":2}
DAYS_OF_WEEK=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Creazione di una quest
def create_quest(title, duration, type, difficulty, description, illustration):
    conn=sqlite3.connect(DB_PATH)
    cursor=conn.cursor()
    query="INSERT INTO quests (title, duration, type, difficulty, description, illustration) VALUES (?,?,?,?,?,?)"
    cursor.execute(query, (title, duration, type, difficulty, description, illustration))
    id=cursor.lastrowid # serve a prendere l'id della quest appena creata
    conn.commit()
    cursor.close()
    conn.close()
    return id

# Restituisce tutte le informazioni, come id, titolo, durata, tipo, difficoltà
# illustrazione e descrizione relative ad una certa quest con un certo id 
# (l'id è il valore intero ed auto-incrementale assegnato automaticamente dal db)
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
    # USO DEL LEFT JOIN: serve per consentire la visualizzazione delle quest che NON 
    # hanno ancora nessuna sessione associata. Se al posto del LEFT JOIN venisse 
    # utilizzato un semplice INNER JOIN, il database escluderebbe immediatamente 
    # dal risultato tutte le quest che hanno zero corrispondenze nella tabella 
    # sessions. Di conseguenza, una quest appena creata senza sessioni diventerebbe
    # completamente invisibile sul sito. Le quest senza sessioni non spariscono dal 
    # sistema, ma vengono relegate programmaticamente in fondo alla lista della pagina.
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

# Operazione di filtraggio delle quest presenti nel database sulla base
# dei filtri selezionati dall'utente e passati a tale funzione dal file
# app.py (in particolare dalla funzione home_filter() del file app.py)
def get_filtered_quest(day, type, difficulty, role):
    conn=sqlite3.connect(DB_PATH)
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()
    filtered_quests=[]
    # Siccome tramite get_all_quest() ottengo tutte le sessioni già ordinate
    # in ordine temporale come richiesto, in questo caso NON è necessario
    # effettuare successivamente un'operazione di ordinamento siccome ho una lista
    # vuota dove vado ad aggiungere in fondo (tramite append()) le quest, che 
    # vengono però già scandite nell'ordine corretto (grazie appunto a get_all_quest())
    for quest in get_all_quest():
        # Se il filtro di tipo esiste ed il tipo della sessione attualmente 
        # considerata è diverso dal tipo selezionato dall'utente, allora scarto 
        # tale quest e passo alla successiva
        if type and quest['type']!=type:
            continue

        # Se il filtro di difficoltà esiste ed la difficoltà della sessione 
        # attualmente considerata è diversa dalla difficoltà selezionata 
        # dall'utente, allora scarto tale quest e passo alla successiva
        if difficulty and quest['difficulty']!=difficulty:
            continue

        # Questa condizione è assolutamente IMPORTANTE e serve a far sì che
        # le quest senza sessioni NON vengano scartate a priori. Infatti,
        # senza questa riga e se l'utente NON selezionasse il giorno, la
        # funzione entrerebbe nell'else legato alla condizione
        # (if day is not None:) e andrebbe a prendere tutte le sessioni 
        # legati a quella quest. Se la quest NON ha sessioni, allora la
        # lista "sessions_to_check" sarebbe vuota e, per il controllo
        # (if not sessions_to_check:) tale quest verrebbe quindi saltata di default.
        # Anche se l'utente non ha chiesto di filtrare per giorno o ruolo, tutte 
        # le quest senza sessioni diventerebbero invisibili sul sito, annullando 
        # completamente il senso del LEFT JOIN che hai usato nella query principale.
        if (day is not None) or role:

            # Se il filtro di giorno esiste (cioè se è stato selezionato
            # dall'utente), allora prendo tutte le sessioni legate alle quest
            # corrente e che si svolgono nel giorno scelto dall'utente.
            # Se NON ve ne fossero, la lista "session_to_check" sarebbe nulla
            if day is not None:
                query="SELECT * FROM sessions WHERE quest_id=? AND day=?"
                cursor.execute(query, (quest["id"], day))
                sessions_to_check=cursor.fetchall()
            else:
                # Altrimenti prendo tutte le sessioni legate alla quest corrente
                # Se la quest corrente NON dovesse avere sessioni, allora la
                # lista "session_to_check" sarà vuota
                query="SELECT * FROM sessions WHERE quest_id=?"
                cursor.execute(query, (quest["id"],))
                sessions_to_check=cursor.fetchall()
            # Se la lista "session_to_check" è vuota, o perché la quest
            # corrente NON ha proprio sessioni o perché essa NON ha sessioni
            # che si svolgono nel giorno selezionato, allora scarto tale quest
            if not sessions_to_check:
                continue

            # Se il filtro di ruolo esiste (cioè se è stato selezionato
            # dall'utente), allora prendo tutte le sessioni che hanno superato
            # l'eventuale filtraggio di data precedente, per ognuna di tali
            # sessioni conto (tramite SUM dalla tabella reservation) quanti
            # sono i posti già occupati per quella determinata sessione e 
            # per il ruolo richiesto dall'utente e verifico se ne ve sono ancora
            # di disponibili. Se la quest ha anche solo una sessione con un solo
            # posto disponibile per il ruolo richiesto dall'utente, allora
            # tale quest è CORRETTA e viene mostrato a schermo.
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
        # Se la quest ha superato tutti controlli allora significa che
        # rispetta i filtri inseriti dall'utente e viene inserita in fondo
        # alla lista (in questo modo preservo anche l'ordinamento temporale
        # che era già presente nelle sessioni per come era restituite da get_all_quest())
        filtered_quests.append(quest)
    conn.commit()
    cursor.close()
    conn.close()
    return filtered_quests

# Funzione che viene usata all'interno della route profile_master() nel file app.py
# al fine di ottenere tutte le informazioni significative di una determinata
# quest e relative sessioni. 
def get_all_info_of_all_quests():
    # Devo convertire tutte le quest in un dizionario siccome se no quanto
    # restituito dalla funzione get_all_qeust() che fa uso di conn.row_factory=sqlite3.Row
    # sarebbe un oggetto immutabile e quindi NON modificabile.
    # Siccome la funzione get_all_quest() [definita in questo file poco sopra]
    # ordinava già tutte le quest in base al crtierio temporale richiesto, le
    # quest nel profile master verranno visualizzate rispettando tale criterio temporale
    quests=[dict(row) for row in get_all_quest()]
    
    # Una volta ottenute tutte le quest presenti nel database ciclo su ogni
    # quest al fine di calcolarne le informazioni richieste
    for quest in quests:
        # Lista vuota in cui andrò ad inserire in fondo, di volta in volta
        # le sessioni non appena queste disporranno di tutte le info necessarie
        quest["sessions"]=[]

        # Estraggo dal database la lista (convertita in dizionario per renderla
        # modificabile) contenente tutte le info contenute nella tabella sessions 
        # del database (come id della sessione, id della quest a cui è legata tale 
        # sessione, giorno, ore, minuti e luogo di tale sessione) relative a tutte
        # le sessioni legate alla quest attualmente considerata
        sessions_of_quest=[dict(session) for session in session_dao.get_sessions_of_quest(quest["id"])]
        
        # Cilo poi su ognuna di tale sessione per arricchire il numero di
        # informazioni legate a ciascuna di esse
        for session in sessions_of_quest:
            # converto il giorno da intero (che è come il giorno è salvato nel
            # database) ad una stringa (il nome in inglese)
            session["day"]=DAYS_OF_WEEK[session["day"]]

            # Creo una lista vuota che andrà a contenere le informazioni (username,
            # nome, cognome e compagno di viaggio scelto) relative a tutti gli 
            # avventurieri che hanno prenotato la sessione attuale
            session["adventurers"]=[]
            # Quindi estraggo le informazioni relative a tutte le prenotazioni
            # fatte ed attive per la sessione attualmente considerata
            reservations=reservation_dao.get_reservations_for_session(session["id"])
            
            # Contatore del totale (avventurieri ed eventuali accompagnatori)
            # delle persone iscritte ad una determinata sessione
            total_booked=0
            # Contatore del numero totale di posti per ruolo attualmente già 
            # occupati per la sessione considerata
            role_counts={"Warrior": 0, "Mage": 0, "Healer": 0}

            # Ciclo su tutte le prenotazioni fatte per la sessione attuale
            for reservation in reservations:
                # Questo serve siccome nella tabella reservation solo solo presenti
                # le informazioni relative a (session_id, quest_id, role e total_people
                # (cioè numero totale di persone incluse in quella prenotazione (che
                # può essere 1 se l'avventuriero è solo, o 2 se è accompagnato)))
                # ma io per ogni avventurieri sono anche interessato ad informazioni
                # come username, nome e cognome
                user=users_dao.get_user_by_id(reservation["user_id"])
                session["adventurers"].append({
                    "username":user["username"],"name":user["name"], "surname":user["surname"], "role":reservation["role"],
                    "companions":[comp_row['username'] for comp_row in reservation_dao.get_companions_for_reservation(reservation["id"])]})
                
                # Ogni prenotazione contiene informazioni relative al numero
                # totale di persone incluse in quella specifica prenotazione
                # ed il ruolo scelto dalle persone di quella prenotazione.
                # Queste informazioni vengono usate per aggiornare il contatore di
                # persone iscritte a tale sessione e il numero di posti occupati
                # per ciascun ruolo in quella specifica sessione
                total_booked+=reservation["total_people"]
                role_counts[reservation["role"]]+=reservation["total_people"]
            
            # Ruolo (come mago, healer o guerriero) più richiesto per la sessione corrente
            session["most_requested_roles"]=[]
            # Affinché la sessione abbia effettivamente un ruolo più richiesto è
            # necessario che sia stata fatta almeno una prenotazioe (altrimenti avrei
            # tutti i ruoli con 0 posti prenotati e tutti segnati come più richiesti)
            if total_booked>0:
                most_requested=[role for role, count in role_counts.items() if count==max(role_counts.values())]
                session["most_requested_roles"]=most_requested
            
            session["total_booked"]=total_booked
            for role in LIMITS:
                session[role]=LIMITS[role]-role_counts[role]
            quest["sessions"].append(session)
    return quests


# Prende tutte le informazioni dettagliate ricavate sopra e le usa per
# ottenere delle statistiche generali relative alla piattaforma per l'admin
def get_admin_stats():
    # Prendo tutte le informazioni ben dettagliate relative a quest
    # e sessioni ad esse associate (funzione immediatamente sopra)
    all_detailed_quests=get_all_info_of_all_quests()

    # Dizionario in cui vengono memorizzate tutte le stastiche generali
    all_info={"total_adventurers":len(users_dao.get_adventures_with_number_of_participation()), "total_quests":len(all_detailed_quests), "total_sessions":0, "total_participations":0, "popular_types":[]}
    
    # Dizionari usati come contatori per sapere quante sono le partecipazioni
    # totali, tra tutte le quest, per ciascun ruolo e per ciascun tipo di quest
    total_roles={"Warrior":0, "Mage":0, "Healer":0}
    total_types={"Combact":0, "Exploration":0, "Stealth":0, "Magic":0, "Survival":0}
    
    popular_sessions=[]
    max_popular_session=0
    # Scandisco le quest ad una ad una
    for quest in all_detailed_quests:
        # Scandisco le sessioni relative ad ogni sessione ad una ad una per analizzarle attentamente
        for session in quest["sessions"]:
            # Ovviamente ogni sessione scandita fa aumentare di uno il contatore
            # globale delle sessioni
            all_info["total_sessions"]+=1

            # Per ogni sessione conosco già il numero totale di iscritti quindi
            # il numero totale di partecipazioni all'interno della piattaforma
            # è dato dalla somma delle partecipazioni totali alle singole sessioni
            all_info["total_participations"]+=session["total_booked"]

            # Calcolo il numero totale di partecipani per ogni tipo (come
            # combact, stealth, ..) di quest al fine di sapere alla fine qual
            # il tipo (o i tipi) di quest più popolare
            total_types[quest["type"]]+=session["total_booked"]

            # Cerco di volta in volta quali sono le sessioni più popolari
            if session["total_booked"]>max_popular_session:
                # Se la nuova sessione è più popolare delle precedenti allora
                # svuoto la lista presente precedentemente e la riempo con le
                # sole info relative alla sessione corrente
                max_popular_session=session["total_booked"]
                popular_sessions=[{"id": session["id"], "total":session["total_booked"], 
                    "title":quest["title"], "location":session["location"], "day_name":session["day"], "hour":session["hour"], "minute":session["minute"]}]

            # Il controllo (session["total_booked"]!=0) serve ad evitare che
            # nel caso in cui NON vi sia ancora alcuna prenotazione ad una sessione
            # allora tutte le sessioni vengano considerate come popolari  
            elif session["total_booked"]==max_popular_session and session["total_booked"]!=0:
                # Altrimenti, se ci sono più sessioni ugualmente popolari 
                # le aggiungo tutte alla lista della sessioni più popolari
                popular_sessions.append({"id": session["id"], "total":session["total_booked"], 
                    "title":quest["title"], "location":session["location"], "day_name":session["day"], "hour":session["hour"], "minute":session["minute"]})
            
            # Tengo il conteggio del numero totale di partecipazioni per ciascun ruolo
            for adventurer in session["adventurers"]:
                total_roles[adventurer["role"]]+=(len(adventurer["companions"])+1)
    
    all_info["total_roles"]=total_roles
    # Tra tutti i tipi di quest cerco quello (o quelli più popolari)
    for key, val in total_types.items():
        if max(total_types.values())>0 and val==max(total_types.values()):
            all_info["popular_types"].append(key)
    all_info["popular_sessions"]=popular_sessions
    return all_info