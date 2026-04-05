# CredsCore - Credit Risk Prediction API

A production-grade credit risk system that separates ML risk estimation from policy decisions.

## Architecture

Based on the principle: **"Models estimate risk; policies make decisions."**

### Layer 1: ML Risk Estimation
- LightGBM model produces continuous default probability (0-1)
- Learns from financial, behavioral, and credit-history signals
- SHAP explanations for interpretability
- Optimized for statistical accuracy

### Layer 2: Rule-Based Policy Engine
- Converts risk scores into APPROVE/REVIEW/DECLINE decisions
- Applies risk grades (A-E), interest rates, and loan limits
- Fully auditable and configurable without retraining
- Supports compliance overrides and manual review triggers

## Features

- FastAPI-based REST API for credit risk prediction
- LightGBM model for binary classification (default probability)
- SHAP explanations for model interpretability
- **Policy engine** separating risk estimation from decisions
- **Risk grades (A-E)** with interest rate adjustments
- **Log-space transformations** for financial variables
- **Naira-first** monetary values (human-readable input/output)
- FAISS similarity search for peer comparison

## Project Structure

```
server/
├── main.py              # FastAPI application and endpoints
├── requirements.txt     # Python dependencies
├── app/
│   ├── models.py        # Pydantic data models
│   ├── policy.py        # Rule-based policy engine
│   ├── transforms.py    # Log-space transformations
│   └── faiss_index.py   # FAISS similarity search
├── saved_models/
│   ├── lightgbm_credit_model.pkl
│   ├── shap_explainer.pkl
│   └── feature_names.pkl
└── data/
    └── cs-training.csv  # Training dataset
```

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Hakkarian/CredsCore.git
cd CredsCore
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
   - Windows:
   ```bash
   venv\Scripts\activate
   ```
   - macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. Install dependencies:
```bash
pip install -r server/requirements.txt
```

## Running the API

### Option 1: Using uvicorn directly
```bash
cd server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Option 2: Running the Python file
```bash
cd server
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Root Endpoint
- **GET /** - API information and available endpoints

### Health Check
- **GET /health** - Check if the service is operational

### Model Information
- **GET /model-info** - Get information about the ML model

### Predict Credit Risk
- **POST /predict** - Make a credit risk prediction (ML score only)

#### Request Body (JSON):
```json
{
  "RevolvingUtilizationOfUnsecuredLines": 0.1,
  "age": 45,
  "NumberOfTime30_59DaysPastDueNotWorse": 0,
  "DebtRatio": 0.3,
  "MonthlyIncome": 5000.0,
  "NumberOfOpenCreditLinesAndLoans": 5,
  "NumberOfTimes90DaysLate": 0,
  "NumberRealEstateLoansOrLines": 2,
  "NumberOfTime60_89DaysPastDueNotWorse": 0,
  "NumberOfDependents": 2
}
```

#### Response (JSON):
```json
{
  "prediction": 0,
  "default_probability": 0.15,
  "risk_level": "low",
  "message": "Low risk - approved"
}
```

### Full Risk Assessment (NEW)
- **POST /assess** - Full risk assessment with policy decision

Combines ML risk estimation (Layer 1) with policy decision engine (Layer 2).

#### Request Body (JSON):
```json
{
  "RevolvingUtilizationOfUnsecuredLines": 0.1,
  "age": 45,
  "NumberOfTime30_59DaysPastDueNotWorse": 0,
  "DebtRatio": 0.3,
  "MonthlyIncome": 5000.0,
  "NumberOfOpenCreditLinesAndLoans": 5,
  "NumberOfTimes90DaysLate": 0,
  "NumberRealEstateLoansOrLines": 2,
  "NumberOfTime60_89DaysPastDueNotWorse": 0,
  "NumberOfDependents": 2,
  "credit_report": {
    "recent_inquiries": 2,
    "credit_history_months": 36
  },
  "financial_stability": {
    "employment_tenure_months": 24
  },
  "structural_profile": {
    "loan_amount_requested": 500000
  }
}
```

#### Response (JSON):
```json
{
  "risk_score": 0.12,
  "default_probability": 0.12,
  "top_risk_factors": [...],
  "policy": {
    "decision": "APPROVE",
    "risk_grade": "A",
    "interest_rate": 5.0,
    "recommended_max_amount": 120000.0,
    "rationale": "Risk score: 12.0%. Assigned to tier A (excellent credit profile - instant approval)",
    "conditions": [],
    "policy_version": "v1.0"
  },
  "human_summary": "Risk score: 12.0% | Grade A | Decision: APPROVE. Monthly income: ₦5,000. Recommended max loan: ₦120,000 at 5.0% interest.",
  "tier_message": "Approved with Grade A credit profile."
}
```

### Policy Information
- **GET /policy-info** - Get current policy tier configuration

### Other Endpoints
- **POST /similar-applicants** - Find similar past applicants
- **POST /explain-denial** - Explain denial with counterfactual examples
- **POST /thin-file-predict** - Enhanced prediction for thin-file applicants
- **POST /monitor-drift** - Monitor feature drift
- **POST /peer-groups** - Customer segmentation

## Interactive API Documentation

Once the server is running, access the interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Model Training

To retrain the model and generate new visualizations:

```bash
cd server/app
python core.py
```

This will:
- Train a new LightGBM model
- Generate SHAP explanations
- Create visualization plots (saved as PNG files)
- Save the model to `saved_models/`

## Features Used for Prediction

1. **RevolvingUtilizationOfUnsecuredLines** - Revolving utilization of unsecured lines
2. **age** - Age of the client
3. **NumberOfTime30_59DaysPastDueNotWorse** - Number of times 30-59 days past due
4. **DebtRatio** - Debt ratio
5. **MonthlyIncome** - Monthly income
6. **NumberOfOpenCreditLinesAndLoans** - Number of open credit lines and loans
7. **NumberOfTimes90DaysLate** - Number of times 90 days late
8. **NumberRealEstateLoansOrLines** - Number of real estate loans or lines
9. **NumberOfTime60_89DaysPastDueNotWorse** - Number of times 60-89 days past due
10. **NumberOfDependents** - Number of dependents

## License

See [LICENSE](LICENSE) file for details.

## Author

Hakkarian