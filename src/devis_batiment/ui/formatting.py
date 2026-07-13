from __future__ import annotations


def format_amount(amount: float, currency: str = "Ar") -> str:
    return f"{amount:,.0f} {currency}".replace(",", " ")
