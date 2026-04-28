from curl_cffi import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import re
import json


class DraftKingsScraper:
    def __init__(self):
        self.name = "Draft Kings"
        self.url = "https://sportsbook.draftkings.com/"

    def fetch_response(self):
        try:
            response = requests.get(self.url, impersonate="chrome")

            return response
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
            NBA_url = f"{self.url}leagues/basketball/nba"
            return NBA_url
        if sport == "nhl":
            NHL_url = f"{self.url}leagues/hockey/nhl"
            return NHL_url
        if sport == "mlb":
            MLB_url = f"{self.url}leagues/baseball/mlb"
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

            cleaned_date = re.sub(r'(\d{1,2})(st|nd|rd|th)', r'\1', date_text)

            parts = cleaned_date.split()
            month_day = " ".join(parts[1:])

            game_date = datetime.strptime(month_day,  "%b %d").date()
            game_date = game_date.replace(year=now.year)

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
        time.sleep(3)
        link_elements = WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, 'a[data-testid="lp-nav-link"]')
            )
        )

        links = []

        for element in link_elements:
            href = element.get_attribute("href")
            if href and href not in links and href[-4:] == "true":
                links.append(href)

        for game in links:
            driver.get(game)
            time.sleep(1)
            try:
                time_element = driver.find_element(By.CSS_SELECTOR, 'p[data-testid="scoreboard-date"]')
                start_time = time_element.text
                parts = start_time.split()
                if parts[0].lower() in ["today", "tomorrow"]:
                    date_text = parts[0]
                    time_text = " ".join(parts[1:])
                    commence_time = self.convert_time(date_text, time_text)
                else:
                    date_text = " ".join(parts[0:3])
                    time_text = " ".join(parts[3:])
                    commence_time = self.convert_time(date_text, time_text)

            except NoSuchElementException:
                commence_time = None
            except Exception:
                commence_time = None

            teams = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'p[data-testid="market-label"')))
            buttons = driver.find_elements(By.CSS_SELECTOR, 'button[data-testid="market-button"')
            bttn_list = []
            for btn in buttons:
                bttn_list.append(btn.text)

            moneyline_odds = [item.strip() for item in bttn_list if "\n" not in item]


            team_names = [t.text.strip() for t in teams]

            data_team = {
                "sportsbook": self.name,
                "sport": sport,
                "teamA": team_names[0].lower(),
                "moneylineA": moneyline_odds[0],
                "odds_decimalA": self.american_to_decimal(moneyline_odds[0]),
                "teamB": team_names[1].lower(),
                "moneylineB": moneyline_odds[1],
                "odds_decimalB": self.american_to_decimal(moneyline_odds[1]),
                "game_url": game,
                "commence_time": commence_time,
                "time":  datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                }



            data_list.append(data_team)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"data/raw_data/{sport}/{sport}_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data_list, f, indent=2)
        return data_list



