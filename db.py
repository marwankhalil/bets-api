import os
import psycopg2


class db_connection():
    def __init__(self):
        conn_str = os.environ.get("BETS_DB_CONN_STR")
        self.conn = psycopg2.connect(conn_str)
    def get_cursor(self):
        return self.conn.cursor()
    def commit(self):
        self.conn.commit()

db = db_connection()

def get_games():
    with db.get_cursor() as cursor:
        cursor.execute("SELECT * FROM games;")
        return cursor.fetchall()

def place_bet(game_id, bet_amount, bet_on):
    with db.get_cursor() as cursor:
        try:
            query = """
                INSERT INTO bets (game_id, bet_amount, team_bet_on) VALUES
                (%s, %s, %s);
            """
            cursor.execute(query, (game_id, bet_amount, bet_on))
            db.commit()
        except Exception as e:
            print(e)