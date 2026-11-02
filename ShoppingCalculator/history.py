import json

from datetime import datetime

from config import HISTORY_DIR

from taxes import calculate


def save_history(budget, items):

    tax = calculate(sum(i.total for i in items))

    filename = HISTORY_DIR / (
        datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".json"
    )

    data = {

        "date": datetime.now().isoformat(),

        "budget": str(budget),

        "subtotal": str(tax["subtotal"]),

        "sales_tax": str(tax["sales_tax"]),

        "grand_total": str(tax["grand_total"]),

        "items": [
            x.to_dict()
            for x in items
        ]
    }

    with open(filename, "w") as f:
        json.dump(data, f, indent=4)


def get_history():

    files = []

    for file in HISTORY_DIR.glob("*.json"):

        files.append(file)

    files.sort(reverse=True)

    return files
