from decimal import Decimal
from pathlib import Path

APP_NAME = "Dowe Shopping Calculator"
VERSION = "1.0"

BASE_DIR = Path(__file__).parent

DATA_DIR = BASE_DIR / "data"
SHOPPING_DIR = DATA_DIR / "shopping_lists"
HISTORY_DIR = DATA_DIR / "history"

RECEIPTS_DIR = BASE_DIR / "receipts"
TXT_DIR = RECEIPTS_DIR / "txt"
CSV_DIR = RECEIPTS_DIR / "csv"
JSON_DIR = RECEIPTS_DIR / "json"

AUTOSAVE = DATA_DIR / "autosave.json"
SETTINGS = DATA_DIR / "settings.json"

for folder in (
    DATA_DIR,
    SHOPPING_DIR,
    HISTORY_DIR,
    RECEIPTS_DIR,
    TXT_DIR,
    CSV_DIR,
    JSON_DIR,
):
    folder.mkdir(parents=True, exist_ok=True)

STATE_NAME = "Colorado"
COUNTY_NAME = "Pueblo County"
CITY_NAME = "City of Pueblo"

STATE_TAX = Decimal("0.029")
COUNTY_TAX = Decimal("0.010")
CITY_TAX = Decimal("0.037")

TOTAL_TAX = STATE_TAX + COUNTY_TAX + CITY_TAX

DEFAULT_BUDGET = Decimal("0.00")
