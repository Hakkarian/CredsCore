from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
import httpx
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CredsCore API Gateway",
    description="Central entry point for all CredsCore services",
    version="1.0.0"
)

# Service endpoint mappings
SERVICE_ENDPOINTS = {
    '/predict': os.getenv('MAIN_SERVER_URL', 'http://server:8000'),
    '/health': os.getenv('MAIN_SERVER_URL', 'http://server:8000'),
    '/model-info': os.getenv('MAIN_SERVER_URL', 'http://server:8000'),
    '/similar-applicants': os.getenv('MAIN_SERVER_URL', 'http://server:8000'),
    '/explain-denial': os.getenv('MAIN_SERVER_URL', 'http://server:8000'),
    '/thin-file-predict': os.getenv('MAIN_SERVER_URL', 'http://server:8000'),
    '/monitor-drift': os.getenv('MAIN_SERVER_URL', 'http://server:8000'),
    '/peer-groups': os.getenv('MAIN_SERVER_URL', 'http://server:8000'),
    '/apply': os.getenv('ORCHESTRATOR_URL', 'http://orchestrator:8000'),
    '/applications': os.getenv('ORCHESTRATOR_URL', 'http://orchestrator:8000'),
    '/score': os.getenv('CREDIT_SCORING_URL', 'http://credit-scoring:8000'),
    '/similar': os.getenv('FRAUD_DETECTION_URL', 'http://fraud-detection:8000'),
    '/evaluate': os.getenv('POLICY_URL', 'http://policy:8000'),
    '/enrich': os.getenv('DATA_ENRICHMENT_URL', 'http://data-enrichment:8000'),
}

# Default service URL
DEFAULT_SERVICE_URL = os.getenv('MAIN_SERVER_URL', 'http://server:8000')

@app.api_route('/{path:path}', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
async def proxy(request: Request, path: str):
    try:
        # Determine target service based on path
        target_service_url = DEFAULT_SERVICE_URL
        
        # Check if path matches any service endpoint
        for endpoint, service_url in SERVICE_ENDPOINTS.items():
            if path.startswith(endpoint.lstrip('/')):
                target_service_url = service_url
                break
        
        # Construct target URL
        target_url = f"{target_service_url}/{path}"
        
        # Get request headers, excluding internal headers
        headers = dict(request.headers)
        # Remove headers that might cause issues
        headers.pop('host', None)
        headers.pop('content-length', None)
        
        # Add gateway identification headers
        headers['x-gateway-request'] = 'true'
        headers['x-gateway-service'] = target_service_url
        
        # Prepare request data
        body = await request.body()
        
        # Make the request to the target service
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=dict(request.query_params),
                timeout=30.0
            )
        
        # Return response from target service
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
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

@app.get('/health')
async def health_check():
    """Health check endpoint for the API Gateway itself"""
    return {
        "status": "healthy",
        "timestamp": "2026-04-08T16:10:56Z",
        "uptime": 0,
        "gateway_version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv('PORT', '4000')))