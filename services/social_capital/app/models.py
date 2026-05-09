"""Pydantic models for Social Capital Scoring Service.

These models align with the TypeScript types defined in client/src/lib/types.ts
"""
from typing import Dict, List, Literal, Optional, Any
from pydantic import BaseModel, Field


class NetworkNode(BaseModel):
    """A node in the social network graph."""
    id: str = Field(..., description="Unique identifier for the node")
    label: str = Field(..., description="Display name/label for the node")
    type: Literal["individual", "organization", "business", "influencer"] = Field(
        ..., description="Type of entity"
    )
    centrality_score: float = Field(default=0.0, description="Network centrality score")
    influence_score: float = Field(default=0.0, description="Influence score (PageRank-like)")
    trust_score: float = Field(default=0.0, description="Trust score based on network position")
    community_count: int = Field(default=0, description="Number of communities this node belongs to")
    x: Optional[float] = Field(default=None, description="X coordinate for visualization")
    y: Optional[float] = Field(default=None, description="Y coordinate for visualization")
    vx: Optional[float] = Field(default=None, description="Velocity X for simulation")
    vy: Optional[float] = Field(default=None, description="Velocity Y for simulation")


class NetworkEdge(BaseModel):
    """An edge connecting two nodes in the social network graph."""
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    weight: float = Field(default=1.0, description="Edge weight/strength")
    relationship: Literal["friend", "colleague", "family", "business", "influencer"] = Field(
        ..., description="Type of relationship"
    )


class SocialMetrics(BaseModel):
    """Social capital metrics for an entity."""
    centrality: float = Field(default=0.0, description="Network centrality score")
    influence: float = Field(default=0.0, description="Overall influence in network")
    trust: float = Field(default=0.0, description="Trustworthiness score")
    reach: float = Field(default=0.0, description="Network reach/expansion")
    engagement: float = Field(default=0.0, description="Engagement level")
    communities: int = Field(default=0, description="Number of communities connected")


class SocialCapitalRequest(BaseModel):
    """Request to calculate social capital metrics."""
    entity_id: str = Field(..., description="Unique identifier for the entity")
    entity_type: Literal["individual", "organization", "business"] = Field(
        default="individual", description="Type of entity"
    )
    depth: int = Field(default=2, ge=1, le=5, description="Network exploration depth")
    include_network: bool = Field(default=True, description="Include full network data")


class RiskIndicators(BaseModel):
    """Risk indicators based on network analysis."""
    fraud_risk: float = Field(default=0.0, ge=0.0, le=1.0, description="Fraud risk score")
    default_risk: float = Field(default=0.0, ge=0.0, le=1.0, description="Default risk score")
    reputational_risk: float = Field(default=0.0, ge=0.0, le=1.0, description="Reputational risk score")
    anomaly_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Network anomaly score")


class SocialCapitalResponse(BaseModel):
    """Response containing social capital scores."""
    entity_id: str = Field(..., description="Entity identifier")
    entity_type: str = Field(..., description="Entity type")
    scores: SocialMetrics = Field(..., description="Social capital metrics")
    network_size: int = Field(default=0, description="Total nodes in network")
    connection_count: int = Field(default=0, description="Direct connections")
    risk_indicators: RiskIndicators = Field(..., description="Calculated risk indicators")
    analysis_summary: str = Field(..., description="Human-readable summary")
    timestamp: str = Field(..., description="Analysis timestamp")


class NetworkData(BaseModel):
    """Complete network data for visualization."""
    nodes: List[NetworkNode] = Field(default_factory=list, description="Network nodes")
    edges: List[NetworkEdge] = Field(default_factory=list, description="Network edges")
    entity_id: str = Field(..., description="Focus entity ID")
    total_nodes: int = Field(default=0, description="Total node count")
    total_edges: int = Field(default=0, description="Total edge count")
    communities: int = Field(default=0, description="Detected community count")


class NetworkAnalysisRequest(BaseModel):
    """Request for network analysis."""
    nodes: List[NetworkNode] = Field(..., description="Network nodes")
    edges: List[NetworkEdge] = Field(..., description="Network edges")
    analysis_type: Literal["centrality", "community", "influence", "full"] = Field(
        default="full", description="Type of analysis to perform"
    )
    entity_ids: Optional[List[str]] = Field(default=None, description="Specific entities to analyze")


class NetworkAnalysisResult(BaseModel):
    """Result of network analysis."""
    centrality_scores: Dict[str, float] = Field(default_factory=dict, description="Centrality by node")
    community_assignments: Dict[str, int] = Field(default_factory=dict, description="Community by node")
    influence_scores: Dict[str, float] = Field(default_factory=dict, description="Influence by node")
    network_density: float = Field(default=0.0, description="Network density")
    average_clustering: float = Field(default=0.0, description="Average clustering coefficient")
    community_count: int = Field(default=0, description="Number of communities")
    modularity: float = Field(default=0.0, description="Community modularity score")
    recommendations: List[str] = Field(default_factory=list, description="Analysis recommendations")


class EntityCacheEntry(BaseModel):
    """Cached social capital score for an entity."""
    entity_id: str = Field(..., description="Entity identifier")
    scores: SocialMetrics = Field(..., description="Social capital metrics")
    network_data: Optional[NetworkData] = Field(default=None, description="Associated network data")
    risk_indicators: RiskIndicators = Field(..., description="Risk indicators")
    calculated_at: str = Field(..., description="Calculation timestamp")
    expires_at: Optional[str] = Field(default=None, description="Cache expiration")


class EntityResponse(BaseModel):
    """Response for entity lookup."""
    entity_id: str = Field(..., description="Entity identifier")
    cached: bool = Field(default=False, description="Whether result is cached")
    data: Optional[SocialCapitalResponse] = Field(default=None, description="Entity data if found")
    message: str = Field(default="Entity found", description="Status message")


class VisualizationDataRequest(BaseModel):
    """Request for visualization data."""
    entity_id: str = Field(..., description="Center entity ID")
    depth: int = Field(default=2, ge=1, le=4, description="Network depth")
    max_nodes: int = Field(default=100, ge=10, le=500, description="Maximum nodes to return")
    include_metrics: bool = Field(default=True, description="Include calculated metrics")


class VisualizationDataResponse(BaseModel):
    """Response containing visualization-ready network data."""
    entity_id: str = Field(..., description="Center entity ID")
    network: NetworkData = Field(..., description="Network graph data")
    metrics: Optional[SocialMetrics] = Field(default=None, description="Focus entity metrics")
    risk_indicators: Optional[RiskIndicators] = Field(default=None, description="Risk indicators")
    layout_algorithm: str = Field(default="force-directed", description="Layout algorithm used")


class AnomalyDetectionResult(BaseModel):
    """Result of anomaly detection on network."""
    anomalies_detected: bool = Field(default=False, description="Whether anomalies were found")
    anomaly_count: int = Field(default=0, description="Number of anomalies")
    suspicious_nodes: List[str] = Field(default_factory=list, description="Suspicious node IDs")
    suspicious_patterns: List[str] = Field(default_factory=list, description="Detected patterns")
    risk_level: Literal["low", "medium", "high"] = Field(default="low", description="Overall risk level")
    details: Dict[str, Any] = Field(default_factory=dict, description="Detailed findings")


class CentralityMetrics(BaseModel):
    """Detailed centrality metrics for a node."""
    degree: float = Field(default=0.0, description="Degree centrality")
    betweenness: float = Field(default=0.0, description="Betweenness centrality")
    closeness: float = Field(default=0.0, description="Closeness centrality")
    eigenvector: float = Field(default=0.0, description="Eigenvector centrality")
    normalized: bool = Field(default=True, description="Whether values are normalized")


class CommunityInfo(BaseModel):
    """Information about a detected community."""
    community_id: int = Field(..., description="Community identifier")
    size: int = Field(default=0, description="Number of members")
    members: List[str] = Field(default_factory=list, description="Member node IDs")
    density: float = Field(default=0.0, description="Internal density")
    avg_centrality: float = Field(default=0.0, description="Average centrality")


class RiskCalculationRequest(BaseModel):
    """Request for risk indicator calculation."""
    entity_id: str = Field(..., description="Entity to analyze")
    network_data: Optional[NetworkData] = Field(default=None, description="Pre-computed network data")
    depth: int = Field(default=2, ge=1, le=5, description="Analysis depth")


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str = Field(default="healthy", description="Service status")
    version: str = Field(default="1.0.0", description="Service version")
    timestamp: str = Field(..., description="Check timestamp")
    uptime_seconds: int = Field(default=0, description="Service uptime")


class ErrorResponse(BaseModel):
    """Error response."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error info")
    code: Optional[str] = Field(default=None, description="Error code")
