"""
Transformer Service 설정
"""
from pydantic_settings import BaseSettings
from typing import Optional


class TransformerServiceConfig(BaseSettings):
    """Transformer 서비스 설정"""
    
    service_name: str = "transformer"
    service_version: str = "1.0.0"
    port: int = 9004
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

