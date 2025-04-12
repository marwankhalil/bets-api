from db.bets_db import (
    place_bet_in_db,
    get_user_bets_from_db
)
from db.matches_db import (
    get_match_by_id_from_db
)
from db.user_db import (
    get_user_by_id_from_db
)

def place_bet_controller(user_id, match_id, bet_type, bet_amount, odds):
    # Validate required fields
    if not bet_type or not isinstance(bet_amount, (int, float)) or bet_amount <= 0 or not isinstance(odds, (int, float)) or odds <= 1.0:
        return {"error": "Invalid bet input. Ensure bet_type is provided, bet_amount is positive, and odds are greater than 1.0"}, 400

    match = get_match_by_id_from_db(match_id)
    if not match:
        return {"error": "match_not_found"}, 404
    if match["match_status"] == "completed" or match["match_status"] == "in_progress":
        return {"error": "match_completed_or_in_progress"}, 400

    # Check if user has enough balance
    user = get_user_by_id_from_db(user_id)
    if not user:
        return {"error": "user_not_found"}, 404
    if user["balance"] < bet_amount:
        return {"error": "insufficient_balance"}, 400

    # Call the database function
    result = place_bet_in_db(user_id, match_id, bet_type, bet_amount, odds)
    if result == "error":
        return {"error": "Failed to place bet"}, 500
    else:
        return {"message": "Bet placed successfully", "bet_id": result["bet_id"]}, 201

def get_user_bets_controller(user_id):
    # Check if user exists
    user = get_user_by_id_from_db(user_id)
    if not user:
        return {"error": "user_not_found"}, 404

    # Call the database function
    result = get_user_bets_from_db(user_id)
    if result == "error":
        return {"error": "Failed to fetch user bets"}, 500
    else:
        return {"bets": result}, 200

