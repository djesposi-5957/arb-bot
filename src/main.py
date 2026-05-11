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
import threading
import itertools
import msvcrt
import sys


status = {
    "running": True,
    "times_run": 0
}

def status_bar():
    spinner = itertools.cycle(["|", "/", "-", "\\"])
    while status["running"]:
        symbol = next(spinner)
        print(
            f"\r[{symbol}] Looking for Arbitrage Opportunities... Press 't' for run count.",
            end="",
            flush=True
        )

        if msvcrt.kbhit():

            key = msvcrt.getch().decode("utf-8").lower()

            if key == "t":
                print(
                    f"\rTimes Run: {status['times_run']}                                "
                )

        time.sleep(0.15)

def scrape(selected_sites, selected_sports, timestamp, headless):


    mlb_rows = []
    nba_rows = []
    nhl_rows = []

    one_site = []
    many_sites = []

    for site in selected_sites:
        if site in ["fanduel", "bovada", "betrivers"]:
            many_sites.append(site)
        else:
            one_site.append(site)

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


    if one_site:
         for site in one_site:
             scraper = scrapers[site]()

             for sport in selected_sports:
                 data = scraper.fetch_data(sport, headless)
                 cleaned_df = clean_data(data)

                 cleaned_rows = cleaned_df.to_dict("records")

                 if sport == "nba":
                     nba_rows.extend(cleaned_rows)
                 elif sport == "mlb":
                     mlb_rows.extend(cleaned_rows)
                 elif sport == "nhl":
                     nhl_rows.extend(cleaned_rows)


    if mlb_rows:
        df = pd.DataFrame(mlb_rows)
        base_dir = "../data/cleaned_data/mlb/mlb_master.csv"
        snapshot_dir = f"../data/cleaned_data/mlb/snapshots/{timestamp}.csv"
        df.to_csv(snapshot_dir, index=False, encoding="utf-8")
        df.to_csv(base_dir, mode="a", index=False, encoding="utf-8")

    if nba_rows:
        df = pd.DataFrame(nba_rows)
        base_dir = "../data/cleaned_data/nba/nba_master.csv"
        snapshot_dir = f"../data/cleaned_data/nba/snapshots/{timestamp}.csv"
        df.to_csv(snapshot_dir, index=False, encoding="utf-8")
        df.to_csv(base_dir, mode="a", index=False, encoding="utf-8")

    if nhl_rows:
        df = pd.DataFrame(nhl_rows)
        base_dir = "../data/cleaned_data/nhl/nhl_master.csv"
        snapshot_dir = f"../data/cleaned_data/nhl/snapshots/{timestamp}.csv"
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

    parser.add_argument("--site", nargs="+", metavar="SPORTSBOOK", choices=all_books + ["all"], required=True, help=f"Two or more sportsbooks. Choices: {', '.join(all_books + ['all'])}")
    parser.add_argument("--sport", nargs="+", metavar="SPORT", choices=all_sports + ["all"], required=True, help=f"One or more sports. Choices: {', '.join(all_sports + ['all'])}")
    parser.add_argument("--interval", type=int, default=90, help="Time between scrape cycles in seconds")
    parser.add_argument("--headless", type=bool, default=False, help="Browser run in headless or non-headless mode")

    args = parser.parse_args()

    if "all" in args.site:
        selected_sites = ["draftkings", "betmgm", "fanduel", "bovada", "betrivers"]
    else:
        selected_sites = args.site

    if "all" in args.sport:
        selected_sports = ["nba", "nhl", "mlb"]
    else:
        selected_sports = args.sport

    interval = args.interval
    headless = args.headless

    status_thread = threading.Thread(target=status_bar, daemon=True)
    status_thread.start()

    i = 0
    while True:
        i += 1
        status["times_run"] = i
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        scrape(selected_sites, selected_sports, timestamp, headless)
        opps = find_arbitrage(timestamp)
        if opps:
            df = pd.DataFrame(opps)
            file_path = "../data/arbitrage/arbitrage_master.csv"
            df.to_csv(file_path, mode="a", index=False, encoding="utf-8")

        time.sleep(interval)

        snapshot_mlb = f"../data/cleaned_data/mlb/snapshots/{timestamp}.csv"
        if os.path.isfile(snapshot_mlb):
            os.remove(snapshot_mlb)
        snapshot_nba = f"../data/cleaned_data/nba/snapshots/{timestamp}.csv"
        if os.path.isfile(snapshot_nba):
            os.remove(snapshot_nba)
        snapshot_nhl = f"../data/cleaned_data/nhl/snapshots/{timestamp}.csv"
        if os.path.isfile(snapshot_nhl):
            os.remove(snapshot_nhl)