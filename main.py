import argparse
from scrapers.draftkings import DraftKingsScraper
from scrapers.betmgm import BetMGMScraper
from scrapers.theodds import TheOddsApiCall

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

if one_site:
    for site in selected_sites:
        scraper = scrapers[site]()

        for sport in selected_sports:
            data = scraper.fetch_data(sport)