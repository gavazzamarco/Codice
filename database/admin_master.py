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
    admin_name = "Guild Council administrator"
    admin_surname = ""
    admin_username = "admin"
    admin_password = generate_password_hash("Admin")  # NOTA: In produzione la password dovrebbe essere hashata
    admin_role = "admin"                  # Viene inserito come un normale utente ma con ruolo 'admin'
    admin_img = ""
    admin_bio = ""

    admin_name = "Luna"
    admin_surname = ""
    admin_username = "luna"
    admin_password = generate_password_hash("Luna")  # NOTA: In produzione la password dovrebbe essere hashata
    admin_role = "master"                  # Viene inserito come un normale utente ma con ruolo 'admin'
    admin_img = "images/profile_imgs/luna.png"
    admin_bio = "Welcome to the Axel Adventurer's Guild! My name is Luna, and I am the head receptionist here. My main achievements include managing the daily quest board, processing bounty rewards, and somehow keeping this entire establishment running smoothly despite the daily chaos. If you want to register as an adventurer, pick up a quest, or cash in a reward, I am always happy to assist you! Please choose your quests responsibly... my stress levels are counting on it."

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