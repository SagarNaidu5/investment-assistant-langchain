import os
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path
import logging

@dataclass
class ProductionConfig:
    """Production configuration management"""

    # Environment settings
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")

    # LLM Configuration
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    model_temperature: float = field(default_factory=lambda: float(os.getenv("MODEL_TEMPERATURE", "0.1")))
    model_timeout: int = field(default_factory=lambda: int(os.getenv("MODEL_TIMEOUT", "60")))

    # API Rate Limiting
    max_requests_per_minute: int = field(default_factory=lambda: int(os.getenv("MAX_REQUESTS_PER_MINUTE", "60")))
    max_requests_per_day: int = field(default_factory=lambda: int(os.getenv("MAX_REQUESTS_PER_DAY", "1000")))

    # Caching
    enable_caching: bool = field(default_factory=lambda: os.getenv("ENABLE_CACHING", "true").lower() == "true")
    cache_ttl: int = field(default_factory=lambda: int(os.getenv("CACHE_TTL", "3600")))  # 1 hour

    # Logging and Monitoring
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_tracing: bool = field(default_factory=lambda: os.getenv("ENABLE_TRACING", "true").lower() == "true")

    # Security
    api_key_required: bool = field(default_factory=lambda: os.getenv("API_KEY_REQUIRED", "false").lower() == "true")
    allowed_origins: List[str] = field(default_factory=lambda: os.getenv("ALLOWED_ORIGINS", "*").split(","))

    # Data Storage
    data_dir: Path = field(default_factory=lambda: Path(os.getenv("DATA_DIR", "./data")))
    backup_enabled: bool = field(default_factory=lambda: os.getenv("BACKUP_ENABLED", "true").lower() == "true")

    def __post_init__(self):
        # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True)

        # Setup logging
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format=self.log_format,
        )

# Global configuration instance
config = ProductionConfig()
