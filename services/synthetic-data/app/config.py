"""Configuration for the Synthetic Data Service."""

import os
from typing import Dict, Any


class SyntheticDataConfig:
    """Configuration settings."""

    service_name: str = "synthetic-data"
    port: int = int(os.getenv("PORT", "8007"))
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Training hyperparameters - reduced for faster startup
    epochs: int = int(os.getenv("EPOCHS", "10"))
    batch_size: int = int(os.getenv("BATCH_SIZE", "500"))

    # Feature constraints
    feature_ranges: Dict[str, Dict[str, float]] = {
        "RevolvingUtilizationOfUnsecuredLines": {"min": 0.0, "max": 1.0},
        "age": {"min": 18, "max": 100},
        "NumberOfTime30_59DaysPastDueNotWorse": {"min": 0, "max": 10},
        "DebtRatio": {"min": 0.0, "max": 2.0},
        "MonthlyIncome": {"min": 1000.0, "max": 50000.0},
        "NumberOfOpenCreditLinesAndLoans": {"min": 0, "max": 30},
        "NumberOfTimes90DaysLate": {"min": 0, "max": 10},
        "NumberRealEstateLoansOrLines": {"min": 0, "max": 10},
        "NumberOfTime60_89DaysPastDueNotWorse": {"min": 0, "max": 10},
        "NumberOfDependents": {"min": 0, "max": 10},
    }


# Global configuration instance
config = SyntheticDataConfig()
