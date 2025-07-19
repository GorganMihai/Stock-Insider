import os
import time
from pyfiglet import figlet_format
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
import pandas as pd

API_KEY = "OpenAI API key"

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    banner = figlet_format("Stock Insider", font="slant")
    console.print(f"[bold cyan]{banner}[/bold cyan]")


def show_loading(message="Loading..."):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        transient=True,
    ) as progress:
        task = progress.add_task(f"[cyan]{message}", total=100)
        for _ in range(10):
            progress.update(task, advance=10)
            time.sleep(0.05)


def get_raw_value(value):
    if isinstance(value, dict):
        return value.get("raw", None)
    return value


def format_percent(value):
    if pd.isnull(value):
        return "-"
    color = "green" if value >= 0 else "red"
    return f"[{color}]{value:+.2f}%[/{color}]"


def format_price(value):
    return f"${value:.2f}" if pd.notnull(value) else "-"


def format_volume(value):
    return f"{int(value):,}" if pd.notnull(value) else "-"
