from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align

from taxes import calculate


console = Console()


def receipt_standard(budget, items):

    tax = calculate(sum(i.total for i in items))

    console.clear()

    console.print(
        Panel.fit(
            "[bold cyan]SHOPPING RECEIPT[/bold cyan]",
            border_style="bright_blue"
        )
    )

    table = Table()

    table.add_column("ITEM", style="cyan")
    table.add_column("PRICE", justify="right")
    table.add_column("QTY", justify="center")
    table.add_column("ITEM TOTAL", justify="right")

    for item in items:

        table.add_row(
            item.name,
            f"${item.price:.2f}",
            str(item.quantity),
            f"${item.total:.2f}"
        )

    console.print(table)

    console.print()

    totals = Table(show_header=False)

    totals.add_row(
        "[yellow]Subtotal[/yellow]",
        f"${tax['subtotal']:.2f}"
    )

    totals.add_row(
        f"{tax['state_name']} ({tax['state_rate']*100:.1f}%)",
        f"${tax['state_tax']:.2f}"
    )

    totals.add_row(
        f"{tax['county_name']} ({tax['county_rate']*100:.1f}%)",
        f"${tax['county_tax']:.2f}"
    )

    totals.add_row(
        f"{tax['city_name']} ({tax['city_rate']*100:.1f}%)",
        f"${tax['city_tax']:.2f}"
    )

    totals.add_row(
        "[bold green]Sales Tax[/bold green]",
        f"[green]${tax['sales_tax']:.2f}[/green]"
    )

    totals.add_row(
        "[bold cyan]Grand Total[/bold cyan]",
        f"[bold cyan]${tax['grand_total']:.2f}[/bold cyan]"
    )

    totals.add_row(
        "Budget",
        f"${budget:.2f}"
    )

    totals.add_row(
        "[bold yellow]Remaining[/bold yellow]",
        f"[bold yellow]${budget-tax['grand_total']:.2f}[/bold yellow]"
    )

    console.print(totals)


def receipt_store(budget, items):

    tax = calculate(sum(i.total for i in items))

    console.clear()

    console.print(
        Panel.fit(
            "[bold green]DOWE SHOPPING CALCULATOR[/bold green]\n"
            "Pueblo, Colorado",
            border_style="green"
        )
    )

    for item in items:

        console.print(item.name, style="cyan")

        console.print(
            f"   ${item.price:.2f} x {item.quantity}",
            f"[bold yellow]${item.total:.2f}[/bold yellow]"
        )

        console.print()

    console.rule()

    console.print(
        f"Subtotal:        ${tax['subtotal']:.2f}"
    )

    console.print(
        f"State Tax:       ${tax['state_tax']:.2f}"
    )

    console.print(
        f"County Tax:      ${tax['county_tax']:.2f}"
    )

    console.print(
        f"City Tax:        ${tax['city_tax']:.2f}"
    )

    console.rule()

    console.print(
        f"[bold green]TOTAL: ${tax['grand_total']:.2f}[/bold green]"
    )

    console.print(
        f"Remaining: ${budget-tax['grand_total']:.2f}"
    )


def receipt_detailed(budget, items):

    tax = calculate(sum(i.total for i in items))

    console.clear()

    console.print(
        Panel.fit(
            "[bold magenta]SHOPPING REPORT[/bold magenta]",
            border_style="magenta"
        )
    )

    table = Table(show_lines=True)

    table.add_column("#")

    table.add_column("Item")

    table.add_column("Price")

    table.add_column("Qty")

    table.add_column("Total")

    qty = 0

    for index, item in enumerate(items, start=1):

        qty += item.quantity

        table.add_row(
            str(index),
            item.name,
            f"${item.price:.2f}",
            str(item.quantity),
            f"${item.total:.2f}"
        )

    console.print(table)

    console.print()

    console.print(
        f"Items Purchased : [cyan]{qty}[/cyan]"
    )

    console.print(
        f"Unique Items    : [cyan]{len(items)}[/cyan]"
    )

    console.print(
        f"Subtotal        : [yellow]${tax['subtotal']:.2f}[/yellow]"
    )

    console.print()

    console.print("[bold]Sales Taxes[/bold]")

    console.print(
        f"Colorado State : ${tax['state_tax']:.2f}"
    )

    console.print(
        f"Pueblo County  : ${tax['county_tax']:.2f}"
    )

    console.print(
        f"City of Pueblo : ${tax['city_tax']:.2f}"
    )

    console.print()

    console.print(
        f"[green]Sales Tax : ${tax['sales_tax']:.2f}[/green]"
    )

    console.print(
        f"[bold cyan]Grand Total : ${tax['grand_total']:.2f}[/bold cyan]"
    )

    console.print(
        f"Remaining Budget : ${budget-tax['grand_total']:.2f}"
    )
