from pydantic_settings import BaseSettings
from typing import Optional


class ServiceConfig(BaseSettings):
    service_name: str = "credscore-service"
    port: int = 8000
    debug: bool = False

    database_path: str = "data/service.db"

    redis_url: Optional[str] = None
    kafka_bootstrap_servers: Optional[str] = None

    credit_scoring_url: str = "http://credit-scoring:8000"
    fraud_detection_url: str = "http://fraud-detection:8000"
    policy_url: str = "http://policy:8000"
    report_generator_url: str = "http://report-generator:8000"
    orchestrator_url: str = "http://orchestrator:8000"

    pocketbase_url: str = "http://pocketbase:8090"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}