from rich.panel import Panel
from rich.table import Table
from rich.align import Align


def main_menu(console):

    while True:

        console.clear()

        table = Table.grid(expand=True)

        table.add_row("[bold cyan]Budget[/bold cyan]", "[green]$0.00[/green]")
        table.add_row("[bold cyan]Items[/bold cyan]", "[yellow]0[/yellow]")

        console.print(
            Panel(
                Align.center(table),
                title="[bold white]DOWE SHOPPING CALCULATOR[/bold white]",
                border_style="cyan",
            )
        )

        menu = Table(
            show_header=False,
            box=None,
            padding=(0, 2),
            expand=True,
        )

        menu.add_row("[cyan]1[/cyan]", "Add Item")
        menu.add_row("[cyan]2[/cyan]", "Remove Item")
        menu.add_row("[cyan]3[/cyan]", "Edit Item")
        menu.add_row("[cyan]4[/cyan]", "Shopping Cart")
        menu.add_row("[cyan]5[/cyan]", "Print Receipt")
        menu.add_row("[cyan]6[/cyan]", "Save Shopping List")
        menu.add_row("[cyan]7[/cyan]", "Load Shopping List")
        menu.add_row("[cyan]8[/cyan]", "Shopping History")
        menu.add_row("[cyan]9[/cyan]", "Export Receipt")
        menu.add_row("[cyan]10[/cyan]", "Settings")
        menu.add_row("[cyan]11[/cyan]", "Statistics")
        menu.add_row("[red]0[/red]", "Exit")

        console.print(
            Panel(
                menu,
                border_style="bright_blue",
            )
        )

        choice = console.input("\n[bold green]> [/bold green]")

        if choice == "0":
            break

        console.print(
            f"\n[bold yellow]Option {choice} isn't implemented yet.[/bold yellow]"
        )

        input("\nPress ENTER...")
