def validate_explanation_quality(explanation):
    issues = []
    if not explanation or not isinstance(explanation, str):
        issues.append("Missing or invalid explanation")
        return issues
    if len(explanation) < 50:
        issues.append(f"Too short: {len(explanation)} chars")
    placeholders = ["TODO", "FIXME", "placeholder", "N/A", "None", "undefined"]
    for placeholder in placeholders:
        if placeholder.lower() in explanation.lower():
            issues.append(f"Contains placeholder: '{placeholder}'")
    if not any(char.isdigit() for char in explanation):
        issues.append("No numerical values found")
    return issues