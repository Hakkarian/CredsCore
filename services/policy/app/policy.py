from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class PolicyRule:
    name: str
    condition: callable
    action: str
    severity: str


class PolicyEngine:
    def __init__(self):
        self.rules = self._build_rules()

    def _build_rules(self) -> List[PolicyRule]:
        return [
            PolicyRule("min_score", lambda p: p < 0.1, "auto_approve", "info"),
            PolicyRule("max_score", lambda p: p > 0.8, "auto_reject", "critical"),
            PolicyRule("high_fraud", lambda p: p > 0.5, "manual_review", "high"),
            PolicyRule("medium_risk", lambda p: 0.3 < p <= 0.5, "manual_review", "medium"),
        ]

    def evaluate(self, probability: float, fraud_score: float = 0, enriched_data: Dict = None) -> Dict[str, Any]:
        effective_score = max(probability, fraud_score)
        for rule in self.rules:
            if rule.condition(effective_score):
                return {
                    "decision": rule.action,
                    "rule_triggered": rule.name,
                    "severity": rule.severity,
                    "probability": probability,
                    "fraud_score": fraud_score,
                }
        return {
            "decision": "manual_review",
            "rule_triggered": "default",
            "severity": "low",
            "probability": probability,
            "fraud_score": fraud_score,
        }