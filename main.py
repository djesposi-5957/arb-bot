import argparse
import time
from scrapers.draftkings import DraftKingsScraper
from scrapers.betmgm import BetMGMScraper
from scrapers.theodds import TheOddsApiCall
from cleaner import clean_data, clean_data_api
import pandas as pd
from arbitrage import find_arbitrage
from datetime import datetime
import os

def scrape(selected_sites, selected_sports, timestamp):


    mlb_rows = []
    nba_rows = []
    nhl_rows = []

    one_site = []
    many_sites = []

    for site in selected_sites:
        if site in ["fanduel", "bovada", "betrivers", "draftkings", "betmgm"]:
            many_sites.append(site)
        # else:
            # one_site.append(site)

    if many_sites:
        scraper = TheOddsApiCall()

        for sport in selected_sports:
            data = scraper.fetch_data(sport, many_sites)
            cleaned_df = clean_data_api(data)

            cleaned_rows = cleaned_df.to_dict("records")

            if sport == "nba":
                nba_rows.extend(cleaned_rows)
            elif sport == "mlb":
                mlb_rows.extend(cleaned_rows)
            elif sport == "nhl":
                nhl_rows.extend(cleaned_rows)


    # if one_site:
    #     for site in one_site:
    #         scraper = scrapers[site]()
    #
    #         for sport in selected_sports:
    #             data = scraper.fetch_data(sport)
    #             cleaned_df = clean_data(data)
    #
    #             cleaned_rows = cleaned_df.to_dict("records")
    #
    #             if sport == "nba":
    #                 nba_rows.extend(cleaned_rows)
    #             elif sport == "mlb":
    #                 mlb_rows.extend(cleaned_rows)
    #             elif sport == "nhl":
    #                 nhl_rows.extend(cleaned_rows)


    if mlb_rows:
        df = pd.DataFrame(mlb_rows)
        base_dir = "data/cleaned_data/mlb/mlb_master.csv"
        snapshot_dir = f"data/cleaned_data/mlb/snapshots/{timestamp}.csv"
        df.to_csv(snapshot_dir, index=False, encoding="utf-8")
        df.to_csv(base_dir, mode="a", index=False, encoding="utf-8")

    if nba_rows:
        df = pd.DataFrame(nba_rows)
        base_dir = "data/cleaned_data/nba/nba_master.csv"
        snapshot_dir = f"data/cleaned_data/nba/snapshots/{timestamp}.csv"
        df.to_csv(snapshot_dir, index=False, encoding="utf-8")
        df.to_csv(base_dir, mode="a", index=False, encoding="utf-8")

    if nhl_rows:
        df = pd.DataFrame(nhl_rows)
        base_dir = "data/cleaned_data/nhl/nhl_master.csv"
        snapshot_dir = f"data/cleaned_data/nhl/snapshots/{timestamp}.csv"
        df.to_csv(snapshot_dir, index=False, encoding="utf-8")
        df.to_csv(base_dir, mode="a", index=False, encoding="utf-8")


if __name__ == "__main__":
    all_books = ["draftkings", "betmgm", "fanduel", "bovada", "betrivers"]
    all_sports = ["nba", "nhl", "mlb"]
    scrapers = {
        "draftkings": DraftKingsScraper,
        "betmgm": BetMGMScraper,
        "fanduel": TheOddsApiCall,
        "bovada": TheOddsApiCall,
        "betrivers": TheOddsApiCall
    }

    parser = argparse.ArgumentParser()

    parser.add_argument("--site", nargs="+", choices=all_books + ["all"], required=True, help="Two or more sportsbooks")
    parser.add_argument("--sport", nargs="+", choices=all_sports + ["all"], required=True, help="One or more sports")

    args = parser.parse_args()

    if "all" in args.site:
        selected_sites = ["draftkings", "betmgm", "fanduel", "bovada", "betrivers"]
    else:
        selected_sites = args.site

    if "all" in args.sport:
        selected_sports = ["nba", "nhl", "mlb"]
    else:
        selected_sports = args.sport

    while True:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        scrape(selected_sites, selected_sports, timestamp)
        opps = find_arbitrage(timestamp)
        if opps:
            df = pd.DataFrame(opps)
            file_path = "data/arbitrage/arbitrage_master.csv"
            df.to_csv(file_path, mode="a", index=False, encoding="utf-8")

        time.sleep(300)

        snapshot_mlb = f"data/cleaned_data/mlb/snapshots/{timestamp}.csv"
        if os.path.isfile(snapshot_mlb):
            os.remove(snapshot_mlb)
        snapshot_nba = f"data/cleaned_data/nba/snapshots/{timestamp}.csv"
        if os.path.isfile(snapshot_nba):
            os.remove(snapshot_nba)
        snapshot_nhl = f"data/cleaned_data/nhl/snapshots/{timestamp}.csv"
        if os.path.isfile(snapshot_nhl):
            os.remove(snapshot_nhl)