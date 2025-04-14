from db.bets_db import (
    place_bet_in_db,
    get_match_bets_from_db,
    update_bet_result_in_db,
    get_user_bets_from_db
)
from db.matches_db import (
    get_match_by_id_from_db,
)
from db.user_db import (
    get_user_by_id_from_db,
    update_user_balance_in_db
)


def place_bet_controller(data):
    """
    Controller for placing bets.
    Handles validation and processing for both old and new betting systems.
    """
    # Validate required fields
    required_fields = ["user_id", "match_id", "bet_amount", "odds", "advanced_bet_type", "bet_parameters"]
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return {"error": f"Missing required fields: {', '.join(missing_fields)}"}, 400

    # Extract and validate numeric fields
    try:
        bet_amount = float(data["bet_amount"])
        odds = float(data["odds"])
    except ValueError:
        return {"error": "bet_amount and odds must be valid numbers"}, 400

    if bet_amount <= 0:
        return {"error": "Bet amount must be positive"}, 400
    
    if odds <= 1.0:
        return {"error": "Odds must be greater than 1.0"}, 400

    # Get and validate match
    match = get_match_by_id_from_db(data["match_id"])
    if not match:
        return {"error": "Match not found"}, 404
    
    if match["match_status"] != "upcoming":
        return {"error": "Match is not open for betting"}, 400

    # Get and validate user
    user = get_user_by_id_from_db(data["user_id"])
    if not user:
        return {"error": "User not found"}, 404
    
    if user["balance"] < bet_amount:
        return {"error": "Insufficient balance"}, 400

    if data["advanced_bet_type"] == "team_to_win":
        if not data["bet_parameters"].get("team") in ["team_1", "team_2", "draw"]:
            return {"error": "Invalid team selection for team_to_win bet"}, 400

    result = place_bet_in_db(
        user_id=data["user_id"],
        match_id=data["match_id"],
        bet_amount=bet_amount,
        odds=odds,
        advanced_bet_type=data["advanced_bet_type"],
        bet_parameters=data["bet_parameters"]
    )

    if result == "error":
        return {"error": "Failed to place bet"}, 500

    return {
        "message": "Bet placed successfully",
        "bet_id": result["bet_id"],
        "system": "advanced" if "advanced_bet_type" in data else "standard"
    }, 201


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

def handle_bets_for_match(match_id):
    match = get_match_by_id_from_db(match_id)
    match_bets = get_match_bets_from_db(match_id)
    for bet in match_bets:
        won = False
        if bet["advanced_bet_type"] == "team_to_win":
            won = handle_team_to_win_bet(bet, match)
        update_user_balance_in_db(bet["user_id"], bet["bet_amount"] * bet["odds"]) if won else None
        update_bet_result_in_db(bet["bet_id"], "won" if won else "lost")

def handle_team_to_win_bet(bet, match):
    if bet["bet_parameters"]["team"] == "draw":
        if match["result"] == "draw":
            return True
        else:
            return False
    else:
        if bet["bet_parameters"]["team"] == match["result"]:
            return True
        else:
            return False

