import requests
import pandas as pd
import time
from datetime import datetime
from rich.console import Console
from rich.columns import Columns
from rich.table import Table
from rich.prompt import Prompt
from watchlist import add_stock_by_symbol
from utils import show_loading, get_raw_value, format_price, format_percent, format_volume

console = Console()

def fetch_top_movers():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    endpoints = {
        "gainers": "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?formatted=true&scrIds=day_gainers&count=20",
        "losers": "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?formatted=true&scrIds=day_losers&count=20",
    }

    movers = {}
    for label, url in endpoints.items():
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"{response.status_code} {response.reason} for {label}")
        data = response.json()
        quotes = data["finance"]["result"][0]["quotes"]
        df = pd.DataFrame([
            {
                "symbol": quote.get("symbol"),
                "price": get_raw_value(quote.get("regularMarketPrice")),
                "percentChange": get_raw_value(quote.get("regularMarketChangePercent")),
                "volume": get_raw_value(quote.get("regularMarketVolume")),
            }
            for quote in quotes
        ])
        movers[label] = df
    return movers


def create_table(df, title):
    table = Table(title=title, expand=True)
    table.add_column("Symbol", justify="left", style="bold")
    table.add_column("Price", justify="right")
    table.add_column("% Change", justify="right")
    table.add_column("Volume", justify="right")

    for _, row in df.iterrows():
        table.add_row(
            row["symbol"],
            format_price(row["price"]),
            format_percent(row["percentChange"]),
            format_volume(row["volume"])
        )
    return table

def display_movers():
    try:
        show_loading("Fetching stock data...")
        movers = fetch_top_movers()
    except Exception as e:
        console.print(f"[red]Error fetching data:[/red] {e}")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    console.print(f"[bold yellow]📊 Stock Movers - {today}[/bold yellow]")
    console.rule("", style="green")

    gainers_table = create_table(movers["gainers"], "🏆 Top 20 Gainers")
    losers_table = create_table(movers["losers"], "📉 Top 20 Losers")

    console.print(Columns([gainers_table, losers_table], padding=(1, 4)))
    
    console.print("\n[bold cyan]Would you like to add a stock to your Watch List?[/bold cyan]")
    answer = Prompt.ask("Enter a stock symbol to add or press Enter to skip", default="").upper()

    if answer:
        add_stock_by_symbol(answer)


