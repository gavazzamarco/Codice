import sqlite3

DB_PATH = "Konosuba_db.db"

def get_user_by_id(user_id):
    query = "SELECT * FROM Users WHERE users.id = ?"
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, (user_id,))
    db_user = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return db_user

def create_user(name, surname, username, password, profile_img):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = "INSERT INTO users (name, surname, email, password, profile_img) VALUES (?,?,?,?,?)"
    cursor.execute(query, (name, surname, username, password, profile_img))
    conn.commit()
    cursor.close()
    conn.close()