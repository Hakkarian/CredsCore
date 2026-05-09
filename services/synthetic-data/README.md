# Synthetic Data Service

A FastAPI microservice for generating privacy-safe synthetic credit application data using CTGAN (Conditional Tabular GAN).

## Overview

This service provides:
- **CTGAN-based synthetic data generation** for tabular credit application data
- **Privacy preservation** - generated data cannot be reverse-engineered to real individuals
- **Quality validation** with statistical similarity tests (KS-test)
- **Async training pipeline** for GAN model training
- **Model versioning and management**

## Features

### Credit Application Features
The service generates synthetic data matching the existing CredsCore schema:

| Feature | Type | Range |
|---------|------|-------|
| RevolvingUtilizationOfUnsecuredLines | float | 0.0 - 1.0 |
| age | int | 18 - 100 |
| NumberOfTime30_59DaysPastDueNotWorse | int | 0 - 10 |
| DebtRatio | float | 0.0 - 2.0 |
| MonthlyIncome | float | 1000 - 50000 |
| NumberOfOpenCreditLinesAndLoans | int | 0 - 30 |
| NumberOfTimes90DaysLate | int | 0 - 10 |
| NumberRealEstateLoansOrLines | int | 0 - 10 |
| NumberOfTime60_89DaysPastDueNotWorse | int | 0 - 10 |
| NumberOfDependents | int | 0 - 10 |

## API Endpoints

### Health & Info
- `GET /health` - Health check
- `GET /` - API info
- `GET /config` - Service configuration
- `GET /stats` - Service statistics

### Model Management
- `GET /models` - List trained models
- `POST /models` - Create and train new model
- `GET /models/{model_id}` - Get model details
- `DELETE /models/{model_id}` - Delete model
- `POST /models/{model_id}/train` - Trigger training

### Generation
- `POST /generate` - Generate synthetic data
- `POST /validate` - Validate synthetic data quality
- `GET /features/schema` - Get feature schema

## Usage Examples

### Create and Train a Model
```bash
curl -X POST http://localhost:8007/models \
  -H "Content-Type: application/json" \
  -d '{
    "model_name": "credit-gan-v1",
    "description": "Initial GAN model for credit data",
    "config": {
      "epochs": 300,
      "batch_size": 500,
      "latent_dim": 128
    }
  }'
```

### Generate Synthetic Data
```bash
curl -X POST http://localhost:8007/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "your-model-id",
    "num_records": 1000,
    "apply_constraints": true,
    "random_seed": 42
  }'
```

### Validate Synthetic Data
```bash
curl -X POST http://localhost:8007/validate \
  -H "Content-Type: application/json" \
  -d '{
    "synthetic_data": [...],
    "reference_data": [...]
  }'
```

## Architecture

### Components

1. **CTGAN Engine** (`gan_engine.py`)
   - Wraps CTGAN library
   - Handles model training and generation
   - Applies feature constraints

2. **Training Pipeline** (`training.py`)
   - Async job management
   - Progress tracking
   - Model checkpointing

3. **Data Generator** (`generation.py`)
   - Synthetic record generation
   - Quality metrics computation
   - Batch generation support

4. **Validation** (`validation.py`)
   - KS-test for distribution similarity
   - Privacy score calculation
   - Exact match detection

## Running the Service

### Local Development
```bash
cd services/synthetic-data
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8007
```

### Using PowerShell Script
```powershell
.\scripts\start-synthetic-data.ps1
```

### Docker
```bash
cd services/synthetic-data
docker build -t credscore-synthetic-data .
docker run -p 8007:8007 credscore-synthetic-data
```

## Quality Metrics

The service computes several quality metrics:

- **Similarity Score** (0-1): Statistical similarity to real data using KS-tests
- **Privacy Score** (0-1): Privacy preservation based on distance to nearest real record
- **Validity Score** (0-1): Percentage of records within valid feature ranges
- **Overall Score**: Weighted combination of above metrics

## Configuration

Environment variables:
- `PORT` - Service port (default: 8007)
- `MODELS_DIR` - Directory for model storage
- `PRIVACY_THRESHOLD` - Minimum privacy score (default: 0.95)
- `SIMILARITY_THRESHOLD` - Minimum similarity score (default: 0.80)

## Dependencies

- fastapi>=0.109.0
- ctgan>=0.10.0 (CTGAN library)
- sdv>=1.12.0 (Synthetic Data Vault)
- torch>=2.2.0
- pandas>=2.2.0
- scikit-learn>=1.4.0

## Testing

```bash
cd services/synthetic-data
pytest tests/test_service.py -v
```

## License

Internal use only - CredsCore Platform
