from decimal import Decimal, ROUND_HALF_UP

from config import (
    STATE_NAME,
    COUNTY_NAME,
    CITY_NAME,
    STATE_TAX,
    COUNTY_TAX,
    CITY_TAX,
)


TWOPLACES = Decimal("0.01")


def money(value):
    return Decimal(value).quantize(TWOPLACES, ROUND_HALF_UP)


def calculate(subtotal):

    subtotal = Decimal(subtotal)

    state = money(subtotal * STATE_TAX)
    county = money(subtotal * COUNTY_TAX)
    city = money(subtotal * CITY_TAX)

    total = state + county + city

    return {
        "subtotal": money(subtotal),

        "state_name": STATE_NAME,
        "county_name": COUNTY_NAME,
        "city_name": CITY_NAME,

        "state_rate": STATE_TAX,
        "county_rate": COUNTY_TAX,
        "city_rate": CITY_TAX,

        "state_tax": state,
        "county_tax": county,
        "city_tax": city,

        "sales_tax": total,
        "grand_total": money(subtotal + total)
    }
