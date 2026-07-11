from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All configuration comes from env vars / .env — nothing hardcoded."""

    model_config = SettingsConfigDict(
        env_prefix="MYSTIC_", env_file=".env", extra="ignore"
    )

    # where the agent keeps its local state (vault, audit, skills);
    # kept apart from ~/.mystic-agent/venv so 'reset' never touches the app
    data_dir: Path = Path.home() / ".mystic-agent" / "data"

    # http api / dashboard
    host: str = "127.0.0.1"
    port: int = 7700
    # telephony relay — separate, minimal server; ONLY this port is ever
    # exposed via a tunnel, never the dashboard/vault endpoints
    relay_port: int = 7701

    # llm — provider is inferred from the model name prefix
    llm_model: str = "claude-sonnet-5"
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # telegram
    telegram_bot_token: str = ""
    telegram_owner_id: int = 0  # only this chat id may command the agent

    # heartbeat event interval in seconds; 0 disables it
    heartbeat_seconds: int = 0

    @property
    def db_path(self) -> Path:
        return self.data_dir / "mystic.sqlite3"

    @property
    def vault_key_path(self) -> Path:
        return self.data_dir / "vault.key"

    def ensure_dirs(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
