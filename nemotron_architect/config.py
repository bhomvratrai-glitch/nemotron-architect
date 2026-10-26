import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

@dataclass
class Config:
    # Nebius Token Factory & NVIDIA Model Settings
    nebius_api_key: str = os.getenv("NEBIUS_API_KEY", "")
    nebius_base_url: str = os.getenv("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1")
    nebius_model: str = os.getenv("NEBIUS_MODEL", "nvidia/llama-3.1-nemotron-70b-instruct")

    # Tavily Real-Time Search API
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")

    # Execution Sandbox Settings
    max_self_heal_attempts: int = int(os.getenv("MAX_SELF_HEAL_ATTEMPTS", "3"))
    timeout_seconds: int = int(os.getenv("EXECUTION_TIMEOUT_SECONDS", "30"))

    # Server Settings
    server_host: str = os.getenv("HOST", "127.0.0.1")
    server_port: int = int(os.getenv("PORT", "8000"))

config = Config()
