import json

from decimal import Decimal

from models import ShoppingItem

from config import (
    AUTOSAVE,
    SHOPPING_DIR,
)


def save_autosave(budget, items):

    data = {
        "budget": str(budget),
        "items": [i.to_dict() for i in items]
    }

    with open(AUTOSAVE, "w") as f:
        json.dump(data, f, indent=4)


def load_autosave():

    if not AUTOSAVE.exists():
        return Decimal("0.00"), []

    with open(AUTOSAVE) as f:
        data = json.load(f)

    budget = Decimal(data["budget"])

    items = [
        ShoppingItem.from_dict(x)
        for x in data["items"]
    ]

    return budget, items


def save_list(name, budget, items):

    file = SHOPPING_DIR / f"{name}.json"

    data = {
        "budget": str(budget),
        "items": [
            x.to_dict()
            for x in items
        ]
    }

    with open(file, "w") as f:
        json.dump(data, f, indent=4)


def load_list(name):

    file = SHOPPING_DIR / f"{name}.json"

    with open(file) as f:
        data = json.load(f)

    budget = Decimal(data["budget"])

    items = [
        ShoppingItem.from_dict(x)
        for x in data["items"]
    ]

    return budget, items


def get_lists():

    files = []

    for x in SHOPPING_DIR.glob("*.json"):
        files.append(x.stem)

    files.sort()

    return files
