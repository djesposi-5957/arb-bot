import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse


def opportunities_over_time(df):
    # Remove rows where time or profit margin don't exist (happens occasionally with Betmgm and Draftkings scrapers)
    df = df.dropna(subset=["time", "profit_margin"])

    # There can be many arbitrage opportunities per hour so this groups them together, then resets back to normal df
    freq_df = df.groupby(df["time"].dt.floor("h")).size()
    freq_df = freq_df.reset_index()
    # Renames columns
    freq_df.columns = [
        "time",
        "opportunity_count"
    ]

    plt.figure(figsize=(12, 6))
    plt.plot(freq_df["time"], freq_df["opportunity_count"], marker="o")
    plt.title("Frequency of Arbitrage Opportunities Over Time")
    plt.xlabel("Time")
    plt.ylabel("Number of Opportunities")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def opportunities_per_sport(df):
    # Counts number of times sport is present in df
    sport_counts = df["sport"].value_counts()

    plt.figure(figsize=(8, 5))
    plt.bar(sport_counts.index, sport_counts.values)
    plt.title("Arbitrage Opportunities by Sport")
    plt.xlabel("Sport")
    plt.ylabel("Number of Opportunities")
    plt.show()


def profit_margins_totals(df):
    # 20 bins was chosen as there are a wide range of profit margins
    plt.figure(figsize=(10, 6))
    plt.hist(df["profit_margin"], bins=20, rwidth=0.9)

    plt.title("Distribution of Arbitrage Profit Margins")
    plt.xlabel("Profit Margin (%)")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.show()


def profit_margins_sport(df):
    # Create separate df of mean profit margins with their associated sport
    avg_profit = (df.groupby("sport")["profit_margin"].mean())

    plt.figure(figsize=(8, 5))
    plt.bar(avg_profit.index, avg_profit.values)
    plt.title("Average Profit Margin by Sport")
    plt.xlabel("Sport")
    plt.ylabel("Average Profit Margin (%)")
    plt.tight_layout()
    plt.show()


def arbitrage_per_hour(df):
    # Group by hours and count number of rows per hour since each hour is an arbitrage opportunity
    hours = df["time"].dt.hour
    hourly_groups = df.groupby(hours)
    hourly_counts = hourly_groups.size()

    plt.figure(figsize=(10, 5))
    plt.bar(hourly_counts.index, hourly_counts.values)
    plt.title("Arbitrage Opportunities by Hour")
    plt.xlabel("Hour of Day")
    plt.ylabel("Opportunity Count")
    plt.tight_layout()
    plt.show()


def best_sportsbook_pairings(df):
    # Group rows by pairs of sportsbooks
    sportsbook_groups = df.groupby(["sportsbook_a", "sportsbook_b"])
    # Count rows of each pair, sort from largest to smallest, and keep largest 10 incase more books are added
    pair_counts = sportsbook_groups.size()
    pair_counts = pair_counts.sort_values(ascending=False)
    pair_counts = pair_counts.head(10)

    # Make list of sportsbook pairs
    labels = []
    for a, b in pair_counts.index:
        labels.append(f"{a} vs {b}")

    plt.figure(figsize=(12, 6))
    plt.bar(labels, pair_counts.values)
    plt.title("Top Sportsbook Pairings for Arbitrage")
    plt.xlabel("Sportsbook Pair")
    plt.ylabel("Opportunity Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def sportsbook_heatmap(df):
    # Group rows by pairs of sportsbooks
    book_groups = df.groupby(["sportsbook_a", "sportsbook_b"])
    # Count rows of each pair and turn back into df
    heatmap_df = book_groups.size()
    heatmap_df = heatmap_df.reset_index()
    # Heatmap df column names
    heatmap_df.columns = [
        "sportsbook_a",
        "sportsbook_b",
        "opportunity_count"
    ]
    # Shapes df into grid with sportsbook_a as rows sportsbook_b as columns and opportunity_count as values
    heatmap_table = heatmap_df.pivot(index="sportsbook_a", columns="sportsbook_b", values="opportunity_count")
    heatmap_table = heatmap_table.fillna(0)

    plt.figure(figsize=(10, 8))
    sns.heatmap(heatmap_table, annot=True, fmt=".0f", cmap="Reds")
    plt.title("Sportsbook Pairs Producing Arbitrage Opportunities")
    plt.xlabel("Sportsbook B")
    plt.ylabel("Sportsbook A")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Visualize arbitrage opportunity data collected from sportsbooks.")

    parser.add_argument("--all", action="store_true", help="Generate all visualizations")
    parser.add_argument("--ot", action="store_true", help="Frequency of Arbitrage Opportunities Over Time")
    parser.add_argument("--os", action="store_true", help="Arbitrage Opportunities by Sport")
    parser.add_argument("--pt", action="store_true", help="Distribution of Arbitrage Profit Margins")
    parser.add_argument("--ps", action="store_true", help="Average Profit Margin by Sport")
    parser.add_argument("--ah", action="store_true", help="Arbitrage Opportunities by Hour")
    parser.add_argument("--bp", action="store_true", help="Top Sportsbook Pairings for Arbitrage")
    parser.add_argument("--hm", action="store_true", help="Sportsbook Pairs Producing Arbitrage Opportunities heatmap")

    args = parser.parse_args()

    # Read CSV and eliminate duplicate rows
    df = pd.read_csv("data/arbitrage/arbitrage_master.csv")
    df = df[df["sport"] != "sport"].copy()
    # Format time and profit margin for calculation
    df["time"] = pd.to_datetime(df["time"], format="%Y%m%d_%H%M%S")
    df["profit_margin"] = (df["profit_margin"].str.replace("%", "", regex=False).astype(float))

    if args.all:
        opportunities_over_time(df)
        opportunities_per_sport(df)
        profit_margins_totals(df)
        profit_margins_sport(df)
        arbitrage_per_hour(df)
        best_sportsbook_pairings(df)
        sportsbook_heatmap(df)
    if args.ot:
        opportunities_over_time(df)
    if args.os:
        opportunities_per_sport(df)
    if args.pt:
        profit_margins_totals(df)
    if args.ps:
        profit_margins_sport(df)
    if args.ah:
        arbitrage_per_hour(df)
    if args.bp:
        best_sportsbook_pairings(df)
    if args.hm:
        sportsbook_heatmap(df)
