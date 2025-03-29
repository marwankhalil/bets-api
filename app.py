from flask import Flask, request, jsonify
import json
app = Flask(__name__)
from flask_cors import CORS
CORS(app)

@app.route('/')
def index():
    return "Hello, World!" # Correct - returns a string

from api.matches_controller import (
    get_matches_controller,
    get_match_by_id_controller,
    add_match_controller,
    update_match_status_controller,
    get_upcoming_matches_controller,
    sync_odds_controller,
    update_matches_to_in_progress_controller,
    complete_matches_controller
)
from api.bets_controller import (
    place_bet_controller,
    get_user_bets_controller
)
from api.users_controller import (
    login_controller,
    set_username_controller
)

@app.route('/matches', methods=["GET"])
def get_matches():
    response, status_code = get_matches_controller()
    return jsonify(response), status_code

@app.route('/upcoming_matches', methods=["GET"])
def get_upcoming_matches():
    response, status_code = get_upcoming_matches_controller()
    return jsonify(response), status_code


@app.route('/matches/<match_id>', methods=["GET"])
def get_match_by_id(match_id):
    response, status_code = get_match_by_id_controller(match_id)
    return jsonify(response), status_code


@app.route('/matches', methods=["POST"])
def add_match():
    response, status_code = add_match_controller(request.get_json())
    return jsonify(response), status_code

@app.route('/matches/<match_id>/status', methods=["PATCH"])
def update_match_status(match_id):
    data = request.get_json()

    if "match_status" not in data:
        return jsonify({"error": "Missing required field: match_status"}), 400

    response, status_code = update_match_status_controller(match_id, data["match_status"])
    return jsonify(response), status_code


@app.route('/bets', methods=["POST"])
def place_bet():
    data = request.get_json()

    # Validate request payload
    required_fields = ["user_id", "match_id", "bet_type", "bet_amount", "odds"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    # Call the controller function
    response, status_code = place_bet_controller(
        data["user_id"],
        data["match_id"],
        data["bet_type"],
        data["bet_amount"],
        data["odds"]
    )
    return jsonify(response), status_code

@app.route('/bets/<user_id>', methods=["GET"])
def get_user_bets(user_id):
    response, status_code = get_user_bets_controller(user_id)
    return jsonify(response), status_code

@app.route('/internal/sync_odds', methods=["GET"])
def sync_odds():
    response, status_code = sync_odds_controller()
    return jsonify(response), status_code

@app.route('/internal/update-in-progress', methods=["POST"])
def update_matches_to_in_progress():
    response, status_code = update_matches_to_in_progress_controller()
    return jsonify(response), status_code

@app.route('/internal/complete-matches', methods=["POST"])
def complete_matches():
    response, status_code = complete_matches_controller()
    return jsonify(response), status_code

@app.route('/api/login', methods=['POST'])
def login():
    print("Request received: /api/login request: ", request.get_json())
    data = request.get_json()
    firebase_uid = data.get('firebase_uid')
    email = data.get('email')
    id_token = data.get('id_token')

    if not firebase_uid or not id_token:
        return jsonify({"error": "Missing firebase_uid or id_token"}), 400

    response, status_code = login_controller(firebase_uid, email, id_token)
    return jsonify(response), status_code

@app.route('/api/set_username', methods=['POST'])
def set_username():
    print("Request received: /api/set_username request: ", request.get_json())
    data = request.get_json()
    user_id = data.get('user_id')
    username = data.get('username')

    if not user_id or not username:
        return jsonify({"error": "Missing user_id or username"}), 400

    response, status_code = set_username_controller(user_id, username)
    return jsonify(response), status_code