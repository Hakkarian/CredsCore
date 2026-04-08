# CredsCore Python API Gateway

This is the central API gateway for the CredsCore platform, implemented in Python using FastAPI. It serves as a single entry point for all client requests, routing them to appropriate microservices while providing cross-cutting concerns like authentication, rate limiting, logging, and monitoring.

## Features

- Request routing to microservices
- Authentication and authorization (to be implemented)
- Rate limiting (to be implemented)
- Request/response logging
- CORS handling
- Security headers
- Error handling
- Health checks

## Environment Variables

- `MAIN_SERVER_URL`: URL of the main server (default: http://server:8000)
- `CREDIT_SCORING_URL`: URL of the credit scoring service (default: http://credit-scoring:8000)
- `FRAUD_DETECTION_URL`: URL of the fraud detection service (default: http://fraud-detection:8000)
- `DATA_ENRICHMENT_URL`: URL of the data enrichment service (default: http://data-enrichment:8000)
- `POLICY_URL`: URL of the policy service (default: http://policy:8000)
- `ORCHESTRATOR_URL`: URL of the orchestrator service (default: http://orchestrator:8000)
- `PORT`: Port to listen on (default: 4000)

## Running Locally

```bash
cd services/api-gateway
pip install -r requirements.txt
python main.py
```

## Building for Production

```bash
docker build -t credscore-api-gateway .
docker run -p 4000:4000 credscore-api-gateway
```