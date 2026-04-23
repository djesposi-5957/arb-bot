import requests
import json


class TheOddsApiCall:
    def __init__(self):
        self.api_key = "4e504fd0db7fe5e6e08fa3278df3cb14"
        self.market = "h2h"
        self.odds = "decimal"
        self.date = "iso"


    def fetch_data(self, sport, books):

        if sport == "mlb":
            sport = "baseball_mlb"
        if sport == "nhl":
            sport = "icehockey_nhl"
        if sport == "nba":
            sport = "basketball_nba"

        if len(books) > 1:
            books = ",".join(books)
        else:
            books = books

        odds_response = requests.get(f'https://api.the-odds-api.com/v4/sports/{sport}/odds?', params={
            'api_key': self.api_key,
            'bookmakers': books,
            'markets': self.market,
            'oddsFormat': self.odds,
            'dateFormat': self.date
        })

        odds_json = odds_response.json()
        print(json.dumps(odds_json, indent=2))
        print('Total credits remaining', odds_response.headers['x-requests-remaining'])
        return odds_json



