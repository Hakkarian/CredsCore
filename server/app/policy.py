"""
Rule-based Policy Engine for Credit Risk Decisions.

This layer converts ML risk scores into approve/review/decline decisions.
It applies pricing, thresholds, and overrides - separate from the ML model.

Key principle: Models estimate risk; policies make decisions.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class RiskGrade(str, Enum):
    """Risk grade classification (A = best, E = worst)."""
    A = "A"  # Excellent
    B = "B"  # Good
    C = "C"  # Moderate
    D = "D"  # High
    E = "E"  # Very High


class Decision(str, Enum):
    """Policy decision outcomes."""
    APPROVE = "APPROVE"
    REVIEW = "REVIEW"
    DECLINE = "DECLINE"


@dataclass
class RiskTier:
    """Configuration for a risk tier."""
    grade: RiskGrade
    min_score: float
    max_score: float
    decision: Decision
    base_interest_rate: float
    max_debt_to_income: float
    description: str


# Default policy configuration
DEFAULT_TIERS = [
    RiskTier(
        grade=RiskGrade.A,
        min_score=0.0,
        max_score=0.15,
        decision=Decision.APPROVE,
        base_interest_rate=5.0,
        max_debt_to_income=0.50,
        description="Excellent credit profile - instant approval"
    ),
    RiskTier(
        grade=RiskGrade.B,
        min_score=0.15,
        max_score=0.30,
        decision=Decision.APPROVE,
        base_interest_rate=6.5,
        max_debt_to_income=0.45,
        description="Good credit profile - standard approval"
    ),
    RiskTier(
        grade=RiskGrade.C,
        min_score=0.30,
        max_score=0.50,
        decision=Decision.REVIEW,
        base_interest_rate=8.5,
        max_debt_to_income=0.40,
        description="Moderate risk - manual review required"
    ),
    RiskTier(
        grade=RiskGrade.D,
        min_score=0.50,
        max_score=0.70,
        decision=Decision.REVIEW,
        base_interest_rate=11.0,
        max_debt_to_income=0.35,
        description="High risk - comprehensive review required"
    ),
    RiskTier(
        grade=RiskGrade.E,
        min_score=0.70,
        max_score=1.0,
        decision=Decision.DECLINE,
        base_interest_rate=15.0,
        max_debt_to_income=0.30,
        description="Very high risk - decline application"
    ),
]


@dataclass
class PolicyResult:
    """Result of policy evaluation."""
    decision: Decision
    grade: RiskGrade
    interest_rate: float
    recommended_max_amount: Optional[float] = None
    rationale: str = ""
    conditions: List[str] = field(default_factory=list)
    policy_version: str = "v1.0"


class RiskPolicy:
    """
    Rule-based policy engine that converts risk scores into decisions.
    
    This is intentionally separate from the ML model so that:
    - Policies can change without retraining models
    - Compliance rules are explicit and auditable
    - Manual overrides can be applied
    """
    
    def __init__(self, tiers: List[RiskTier] = None, policy_version: str = "v1.0"):
        """
        Initialize the policy engine.
        
        Args:
            tiers: List of risk tier configurations
            policy_version: Version identifier for audit trail
        """
        self.tiers = tiers or DEFAULT_TIERS
        self.policy_version = policy_version
    
    def get_tier(self, risk_score: float) -> Optional[RiskTier]:
        """
        Get the risk tier for a given risk score.
        
        Args:
            risk_score: Risk score between 0 and 1
                
        Returns:
            RiskTier configuration or None if no match
        """
        for tier in self.tiers:
            if tier.min_score <= risk_score < tier.max_score:
                return tier
        # Handle edge case where score is exactly 1.0
        if risk_score >= 1.0:
            return self.tiers[-1]
        return None
    
    def calculate_max_amount(self, monthly_income: float, dti_ratio: float, 
                            debt_ratio: float) -> Optional[float]:
        """
        Calculate recommended maximum loan amount based on income and ratios.
        
        Args:
            monthly_income: Applicant's monthly income
            dti_ratio: Debt-to-income ratio
            debt_ratio: Current debt ratio
            
        Returns:
            Recommended maximum loan amount or None
        """
        if monthly_income <= 0:
            return None
        
        # Use the more conservative of DTI or debt ratio
        effective_ratio = min(dti_ratio, debt_ratio) if debt_ratio > 0 else dti_ratio
        available_income = monthly_income * (1 - effective_ratio)
        
        # Recommend max loan as 24 months of available income (2 years)
        max_amount = available_income * 24
        
        return max(max_amount, 0)
    
    def evaluate(self, risk_score: float, monthly_income: float = 0,
                 debt_ratio: float = 0, employment_months: int = 0,
                 recent_inquiries: int = 0, requested_amount: float = None) -> PolicyResult:
        """
        Evaluate an application against policy rules.
        
        Args:
            risk_score: ML risk score (0-1)
            monthly_income: Applicant's monthly income
            debt_ratio: Current debt ratio
            employment_months: Months of employment stability
            recent_inquiries: Number of recent credit inquiries
            requested_amount: Requested loan amount (optional)
            
        Returns:
            PolicyResult with decision and rationale
        """
        tier = self.get_tier(risk_score)
        
        if tier is None:
            return PolicyResult(
                decision=Decision.DECLINE,
                grade=RiskGrade.E,
                interest_rate=15.0,
                rationale="Risk score out of range"
            )
        
        conditions = []
        interest_rate = tier.base_interest_rate
        
        # Employment stability check
        if employment_months < 6:
            conditions.append("Employment stability: Less than 6 months")
            interest_rate += 1.0
        elif employment_months < 12:
            conditions.append("Employment stability: 6-12 months")
            interest_rate += 0.5
        
        # Credit inquiry check
        if recent_inquiries > 5:
            conditions.append("High credit inquiry activity")
            interest_rate += 0.5
        elif recent_inquiries > 3:
            conditions.append("Moderate credit inquiry activity")
        
        # Calculate max amount if income provided
        max_amount = None
        if monthly_income > 0:
            max_amount = self.calculate_max_amount(monthly_income, debt_ratio, debt_ratio)
            
            # Check if requested amount exceeds recommendation
            if requested_amount and requested_amount > max_amount:
                conditions.append(f"Requested amount exceeds recommendation ({max_amount:,.0f})")
        
        # Build rationale
        rationales = [
            f"Risk score: {risk_score:.1%}",
            f"Assigned to tier {tier.grade.value} ({tier.description.lower()})"
        ]
        if conditions:
            rationales.append("Conditions: " + "; ".join(conditions))
        
        return PolicyResult(
            decision=tier.decision,
            grade=tier.grade,
            interest_rate=round(interest_rate, 1),
            recommended_max_amount=max_amount,
            rationale=". ".join(rationales),
            conditions=conditions,
            policy_version=self.policy_version
        )


# Default policy instance
default_policy = RiskPolicy()


def assess_risk(risk_score: float, monthly_income: float = 0,
                debt_ratio: float = 0, employment_months: int = 0,
                recent_inquiries: int = 0, requested_amount: float = None) -> dict:
    """
    Convenience function to assess risk and return a dict.
    
    Args:
        risk_score: ML risk score (0-1)
        monthly_income: Applicant's monthly income
        debt_ratio: Current debt ratio
        employment_months: Months of employment stability
        recent_inquiries: Number of recent credit inquiries
        requested_amount: Requested loan amount (optional)
        
    Returns:
        Dictionary with assessment results
    """
    result = default_policy.evaluate(
        risk_score=risk_score,
        monthly_income=monthly_income,
        debt_ratio=debt_ratio,
        employment_months=employment_months,
        recent_inquiries=recent_inquiries,
        requested_amount=requested_amount
    )
    
    return {
        "decision": result.decision.value,
        "risk_grade": result.grade.value,
        "interest_rate": result.interest_rate,
        "recommended_max_amount": result.recommended_max_amount,
        "rationale": result.rationale,
        "conditions": result.conditions,
        "policy_version": result.policy_version
    }