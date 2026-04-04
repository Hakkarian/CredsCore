import requests
import sys
from tests.fixtures.applicants import TEST_CASES
from tests.validators.explanation_validator import validate_explanation_quality

BASE_URL = "http://localhost:8000"
validation_results = []


def test_endpoint(endpoint, applicant, test_name, params=None):
    print(f"\n{'='*60}\nTesting: {test_name}\n{'='*60}")
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", json=applicant, params=params or {})
        result = response.json()
        explanation = result.get('human_explanation', 'N/A')
        print(f"Human Explanation:\n{explanation}")
        issues = validate_explanation_quality(explanation)
        if issues:
            print(f"\nIssues: {issues}")
            validation_results.append({"test": test_name, "endpoint": endpoint, "status": "FAILED", "issues": issues})
            return False
        print("\nValidation: PASSED")
        validation_results.append({"test": test_name, "endpoint": endpoint, "status": "PASSED"})
        return True
    except Exception as e:
        print(f"Error: {e}")
        validation_results.append({"test": test_name, "endpoint": endpoint, "status": "ERROR", "issues": [str(e)]})
        return False


def check_server_health():
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.json().get('status') != 'healthy':
            print("Server not healthy!")
            return False
        print("Server: HEALTHY")
        return True
    except Exception:
        print("Server not running!")
        return False


if __name__ == "__main__":
    print("="*60)
    print("HUMAN EXPLANATION VALIDATION - MULTIPLE TEST CASES")
    print("="*60)
    if not check_server_health():
        sys.exit(1)
    for test_name, applicant in TEST_CASES.items():
        print(f"\n\n{'#'*60}\nTEST CASE: {test_name}\n{'#'*60}")
        test_endpoint("/similar-applicants?k=10", applicant.copy(), f"{test_name} - Similar Applicants")
        test_endpoint("/explain-denial?k=20", applicant.copy(), f"{test_name} - Explain Denial")
        test_endpoint("/thin-file-predict?k=5", applicant.copy(), f"{test_name} - Thin File Predict")
    print(f"\n\n{'='*60}\nVALIDATION SUMMARY\n{'='*60}")
    passed = sum(1 for r in validation_results if r['status'] == 'PASSED')
    failed = sum(1 for r in validation_results if r['status'] == 'FAILED')
    errors = sum(1 for r in validation_results if r['status'] == 'ERROR')
    print(f"\nTotal Tests: {len(validation_results)}\nPassed: {passed}\nFailed: {failed}\nErrors: {errors}")
    if failed > 0 or errors > 0:
        print(f"\nFailed/Error Tests:")
        for r in validation_results:
            if r['status'] != 'PASSED':
                print(f"  - {r['test']}: {r['status']}")
                if 'issues' in r:
                    for issue in r['issues']:
                        print(f"      {issue}")
    if failed == 0 and errors == 0:
        print("\nALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\nSOME TESTS FAILED!")
        sys.exit(1)