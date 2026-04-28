import pandas as pd
import normalizer
from datetime import datetime, timezone

columns = [
    "sportsbook",
    "sport",
    "game_id",
    "team",
    "odds",
    "commence_time",
    "status",
    "scrape_time"
]

def clean_data_api(dirty_data):

    rows = []

    for game in dirty_data:
        sport = game.get("sport_title").lower()
        commence_str = game.get("commence_time")
        team_a = game.get("home_team", "").lower().strip()
        team_b = game.get("away_team", "").lower().strip()

        if sport == "mlb":
            team_a = normalizer.MLB_TEAM_MAP.get(team_a, team_a)
            team_b = normalizer.MLB_TEAM_MAP.get(team_b, team_b)
        elif sport == "nba":
            team_a = normalizer.NBA_TEAM_MAP.get(team_a, team_a)
            team_b = normalizer.NBA_TEAM_MAP.get(team_b, team_b)
        elif sport == "nhl":
            team_a = normalizer.NHL_TEAM_MAP.get(team_a, team_a)
            team_b = normalizer.NHL_TEAM_MAP.get(team_b, team_b)

        game_id = "__".join(sorted([team_a, team_b]))
        now = datetime.now(timezone.utc)
        commence_time = datetime.fromisoformat(commence_str.replace("Z", "+00:00"))
        if now > commence_time:
            status = "live"
        else:
            status = "upcoming"

        for bookmaker in game.get("bookmakers", []):
            sportsbook = bookmaker.get("title").lower()
            scrape_time = bookmaker.get("last_update")
            for market in bookmaker.get("markets", []):
                odds_list = []
                for outcome in market.get("outcomes", []):
                    odds_decimal = outcome.get("price")
                    odds_list.append(odds_decimal)

                rows.append({
                    "sportsbook": sportsbook,
                    "sport": sport,
                    "game_id": game_id,
                    "team": team_a,
                    "odds_decimal": odds_list[0],
                    "commence_time": commence_str,
                    "status": status,
                    "scrape_time": scrape_time
                })

                rows.append({
                    "sportsbook": sportsbook,
                    "sport": sport,
                    "game_id": game_id,
                    "team": team_b,
                    "odds_decimal": odds_list[1],
                    "commence_time": commence_str,
                    "status": status,
                    "scrape_time": scrape_time
                })


    return pd.DataFrame(rows)

def clean_data(dirty_data):

    rows = []

    for game in dirty_data:
        sport = game.get("sport")
        team_a = game.get("teamA", "").lower().strip()
        team_b = game.get("teamB", "").lower().strip()
        if sport == "mlb":
            team_a = normalizer.MLB_TEAM_MAP.get(team_a, team_a)
            team_b = normalizer.MLB_TEAM_MAP.get(team_b, team_b)
        elif sport == "nba":
            team_a = normalizer.NBA_TEAM_MAP.get(team_a, team_a)
            team_b = normalizer.NBA_TEAM_MAP.get(team_b, team_b)
        elif sport == "nhl":
            team_a = normalizer.NHL_TEAM_MAP.get(team_a, team_a)
            team_b = normalizer.NHL_TEAM_MAP.get(team_b, team_b)

        game_id = "__".join(sorted([team_a, team_b]))

        if game.get("commence_time") == None:
            status = "live"
        else:
            status = "upcoming"

        rows.append({
            "sportsbook": game.get("sportsbook"),
            "sport": sport,
            "game_id": game_id,
            "team": team_a,
            "odds_decimal": game.get("odds_decimalA"),
            "commence_time": game.get("commence_time"),
            "status": status,
            "scrape_time": game.get("time")
        })

        rows.append({
            "sportsbook": game.get("sportsbook"),
            "sport": sport,
            "game_id": game_id,
            "team": team_b,
            "odds_decimal": game.get("odds_decimalB"),
            "commence_time": game.get("commence_time"),
            "status": status,
            "scrape_time": game.get("time")
        })

    return pd.DataFrame(rows)



