Right now the script just scrapes the data off one website "DraftKings". You can choose one of three sports to scrape
data from: NBA, NHL, or MLB assuming that the sport is in season.
1. Install requirements from requirements.txt
2. Run script with following flags for standard output main.py --site draftkings --sport [MLB, NBA, NHL]
3. Run script N times: main.py 10 --site draftkings --sport [MLB, NBA, NHL]
    This will print the first 10 entries
4. main.py --site draftkings --sport [MLB, NBA, NHL] --save <path_to_dataset>
NOTE: selenium is being used in a headless mode, thus if you make too many requests in a short time span the website
will deny access. This won't be a problem in the final version as a time.sleep() function will be implemented before
each round of scraping.