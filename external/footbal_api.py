import random

def get_match_result_from_api(match_id, team_1, team_2, match_date):
    result = random.choice(['team_1_win', 'team_2_win', 'draw'])
    return result

