import os
import sqlite3

def inizializza_database():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_name = os.path.join(BASE_DIR, "Konosuba.db")
    
    # Definiamo la stringa contenente tutte le query SQL del tuo schema
    schema_sql = """
        CREATE TABLE "users" (
        "id" INTEGER NOT NULL UNIQUE,
        "name" TEXT NOT NULL,
        "surname" TEXT NOT NULL,
        "username" TEXT NOT NULL UNIQUE,
        "password" TEXT NOT NULL,
        "role" TEXT NOT NULL,
        "profile_img" TEXT,
        PRIMARY KEY("id" AUTOINCREMENT)
    );
    """

    try:
        # Stabilisce la connessione con il database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Abilita esplicitamente il supporto alle Foreign Key (chiavi esterne) in SQLite
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        # executescript permette di eseguire più query separate da punto e virgola in un colpo solo
        cursor.executescript(schema_sql)
        
        # Salva le modifiche
        conn.commit()
        print(f"Database '{db_name}' inizializzato con successo con tutte le tabelle!")
        
    except sqlite3.Error as e:
        print(f"Si è verificato un errore durante l'inizializzazione: {e}")
        
    finally:
        # Chiude la connessione se è stata aperta
        if conn:
            conn.close()

if __name__ == "__main__":
    inizializza_database()