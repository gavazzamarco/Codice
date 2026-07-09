import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'Konosuba.db')

def conn_init():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def delete_all():
    conn = conn_init()
    cursor = conn.cursor()
    
    # Disabilita temporaneamente i vincoli per svuotare tutto senza errori di dipendenza
    cursor.execute("PRAGMA foreign_keys = OFF;")
    
    tabelle = [
        "users",
        "quests",
        "sessions",
        "reservations",
        "companions",
        "sqlite_sequence"     # Per azzerare gli ID incrementali
    ]
    
    try:
        for tabella in tabelle:
            cursor.execute(f"DELETE FROM {tabella}")
            
        conn.commit()
        print("Database ripulito con successo.")
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Errore database: {e}")
    finally:
        # Riabilita le foreign keys prima di chiudere
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.close()
        conn.close()

    # === NUOVA SEZIONE: Cancellazione foto dai file di upload ===
    # Risaliamo alla cartella principale del progetto (esame/) partendo da BASE_DIR (esame/database)
    esame_dir = os.path.dirname(BASE_DIR)
    
    cartelle_foto = [
        os.path.join(esame_dir, 'static', 'images', 'profile_imgs'),
        os.path.join(esame_dir, 'static', 'images', 'illustrations'),
    ]
    
    print("Inizio rimozione file multimediali...")
    for cartella in cartelle_foto:
        if os.path.exists(cartella):
            for file_name in os.listdir(cartella):
                file_path = os.path.join(cartella, file_name)
                try:
                    # Rimuove solo i file o i link simbolici, salvaguardando la struttura della cartella
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                        print(f"Eliminato file: {file_path}")
                except Exception as e:
                    print(f"Impossibile eliminare {file_path}: {e}")
        else:
            print(f"La cartella {cartella} non esiste, salto il passaggio.")

delete_all()