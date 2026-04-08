import sys
import os
# Add shared library path for local development
shared_path = os.path.join(os.path.dirname(__file__), '..', 'shared')
sys.path.insert(0, shared_path)

# Add current directory to Python path to resolve 'app' imports
sys.path.insert(0, os.path.dirname(__file__))

# Add parent directory to Python path to resolve 'app' module
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os

from credscore_shared import (
    ClientData,
    ScoreRequest,
    ScoreResult,
    RiskFactor,
    RGCNFeaturesResponse,
    HealthCheckResponse,
)
from app.predictor import CreditPredictor

app = FastAPI(
    title="Credit Scoring Service",
    description="LightGBM + RGCN credit risk prediction",
    version="1.0.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

predictor: Optional[CreditPredictor] = None


@app.on_event("startup")
async def startup():
    global predictor
    # Use local path for development, /app/saved_models for Docker
    model_dir = os.getenv("MODEL_DIR", os.path.join(os.path.dirname(__file__), '..', 'saved_models'))
    predictor = CreditPredictor(model_dir)
    try:
        predictor.load_rgcn(model_dir)
    except Exception as e:
        print(f"RGCN not loaded: {e}")


@app.get("/health", response_model=HealthCheckResponse)
def health():
    return HealthCheckResponse(
        status="healthy" if predictor else "unhealthy",
        service_name="credit-scoring",
        dependencies={
            "lightgbm": str(predictor is not None),
            "rgcn": str(predictor.rgcn_loaded if predictor else False),
        },
    )


@app.post("/score")
def score(req: ScoreRequest):
    if not predictor:
        raise HTTPException(status_code=503, detail="Model not loaded")
    try:
        cd = req.applicant.model_dump()
        result = predictor.predict(cd, use_rgcn=req.use_rgcn)
        risk_factors = [RiskFactor(**rf) for rf in result["risk_factors"]]
        rgcn_features = None
        if result.get("rgcn_features"):
            rgcn_features = RGCNFeaturesResponse(**result["rgcn_features"])
        return ScoreResult(
            base_probability=result["base_probability"],
            rgcn_probability=result.get("rgcn_probability"),
            risk_level=result["risk_level"],
            top_risk_factors=risk_factors,
            rgcn_features=rgcn_features,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rgcn-features")
def get_rgcn_features(cd: ClientData):
    if not predictor or not predictor.rgcn_loaded:
        raise HTTPException(status_code=503, detail="RGCN not available")
    try:
        result = predictor.predict(cd.model_dump(), use_rgcn=True)
        if not result.get("rgcn_features"):
            raise HTTPException(status_code=500, detail="Failed to extract RGCN features")
        return RGCNFeaturesResponse(**result["rgcn_features"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/model-info")
def model_info():
    if not predictor:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return predictor.get_model_info()


@app.get("/")
def root():
    return {
        "service": "credit-scoring",
        "version": "1.0.0",
        "endpoints": {
            "/health": "Health check",
            "/score": "Score applicant (POST)",
            "/rgcn-features": "Get RGCN embeddings (POST)",
            "/model-info": "Model information",
        },
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)