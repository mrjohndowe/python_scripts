import csv
import json
from datetime import datetime

from taxes import calculate
from config import TXT_DIR, CSV_DIR, JSON_DIR


def export_txt(budget, items):

    tax = calculate(sum(i.total for i in items))

    filename = TXT_DIR / (
        datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".txt"
    )

    with open(filename, "w", encoding="utf-8") as f:

        f.write("=" * 60 + "\n")
        f.write("SHOPPING RECEIPT\n")
        f.write("=" * 60 + "\n\n")

        for item in items:

            f.write(
                f"{item.name:30}"
                f"${item.price:>8.2f}"
                f" x{item.quantity:<3}"
                f"${item.total:>10.2f}\n"
            )

        f.write("\n")

        f.write(f"Subtotal: ${tax['subtotal']:.2f}\n")
        f.write(f"State Tax: ${tax['state_tax']:.2f}\n")
        f.write(f"County Tax: ${tax['county_tax']:.2f}\n")
        f.write(f"City Tax: ${tax['city_tax']:.2f}\n")
        f.write(f"Sales Tax: ${tax['sales_tax']:.2f}\n")
        f.write(f"Grand Total: ${tax['grand_total']:.2f}\n")
        f.write(f"Remaining: ${(budget-tax['grand_total']):.2f}\n")

    return filename

def export_csv(budget, items):

    tax = calculate(sum(i.total for i in items))

    filename = CSV_DIR / (
        datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".csv"
    )

    with open(filename, "w", newline="", encoding="utf-8") as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow([
            "Item",
            "Price",
            "Quantity",
            "Item Total"
        ])

        for item in items:

            writer.writerow([
                item.name,
                item.price,
                item.quantity,
                item.total
            ])

        writer.writerow([])

        writer.writerow(["Subtotal", tax["subtotal"]])
        writer.writerow(["State Tax", tax["state_tax"]])
        writer.writerow(["County Tax", tax["county_tax"]])
        writer.writerow(["City Tax", tax["city_tax"]])
        writer.writerow(["Sales Tax", tax["sales_tax"]])
        writer.writerow(["Grand Total", tax["grand_total"]])
        writer.writerow(["Remaining", budget-tax["grand_total"]])

    return filename

def export_json(budget, items):

    tax = calculate(sum(i.total for i in items))

    filename = JSON_DIR / (
        datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".json"
    )

    data = {

        "budget": str(budget),

        "taxes": {

            "state": str(tax["state_tax"]),
            "county": str(tax["county_tax"]),
            "city": str(tax["city_tax"]),
            "sales_tax": str(tax["sales_tax"])
        },

        "grand_total": str(tax["grand_total"]),

        "items": [
            x.to_dict()
            for x in items
        ]
    }

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

    return filename
