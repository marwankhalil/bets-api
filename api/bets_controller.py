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


def place_bet_controller(data):
    """
    Controller for placing bets.
    Handles validation and processing for both old and new betting systems.
    """
    # Validate required fields
    required_fields = ["user_id", "match_id", "bet_amount", "odds"]
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

    # Handle bet placement based on type
    if "advanced_bet_type" in data:
        # New system
        if "bet_parameters" not in data:
            return {"error": "bet_parameters required for advanced bet types"}, 400

        if data["advanced_bet_type"] == "team_to_win":
            if not data["bet_parameters"].get("team") in ["team_1", "team_2", "draw"]:
                return {"error": "Invalid team selection for team_to_win bet"}, 400

        result = place_bet_in_db(
            user_id=data["user_id"],
            match_id=data["match_id"],
            bet_type=None,
            bet_amount=bet_amount,
            odds=odds,
            advanced_bet_type=data["advanced_bet_type"],
            bet_parameters=data["bet_parameters"]
        )
    else:
        # Old system
        if "bet_type" not in data:
            return {"error": "bet_type required for standard bets"}, 400

        if data["bet_type"] not in ["team_1", "team_2"]:
            return {"error": "Invalid bet type"}, 400

        result = place_bet_in_db(
            user_id=data["user_id"],
            match_id=data["match_id"],
            bet_type=data["bet_type"],
            bet_amount=bet_amount,
            odds=odds
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

