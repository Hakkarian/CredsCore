import requests
import sys
import numpy as np
import pandas as pd
from tests.fixtures.endpoints import SAMPLE_APPLICANT, HIGH_RISK_APPLICANT, LOW_RISK_APPLICANT, BASE_URL
from tests.validators.human_explanation import validate_endpoint_explanation, validate_denial_explanation

validation_results = []
all_passed = True


def test_health():
    try:
        response = requests.get(f"{BASE_URL}/health")
        result = response.json()
        print(f"Status: {result.get('status')}")
        return result.get('status') == 'healthy'
    except Exception as e:
        print(f"Health check failed: {e}")
        return False


def test_predict():
    try:
        response = requests.post(f"{BASE_URL}/predict", json=SAMPLE_APPLICANT)
        result = response.json()
        print(f"Prediction: {result.get('prediction')}, Probability: {result.get('default_probability'):.4f}")
        required_fields = ['prediction', 'default_probability', 'risk_level', 'top_risk_factors']
        missing = [f for f in required_fields if f not in result]
        if missing:
            print(f"Missing required fields: {missing}")
            return False
        return True
    except Exception as e:
        print(f"Test failed: {e}")
        return False


def test_similar_applicants():
    global all_passed
    try:
        response = requests.post(f"{BASE_URL}/similar-applicants?k=10", json=SAMPLE_APPLICANT)
        result = response.json()
        passed, issues = validate_endpoint_explanation("/similar-applicants", result.get('human_explanation'), min_length=80, required_keywords=["default", "similar", "applicant"])
        validation_results.append({"endpoint": "/similar-applicants", "status": "PASSED" if passed else "FAILED", "issues": issues if not passed else None})
        if not passed:
            all_passed = False
        return passed
    except Exception as e:
        print(f"Test failed: {e}")
        return False


def test_explain_denial():
    global all_passed
    try:
        response = requests.post(f"{BASE_URL}/explain-denial?k=20", json=HIGH_RISK_APPLICANT)
        result = response.json()
        passed, issues = validate_denial_explanation(result.get('human_explanation'))
        validation_results.append({"endpoint": "/explain-denial", "status": "PASSED" if passed else "FAILED", "issues": issues if not passed else None})
        if not passed:
            all_passed = False
        return passed
    except Exception as e:
        print(f"Test failed: {e}")
        return False


def test_thin_file_predict():
    global all_passed
    try:
        response = requests.post(f"{BASE_URL}/thin-file-predict?k=5", json=LOW_RISK_APPLICANT)
        result = response.json()
        passed, issues = validate_endpoint_explanation("/thin-file-predict", result.get('human_explanation'), min_length=80, required_keywords=["prediction", "risk", "model"])
        validation_results.append({"endpoint": "/thin-file-predict", "status": "PASSED" if passed else "FAILED", "issues": issues if not passed else None})
        if not passed:
            all_passed = False
        return passed
    except Exception as e:
        print(f"Test failed: {e}")
        return False


def generate_random_data(n_samples, col_names):
    return pd.DataFrame({
        col_names[0]: np.random.exponential(0.5, n_samples),
        col_names[1]: np.random.normal(45, 10, n_samples).clip(18, 80),
        col_names[2]: np.random.poisson(0.5, n_samples),
        col_names[3]: np.random.exponential(1.0, n_samples),
        col_names[4]: np.random.lognormal(8.5, 0.5, n_samples),
        col_names[5]: np.random.poisson(8, n_samples),
        col_names[6]: np.random.poisson(0.2, n_samples),
        col_names[7]: np.random.poisson(1.5, n_samples),
        col_names[8]: np.random.poisson(0.3, n_samples),
        col_names[9]: np.random.poisson(1, n_samples),
    }).rename(columns=dict(zip([col_names[0], col_names[1], col_names[2], col_names[3], col_names[4], col_names[5], col_names[6], col_names[7], col_names[8], col_names[9]], col_names)))


def test_monitor_drift():
    global all_passed
    try:
        col_names = ['RevolvingUtilizationOfUnsecuredLines', 'age', 'NumberOfTime30-59DaysPastDueNotWorse', 'DebtRatio', 'MonthlyIncome', 'NumberOfOpenCreditLinesAndLoans', 'NumberOfTimes90DaysLate', 'NumberRealEstateLoansOrLines', 'NumberOfTime60-89DaysPastDueNotWorse', 'NumberOfDependents']
        np.random.seed(42)
        recent_data = generate_random_data(1000, col_names)
        response = requests.post(f"{BASE_URL}/monitor-drift?n_clusters=10", json=recent_data.to_dict(orient='records'))
        result = response.json()
        passed, issues = validate_endpoint_explanation("/monitor-drift", result.get('human_explanation'), min_length=100, required_keywords=["drift", "model", "data", "training"])
        validation_results.append({"endpoint": "/monitor-drift", "status": "PASSED" if passed else "FAILED", "issues": issues if not passed else None})
        if not passed:
            all_passed = False
        return passed
    except Exception as e:
        print(f"Test failed: {e}")
        return False


def test_peer_groups():
    global all_passed
    try:
        col_names = ['RevolvingUtilizationOfUnsecuredLines', 'age', 'NumberOfTime30-59DaysPastDueNotWorse', 'DebtRatio', 'MonthlyIncome', 'NumberOfOpenCreditLinesAndLoans', 'NumberOfTimes90DaysLate', 'NumberRealEstateLoansOrLines', 'NumberOfTime60-89DaysPastDueNotWorse', 'NumberOfDependents']
        np.random.seed(42)
        customer_data = generate_random_data(5000, col_names)
        response = requests.post(f"{BASE_URL}/peer-groups?n_clusters=5", json=customer_data.to_dict(orient='records'))
        result = response.json()
        passed, issues = validate_endpoint_explanation("/peer-groups", result.get('human_explanation'), min_length=80, required_keywords=["segment", "customer", "group"])
        validation_results.append({"endpoint": "/peer-groups", "status": "PASSED" if passed else "FAILED", "issues": issues if not passed else None})
        if not passed:
            all_passed = False
        return passed
    except Exception as e:
        print(f"Test failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("HUMAN EXPLANATION STRICT VALIDATION")
    print("=" * 60)
    if not test_health():
        print("\nServer is not healthy.")
        sys.exit(1)
    test_predict()
    test_similar_applicants()
    test_explain_denial()
    test_thin_file_predict()
    test_monitor_drift()
    test_peer_groups()
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    passed = sum(1 for r in validation_results if r['status'] == 'PASSED')
    failed = sum(1 for r in validation_results if r['status'] == 'FAILED')
    for result in validation_results:
        status_icon = "PASSED" if result['status'] == 'PASSED' else "FAILED"
        print(f"{status_icon}: {result['endpoint']}")
        if result.get('issues'):
            for issue in result['issues']:
                print(f"   - {issue}")
    print(f"\nTotal: {passed + failed} endpoints tested\nPassed: {passed}\nFailed: {failed}")
    if all_passed and failed == 0:
        print("\nALL HUMAN EXPLANATION VALIDATIONS PASSED!")
        sys.exit(0)
    else:
        print("\nSOME VALIDATIONS FAILED!")
        sys.exit(1)