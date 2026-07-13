import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# Configurazione del percorso del database esistente nel codice
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "Konosuba.db")

def create_user(name, surname, username, password, role, profile_img, bio):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = "INSERT INTO users (name, surname, username, password, role, profile_img, bio) VALUES (?,?,?,?,?,?,?)"
    cursor.execute(query, (name, surname, username, password, role, profile_img, bio))
    conn.commit()
    cursor.close()
    conn.close()

# Esempio di inserimento dell'utente amministratore
if __name__ == "__main__":
    # Definizione dei dati dell'amministratore
    admin_name = "Admin"
    admin_surname = "Global"
    admin_username = "admin"
    admin_password = generate_password_hash("Admin")  # NOTA: In produzione la password dovrebbe essere hashata
    admin_role = "admin"                  # Viene inserito come un normale utente ma con ruolo 'admin'
    admin_img = ""
    admin_bio = ""

    try:
        create_user(
            name=admin_name,
            surname=admin_surname,
            username=admin_username,
            password=admin_password,
            role=admin_role,
            profile_img=admin_img,
            bio=admin_bio
        )
        print(f"Utente admin '{admin_username}' inserito con successo.")
    except sqlite3.IntegrityError as e:
        print(f"Errore durante l'inserimento: {e}. Probabilmente lo username '{admin_username}' esiste già.")