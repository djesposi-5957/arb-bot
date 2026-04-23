import time
from curl_cffi import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class BetMGMScraper:
    def __init__(self):
        self.name = "BetMGM"
        self.url = ("https://www.az.betmgm.com/")

    def fetch_response(self):
        try:
            resposne = requests.get(self.url, impersonate="chrome")
            return resposne
        except:
            return None

    def american_to_decimal(self, odds_str):
        odds_str = odds_str.strip().replace("−", "-")
        odds = int(odds_str)
        if odds > 0:
            return round(1 + (odds / 100), 3)
        else:
            return round(1 + (100 / abs(odds)), 3)

    def fetch_sport_url(self, sport):
        if sport == "nba":
            NBA_url = f"{self.url}en/sports/basketball-7/betting/usa-9/nba-6004"
            return NBA_url
        if sport == "nhl":
            NHL_url = f"{self.url}en/sports/hockey-12/betting/usa-9/nhl-34"
            return NHL_url
        if sport == "mlb":
            MLB_url = f"{self.url}en/sports/baseball-23/betting/usa-9/mlb-75"
            return MLB_url

    def start_driver(self):
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome()
        return driver

    def convert_time(self, date, time):
        now = datetime.now(ZoneInfo("America/Los_Angeles"))
        date_text = date.strip()
        time_text = time.replace("\u202f", " ")

        if date_text.lower() == "today":
            game_date = now.date()
        elif date_text.lower() == "tomorrow":
            game_date = (now + timedelta(days=1)).date()
        else:
            game_date = datetime.strptime(date_text, "%m/%d/%y").date()

        local_time = datetime.strptime(time_text, "%I:%M %p").time()
        local_dt = datetime.combine(game_date, local_time)
        local_dt = local_dt.replace(tzinfo=ZoneInfo("America/Los_Angeles"))

        utc_dt = local_dt.astimezone(ZoneInfo("UTC"))

        return utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    def fetch_data(self, sport):
        response = self.fetch_response()

        if response is None:
            return None

        data_list = []
        driver = self.start_driver()
        scrape_sport = self.fetch_sport_url(sport)
        driver.get(scrape_sport)

        time.sleep(5)

        elements = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/en/sports/events/"]')

        links = []
        for el in elements:
            href = el.get_attribute("href")
            if href:
                links.append(href)

        for game in links:
            driver.get(game)
            time.sleep(3)
            rows = driver.find_elements(By.CSS_SELECTOR, "ms-six-pack-option-group .option-row")
            scoreboard = driver.find_element(By.TAG_NAME, "ms-prematch-scoreboard")
            date_text = scoreboard.find_element(By.CSS_SELECTOR, ".event-time .date").text.strip()
            time_text = scoreboard.find_element(By.CSS_SELECTOR, ".event-time .time").text.strip()



            records = []

            for row in rows:
                try:

                    team = row.find_element(By.CSS_SELECTOR, "div.six-pack-player-name span").text.strip()
                    options = row.find_elements(By.CSS_SELECTOR, "div.options-container ms-option")

                    if len(options) < 3:

                        continue

                    moneyline_span = options[2].find_elements(By.CSS_SELECTOR, "span.custom-odds-value-style")
                    if not moneyline_span:
                        continue

                    moneyline_odds = moneyline_span[0].text.strip()

                    records.append({
                        "team": team,
                        "odds_american": moneyline_odds
                    })

                except Exception as e:
                    print("Row failed:", e)

            if len(records) != 0:
                data_team = {
                    "sportsbook": self.name,
                    "sport": sport,
                    "teamA": records[0]["team"],
                    "moneylineA": records[0]["odds_american"],
                    "odds_decimalA": self.american_to_decimal(records[0]["odds_american"]),
                    "teamB": records[1]["team"],
                    "moneylineB": records[1]["odds_american"],
                    "odds_decimalB": self.american_to_decimal(records[1]["odds_american"]),
                    "game_url": game,
                    "commence_time": self.convert_time(date_text, time_text),
                    "time": time.asctime(time.localtime())
                }

                data_list.append(data_team)
        return data_list

app = BetMGMScraper()
print(app.fetch_data("nba"))