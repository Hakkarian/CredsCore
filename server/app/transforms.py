"""
Log-space transformations for financial variables.

Financial values are often highly skewed. Log transformations:
- Stabilize variance
- Improve model convergence
- Preserve proportional differences
- Match how risk scales in reality

Users see naira (₦80,000), models see logarithms.
"""

import numpy as np
from typing import Union


def safe_log(x: Union[float, int, None], floor: float = 1.0) -> float:
    """
    Safe logarithm transformation for financial values.
    
    Args:
        x: The value to transform (can be None, 0, or negative)
        floor: Minimum value before applying log (default 1.0)
    
    Returns:
        Log-transformed value, or 0.0 if input is None/invalid
    """
    if x is None or x < 0:
        return 0.0
    return float(np.log(max(float(x), floor)))


def safe_log_series(series, floor: float = 1.0):
    """Apply safe_log to a pandas Series."""
    return series.apply(lambda x: safe_log(x, floor))


def format_currency(amount: float, currency: str = "NGN", show_symbol: bool = True) -> str:
    """
    Format a monetary amount for display.
    
    Args:
        amount: The amount to format
        currency: Currency code (default NGN for Nigerian Naira)
        show_symbol: Whether to show currency symbol
    
    Returns:
        Formatted currency string
    """
    if amount is None or amount < 0:
        return "₦0" if show_symbol else "0"
    
    amount = round(amount, 2)
    formatted = f"{amount:,.2f}"
    
    if show_symbol and currency == "NGN":
        return f"₦{formatted}"
    return formatted


def parse_currency(amount: Union[str, float]) -> float:
    """
    Parse a currency string or number to float.
    
    Args:
        amount: Currency string (e.g., "₦80,000") or number
    
    Returns:
        Float value
    """
    if isinstance(amount, (int, float)):
        return float(amount)
    if isinstance(amount, str):
        cleaned = amount.replace("₦", "").replace(",", "").replace("NGN", "").strip()
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    return 0.0


# Financial fields that should use log-space transformation
MONETARY_FIELDS = [
    "monthly_income",
    "loan_amount",
    "monthly_repayment",
    "total_debt",
    "annual_income",
]


def apply_log_transforms(data: dict, fields: list = None) -> dict:
    """
    Apply log-space transforms to specified fields in a data dict.
    
    Args:
        data: Input dictionary with raw values
        fields: List of field names to transform (defaults to MONETARY_FIELDS)
    
    Returns:
        Dictionary with transformed values
    """
    if fields is None:
        fields = MONETARY_FIELDS
    
    result = data.copy()
    for field in fields:
        if field in result:
            result[field] = safe_log(result[field])
    return result