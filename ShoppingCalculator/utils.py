from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()


def pause():

    input("\nPress ENTER to continue...")


def header(title):

    console.clear()

    console.print(
        Panel.fit(
            f"[bold cyan]{title}[/bold cyan]",
            border_style="bright_blue",
        )
    )


def ask(text):

    return Prompt.ask(text)


def ask_int(text):

    while True:

        try:
            return int(Prompt.ask(text))

        except ValueError:
            console.print("[red]Please enter a number.[/red]")


def ask_float(text):

    while True:

        try:
            return float(Prompt.ask(text))

        except ValueError:
            console.print("[red]Invalid number.[/red]")


def yes_no(question):

    return Confirm.ask(question)
