import asyncio
from typing import Optional
from .feature_factory import RGCNFeatureFactory


# Global RGCN feature factory instance
_rgcn_factory: Optional[RGCNFeatureFactory] = None


def get_rgcn_factory() -> Optional[RGCNFeatureFactory]:
    """Get or create the global RGCN feature factory instance."""
    global _rgcn_factory
    if _rgcn_factory is None:
        try:
            model_dir = get_rgcn_model_dir()
            _rgcn_factory = RGCNFeatureFactory()
            _rgcn_factory.load(model_dir)
        except Exception as e:
            print(f"Warning: Could not initialize RGCN factory: {e}")
            _rgcn_factory = None
    return _rgcn_factory


def get_rgcn_model_dir() -> str:
    """Get the path to the saved RGCN models directory."""
    import os

    return os.path.join(os.path.dirname(__file__), "..", "..", "saved_models")


async def predict_rgcn_features(request) -> dict:
    """
    Extract RGCN features for an applicant.

    Args:
        request: PredictionRequest with applicant data

    Returns:
        dict: RGCN features in RGCNFeaturesResponse format
    """
    factory = get_rgcn_factory()
    if factory is None or not factory.is_loaded:
        return {
            "features": [],
            "feature_names": [],
            "confidence": 0.0,
        }

    import pandas as pd

    df = pd.DataFrame([{fn: getattr(request, fn, 0) for fn in factory.feature_names}])

    try:
        embeddings = factory.get_embedding_only(df)
        feature_list = embeddings[0].tolist()

        return {
            "features": feature_list,
            "feature_names": [f"rgcn_dim_{i}" for i in range(len(feature_list))],
            "confidence": 0.85,
        }
    except Exception as e:
        print(f"Error extracting RGCN features: {e}")
        return {
            "features": [],
            "feature_names": [],
            "confidence": 0.0,
        }
