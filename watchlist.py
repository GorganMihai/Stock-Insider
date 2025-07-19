import os
import time
import pandas as pd
import boto3
import openai
from botocore.exceptions import ClientError
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from utils import clear_screen, print_banner, show_loading
from utils import API_KEY

console = Console()

# S3 Configuration
S3_BUCKET_NAME = "csv-stock-bucket-2025"
S3_OBJECT_KEY = "watchlist.csv"

# Local Data Directory Setup
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

WATCHLIST_FILE = os.path.join(DATA_DIR, "watchlist.csv")

# boto3 client for S3
s3_client = boto3.client("s3")


def download_watchlist_from_s3():
    show_loading("Loading...")
    try:
        s3_client.download_file(S3_BUCKET_NAME, S3_OBJECT_KEY, WATCHLIST_FILE)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code in ['NoSuchKey', '404']:
            console.print("[orange1]File watchlist.csv not found on S3, creating an empty one and uploading it...[/orange1]")
            columns = ["Symbol", "Company", "YTD Return", "6 Months Return", "1 Week Return"]
            example_data = [
                ["AAPL", "Apple Inc.", "x", "x", "x"],
                ["GOOG", "Alphabet Inc.", "x", "x", "x"],
                ["AMZN", "Amazon.com Inc.", "x", "x", "x"],
                ["TSLA", "Tesla Inc.", "x", "x", "x"],
            ]
            df = pd.DataFrame(example_data, columns=columns)
            df.to_csv(WATCHLIST_FILE, index=False)
            upload_watchlist_to_s3()
        else:
            raise e


def upload_watchlist_to_s3():
    s3_client.upload_file(WATCHLIST_FILE, S3_BUCKET_NAME, S3_OBJECT_KEY)


def ensure_watchlist_file():
    download_watchlist_from_s3()


def display_watchlist():
    ensure_watchlist_file()
    df = pd.read_csv(WATCHLIST_FILE)
    if df.empty:
        console.print("[bold orange1]📭 Watch list is empty.[/bold orange1]")
    else:
        table = Table(title="👀 Your Watch List")
        for col in df.columns:
            table.add_column(col, style="cyan", justify="left")
        for _, row in df.iterrows():
            table.add_row(*[str(row[col]) for col in df.columns])
        console.print(table)


def add_stock_by_symbol(symbol):
    ensure_watchlist_file()
    df = pd.read_csv(WATCHLIST_FILE)
    symbol = symbol.upper()
    if symbol in df["Symbol"].values:
        console.print(f"[orange1]{symbol} is already in the watch list.[/orange1]")
        return

    new_row = {
        "Symbol": symbol,
        "Company": "x",
        "YTD Return": "x",
        "6 Months Return": "x",
        "1 Week Return": "x"
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(WATCHLIST_FILE, index=False)
    upload_watchlist_to_s3()
    console.print(f"[green]{symbol} added to watch list.[/green]")


def add_to_watchlist():
    ensure_watchlist_file()
    symbol = Prompt.ask("Enter the stock symbol to add").upper()
    add_stock_by_symbol(symbol)


def delete_from_watchlist():
    ensure_watchlist_file()
    df = pd.read_csv(WATCHLIST_FILE)
    symbol = Prompt.ask("Enter the stock symbol to delete").upper()

    if symbol not in df["Symbol"].values:
        console.print(f"[red]{symbol} not found in the watch list.[/red]")
        return

    df = df[df["Symbol"] != symbol]
    df.to_csv(WATCHLIST_FILE, index=False)
    upload_watchlist_to_s3()
    console.print(f"[green]{symbol} removed from watch list.[/green]")


import openai

def analyze_watchlist():
    # Ensure the watchlist CSV file is downloaded from S3
    ensure_watchlist_file()
    df = pd.read_csv(WATCHLIST_FILE)
    
    if df.empty:
        console.print("[orange1]Nothing to analyze, watch list is empty.[/orange1]")
        return

    console.print("[bold blue]🔍 Analyzing Watch List with AI...[/bold blue]")

    # Convert DataFrame to CSV string without index
    csv_text = df.to_csv(index=False)

    # Prepare the prompt to send to OpenAI
    prompt_text = (
        "You are a financial data assistant. Given the following stock watchlist CSV data with columns:\n"
        "Symbol, Company, YTD Return, 6 Months Return, 1 Week Return.\n"
        "Analyze the stocks and provide a brief comment for each stock symbol based on the data.\n"
        "Return a list with Symbol and your comment.\n\n"
        + csv_text
    )

        
    try:
        # Initialize OpenAI client with API key
        client = openai.OpenAI(api_key=API_KEY)

        # Create a chat completion request
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful financial assistant."},
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.5,
            max_tokens=500,
        )

        # Extract the AI's response content
        answer = response.choices[0].message.content.strip()
        
        # Print the AI's analysis to the console in green
        console.print("[green]" + answer + "[/green]")

    except Exception as e:
        # Print any errors that occur during the API call
        console.print(f"[red]Error calling OpenAI API: {e}[/red]")



def watchlist_menu():
    while True:
        console.print("[bold white]Watch List Menu:[/bold white]")
        console.print("[cyan]1[/cyan]: Display Watch List")
        console.print("[cyan]2[/cyan]: Analyze Watch List (AI)")
        console.print("[cyan]3[/cyan]: Add to Watch List")
        console.print("[cyan]4[/cyan]: Delete from Watch List")
        console.print("[cyan]5[/cyan]: Back to Main Menu")

        choice = Prompt.ask("Choose an option")

        clear_screen()
        print_banner()

        if choice == "1":
            display_watchlist()
        elif choice == "2":
            analyze_watchlist()
        elif choice == "3":
            add_to_watchlist()
        elif choice == "4":
            delete_from_watchlist()
        elif choice == "5":
            break
        else:
            console.print("[red]Invalid choice. Try again.[/red]")

        input("\n[Press Enter to continue]")
