import glob
import os
import pandas as pd


def get_snapshot_path(sport, time):
    return f"data/cleaned_data/{sport}/snapshots/{time}.csv"

def find_arbitrage(time):

    all_opportunities = []

    for sport in ["nba", "nhl", "mlb"]:
        file_path = get_snapshot_path(sport, time)

        if not os.path.exists(file_path):
            print(f"No snapshot found for {sport}")
            continue
        print(f"Checking {sport}: {file_path}")

        df = pd.read_csv(file_path)

        df = df[df["status"] != "live"]
        df = df.dropna(subset=["odds_decimal"])

        opportunities = []

        grouped = df.groupby(["game_id", "commence_time"])

        for key, game_group in grouped:
            game_id = key[0]
            commence_time = key[1]

            teams = game_group["team"].unique()

            if len(teams) != 2:
                continue

            team_a = teams[0]
            team_b = teams[1]

            team_a_rows = game_group[game_group["team"] == team_a]
            team_b_rows = game_group[game_group["team"] == team_b]

            best_a_index = team_a_rows["odds_decimal"].idxmax()
            best_a = team_a_rows.loc[best_a_index]
            best_b_index = team_b_rows["odds_decimal"].idxmax()
            best_b = team_b_rows.loc[best_b_index]

            probability = (1 / best_a["odds_decimal"]) + (1 / best_b["odds_decimal"])
            if probability < 1:
                profit_perc = (1 - probability) * 100

                opportunity = {
                    "sport": sport,
                    "game_id": game_id,
                    "commence_time": commence_time,
                    "team_a": team_a,
                    "sportsbook_a": best_a["sportsbook"],
                    "odds_a": best_a["odds_decimal"],
                    "team_b": team_b,
                    "sportsbook_b": best_b["sportsbook"],
                    "odds_b": best_b["odds_decimal"],
                    "probability": round(probability, 4),
                    "profit_margin": f"{round(profit_perc, 2)}%",
                    "time": time
                }
                opportunities.append(opportunity)

                print("\nARBITRAGE FOUND")
                print(f"Sport: {sport}")
                print(f"Game: {game_id}")
                print(f"Start time: {commence_time}")
                print(f"Bet {team_a} on {best_a['sportsbook']} at {best_a['odds_decimal']}")
                print(f"Bet {team_b} on {best_b['sportsbook']} at {best_b['odds_decimal']}")
                print(f"Profit margin: {round(profit_perc, 2)}%")

        if not opportunities:
            print(f"No arbitrage found for {sport}")

        all_opportunities.extend(opportunities)

    if not all_opportunities:
        print("No arbitrage opportunities found across all sports.")

    return all_opportunities