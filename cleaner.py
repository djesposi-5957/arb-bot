import pandas as pd
import normalizer

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

def clean_data(dirty_data):

    rows = []

    for game in dirty_data:
        sport = game.get("sport")
        team_a = game.get("teamA").strip()
        team_b = game.get("teamB").strip()
        if sport == "mlb":
            team_a = team_normalizer.MLB_TEAM_MAP.get(team_a, team_a)
            team_b = team_normalizer.MLB_TEAM_MAP.get(team_b, team_b)
        elif sport == "nba":
            team_a = team_normalizer.NBA_TEAM_MAP.get(team_a, team_a)
            team_b = team_normalizer.NBA_TEAM_MAP.get(team_b, team_b)
        elif sport == "nhl":
            team_a = team_normalizer.NHL_TEAM_MAP.get(team_a, team_a)
            team_b = team_normalizer.NHL_TEAM_MAP.get(team_b, team_b)

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



