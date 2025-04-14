from flask import jsonify
from datetime import datetime
from dateutil import parser


from db.matches_db import (
    get_matches_from_db,
    get_match_by_id_from_db,
    add_match_to_db,
    update_match_status_in_db,
    get_upcoming_matches_from_db,
    add_match_or_update_odds_in_db,
    update_matches_to_in_progress_in_db,
    get_in_progress_matches_older_than_2_hours_from_db
)
from db.bets_db import (
    update_bets_for_match_in_db,
    get_user_bets_for_matches
)
from db.user_db import update_user_balance_in_db
from external.footbal_api import get_match_result_from_api
from external.odds_api import fetch_epl_odds, fetch_epl_results, find_match_result

from api.bets_controller import handle_bets_for_match

def get_matches_controller():
    matches = get_matches_from_db()
    return {"matches": matches}, 200

def get_upcoming_matches_controller(user_id=None):
    """
    Get upcoming matches with optional user bet information.
    
    Args:
        user_id: Optional user ID to check if they've placed bets on the matches
        
    Returns:
        List of upcoming matches with user bet information if user_id is provided
    """
    matches = get_upcoming_matches_from_db()
    
    # If user_id is provided, check if they have bets on these matches
    if user_id:
        # Extract match_ids
        match_ids = [match["match_id"] for match in matches]
        
        # Get user's bets for these matches
        bet_map = get_user_bets_for_matches(user_id, match_ids)
        
        # Add bet information to each match
        for match in matches:
            match_id = match["match_id"]
            match["user_bet"] = bet_map.get(match_id)
    
    return {"matches": matches}, 200

def get_match_by_id_controller(match_id):
    match = get_match_by_id_from_db(match_id)
    if not match:
        return {"error": "Match not found"}, 404
    return {"match": match}, 200

def add_match_controller(data):
    # Validate required fields
    required_fields = ["team_1", "team_2", "match_date"]
    for field in required_fields:
        if field not in data:
            return {"error": f"Missing required field: {field}"}, 400

    match_id = add_match_to_db(
        data["team_1"],
        data["team_2"],
        data["match_date"],
        data.get("match_status", "upcoming")
    )

    if not match_id:
        return {"error": "Failed to create match"}, 500

    return {"match_id": match_id}, 201

def update_match_status_controller(match_id, new_status):
    valid_statuses = ["upcoming", "in_progress", "completed"]
    if new_status not in valid_statuses:
        return {"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}, 400

    result = update_match_status_in_db(match_id, new_status)

    if result == "match_not_found":
        return {"error": "Match not found"}, 404
    elif result == "already_completed":
        return {"error": "Cannot update status of completed match"}, 400
    elif result == "error":
        return {"error": "Internal server error"}, 500
    
    return {"message": "Match status updated successfully"}, 200

def sync_odds_controller():
    print("Fetching odds from TheOddsAPI...")
    matches = fetch_epl_odds()
    for match in matches:
        try:
            team_1 = match["home_team"]
            team_2 = match["away_team"]
            match_date = parser.isoparse(match["commence_time"])

            # Get odds from first bookmaker's h2h market
            outcomes = match["bookmakers"][0]["markets"][0]["outcomes"]
            odds_map = {o["name"]: o["price"] for o in outcomes}
            odds_team_1 = odds_map.get(team_1)
            odds_team_2 = odds_map.get(team_2)
            odds_draw = odds_map.get("Draw")
            if not all([odds_team_1, odds_team_2, odds_draw]):
                continue  # skip if odds missing
            add_match_or_update_odds_in_db(team_1, team_2, match_date, odds_team_1, odds_team_2, odds_draw)
        except Exception as e:
            print(f"Failed to process match: {e}")

    return {"message": "Odds synced successfully"}, 200

def update_matches_to_in_progress_controller():
    updated_match_ids = update_matches_to_in_progress_in_db()
    return {"message": "Matches updated to in progress", "updated_match_ids": updated_match_ids}, 200

def complete_matches_controller():
    # get in-progress matches older than 2 hours
    in_progress_older_than_2_hours_matches = get_in_progress_matches_older_than_2_hours_from_db()
    # get results from the-odds-api
    all_results = fetch_epl_results()
    for match in in_progress_older_than_2_hours_matches:
        result = find_match_result(all_results,  match["team_1"], match["team_2"], match["match_date"])
        if result is None:
            print(f"No result found for match {match['match_id']}")
            continue
        update_match_status_in_db(match["match_id"], "completed", result)
        handle_bets_for_match(match["match_id"])
    return {"message": "Matches completed", "updated_match_ids": in_progress_older_than_2_hours_matches}, 200
