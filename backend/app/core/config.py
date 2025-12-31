"""Call Yala - Configuration."""

from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_env: Literal["local", "development", "production"] = "local"
    port: int = 8000
    data_dir: Path = Path("./data")

    # Google Sheets
    google_sheets_spreadsheet_id: str = ""
    google_sheets_range: str = "Sheet1!A1:Z"
    google_service_account_json_path: Path = Path("./secrets/service_account.json")

    # ElevenLabs
    elevenlabs_api_key: str = ""
    elevenlabs_webhook_secret: str = ""
    elevenlabs_agent_id: str = ""
    elevenlabs_phone_number_id: str = ""

    # Anthropic Claude
    anthropic_api_key: str = ""

    # Behavior
    mock_mode: bool = False
    default_timezone: str = "Asia/Kuwait"
    max_batch_size: int = 200
    http_timeout_seconds: int = 30

    @field_validator("data_dir", mode="before")
    @classmethod
    def ensure_data_dir(cls, v):
        """Ensure data directory exists."""
        path = Path(v)
        path.mkdir(parents=True, exist_ok=True)
        (path / "uploads").mkdir(exist_ok=True)
        return path

    @property
    def campaigns_file(self) -> Path:
        return self.data_dir / "campaigns.json"

    @property
    def calls_file(self) -> Path:
        return self.data_dir / "calls.jsonl"

    @property
    def call_index_file(self) -> Path:
        return self.data_dir / "call_index.json"

    @property
    def sheet_cache_file(self) -> Path:
        return self.data_dir / "sheet_cache.json"

    @property
    def webhook_dedup_file(self) -> Path:
        return self.data_dir / "webhook_dedup.json"

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"


settings = Settings()
