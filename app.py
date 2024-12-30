from flask import Flask, request
import json
app = Flask(__name__)

from db import (
    get_games as get_games_from_db,
    place_bet as place_bet_in_db
)

@app.route('/get_games', methods = ["GET"])
def get_games():
    games = get_games_from_db()
    ret = []
    for game in games:
        ret.append({
            "game_id": game[0],
            "home_team": game[1],
            "away_team": game[2],
            "start_time": game[3]
        })
    return ret

@app.route('/place_bet', methods = ["POST"])
def place_bet():
    data = request.get_json()
    game_id = data.get("game_id")
    bet_amount = data.get("bet_amount")
    bet_on = data.get("bet_on")
    place_bet_in_db(game_id, bet_amount, bet_on)
    return app.response_class(
        status=200,
    )