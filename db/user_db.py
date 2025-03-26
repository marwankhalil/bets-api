from db.db_utils import is_valid_uuid
from db.db_connection import DBConnection

db = DBConnection()

def get_user_by_id_from_db(user_id):
    if not is_valid_uuid(user_id):
        return "user_not_found"
    try:
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT user_id, user_name, balance FROM users WHERE user_id = %s;
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
            db.commit()
    except Exception as e:
        print(f"Error updating user balance for {user_id}: {e}")

