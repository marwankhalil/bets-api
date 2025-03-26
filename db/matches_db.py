from db.db_connection import DBConnection
from db.db_utils import is_valid_uuid

# Initialize a global DB connection object
db = DBConnection()

def get_matches_from_db():
    try:
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT match_id, team_1, team_2, match_date, match_status, result
                FROM matches;
            """)
            matches = cursor.fetchall()
            return matches if matches else []
    except Exception as e:
        print(f"Error fetching matches: {e}")
        return []

def get_upcoming_matches_from_db():
    try:
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT match_id, team_1, team_2, match_date, match_status, odds_team_1, odds_draw, odds_team_2, result
                FROM matches
                WHERE match_status = 'upcoming';
            """)
            matches = cursor.fetchall()
            return matches if matches else []
    except Exception as e:
        print(f"Error fetching matches: {e}")
        return []


def get_match_by_id_from_db(match_id):
    if not is_valid_uuid(match_id):
        print(f"Invalid UUID format: {match_id}")
        return None  # Return None immediately if UUID is invalid

    try:
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT match_id, team_1, team_2, match_date, match_status, odds_team_1, odds_draw, odds_team_2, result
                FROM matches
                WHERE match_id = %s;
            """, (match_id,))
            
            return cursor.fetchone()  # Returns dictionary or None if not found
    except Exception as e:
        print(f"Error fetching match {match_id}: {e}")
        return None


def add_match_to_db(team_1, team_2, match_date, match_status="upcoming"):
    try:
        with db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO matches (match_id, team_1, team_2, match_date, match_status)
                VALUES (uuid_generate_v4(), %s, %s, %s, %s)
                RETURNING match_id;
            """, (team_1, team_2, match_date, match_status))

            match_id = cursor.fetchone()["match_id"]  # Uses dict instead of tuple
            db.commit()  # Explicitly commit the transaction
            return match_id
    except Exception as e:
        print(f"Error adding match: {e}")
        return None


def update_match_status_in_db(match_id, new_status, result=None):
    try:
        with db.get_cursor() as cursor:
            # Check if match exists
            cursor.execute("SELECT match_status FROM matches WHERE match_id = %s;", (match_id,))
            match = cursor.fetchone()
            
            if not match:
                return "match_not_found"

            if match["match_status"] == "completed":
                return "already_completed"

            # Update match status
            cursor.execute("""
                UPDATE matches 
                SET match_status = %s, result = %s
                WHERE match_id = %s;
            """, (new_status, result, match_id))

            db.commit()  # Commit the transaction
            return "success"
    except Exception as e:
        raise e
        print(f"Error updating match status: {e}")
        return "error"

def add_match_or_update_odds_in_db(team_1, team_2, match_date, odds_team_1, odds_team_2, odds_draw):
    try:
        with db.get_cursor() as cursor:
            cursor.execute("""
                INSERT INTO matches (match_id,team_1, team_2, match_date, match_status, odds_team_1, odds_draw, odds_team_2)
                VALUES (uuid_generate_v4(), %s, %s, %s, 'upcoming', %s, %s, %s)
                ON CONFLICT (team_1, team_2, match_date) DO UPDATE
                SET odds_team_1 = EXCLUDED.odds_team_1,
                    odds_draw = EXCLUDED.odds_draw,
                    odds_team_2 = EXCLUDED.odds_team_2
                WHERE matches.match_status = 'upcoming';
            """, (team_1, team_2, match_date, odds_team_1, odds_draw, odds_team_2))

            db.commit()
            return True
    except Exception as e:
        print(f"Error adding match or updating odds: {e}")
        return False


def update_matches_to_in_progress_in_db():
    try:
        with db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE matches
                SET match_status = 'in_progress'
                WHERE match_status = 'upcoming'
                AND match_date <= NOW()
                RETURNING match_id;
            """)
            updated = cursor.fetchall()

        db.commit()
        updated_ids = [row["match_id"] for row in updated]
        print(updated_ids)
        return updated_ids

    except Exception as e:
        print(f"Error updating in-progress matches: {e}")
        return []

def get_in_progress_matches_older_than_2_hours_from_db():
    try:
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT match_id, team_1, team_2, match_date
                FROM matches
                WHERE match_status = 'in_progress'
                AND match_date + interval '2 hours' <= NOW();
            """)
            in_progress_matches_older_than_2_hours = cursor.fetchall()
        return in_progress_matches_older_than_2_hours
    except Exception as e:
        print(f"Error getting in-progress matches older than 2 hours: {e}")
        return []
