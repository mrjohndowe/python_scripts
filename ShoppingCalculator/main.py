from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout

from menu import main_menu

console = Console()


def splash():

    console.clear()

    console.print()

    console.print(
        Panel.fit(
            "[bold cyan]DOWE SHOPPING CALCULATOR[/bold cyan]\n"
            "[green]Version 1.0[/green]\n\n"
            "[yellow]Pueblo, Colorado Sales Tax[/yellow]",
            border_style="bright_blue",
        )
    )

    console.print()

    main_menu(console)


if __name__ == "__main__":
    splash()
