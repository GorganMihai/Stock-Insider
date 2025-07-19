from utils import clear_screen, print_banner
from rich.console import Console
from rich.prompt import Prompt
from movers import display_movers
from watchlist import watchlist_menu

console = Console()

def main_menu():
    """Main CLI menu loop."""
    while True:
        clear_screen()
        print_banner()
        console.print("[bold white]Select an option:[/bold white]")
        console.print("[cyan]1[/cyan]: View Top 20 Gainers & Losers")
        console.print("[cyan]2[/cyan]: Watch List")
        console.print("[cyan]3[/cyan]: Exit")

        choice = Prompt.ask("Enter your choice")

        clear_screen()
        print_banner()

        if choice == "1":
            display_movers()
        elif choice == "2":
            watchlist_menu()
        elif choice == "3":
            console.print("[bold green]Goodbye![/bold green]")
            break
        else:
            console.print("[red]Invalid choice. Please try again.[/red]")

        input("\n[Press Enter to return to menu]")


if __name__ == "__main__":
    main_menu()
