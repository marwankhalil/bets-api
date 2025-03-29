from typing import Dict, Tuple, Optional
from db.user_db import (
    get_user_by_firebase_uid, 
    create_user,
    get_user_by_id_from_db,
    update_username,
    username_exists
)

def format_user_response(user_id: str, username: Optional[str], balance: float = 0) -> Dict:
    """
    Format user response data into a consistent structure.
    
    Args:
        user_id: The user's unique identifier
        username: The user's username (can be None)
        balance: The user's current balance (defaults to 0)
    
    Returns:
        Dict containing formatted user data
    """
    return {
        "user_id": str(user_id),
        "username": username,
        "balance": balance
    }

def handle_existing_user(user: Dict) -> Tuple[Dict, int]:
    """
    Handle response for an existing user.
    
    Args:
        user: Dictionary containing user data
    
    Returns:
        Tuple of (response dict, status code)
    """
    return format_user_response(
        user_id=user["user_id"],
        username=user["username"],
        balance=user.get("balance", 0)
    ), 200

def handle_new_user(firebase_uid: str, email: str) -> Tuple[Dict, int]:
    """
    Handle creation and response for a new user.
    
    Args:
        firebase_uid: Firebase user ID
        email: User's email address
    
    Returns:
        Tuple of (response dict, status code)
    """
    new_user_id = create_user(firebase_uid, email)
    if not new_user_id:
        return {"error": "Failed to create user"}, 500
    
    return format_user_response(
        user_id=new_user_id,
        username=None,
        balance=1000
    ), 201

def login_controller(firebase_uid: str, email: str, id_token: str) -> Tuple[Dict, int]:
    """
    Handle user login and authentication.
    
    Args:
        firebase_uid: Firebase user ID
        email: User's email address
        id_token: Firebase ID token (for future token verification)
    
    Returns:
        Tuple of (response dict, status code)
    """
    try:
        # TODO: Implement Firebase token verification
        user = get_user_by_firebase_uid(firebase_uid)
        
        if user:
            return handle_existing_user(user)
        else:
            return handle_new_user(firebase_uid, email)

    except Exception as e:
        print(f"Login failed: {e}")
        return {"error": "Internal server error"}, 500

def set_username_controller(user_id: str, username: str) -> Tuple[Dict, int]:
    try:
        user = get_user_by_id_from_db(user_id)
        if not user or user == "user_not_found":
            return {"error": "User not found"}, 404
        if username_exists(username):
            return {"error": "Username already taken"}, 409
        update_username(user_id, username)
        return {"message": "Username updated successfully"}, 200
    except Exception as e:
        print(f"Error setting username: {e}")
        return {"error": "Internal server error"}, 500

