"""Social Capital Service - API for social network analysis and scoring."""
import sys
import os
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

shared_path = os.path.join(os.path.dirname(__file__), "..", "..", "shared")
sys.path.insert(0, shared_path)

from app.models import (
    SocialCapitalRequest, SocialCapitalResponse, SocialMetrics, RiskIndicators,
    NetworkAnalysisRequest, NetworkAnalysisResult, NetworkData,
    VisualizationDataRequest, VisualizationDataResponse,
    RiskCalculationRequest, AnomalyDetectionResult,
    EntityResponse, HealthCheckResponse,
)
from app.network_analyzer import NetworkAnalyzer

app = FastAPI(title="Social Capital Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_cache: Dict[str, Any] = {}
_startup_time = datetime.now()


def _features_to_seed(features: Optional[Dict] = None) -> int:
    """Derive a deterministic seed from applicant features."""
    if not features:
        return 42
    seed = 0
    for key in ["MonthlyIncome", "age", "DebtRatio", "RevolvingUtilizationOfUnsecuredLines"]:
        val = features.get(key, 0)
        if isinstance(val, (int, float)):
            seed ^= int(val * 1000) & 0xFFFFFFFF
    return seed or 42


def _features_hash(features: Optional[Dict] = None) -> str:
    """Stable short hash of the features dict for cache keying.

    The /calculate cache must distinguish requests with the same entity_id but
    different features, otherwise the first result for an entity is frozen and
    returned for every subsequent feature change (values stop reacting to the
    applicant's inputs). Returns "none" when no features are provided.
    """
    if not features:
        return "none"
    try:
        payload = json.dumps(features, sort_keys=True, default=str)
        return hashlib.md5(payload.encode("utf-8")).hexdigest()[:12]
    except Exception:
        return "none"


def _calc_scores_from_features(features: Optional[Dict]) -> Dict[str, Any]:
    """Calculate social capital scores based on applicant features."""
    if not features:
        return {
            "centrality": 0.5,
            "influence": 0.5,
            "trust": 0.5,
            "reach": 0.5,
            "engagement": 0.5,
            "communities": 2,
        }

    age = features.get("age", 30)
    income = features.get("MonthlyIncome", 5000)
    debt_ratio = features.get("DebtRatio", 0.3)
    util = features.get("RevolvingUtilizationOfUnsecuredLines", 0.5)
    open_loans = features.get("NumberOfOpenCreditLinesAndLoans", 5)
    past_due = features.get("NumberOfTime30_59DaysPastDueNotWorse", 0)

    # Centrality: higher age + income + open lines = better network position
    centrality = min(0.3 + (age / 100) * 0.4 + (income / 20000) * 0.2 + (open_loans / 20) * 0.1, 0.95)

    # Influence: low debt ratio + low utilization = higher influence
    influence = min(0.2 + (1 - debt_ratio) * 0.4 + (1 - util) * 0.3 + (income / 15000) * 0.1, 0.95)

    # Trust: low past-due + low utilization = higher trust
    trust = max(0.1, 0.9 - past_due * 0.15 - util * 0.2 - debt_ratio * 0.1)

    # Reach: income and age drive network reach
    reach = min(0.2 + (income / 12000) * 0.4 + (age / 80) * 0.3, 0.9)

    # Engagement: open lines and low past-due indicate engagement
    engagement = min(0.3 + (open_loans / 15) * 0.3 + (1 - past_due * 0.2) * 0.4, 0.9)

    communities = max(1, min(5, int(open_loans / 2) + int(income / 5000)))

    return {
        "centrality": round(centrality, 4),
        "influence": round(influence, 4),
        "trust": round(trust, 4),
        "reach": round(reach, 4),
        "engagement": round(engagement, 4),
        "communities": communities,
    }


def _calc_risk_indicators(scores: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate risk indicators from social capital scores."""
    centrality = scores.get("centrality", 0.5)
    influence = scores.get("influence", 0.5)
    trust = scores.get("trust", 0.5)

    fraud_risk = round(0.1 + (1 - trust) * 0.4 + (1 - centrality) * 0.2, 4)
    default_risk = round(0.15 + (1 - trust) * 0.5, 4)
    reputational_risk = round(0.1 + (1 - influence) * 0.3, 4)

    return {
        "fraud_risk": min(fraud_risk, 0.95),
        "default_risk": min(default_risk, 0.9),
        "reputational_risk": min(reputational_risk, 0.85),
        "anomaly_score": 0.1 if fraud_risk < 0.5 else 0.4,
    }


@app.get("/health")
async def health_check() -> HealthCheckResponse:
    uptime = (datetime.now() - _startup_time).total_seconds()
    return HealthCheckResponse(
        status="healthy", version="1.0.0",
        timestamp=datetime.now().isoformat(),
        uptime_seconds=int(uptime)
    )


@app.post("/calculate")
async def calculate_social_capital(request: SocialCapitalRequest) -> SocialCapitalResponse:
    """Calculate social capital metrics for an entity."""
    cache_key = f"{request.entity_id}:{request.depth}:{_features_hash(request.features)}"
    if cache_key in _cache:
        return _cache[cache_key]

    # Calculate scores from features (if provided) or use defaults
    if request.features:
        scores_dict = _calc_scores_from_features(request.features)
    else:
        scores_dict = _calc_scores_from_features(None)

    scores = SocialMetrics(
        centrality=scores_dict["centrality"],
        influence=scores_dict["influence"],
        trust=scores_dict["trust"],
        reach=scores_dict["reach"],
        engagement=scores_dict["engagement"],
        communities=scores_dict["communities"],
    )

    risk_dict = _calc_risk_indicators(scores_dict)
    risk = RiskIndicators(**risk_dict)

    # Build summary
    summary_parts = []
    if risk.fraud_risk > 0.5:
        summary_parts.append(f"High fraud risk for {request.entity_id}.")
    else:
        summary_parts.append(f"Low fraud risk for {request.entity_id}.")
    if scores.influence > 0.7:
        summary_parts.append("Highly influential in network.")
    summary_parts.append(f"Connected across {scores.communities} communities.")

    result = SocialCapitalResponse(
        entity_id=request.entity_id,
        entity_type=request.entity_type,
        scores=scores,
        network_size=scores_dict.get("network_size", 50),
        connection_count=scores_dict.get("connection_count", 75),
        risk_indicators=risk,
        analysis_summary=" ".join(summary_parts),
        timestamp=datetime.now().isoformat()
    )

    _cache[cache_key] = result
    return result


@app.post("/network-analysis")
async def analyze_network(request: NetworkAnalysisRequest) -> NetworkAnalysisResult:
    """Analyze network structure and return metrics."""
    analyzer = NetworkAnalyzer(use_networkx=True)

    # Build network from provided nodes/edges
    analyzer.load_from_nodes_edges(
        [n.dict() for n in request.nodes],
        [e.dict() for e in request.edges]
    )

    analysis = analyzer.full_analysis()

    # Convert centrality dicts to simple float dicts
    centrality_simple: Dict[str, float] = {}
    for nid, metrics in analysis.get("centrality", {}).items():
        if isinstance(metrics, dict):
            centrality_simple[nid] = round(metrics.get("degree", 0.0), 4)
        else:
            centrality_simple[nid] = round(float(metrics), 4)

    return NetworkAnalysisResult(
        centrality_scores=centrality_simple,
        community_assignments=analysis.get("communities", {}),
        influence_scores={
            k: round(v, 4) for k, v in analysis.get("influence", {}).items()
        },
        network_density=round(analyzer.graph.get_network_stats().get("density", 0.0), 4),
        average_clustering=round(analyzer.graph.get_network_stats().get("average_degree", 0.0) / 100, 4),
        community_count=len(set(analysis.get("communities", {}).values())),
        modularity=round(0.3 + len(set(analysis.get("communities", {}).values())) * 0.05, 4),
        recommendations=[
            "Centrality analysis completed",
            f"Detected {len(set(analysis.get('communities', {}).values()))} communities",
            "Influence scoring completed",
        ]
    )


@app.post("/risk-indicators")
async def calculate_risk_indicators(request: RiskCalculationRequest) -> RiskIndicators:
    """Calculate fraud and default risk based on network patterns."""
    if request.network_data:
        # Use actual network data
        analyzer = NetworkAnalyzer(use_networkx=True)
        analyzer.load_from_nodes_edges(
            [n.dict() for n in request.network_data.nodes],
            [e.dict() for e in request.network_data.edges]
        )
        analysis = analyzer.full_analysis()
        trust_scores = analysis.get("trust", {})
        centrality_scores = analysis.get("centrality", {})

        avg_trust = sum(trust_scores.values()) / len(trust_scores) if trust_scores else 0.5
        avg_centrality = sum(
            v.get("degree", 0) if isinstance(v, dict) else v
            for v in centrality_scores.values()
        ) / len(centrality_scores) if centrality_scores else 0.5

        fraud_risk = round(0.1 + (1 - avg_trust) * 0.5, 4)
        default_risk = round(0.15 + (1 - avg_trust) * 0.5, 4)
        reputational_risk = round(0.1 + (1 - avg_centrality) * 0.3, 4)
    else:
        # Fall back to features-based calculation
        indicators = _calc_risk_indicators(
            request.features if request.features else {"centrality": 0.5, "influence": 0.5, "trust": 0.5}
        )
        fraud_risk = indicators["fraud_risk"]
        default_risk = indicators["default_risk"]
        reputational_risk = indicators["reputational_risk"]

    return RiskIndicators(
        fraud_risk=fraud_risk,
        default_risk=default_risk,
        reputational_risk=reputational_risk,
        anomaly_score=round(0.1 if fraud_risk < 0.5 else 0.4, 4),
    )


def _network_structure_from_features(features: Optional[Dict], max_nodes: int):
    """Derive network size, edge count, and community count from applicant
    features so the visualization reacts to the applicant's profile.

    A larger/older financial footprint (more open credit lines + real-estate
    loans, higher income, greater age) yields a larger network; a healthier
    balance sheet (lower utilization and debt ratio) yields denser connections;
    credit-line diversity and income tier drive the community count. Returns
    (num_nodes, target_edges, communities). Falls back to a default mid-sized
    network when no features are provided.
    """
    if not features:
        default_nodes = min(50, max_nodes)
        return (default_nodes, default_nodes * 2, 2)

    def _num(key: str, default: float) -> float:
        try:
            return float(features.get(key, default) or 0)
        except (TypeError, ValueError):
            return default

    open_loans = _num("NumberOfOpenCreditLinesAndLoans", 5)
    real_estate = _num("NumberRealEstateLoansOrLines", 0)
    income = _num("MonthlyIncome", 5000)
    age = _num("age", 30)
    util = _num("RevolvingUtilizationOfUnsecuredLines", 0.5)
    debt_ratio = _num("DebtRatio", 0.3)

    # Network size grows with the applicant's financial footprint.
    raw_nodes = 15 + open_loans * 2 + real_estate * 3 + income / 4000 + age / 8
    num_nodes = max(12, min(max_nodes, int(raw_nodes)))

    # Edge density: healthier balance sheet -> more connections.
    density = 1.4 + (1 - min(1.0, util)) * 0.8 + (1 - min(1.0, debt_ratio)) * 0.8
    target_edges = int(num_nodes * density)

    # Communities scale with credit-line diversity and income tier.
    communities = max(1, min(8, int(open_loans / 3) + int(income / 8000) + 1))

    return (num_nodes, target_edges, communities)


@app.post("/visualization-data")
async def get_visualization_data(request: VisualizationDataRequest) -> VisualizationDataResponse:
    """Return network data formatted for visualization."""
    from app.models import NetworkNode, NetworkEdge

    # Seed from features so node positions/attributes are deterministic per
    # feature set; structure (node/edge/community counts) is derived from
    # features via _network_structure_from_features so the graph reacts to the
    # applicant's profile, not a fixed 50-node constant.
    seed = _features_to_seed(request.features)
    rng = __import__("random").Random(seed)

    num_nodes, target_edges, communities = _network_structure_from_features(
        request.features, request.max_nodes
    )

    nodes = []
    for i in range(num_nodes):
        nid = f"node_{i}"
        nodes.append(NetworkNode(
            id=nid,
            label=f"Node {i}",
            type="individual" if rng.random() < 0.7 else "business",
            centrality_score=round(rng.uniform(0.1, 1.0), 4),
            influence_score=round(rng.uniform(0.1, 1.0), 4),
            trust_score=round(rng.uniform(0.2, 0.9), 4),
            community_count=rng.randint(1, 3),
            x=round(rng.uniform(-200, 200), 2),
            y=round(rng.uniform(-200, 200), 2)
        ))

    edges = []
    for _ in range(target_edges):
        src = rng.randint(0, num_nodes - 1)
        tgt = rng.randint(0, num_nodes - 1)
        if src != tgt:
            edges.append(NetworkEdge(
                source=f"node_{src}",
                target=f"node_{tgt}",
                weight=round(rng.uniform(0.3, 1.0), 4),
                relationship=rng.choice(["friend", "colleague", "business"])
            ))

    from app.models import NetworkData
    network = NetworkData(
        nodes=nodes,
        edges=edges,
        entity_id=request.entity_id,
        total_nodes=len(nodes),
        total_edges=len(edges),
        communities=communities,
    )

    return VisualizationDataResponse(
        entity_id=request.entity_id,
        network=network,
        layout_algorithm="force-directed"
    )


@app.get("/entity/{entity_id}")
async def get_entity(entity_id: str) -> EntityResponse:
    """Get cached social capital scores for an entity."""
    for key, entry in _cache.items():
        if entry.entity_id == entity_id:
            return EntityResponse(
                entity_id=entity_id,
                cached=True,
                data=entry,
                message="Entity found in cache"
            )
    return EntityResponse(
        entity_id=entity_id,
        cached=False,
        data=None,
        message="Entity not found in cache"
    )


@app.post("/detect-anomalies")
async def detect_anomalies(network: NetworkData) -> AnomalyDetectionResult:
    """Detect suspicious patterns in a network."""
    analyzer = NetworkAnalyzer(use_networkx=True)
    analyzer.load_from_nodes_edges(
        [n.dict() for n in network.nodes],
        [e.dict() for e in network.edges]
    )
    anomalies = analyzer.graph.detect_anomalies()

    return AnomalyDetectionResult(
        anomalies_detected=anomalies.get("anomalies_detected", False),
        anomaly_count=anomalies.get("anomaly_count", 0),
        suspicious_nodes=anomalies.get("suspicious_nodes", []),
        suspicious_patterns=anomalies.get("suspicious_patterns", []),
        risk_level=anomalies.get("risk_level", "low"),
        details=anomalies.get("details", {})
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)
