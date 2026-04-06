import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import pandas as pd
import numpy as np
import logging

from app.faiss_index import FAISSCreditIndex
from app.faiss_scorer import FAISSRealTimeScorer
from app.snn_fraud_detector import SNNFraudDetector

logger = logging.getLogger(__name__)


class BatchFraudProcessor:
    """Manages periodic batch processing for SNN fraud ring detection and FAISS index updates."""

    def __init__(
        self,
        data_path: str = "data/cs-training.csv",
        save_dir: str = "saved_models",
        scan_interval_minutes: int = 60,
    ):
        self.data_path = data_path
        self.save_dir = save_dir
        self.scan_interval_minutes = scan_interval_minutes

        self.faiss_index: Optional[FAISSCreditIndex] = None
        self.faiss_scorer: Optional[FAISSRealTimeScorer] = None
        self.snn_detector: Optional[SNNFraudDetector] = None
        self.fraud_cache: Dict[str, Any] = {}
        self.training_data: Optional[pd.DataFrame] = None
        self.training_labels: Optional[pd.Series] = None

        self.last_scan_time: Optional[datetime] = None
        self.is_scanning = False
        self.scan_in_progress = False

    def initialize(self):
        """Load FAISS index and SNN detector from saved state, or initialize them."""
        os.makedirs(self.save_dir, exist_ok=True)

        self.faiss_index = FAISSCreditIndex()
        try:
            self.faiss_index.load_index(self.save_dir)
            self.faiss_scorer = FAISSRealTimeScorer(self.faiss_index)
            logger.info("FAISS index loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load FAISS index: {e}. Building from scratch...")
            self._build_faiss_index()

        self.snn_detector = SNNFraudDetector()
        if not self.snn_detector.load_state(self.save_dir):
            logger.info("SNN detector not found, will build on first scan")

        self._load_training_data()

    def _build_faiss_index(self):
        self._load_training_data()
        if self.training_data is not None and self.training_labels is not None:
            self.faiss_index.build_index(self.training_data, self.training_labels)
            self.faiss_index.save_index(self.save_dir)
            self.faiss_scorer = FAISSRealTimeScorer(self.faiss_index)

    def _load_training_data(self):
        if os.path.exists(self.data_path):
            df = pd.read_csv(self.data_path)
            if "Unnamed: 0" in df.columns:
                df = df.drop("Unnamed: 0", axis=1)
            self.training_labels = df["SeriousDlqin2yrs"]
            self.training_data = df.drop(["SeriousDlqin2yrs"], axis=1)

    async def run_scan(self) -> Dict[str, Any]:
        """Execute a full fraud ring scan. Can be called manually or by scheduler."""
        if self.scan_in_progress:
            return {"status": "scan_already_in_progress", "message": "A scan is currently running. Please wait."}

        self.scan_in_progress = True
        start_time = datetime.now()

        try:
            logger.info("Starting SNN fraud ring detection scan...")
            self._rebuild_snn_graph()

            fraud_rings = self.snn_detector.detect_fraud_rings(
                features=self.training_data.values if self.training_data is not None else None,
                labels=self.training_labels.values if self.training_labels is not None else None,
                faiss_index=self.faiss_index,
            )

            stats = self.snn_detector.get_stats(scan_timestamp=start_time.isoformat())
            self.fraud_cache = stats

            self.snn_detector.save_state(self.save_dir)
            self.last_scan_time = datetime.now()

            elapsed = (self.last_scan_time - start_time).total_seconds()
            stats["scan_duration_seconds"] = round(elapsed, 2)
            stats["status"] = "completed"

            logger.info(
                f"Scan completed in {elapsed:.1f}s. Found {stats['total_rings_detected']} fraud rings "
                f"({stats['high_risk_rings']} high risk, {stats['medium_risk_rings']} medium, {stats['low_risk_rings']} low)"
            )

            return stats

        except Exception as e:
            logger.error(f"Error during fraud ring scan: {e}", exc_info=True)
            return {"status": "error", "message": str(e), "timestamp": datetime.now().isoformat()}
        finally:
            self.scan_in_progress = False

    def _rebuild_snn_graph(self):
        """Rebuild SNN graph with all available applicant data."""
        if self.training_data is not None and self.training_labels is not None:
            features = self.training_data.values.astype(np.float64)
            median = np.nanmedian(features, axis=0)
            features = np.where(np.isnan(features) | np.isinf(features), median, features)
            labels = self.training_labels.values
            self.snn_detector.build_snn_graph(features, labels, self.faiss_index)

    def get_fraud_rings_cache(self) -> Dict[str, Any]:
        """Get cached fraud ring results."""
        if not self.fraud_cache:
            if self.snn_detector and len(self.snn_detector.fraud_rings) > 0:
                self.fraud_cache = self.snn_detector.get_stats()
        return self.fraud_cache

    def get_fraud_ring_by_id(self, ring_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific fraud ring by ID."""
        if not self.snn_detector:
            return None
        for ring in self.snn_detector.fraud_rings:
            if ring.ring_id == ring_id:
                return {
                    "ring_id": ring.ring_id,
                    "member_count": len(ring.members),
                    "avg_risk_score": round(ring.avg_risk_score, 4),
                    "avg_anomaly_score": round(ring.avg_anomaly_score, 4),
                    "cohesiveness": round(ring.cohesiveness, 4),
                    "risk_level": "high" if ring.avg_risk_score > 0.6 else "medium" if ring.avg_risk_score > 0.35 else "low",
                    "risk_factors": ring.risk_factors,
                    "members": [
                        {
                            "index": m.index,
                            "risk_score": round(m.risk_score, 4),
                            "anomaly_score": round(m.anomaly_score, 4),
                            "shared_neighbors": m.shared_neighbor_count,
                        }
                        for m in ring.members
                    ],
                }
        return None

    def score_applicant(self, applicant_data: pd.DataFrame) -> Dict[str, Any]:
        """Score an individual applicant using FAISS real-time scoring."""
        if not self.faiss_scorer:
            raise ValueError("FAISS scorer not initialized")
        return self.faiss_scorer.score_applicant(applicant_data)

    def get_applicant_fraud_rings(self, applicant_index: int) -> List[Dict[str, Any]]:
        """Check if an applicant is part of any detected fraud rings."""
        if not self.snn_detector:
            return []
        return self.snn_detector.get_applicant_rings(applicant_index)

    def get_scan_status(self) -> Dict[str, Any]:
        return {
            "last_scan_time": self.last_scan_time.isoformat() if self.last_scan_time else None,
            "is_scanning": self.scan_in_progress,
            "scan_interval_minutes": self.scan_interval_minutes,
            "fraud_rings_detected": len(self.snn_detector.fraud_rings) if self.snn_detector else 0,
            "faiss_index_size": self.faiss_index.index.ntotal if self.faiss_index and self.faiss_index.index else 0,
        }