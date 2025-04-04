dummy = [
  {
    "id": "a6151a5362fb6365b776880f17a142cc",
    "sport_key": "soccer_epl",
    "sport_title": "EPL",
    "commence_time": "2025-04-01T18:45:00Z",
    "home_team": "Arsenal",
    "away_team": "Fulham",
    "bookmakers": [
      {
        "key": "paddypower",
        "title": "Paddy Power",
        "last_update": "2025-03-22T19:41:15Z",
        "markets": [
          {
            "key": "h2h",
            "last_update": "2025-03-22T19:41:15Z",
            "outcomes": [
              {
                "name": "Arsenal",
                "price": 1.5
              },
              {
                "name": "Fulham",
                "price": 8
              },
              {
                "name": "Draw",
                "price": 4.33
              }
            ]
          }
        ]
      }
    ]
  }
]
import os
import requests

def fetch_epl_odds():
    url = f"https://api.the-odds-api.com/v4/sports/soccer_epl/odds?apiKey={os.getenv('ODDS_API_KEY')}&regions=uk&markets=h2h"
    response = requests.get(url)
    return response.json()



