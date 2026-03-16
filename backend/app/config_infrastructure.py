"""
Infrastructure Configuration Adapter
Adapts MiroFish to use STAX infrastructure (LiteLLM + Qdrant)
"""

import os
from typing import Optional


class InfrastructureConfig:
    """Configuration for STAX infrastructure integration"""

    # LLM Configuration (via LiteLLM Gateway)
    LITELLM_BASE_URL: str = os.getenv(
        "LITELLM_BASE_URL", "http://litellm.inference.svc.cluster.local:4000/v1"
    )
    LITELLM_API_KEY: str = os.getenv("LITELLM_API_KEY", "sk-internal")
    LITELLM_MODEL: str = os.getenv("LITELLM_MODEL", "qwen2.5-coder-32b")

    # Qdrant Configuration (Vector Database for Memory)
    QDRANT_URL: str = os.getenv(
        "QDRANT_URL", "http://qdrant.inference.svc.cluster.local:6333"
    )
    QDRANT_API_KEY: Optional[str] = os.getenv("QDRANT_API_KEY")
    QDRANT_COLLECTION_PREFIX: str = os.getenv("QDRANT_COLLECTION_PREFIX", "mirofish")

    # Langfuse Observability (optional)
    LANGFUSE_PUBLIC_KEY: Optional[str] = os.getenv("LANGFUSE_PUBLIC_KEY")
    LANGFUSE_SECRET_KEY: Optional[str] = os.getenv("LANGFUSE_SECRET_KEY")
    LANGFUSE_HOST: str = os.getenv(
        "LANGFUSE_HOST", "http://langfuse.inference.svc.cluster.local:3000"
    )

    # Legacy Zep Support (fallback)
    USE_ZEP: bool = os.getenv("USE_ZEP", "false").lower() == "true"
    ZEP_API_KEY: Optional[str] = os.getenv("ZEP_API_KEY")

    @classmethod
    def get_llm_config(cls) -> dict:
        """Get LLM configuration for OpenAI SDK"""
        return {
            "api_key": cls.LITELLM_API_KEY,
            "base_url": cls.LITELLM_BASE_URL,
            "default_model": cls.LITELLM_MODEL,
        }

    @classmethod
    def get_qdrant_config(cls) -> dict:
        """Get Qdrant configuration"""
        config = {
            "url": cls.QDRANT_URL,
            "collection_prefix": cls.QDRANT_COLLECTION_PREFIX,
        }
        if cls.QDRANT_API_KEY:
            config["api_key"] = cls.QDRANT_API_KEY
        return config

    @classmethod
    def is_langfuse_enabled(cls) -> bool:
        """Check if Langfuse observability is enabled"""
        return bool(cls.LANGFUSE_PUBLIC_KEY and cls.LANGFUSE_SECRET_KEY)
