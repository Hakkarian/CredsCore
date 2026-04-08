import sys
import os
# Add shared library path for local development
shared_path = os.path.join(os.path.dirname(__file__), '..', '..', 'shared')
sys.path.insert(0, shared_path)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from credscore_shared import HealthCheckResponse, PolicyDecisionRequest, PolicyDecisionResponse
from app.policy import PolicyEngine

app = FastAPI(title="Policy Service", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
engine = PolicyEngine()


@app.get("/health", response_model=HealthCheckResponse)
def health():
    return HealthCheckResponse(status="healthy", service_name="policy", dependencies={"engine": "loaded"})


@app.post("/evaluate")
def evaluate(req: PolicyDecisionRequest):
    result = engine.evaluate(req.probability, req.fraud_score or 0)
    return PolicyDecisionResponse(**result)


@app.get("/")
def root():
    return {"service": "policy", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)