from db.db_utils import is_valid_uuid
from db.db_connection import DBConnection

db = DBConnection()

def get_user_by_id_from_db(user_id):
    if not is_valid_uuid(user_id):
        return "user_not_found"
    try:
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT user_id, username, balance FROM users WHERE user_id = %s;
            """, (user_id,))
            return cursor.fetchone()
    except Exception as e:
        print(f"Error fetching user {user_id}: {e}")
        return None

def update_user_balance_in_db(user_id, amount):
    try:
        with db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE users
                SET balance = balance + %s
                WHERE user_id = %s;
            """, (amount, user_id))
            
    except Exception as e:
        print(f"Error updating user balance for {user_id}: {e}")

def get_user_by_firebase_uid(firebase_uid):
    try:
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT user_id, username, balance FROM users WHERE firebase_uid = %s;
            """, (firebase_uid,))
            row = cursor.fetchone()
            if row:
                return {"user_id": row["user_id"], "username": row["username"], "balance": row["balance"]}
            return None
    except Exception as e:
        print(f"DB error (get_user_by_firebase_uid): {e}")
        return None

def create_user(firebase_uid, email):
    try:
        with db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO users (user_id, firebase_uid, email, balance)
                VALUES (uuid_generate_v4(), %s, %s, 1000)
                RETURNING user_id;
            """, (firebase_uid, email))
            user_id = cursor.fetchone()["user_id"]
            
            return user_id
    except Exception as e:
        print(f"DB error (create_user): {e}")
        return None

def username_exists(username):
    try:
        with db.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS count FROM users WHERE username = %s;", (username,))
            return cursor.fetchone()["count"] > 0
    except Exception as e:
        print(f"DB error (username_exists): {e}")
        return False

def update_username_in_db(user_id: str, username: str) -> bool:
    """
    Update a user's username in the database.
    
    Args:
        user_id: The user's unique identifier
        username: The new username to set
        
    Returns:
        bool: True if update was successful, False otherwise
    """
    try:
        with db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE users
                SET username = %s
                WHERE user_id = %s;
            """, (username, user_id))
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Error updating username for user {user_id}: {e}")
        return False

