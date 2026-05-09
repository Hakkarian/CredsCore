"""CTGAN Engine for synthetic tabular data generation."""

import os
import uuid
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import torch
from ctgan import CTGAN

from app.config import config

# Force CPU usage to avoid CUDA issues
os.environ["CUDA_VISIBLE_DEVICES"] = ""

logger = logging.getLogger(__name__)


class CTGANEngine:
    """Simplified CTGAN engine for synthetic credit data generation."""

    FEATURE_NAMES = [
        "RevolvingUtilizationOfUnsecuredLines",
        "age",
        "NumberOfTime30_59DaysPastDueNotWorse",
        "DebtRatio",
        "MonthlyIncome",
        "NumberOfOpenCreditLinesAndLoans",
        "NumberOfTimes90DaysLate",
        "NumberRealEstateLoansOrLines",
        "NumberOfTime60_89DaysPastDueNotWorse",
        "NumberOfDependents",
    ]

    DISCRETE_COLUMNS = [
        "age",
        "NumberOfTime30_59DaysPastDueNotWorse",
        "NumberOfOpenCreditLinesAndLoans",
        "NumberOfTimes90DaysLate",
        "NumberRealEstateLoansOrLines",
        "NumberOfTime60_89DaysPastDueNotWorse",
        "NumberOfDependents",
    ]

    def __init__(self, epochs: int = 100, batch_size: int = 500):
        """Initialize the CTGAN engine."""
        self.model_id = str(uuid.uuid4())
        self.ctgan: Optional[CTGAN] = None
        self.is_trained = False
        self.epochs = epochs
        self.batch_size = batch_size
        self.created_at = datetime.now(timezone.utc)

    def train(self, data: pd.DataFrame) -> None:
        """Train the CTGAN model on tabular data."""
        import sys

        if data is None or data.empty:
            raise ValueError("Training data cannot be empty")

        # Validate columns
        missing_cols = set(self.FEATURE_NAMES) - set(data.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        # Reorder columns
        data = data[self.FEATURE_NAMES].copy()

        logger.info(f"Training CTGAN model with {self.epochs} epochs...")
        start_time = datetime.now(timezone.utc)

        # Configure for single-process execution on Windows
        if sys.platform == 'win32':
            import torch
            torch.set_num_threads(1)

        # Initialize and train CTGAN (force CPU)
        self.ctgan = CTGAN(
            epochs=self.epochs,
            batch_size=self.batch_size,
            generator_dim=(128, 128),
            discriminator_dim=(128, 128),
            verbose=False,
            cuda=False, # Force CPU to avoid CUDA issues
        )

        # Train - use single worker to avoid Windows pickling issues
        if sys.platform == 'win32':
            # Monkey-patch DataLoader to use 0 workers on Windows
            from torch.utils.data import DataLoader
            orig_init = DataLoader.__init__

            def patched_init(self, *args, **kwargs):
                kwargs['num_workers'] = 0
                kwargs['pin_memory'] = False
                return orig_init(self, *args, **kwargs)

            DataLoader.__init__ = patched_init
            try:
                self.ctgan.fit(data, discrete_columns=self.DISCRETE_COLUMNS)
            finally:
                DataLoader.__init__ = orig_init
        else:
            self.ctgan.fit(data, discrete_columns=self.DISCRETE_COLUMNS)

        self.is_trained = True
        duration = (datetime.now(timezone.utc) - start_time).total_seconds()
        logger.info(f"Training completed in {duration:.2f}s")

    def generate(
        self,
        num_records: int,
        apply_constraints: bool = True,
        random_seed: Optional[int] = None,
    ) -> pd.DataFrame:
        """Generate synthetic records."""
        if not self.is_trained or self.ctgan is None:
            raise RuntimeError("Model must be trained before generating data")

        if random_seed is not None:
            torch.manual_seed(random_seed)
            np.random.seed(random_seed)

        # Generate samples
        synthetic_data = self.ctgan.sample(num_records)

        # Apply constraints
        if apply_constraints:
            synthetic_data = self._apply_constraints(synthetic_data)

        logger.info(f"Generated {num_records} synthetic records")
        return synthetic_data

    def _apply_constraints(self, data: pd.DataFrame) -> pd.DataFrame:
        """Apply feature constraints to ensure valid ranges."""
        data = data.copy()

        for feature_name, ranges in config.feature_ranges.items():
            if feature_name in data.columns:
                min_val = ranges["min"]
                max_val = ranges["max"]
                data[feature_name] = data[feature_name].clip(min_val, max_val)

            # Round integer columns
            if feature_name in self.DISCRETE_COLUMNS:
                data[feature_name] = data[feature_name].round().astype(int)

        return data


def create_sample_training_data(num_records: int = 1000) -> pd.DataFrame:
    """Create sample training data for initial model training."""
    np.random.seed(42)

    data = {
        "RevolvingUtilizationOfUnsecuredLines": np.clip(
            np.random.beta(2, 5, num_records), 0, 1
        ),
        "age": np.random.randint(18, 65, num_records),
        "NumberOfTime30_59DaysPastDueNotWorse": np.random.poisson(
            0.5, num_records
        ).clip(0, 10),
        "DebtRatio": np.clip(np.random.gamma(2, 0.3, num_records), 0, 2),
        "MonthlyIncome": np.random.lognormal(8, 0.5, num_records).clip(1000, 50000),
        "NumberOfOpenCreditLinesAndLoans": np.random.poisson(8, num_records).clip(
            0, 30
        ),
        "NumberOfTimes90DaysLate": np.random.poisson(0.1, num_records).clip(0, 10),
        "NumberRealEstateLoansOrLines": np.random.poisson(1, num_records).clip(0, 10),
        "NumberOfTime60_89DaysPastDueNotWorse": np.random.poisson(
            0.2, num_records
        ).clip(0, 10),
        "NumberOfDependents": np.random.poisson(1, num_records).clip(0, 10),
    }

    return pd.DataFrame(data)


# Global engine instance
global_engine: Optional[CTGANEngine] = None


def get_or_create_engine() -> CTGANEngine:
    """Get existing engine or create and train a new one."""
    global global_engine

    if global_engine is None:
        logger.info("Creating and training new CTGAN model...")
        try:
            global_engine = CTGANEngine(epochs=config.epochs, batch_size=config.batch_size)
            training_data = create_sample_training_data(1000)  # Reduced for speed
            global_engine.train(training_data)
            logger.info(f"Model trained successfully: is_trained={global_engine.is_trained}")
        except Exception as e:
            logger.error(f"Failed to train model: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    return global_engine
