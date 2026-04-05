"""
RGCN Feature Factory for Credit Risk Assessment.

This module provides Relational Graph Convolutional Network (RGCN) capabilities
for augmenting credit risk predictions with graph-based features.

Separation of concerns:
- RGCN generates features (embeddings) only
- LightGBM makes predictions using those features
- Policy engine makes decisions (unchanged)
"""

from .graph_builder import GraphBuilder
from .feature_factory import RGCNFeatureFactory

__all__ = ["GraphBuilder", "RGCNFeatureFactory"]