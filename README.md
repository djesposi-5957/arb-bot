# Sports Betting Arbitrage Detection System

## Author
Dominic Esposito  
DSCI 510 Final Project

---

# Project Overview

This project is an automated sports betting arbitrage detection system built using Python, Selenium, Pandas, and The Odds API.

The purpose of the project is to collect sportsbook odds data from multiple sources, normalize and integrate the data into a unified structure, and automatically identify arbitrage opportunities between sportsbooks.

The system continuously gathers betting odds across multiple sports and analyzes pricing inefficiencies that create guaranteed profit opportunities.

---

# Sportsbooks Used

## Selenium Scraping
- DraftKings
- BetMGM

## API Collection
- FanDuel
- Bovada
- BetRivers


---

# Sports Covered

- NBA
- MLB
- NHL

---

# Technologies Used

- Python
- Selenium
- Pandas
- Matplotlib
- Seaborn
- Requests
- BeautifulSoup
- The Odds API

---

# Important Selenium Notes

The Selenium sportsbooks (DraftKings and BetMGM) may occasionally stop functioning correctly.

Sports betting websites actively attempt to prevent automated scraping and frequently change:
- HTML structure
- CSS classes
- JavaScript rendering behavior
- Dynamic page loading

Because of this, selectors that work one day may fail the next after website updates.

If scraping suddenly stops working:
- Re-check XPath selectors
- Verify CSS selectors still exist
- Check dynamic loading behavior
- Increase Selenium waits if necessary

This is expected behavior when scraping gambling websites.

Additionally, some sportsbooks behaved differently in headless mode during development. Certain elements only loaded correctly when the browser window was visible.

---

# Data Collection

The project collects sportsbook odds data approximately every 90 seconds.

The system:
1. Pulls sportsbook odds data
2. Cleans and normalizes records
3. Integrates data into unified DataFrames
4. Detects arbitrage opportunities
5. Stores results
6. Generates visualizations

Upcoming games are prioritized because live betting odds fluctuate too rapidly and can introduce inconsistencies during arbitrage calculations.

---

# Data Cleaning

The cleaning pipeline standardizes:
- Team names
- Odds formatting
- Event identifiers
- Unicode characters
- Time formatting

Examples:
- `"NY Yankees"` → `"Yankees"`
- `"Montréal Canadiens"` → `"Montreal Canadiens"`

The cleaning process also converts all timestamps into UTC format.

---

# Integrated Data Model

The cleaned sportsbook data is normalized into a shared structure containing:

| Column | Description |
|---|---|
| sportsbook | Sportsbook source |
| sport | NBA / MLB / NHL |
| game_id | Standardized game identifier |
| team | Team name |
| odds_decimal | Decimal betting odds |
| commence_time | Event start time |
| status | upcoming/live |
| scrape_time | Data collection timestamp |

Games are linked across sportsbooks using normalized team names and canonical event identifiers.

Example game ID:

```python
lakers__warriors
```

# Arbitrage Detection Logic

For each sporting event:
1. The system identifies the best available odds for both teams
2. Odds are converted into implied probabilities
3. Implied probabilities are summed
4. If the total is below 1, an arbitrage opportunity exists

Formula:

```python
(1 / odds_team_a) + (1 / odds_team_b) < 1
```

Profit Margin:

```python
(1 - implied_probability_sum) * 100
```

---
# Visualizations Generated

The project generates:
- Arbitrage frequency over time
- Arbitrage opportunities by sport
- Profit margin distributions
- Average profit margin by sport
- Arbitrage opportunities by hour
- Sportsbook pairing comparisons
- Sportsbook heatmaps

---

# Installation

Clone the repository:

```bash
git clone https://github.com/djesposi-5957/arb-bot.git
cd arb-bot
```
Create virtual environment:
```python
python -m venv venv
```
Activate environment on Windows:
```python
venv\Scripts\activate
```
Install dependencies:
```python
pip install -r requirements.txt
```

---

# Running the Project

Run the main pipeline:
```python
python main.py
```
The main script handles:

- Data collection
- Data cleaning
- Arbitrage detection
- Data storage

To visualize the data:
```python
python visualizer.py
```
- Handles graph generation

---

# API Notes
This project uses The Odds API.

Depending on API limitations, request intervals may need to be adjusted.

During development:

- ~90 second intervals were used
- upcoming games were prioritized
- live games were excluded from arbitrage analysis

# Project Structure

```text
DSCI510_Project/
│
├── README.md
├── requirements.txt
├── proposal.pdf
│
├── data/
│   ├── arbitrage/
│   │   └── arbitrage_master.csv
│   │
│   ├── cleaned_data/
│   │   ├── mlb/
│   │   │   ├── snapshots/
│   │   │   └── mlb_master.csv
│   │   │
│   │   ├── nba/
│   │   │   ├── snapshots/
│   │   │   └── nba_master.csv
│   │   │
│   │   └── nhl/
│   │       ├── snapshots/
│   │       └── nhl_master.csv
│   │
│   └── raw_data/
│       ├── mlb/
│       ├── nba/
│       └── nhl/
│
├── results/
│   └── final_report.pdf
│
├── src/
│   ├── arbitrage.py
│   ├── cleaner.py
│   ├── main.py
│   ├── normalizer.py
│   ├── visualizer.py
│   │
│   └── scrapers/
│       ├── betmgm.py
│       ├── draftkings.py
│       └── theodds.py

```

