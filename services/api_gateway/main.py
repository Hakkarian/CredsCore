from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import logging
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("API Gateway starting...")

app = FastAPI(
    title="CredsCore API Gateway",
    description="Central entry point for all CredsCore services",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service endpoint mappings
SERVICE_ENDPOINTS = {
    "/predict": os.getenv("CREDIT_SCORING_URL", "http://localhost:8001"),
    "/client-predict": os.getenv("CREDIT_SCORING_URL", "http://localhost:8001"),
    "/client-predict-large": os.getenv("CREDIT_SCORING_URL", "http://localhost:8001"),
    "/batch-predict": os.getenv("CREDIT_SCORING_URL", "http://localhost:8001"),
    "/rgcn-features": os.getenv("CREDIT_SCORING_URL", "http://localhost:8001"),
    "/model-info": os.getenv("CREDIT_SCORING_URL", "http://localhost:8001"),
    "/similar-applicants": os.getenv("CREDIT_SCORING_URL", "http://localhost:8001"),
    "/explain-denial": os.getenv("CREDIT_SCORING_URL", "http://localhost:8001"),
    "/thin-file-predict": os.getenv("CREDIT_SCORING_URL", "http://localhost:8001"),
    "/monitor-drift": os.getenv("CREDIT_SCORING_URL", "http://localhost:8001"),
    "/peer-groups": os.getenv("CREDIT_SCORING_URL", "http://localhost:8001"),
    "/apply": os.getenv("ORCHESTRATOR_URL", "http://localhost:8005"),
    "/applications": os.getenv("ORCHESTRATOR_URL", "http://localhost:8005"),
    "/score": os.getenv("AUGMENTED_SCORING_URL", "http://localhost:8008"),
    "/similar": os.getenv("FRAUD_DETECTION_URL", "http://localhost:8002"),
    "/similar-combined": os.getenv("FRAUD_DETECTION_URL", "http://localhost:8002"),
    "/fraud-rings": os.getenv("FRAUD_DETECTION_URL", "http://localhost:8002"),
    "/fraud-rings/status": os.getenv("FRAUD_DETECTION_URL", "http://localhost:8002"),
    "/evaluate": os.getenv("POLICY_URL", "http://localhost:8003"),
    "/enrich": os.getenv("DATA_ENRICHMENT_URL", "http://localhost:8006"),
    "/synthetic": os.getenv("SYNTHETIC_DATA_URL", "http://localhost:8007"),
    "/synthetic/health": os.getenv("SYNTHETIC_DATA_URL", "http://localhost:8007"),
    "/synthetic/generate": os.getenv("SYNTHETIC_DATA_URL", "http://localhost:8007"),
    "/synthetic/generate-with-analysis": os.getenv("SYNTHETIC_DATA_URL", "http://localhost:8007"),
    # Augmented Scoring Service (port 8008)
    "/combined": os.getenv("AUGMENTED_SCORING_URL", "http://localhost:8008"),
    "/combined-score": os.getenv("AUGMENTED_SCORING_URL", "http://localhost:8008"),
    "/predict-enhanced": os.getenv("AUGMENTED_SCORING_URL", "http://localhost:8008"),
    # Causal Inference Service (port 8010)
    "/counterfactuals": os.getenv("CAUSAL_INFERENCE_URL", "http://localhost:8010"),
    "/estimate-propensity": os.getenv("CAUSAL_INFERENCE_URL", "http://localhost:8010"),
    "/estimate-treatment-effect": os.getenv("CAUSAL_INFERENCE_URL", "http://localhost:8010"),
    "/uplift-modeling": os.getenv("CAUSAL_INFERENCE_URL", "http://localhost:8010"),
    "/analyze": os.getenv("CAUSAL_INFERENCE_URL", "http://localhost:8010"),
}


# Default service URL
DEFAULT_SERVICE_URL = os.getenv("CREDIT_SCORING_URL", "http://localhost:8001")

# Persistent HTTP Client
http_client: Optional[httpx.AsyncClient] = None


@app.on_event("startup")
async def startup_event():
    global http_client
    http_client = httpx.AsyncClient(timeout=30.0)


@app.on_event("shutdown")
async def shutdown_event():
    if http_client:
        await http_client.aclose()


@app.get("/health")
async def health_check():
    """Health check endpoint for the API Gateway itself"""
    return {
        "status": "healthy",
        "timestamp": "2026-04-08T16:10:56Z",
        "uptime": 0,
        "gateway_version": "1.0.0",
    }


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy(request: Request, path: str):
    # Skip gateway's own endpoints
    if path == "health":
        return await health_check()
    try:
        # Determine target service based on path
        target_service_url = DEFAULT_SERVICE_URL
        path_prefix_to_strip = ""

        # Sort endpoints by length (descending) to match longest first
        # This ensures /synthetic/health matches before /similar
        sorted_endpoints = sorted(SERVICE_ENDPOINTS.items(), key=lambda x: len(x[0]), reverse=True)

        # Check if path matches any service endpoint
        matched_endpoint = None
        for endpoint, service_url in sorted_endpoints:
            endpoint_clean = endpoint.lstrip("/")
            if path.startswith(endpoint_clean):
                target_service_url = service_url
                matched_endpoint = endpoint
                # Strip the prefix for synthetic data routes
                if endpoint.startswith("/synthetic"):
                    path_prefix_to_strip = "synthetic/"
                break
        logger.info(f"Path: {path}, Matched: {matched_endpoint}, Target: {target_service_url}, Strip: {path_prefix_to_strip}")

        # Construct target URL - strip prefix if needed
        target_path = path[len(path_prefix_to_strip):] if path_prefix_to_strip and path.startswith(path_prefix_to_strip) else path
        # Remove leading slash if present to avoid double slashes
        if target_path.startswith("/"):
            target_path = target_path[1:]
        target_url = f"{target_service_url}/{target_path}"
        # Append query parameters if present
        if request.query_params:
            target_url += "?" + str(request.query_params)
        logger.info(f"Proxying to: {target_url}")

        # Get request headers, excluding internal headers
        headers = dict(request.headers)
        # Remove headers that might cause issues
        headers.pop("host", None)
        headers.pop("content-length", None)

        # Add gateway identification headers
        headers["x-gateway-request"] = "true"
        headers["x-gateway-service"] = target_service_url

        # Prepare request data
        body = await request.body()

        # Make the request to the target service
        response = await http_client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=body,
            params=dict(request.query_params),
        )

        # Return response from target service
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
        )

    except httpx.TimeoutException:
        logger.error(f"Timeout while proxying request to {path}")
        return JSONResponse({"error": "Service timeout"}, status_code=504)
    except httpx.ConnectError:
        logger.error(f"Connection error while proxying request to {path}")
        return JSONResponse({"error": "Service unavailable"}, status_code=503)
    except Exception as e:
        logger.error(f"Error proxying request to {path}: {str(e)}")
        return JSONResponse({"error": "Internal server error"}, status_code=500)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "4000")))
