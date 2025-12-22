from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "Trade Opportunities API"
    gemini_api_key: Optional[str] = None
    allowed_sectors: list = [
        "pharmaceuticals", "technology", "agriculture", 
        "automobile", "banking", "renewable-energy",
        "real-estate", "manufacturing", "retail"
    ]
    
    # Rate limiting
    rate_limit_requests: int = 10
    rate_limit_period: int = 60  # seconds
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()