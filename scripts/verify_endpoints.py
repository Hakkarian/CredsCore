"""Verify all service endpoints produce different output for different inputs."""
import json
import urllib.request
import sys

LOW = {"RevolvingUtilizationOfUnsecuredLines": 0.1, "age": 55, "NumberOfTime30_59DaysPastDueNotWorse": 0, "DebtRatio": 0.1, "MonthlyIncome": 15000, "NumberOfOpenCreditLinesAndLoans": 5, "NumberOfTimes90DaysLate": 0, "NumberRealEstateLoansOrLines": 2, "NumberOfTime60_89DaysPastDueNotWorse": 0, "NumberOfDependents": 0}
HIGH = {"RevolvingUtilizationOfUnsecuredLines": 0.95, "age": 22, "NumberOfTime30_59DaysPastDueNotWorse": 8, "DebtRatio": 0.9, "MonthlyIncome": 1000, "NumberOfOpenCreditLinesAndLoans": 20, "NumberOfTimes90DaysLate": 5, "NumberRealEstateLoansOrLines": 0, "NumberOfTime60_89DaysPastDueNotWorse": 6, "NumberOfDependents": 6}


def post(url, data, timeout=8):
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"_error": str(e)}


def check(name, url, low_data, high_data, key_fn):
    r1 = post(url, low_data)
    r2 = post(url, high_data)
    if "_error" in r1:
        print(f"  FAIL | {name} | LOW error: {r1['_error'][:80]}")
        return False
    if "_error" in r2:
        print(f"  FAIL | {name} | HIGH error: {r2['_error'][:80]}")
        return False
    v1, v2 = key_fn(r1), key_fn(r2)
    status = "PASS" if v1 != v2 else "FAIL"
    # Format for display
    def fmt(v):
        if isinstance(v, float):
            return f"{v:.4f}"
        return str(v)
    print(f"  {status} | {name} | LOW={fmt(v1)} | HIGH={fmt(v2)}")
    return v1 != v2


results = []

print("=" * 70)
print("  ENDPOINT VERIFICATION: OUTPUT MUST VARY BY INPUT")
print("=" * 70)

# 1. Credit Scoring
results.append(check(
    "Credit (8001) /client-predict",
    "http://localhost:8001/client-predict", LOW, HIGH,
    lambda d: d.get("default_probability")))

# 2. Fraud Detection
results.append(check(
    "Fraud (8002) /similar",
    "http://localhost:8002/similar", LOW, HIGH,
    lambda d: d.get("estimated_probability")))

# 3. Augmented Scoring /score
results.append(check(
    "AugScore (8008) /score",
    "http://localhost:8008/score", LOW, HIGH,
    lambda d: d.get("combined_risk_score")))

# 4. Augmented Scoring /insights
results.append(check(
    "AugScore (8008) /insights",
    "http://localhost:8008/insights", LOW, HIGH,
    lambda d: d.get("ml_risk")))

# 5. Gateway → Credit
results.append(check(
    "Gateway (4000) /client-predict",
    "http://localhost:4000/client-predict", LOW, HIGH,
    lambda d: d.get("default_probability")))

# 6. Gateway → Augmented Scoring
results.append(check(
    "Gateway (4000) /score",
    "http://localhost:4000/score", LOW, HIGH,
    lambda d: d.get("combined_risk_score")))

# 7. Gateway → Fraud
results.append(check(
    "Gateway (4000) /similar",
    "http://localhost:4000/similar", LOW, HIGH,
    lambda d: d.get("estimated_probability")))

# 8. Explain denial
results.append(check(
    "Credit (8001) /explain-denial",
    "http://localhost:8001/explain-denial", LOW, HIGH,
    lambda d: d.get("prediction")))

# 9. Similar applicants
results.append(check(
    "Credit (8001) /similar-applicants",
    "http://localhost:8001/similar-applicants", LOW, HIGH,
    lambda d: d.get("estimated_probability")))

# 10. Policy Engine — requires applicant + credit_score + risk_score
low_policy = {"applicant": LOW, "credit_score": 0.01, "risk_score": 0.01}
high_policy = {"applicant": HIGH, "credit_score": 0.95, "risk_score": 0.95}
results.append(check(
    "Policy (8003) /evaluate",
    "http://localhost:8003/evaluate", low_policy, high_policy,
    lambda d: d.get("decision", d.get("final_decision", str(d)))))

# 11. Orchestrator — requires nested applicant with client_id, name, email, phone, address, credit_score
low_orch = {"applicant": {"client_id": "low1", "name": "Low Risk", "email": "low@test.com",
            "phone": "555-0001", "address": "1 Low St", "credit_score": 0.01}, "requested_amount": 10000}
high_orch = {"applicant": {"client_id": "high1", "name": "High Risk", "email": "high@test.com",
             "phone": "555-0002", "address": "2 High St", "credit_score": 0.95}, "requested_amount": 500000}
results.append(check(
    "Orchestrator (8005) /apply",
    "http://localhost:8005/apply", low_orch, high_orch,
    lambda d: d.get("application_id", d.get("status", str(d)[:60]))))

# 12. Enrichment — requires client_id, name, email, phone, address, credit_score
low_enrich = {"client_id": "low1", "name": "Low Risk", "email": "low@test.com",
              "phone": "555-0001", "address": "1 Low St", "credit_score": 750}
high_enrich = {"client_id": "high1", "name": "High Risk", "email": "high@test.com",
               "phone": "555-0002", "address": "2 High St", "credit_score": 400}
results.append(check(
    "Enrichment (8006) /enrich",
    "http://localhost:8006/enrich", low_enrich, high_enrich,
    lambda d: d.get("bureau_score", d.get("credit_score", d.get("enriched_score", str(d)[:60])))))

# 13. Augmented Scoring /agents/analyze
results.append(check(
    "AugScore (8008) /agents/analyze",
    "http://localhost:8008/agents/analyze", LOW, HIGH,
    lambda d: d.get("combined_risk_score", str(d)[:60])))

# Summary
passed = sum(results)
total = len(results)
print("")
print("=" * 70)
print(f"  RESULT: {passed}/{total} endpoints produce different output per input")
if passed == total:
    print("  ALL PASS")
else:
    print(f"  {total - passed} FAILURES")
print("=" * 70)
