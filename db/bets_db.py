from db.db_connection import DBConnection
from db.db_utils import is_valid_uuid

# Initialize a global DB connection object
db = DBConnection()

def place_bet_in_db(user_id, match_id, bet_type, bet_amount, odds):
    try:
        with db.get_cursor() as cursor:
            # Insert bet into bets table
            cursor.execute("""
                INSERT INTO bets (bet_id, user_id, match_id, bet_type, bet_amount, odds, result, bet_on)
                VALUES (uuid_generate_v4(), %s, %s, %s, %s, %s, 'pending', %s)
                RETURNING bet_id;
            """, (user_id, match_id, bet_type, bet_amount, odds, bet_type))

            bet_id = cursor.fetchone()["bet_id"]

            # Deduct bet amount from user's balance
            cursor.execute("""
                UPDATE users SET balance = balance - %s WHERE user_id = %s;
            """, (bet_amount, user_id))

              # Commit the transaction
            return {"bet_id": bet_id}
    except Exception as e:
        print(f"Error placing bet: {e}")
        return "error"

def get_user_bets_from_db(user_id):
    try:
        with db.get_cursor() as cursor:
            # Fetch user's bets along with match details, ordered by match date descending
            cursor.execute("""
                SELECT b.bet_id, b.match_id, m.team_1, m.team_2, m.match_date, 
                       b.bet_type, b.bet_amount, b.odds, b.result
                FROM bets b
                JOIN matches m ON b.match_id = m.match_id
                WHERE b.user_id = %s
                ORDER BY m.match_date DESC;
            """, (user_id,))
            
            bets = cursor.fetchall()
            return bets if bets else []
    except Exception as e:
        print(f"Error fetching bets for user {user_id}: {e}")
        return "error"

def get_user_bets_for_matches(user_id, match_ids):
    """
    Check if a user has placed bets on specific matches.
    
    Args:
        user_id: The user's ID
        match_ids: List of match IDs to check
        
    Returns:
        Dict mapping match_id to bet information or None if no bet
    """
    if not match_ids:
        return {}
        
    try:
        with db.get_cursor() as cursor:
            placeholders = ','.join(['%s'] * len(match_ids))
            query = f"""
                SELECT match_id, bet_type, bet_amount, odds, result
                FROM bets
                WHERE user_id = %s AND match_id IN ({placeholders});
            """
            params = [user_id] + match_ids
            cursor.execute(query, params)
            
            bets = cursor.fetchall()
            
            # Create a map of match_id to bet details
            bet_map = {}
            for bet in bets:
                match_id = bet['match_id']
                bet_map[match_id] = {
                    'bet_type': bet['bet_type'],
                    'bet_amount': bet['bet_amount'],
                    'odds': bet['odds'],
                    'result': bet['result']
                }
                
            return bet_map
    except Exception as e:
        print(f"Error fetching user bets for matches: {e}")
        return {}

def process_bets_for_match_in_db(match_id):
    if not is_valid_uuid(user_id):
        return "user_not_found"
    try:
        with db.get_cursor() as cursor:
            # Get match result
            cursor.execute("""
                SELECT result FROM matches WHERE match_id = %s AND match_status = 'completed';
            """, (match_id,))
            match_result = cursor.fetchone()

            if not match_result:
                return "match_not_completed"

            match_result = match_result[0]

            # Get all pending bets for this match
            cursor.execute("""
                SELECT bet_id, user_id, bet_amount, odds, bet_type
                FROM bets
                WHERE match_id = %s AND result = 'pending';
            """, (match_id,))
            
            bets = cursor.fetchall()

            if not bets:
                return "no_pending_bets"

            for bet in bets:
                bet_id, user_id, bet_amount, odds, bet_type = bet

                # Determine if the bet is won or lost
                if (bet_type == "winner" and match_result == "team_1_win") or \
                   (bet_type == "winner" and match_result == "team_2_win"):
                    bet_result = "won"
                    winnings = bet_amount * odds

                    # Update user balance
                    cursor.execute("""
                        UPDATE users SET balance = balance + %s WHERE user_id = %s;
                    """, (winnings, user_id))
                else:
                    bet_result = "lost"

                # Update bet result
                cursor.execute("""
                    UPDATE bets SET result = %s WHERE bet_id = %s;
                """, (bet_result, bet_id))

            
            return "success"
    except Exception as e:
        print(f"Error processing bets for match {match_id}: {e}")
        return "error"

def update_bets_for_match_in_db(match_id, winning_bet_type):
    try:
        with db.get_cursor() as cursor:
            cursor.execute("""
                UPDATE bets
                SET result = CASE
                    WHEN bet_type = %s THEN 'won'
                    ELSE 'lost'
                END
                WHERE match_id = %s
                RETURNING bet_id, result, user_id, bet_amount, odds;
            """, (winning_bet_type, match_id))
            updated_bets = cursor.fetchall()
            
            return updated_bets
    except Exception as e:
        print(f"Error updating bets for match {match_id}: {e}")
        return []

def get_user_bets_for_matches(user_id, match_ids):
     """
     Check if a user has placed bets on specific matches.
     
     Args:
         user_id: The user's ID
         match_ids: List of match IDs to check
         
     Returns:
         Dict mapping match_id to bet information or None if no bet
     """
     if not match_ids:
         return {}
         
     try:
         with db.get_cursor() as cursor:
             placeholders = ','.join(['%s'] * len(match_ids))
             query = f"""
                 SELECT match_id, bet_type, bet_amount, odds, result
                 FROM bets
                 WHERE user_id = %s AND match_id IN ({placeholders});
             """
             params = [user_id] + match_ids
             cursor.execute(query, params)
             
             bets = cursor.fetchall()
             
             # Create a map of match_id to bet details
             bet_map = {}
             for bet in bets:
                 match_id = bet['match_id']
                 bet_map[match_id] = {
                     'bet_type': bet['bet_type'],
                     'bet_amount': bet['bet_amount'],
                     'odds': bet['odds'],
                     'result': bet['result']
                 }
                 
             return bet_map
     except Exception as e:
         print(f"Error fetching user bets for matches: {e}")
         return {}