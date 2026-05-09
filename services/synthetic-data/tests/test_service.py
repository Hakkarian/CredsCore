"""Unit tests for Synthetic Data Service."""

import pytest
import pandas as pd
from datetime import datetime
from fastapi.testclient import TestClient

from app.main import app
from app.gan_engine import CTGANEngine, create_sample_training_data
from app.models import CreditFeatures, GenerationRequest


client = TestClient(app)


class TestCTGANEngine:
    """Test cases for CTGANEngine."""

    def test_engine_initialization(self):
        """Test CTGAN engine initialization."""
        engine = CTGANEngine(epochs=10, batch_size=100)
        assert engine.is_trained is False
        assert engine.ctgan is None

    def test_create_sample_training_data(self):
        """Test sample training data creation."""
        df = create_sample_training_data(num_records=100)
        assert len(df) == 100
        assert all(col in df.columns for col in CTGANEngine.FEATURE_NAMES)

    def test_training(self):
        """Test model training."""
        engine = CTGANEngine(epochs=5, batch_size=100)
        df = create_sample_training_data(200)
        engine.train(df)
        assert engine.is_trained is True

    def test_generation(self):
        """Test data generation."""
        engine = CTGANEngine(epochs=5, batch_size=100)
        df = create_sample_training_data(200)
        engine.train(df)

        synthetic = engine.generate(num_records=10, apply_constraints=True)
        assert len(synthetic) == 10
        assert all(col in synthetic.columns for col in CTGANEngine.FEATURE_NAMES)


class TestCreditFeatures:
    """Test cases for CreditFeatures model."""

    def test_valid_credit_features(self):
        """Test creating valid credit features."""
        features = CreditFeatures(
            RevolvingUtilizationOfUnsecuredLines=0.5,
            age=30,
            NumberOfTime30_59DaysPastDueNotWorse=0,
            DebtRatio=0.3,
            MonthlyIncome=5000.0,
            NumberOfOpenCreditLinesAndLoans=5,
            NumberOfTimes90DaysLate=0,
            NumberRealEstateLoansOrLines=1,
            NumberOfTime60_89DaysPastDueNotWorse=0,
            NumberOfDependents=2,
        )
        assert features.age == 30
        assert features.DebtRatio == 0.3

    def test_invalid_credit_features(self):
        """Test validation catches invalid features."""
        with pytest.raises(Exception):
            CreditFeatures(
                RevolvingUtilizationOfUnsecuredLines=1.5,  # > 1.0
                age=30,
                NumberOfTime30_59DaysPastDueNotWorse=0,
                DebtRatio=0.3,
                MonthlyIncome=5000.0,
                NumberOfOpenCreditLinesAndLoans=5,
                NumberOfTimes90DaysLate=0,
                NumberRealEstateLoansOrLines=1,
                NumberOfTime60_89DaysPastDueNotWorse=0,
                NumberOfDependents=2,
            )


class TestGenerationRequest:
    """Test cases for GenerationRequest."""

    def test_valid_generation_request(self):
        """Test valid generation request."""
        request = GenerationRequest(
            num_records=100,
            apply_constraints=True,
        )
        assert request.num_records == 100
        assert request.apply_constraints is True

    def test_invalid_num_records(self):
        """Test validation of invalid num_records."""
        with pytest.raises(Exception):
            GenerationRequest(num_records=0)  # Must be >= 1


class TestAPIEndpoints:
    """Test cases for API endpoints."""

    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["service"] == "synthetic-data"

    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Synthetic Data Service"
        assert "endpoints" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
