import os
import shutil
from pathlib import Path
import certifi
from dotenv import load_dotenv

# Base directory of the repository
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

# Configure SSL certificates
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

# Auto-configure LangSmith tracing if LANGCHAIN_API_KEY is present
if os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "true")
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "TripMate-MultiAgent")
    os.environ["LANGCHAIN_ENDPOINT"] = os.getenv(
        "LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com"
    )


class Settings:
    """Application and environment configuration settings."""

    BASE_DIR: Path = BASE_DIR
    STATIC_DIR: Path = BASE_DIR / "static"
    TEMPLATES_DIR: Path = BASE_DIR / "templates"

    # API Keys
    GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")
    DATABASE_URL: str | None = os.getenv("DATABASE_URL")
    TAVILY_API_KEY: str | None = os.getenv("TAVILY_API_KEY")
    AVIATION_STACK_API_KEY: str | None = (
        os.getenv("AVIATION_STACK_API_KEY")
        or os.getenv("AVIATIONSTACK_API_KEY")
    )
    OPENWEATHER_API_KEY: str | None = os.getenv("OPENWEATHER_API_KEY")

    # LangSmith Observability & Tracing
    LANGCHAIN_TRACING_V2: str = os.getenv("LANGCHAIN_TRACING_V2", "false")
    LANGCHAIN_API_KEY: str | None = os.getenv("LANGCHAIN_API_KEY")
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "TripMate-MultiAgent")
    LANGCHAIN_ENDPOINT: str = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")

    # MCP and Server paths
    WEATHER_SERVER_PATH: Path = BASE_DIR / "custom_weather_mcp_server.py"
    UVX_COMMAND: str = shutil.which("uvx") or "uvx"

    # LLM Settings
    DEFAULT_LLM_MODEL: str = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")

    @classmethod
    def require(cls, name: str, value: str | None) -> str:
        """Validate and return an environment variable or raise a helpful error."""
        if not value:
            raise RuntimeError(
                f"Missing required configuration: {name}. "
                f"Please add {name}=your_key to your .env file."
            )
        return value

    @classmethod
    def get_database_url(cls) -> str:
        """Get validated PostgreSQL connection string with SSL mode."""
        url = cls.require("DATABASE_URL", cls.DATABASE_URL)
        if "sslmode=" not in url:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}sslmode=require"
        return url


settings = Settings()
