import pytest
from unittest.mock import patch
from api.matches_controller import (
    get_matches_controller,
    get_match_by_id_controller,
    add_match_controller,
    update_match_status_controller
)

# Sample test data
SAMPLE_MATCH = {
    "match_id": "123e4567-e89b-12d3-a456-426614174000",
    "team_1": "Team A",
    "team_2": "Team B",
    "match_date": "2024-03-20",
    "match_status": "upcoming"
}

SAMPLE_MATCHES = [SAMPLE_MATCH]

# Test get_matches_controller
@patch('api.matches_controller.get_matches_from_db')
def test_get_matches_success(mock_get_matches):
    # Arrange
    mock_get_matches.return_value = SAMPLE_MATCHES
    
    # Act
    response, status_code = get_matches_controller()
    
    # Assert
    assert status_code == 200
    assert response == {"matches": SAMPLE_MATCHES}
    mock_get_matches.assert_called_once()

# # Test get_match_by_id_controller
# @patch('api.matches_controller.get_match_by_id_from_db')
# class TestGetMatchById:
#     def test_get_match_by_id_success(self, mock_get_match):
#         # Arrange
#         mock_get_match.return_value = SAMPLE_MATCH
        
#         # Act
#         response, status_code = get_match_by_id_controller("123")
        
#         # Assert
#         assert status_code == 200
#         assert response == {"match": SAMPLE_MATCH}
#         mock_get_match.assert_called_once_with("123")

#     def test_get_match_by_id_not_found(self, mock_get_match):
#         # Arrange
#         mock_get_match.return_value = None
        
#         # Act
#         response, status_code = get_match_by_id_controller("999")
        
#         # Assert
#         assert status_code == 404
#         assert response == {"error": "Match not found"}

# # Test add_match_controller
# @patch('api.matches_controller.add_match_to_db')
# class TestAddMatch:
#     def test_add_match_success(self, mock_add_match):
#         # Arrange
#         mock_add_match.return_value = "new-match-id"
#         valid_data = {
#             "team_1": "Team A",
#             "team_2": "Team B",
#             "match_date": "2024-03-20"
#         }
        
#         # Act
#         response, status_code = add_match_controller(valid_data)
        
#         # Assert
#         assert status_code == 201
#         assert response == {"match_id": "new-match-id"}
#         mock_add_match.assert_called_once_with(
#             "Team A", "Team B", "2024-03-20", "upcoming"
#         )

#     def test_add_match_missing_field(self, mock_add_match):
#         # Arrange
#         invalid_data = {
#             "team_1": "Team A",
#             # missing team_2
#             "match_date": "2024-03-20"
#         }
        
#         # Act
#         response, status_code = add_match_controller(invalid_data)
        
#         # Assert
#         assert status_code == 400
#         assert "Missing required field" in response["error"]
#         mock_add_match.assert_not_called()

#     def test_add_match_db_error(self, mock_add_match):
#         # Arrange
#         mock_add_match.return_value = None
#         valid_data = {
#             "team_1": "Team A",
#             "team_2": "Team B",
#             "match_date": "2024-03-20"
#         }
        
#         # Act
#         response, status_code = add_match_controller(valid_data)
        
#         # Assert
#         assert status_code == 500
#         assert response == {"error": "Failed to create match"}

# # Test update_match_status_controller
# @patch('api.matches_controller.update_match_status_in_db')
# class TestUpdateMatchStatus:
#     def test_update_status_success(self, mock_update_status):
#         # Arrange
#         mock_update_status.return_value = "success"
        
#         # Act
#         response, status_code = update_match_status_controller("123", "in_progress")
        
#         # Assert
#         assert status_code == 200
#         assert response == {"message": "Match status updated successfully"}
#         mock_update_status.assert_called_once_with("123", "in_progress")

#     def test_update_status_invalid_status(self, mock_update_status):
#         # Arrange
#         invalid_status = "invalid_status"
        
#         # Act
#         response, status_code = update_match_status_controller("123", invalid_status)
        
#         # Assert
#         assert status_code == 400
#         assert "Invalid status" in response["error"]
#         mock_update_status.assert_not_called()

#     def test_update_status_match_not_found(self, mock_update_status):
#         # Arrange
#         mock_update_status.return_value = "match_not_found"
        
#         # Act
#         response, status_code = update_match_status_controller("999", "completed")
        
#         # Assert
#         assert status_code == 404
#         assert response == {"error": "Match not found"}

#     def test_update_status_already_completed(self, mock_update_status):
#         # Arrange
#         mock_update_status.return_value = "already_completed"
        
#         # Act
#         response, status_code = update_match_status_controller("123", "in_progress")
        
#         # Assert
#         assert status_code == 400
#         assert "Cannot update status of completed match" in response["error"]

#     def test_update_status_error(self, mock_update_status):
#         # Arrange
#         mock_update_status.return_value = "error"
        
#         # Act
#         response, status_code = update_match_status_controller("123", "completed")
        
#         # Assert
#         assert status_code == 500
#         assert response == {"error": "Internal server error"} 