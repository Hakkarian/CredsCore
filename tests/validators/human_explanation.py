def validate_endpoint_explanation(endpoint_name, explanation, min_length=50, required_keywords=None):
    issues = []
    if explanation is None:
        issues.append("human_explanation field is MISSING")
    elif not isinstance(explanation, str):
        issues.append(f"human_explanation is not a string: {type(explanation)}")
    elif len(explanation.strip()) == 0:
        issues.append("human_explanation is EMPTY")
    elif len(explanation) < min_length:
        issues.append(f"human_explanation is too short ({len(explanation)} chars, minimum {min_length})")
    placeholder_patterns = ["TODO", "FIXME", "placeholder", "test", "Lorem ipsum", "N/A", "None", "undefined"]
    for pattern in placeholder_patterns:
        if pattern.lower() in explanation.lower():
            if pattern.lower() == "example" and "counter-example" in explanation.lower():
                continue
            issues.append(f"Contains placeholder text: '{pattern}'")
    if explanation and not any(char.isdigit() for char in explanation):
        issues.append("Warning: No numerical values found in explanation")
    if required_keywords:
        missing = [kw for kw in required_keywords if kw.lower() not in explanation.lower()]
        if missing:
            issues.append(f"Missing expected keywords: {missing}")
    return len(issues) == 0, issues


def validate_denial_explanation(explanation):
    if explanation is None or not isinstance(explanation, str) or len(explanation) < 100:
        return False, ["Explanation too short or missing"]
    has_denial_term = "denied" in explanation.lower() or "denial" in explanation.lower()
    has_risk = "risk" in explanation.lower()
    has_approved = "approved" in explanation.lower()
    missing = []
    if not has_denial_term:
        missing.append("Missing 'denied' or 'denial' keyword")
    if not has_risk:
        missing.append("Missing 'risk' keyword")
    if not has_approved:
        missing.append("Missing 'approved' keyword")
    return len(missing) == 0, missing