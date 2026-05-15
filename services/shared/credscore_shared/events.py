from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
import json


class EventType(str, Enum):
    LOAN_APPLICATION_SUBMITTED = "loan.application.submitted"
    LOAN_SCORED = "loan.scored"
    LOAN_FRAUD_CHECKED = "loan.fraud_checked"
    LOAN_POLICY_DECIDED = "loan.policy_decided"
    LOAN_COMPLETED = "loan.completed"
    LOAN_FAILED = "loan.failed"
    FRAUD_SCAN_COMPLETED = "fraud.scan.completed"
    FRAUD_RING_DETECTED = "fraud.ring.detected"
    REPORT_REQUESTED = "report.requested"
    REPORT_COMPLETED = "report.completed"
    MODEL_DRIFT_DETECTED = "model.drift.detected"


class CredsEvent:
    def __init__(
        self,
        event_type: EventType,
        payload: Dict[str, Any],
        correlation_id: Optional[str] = None,
        source_service: Optional[str] = None,
    ):
        self.event_id = f"evt_{datetime.utcnow().isoformat()}_{id(self)}"
        self.event_type = event_type
        self.payload = payload
        self.correlation_id = correlation_id or self.event_id
        self.source_service = source_service or "unknown"
        self.timestamp = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "correlation_id": self.correlation_id,
            "source_service": self.source_service,
            "timestamp": self.timestamp,
            "payload": self.payload,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, data: str) -> "CredsEvent":
        d = json.loads(data)
        event = cls(
            event_type=EventType(d["event_type"]),
            payload=d["payload"],
            correlation_id=d.get("correlation_id"),
            source_service=d.get("source_service"),
        )
        event.event_id = d["event_id"]
        event.timestamp = d["timestamp"]
        return event


KAFKA_TOPICS = {
    EventType.LOAN_APPLICATION_SUBMITTED: "loan-applications",
    EventType.LOAN_SCORED: "loan-scoring",
    EventType.LOAN_FRAUD_CHECKED: "loan-fraud-checks",
    EventType.LOAN_POLICY_DECIDED: "loan-policy-decisions",
    EventType.LOAN_COMPLETED: "loan-completions",
    EventType.LOAN_FAILED: "loan-failures",
    EventType.FRAUD_SCAN_COMPLETED: "fraud-scans",
    EventType.FRAUD_RING_DETECTED: "fraud-rings",
    EventType.REPORT_REQUESTED: "report-requests",
    EventType.REPORT_COMPLETED: "report-completions",
    EventType.MODEL_DRIFT_DETECTED: "model-drift",
}