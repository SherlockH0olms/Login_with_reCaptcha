import sqlite3
from pymongo import MongoClient
import os

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/klickon_auth")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client.get_database()
users_coll = db.get_collection("users")

SQLITE_DB = "users.db"

def migrate():
    conn = sqlite3.connect(SQLITE_DB)
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, username, email, password_hash FROM users;")
    except Exception as e:
        print("SQLite tablosu bulunamadı veya hata:", e)
        return
    rows = cur.fetchall()
    for r in rows:
        id_, username, email, password_hash = r
        try:
            users_coll.update_one(
                {"email": email},
                {"$setOnInsert": {"username": username, "email": email, "password_hash": password_hash}},
                upsert=True
            )
            print("Migrated:", email)
        except Exception as e:
            print("Error migrating", email, e)
    conn.close()
    print("Migration tamamlandı.")

if __name__ == "__main__":
    migrate()
