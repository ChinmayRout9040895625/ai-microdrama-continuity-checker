"""All runtime settings come from environment variables / .env, so the model can be swapped without code changes."""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

PROMPT_VERSION = "v2"


@dataclass(frozen=True)
class Settings:
    provider: str = "anthropic"
    model_extract: str = "claude-sonnet-5-5"
    model_check: str = "claude-sonnet-5-5"
    effort_extract: str = "medium"
    effort_check: str = "medium"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    max_workers: int = 4
    cache_dir: str = ".cache"

    def model_for(self, step: str) -> str:
        if self.provider == "ollama":
            return self.ollama_model
        return self.model_extract if step == "extract" else self.model_check

    def effort_for(self, step: str) -> str:
        return self.effort_extract if step == "extract" else self.effort_check


def get_settings(**overrides) -> Settings:
    """Read the environment at call time; keyword overrides win (used by the UI)."""
    env = {
        "provider": os.getenv("LLM_PROVIDER", "anthropic").lower(),
        "model_extract": os.getenv("MODEL_EXTRACT", "claude-sonnet-5-5"),
        "model_check": os.getenv("MODEL_CHECK", "claude-sonnet-5-5"),
        "effort_extract": os.getenv("EFFORT_EXTRACT", "medium"),
        "effort_check": os.getenv("EFFORT_CHECK", "medium"),
        "ollama_url": os.getenv("OLLAMA_URL", "http://localhost:11434"),
        "ollama_model": os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
        "max_workers": int(os.getenv("MAX_WORKERS", "4")),
        "cache_dir": os.getenv("CACHE_DIR", ".cache"),
    }
    env.update({k: v for k, v in overrides.items() if v is not None})
    return Settings(**env)
