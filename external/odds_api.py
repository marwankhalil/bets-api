import os
import requests

def fetch_epl_odds():
  url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds?apiKey={os.getenv('ODDS_API_KEY')}&regions=uk&markets=h2h"
  response = requests.get(url)
  return response.json()

def fetch_epl_results():
  url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/scores/?apiKey={os.getenv('ODDS_API_KEY')}&daysFrom=3&dateFormat=iso"
  response = requests.get(url)
  return response.json()

def find_match_result(all_results, home_team, away_team, match_date):
    """
    Find the result of a match based on home team, away team, and match date.
    
    Args:
        home_team (str): Name of the home team
        away_team (str): Name of the away team
        match_date (datetime): Date of the match
        
    Returns:
        str: 'team_1' if home team won, 'team_2' if away team won, 'draw' if it was a draw
    """
    # Convert match_date to string format matching the dummy data
    match_date_str = match_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Find the matching game
    for game in all_results:
        if (game["home_team"] == home_team and 
            game["away_team"] == away_team and 
            game["commence_time"] == match_date_str and 
            game["completed"] and 
            game["scores"] is not None):
            
            # Initialize scores
            home_score = away_score = None
            
            # Find the correct scores for home and away teams
            for score in game["scores"]:
                if score["name"] == home_team:
                    home_score = int(score["score"])
                elif score["name"] == away_team:
                    away_score = int(score["score"])
            
            # Determine the result
            if home_score > away_score:
                return "team_1"
            elif away_score > home_score:
                return "team_2"
            else:
                return "draw"
    
    # If no match found or match not completed, return None
    return None

