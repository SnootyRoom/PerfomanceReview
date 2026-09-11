from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://app:app@localhost:5432/performance_review"
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60 * 24 * 7

    cors_origins: str = "http://localhost:5173,http://localhost:8080"

    # VK community bot (dev.vk.com/ru/method/messages.send); no-op without a token.
    vk_bot_token: str = ""
    vk_api_version: str = "5.199"
    vk_reminder_days_ahead: int = 3
    vk_reminder_check_interval_hours: int = 24

    # GigaChat (Sber) — free-tier LLM for the AI-analysis feature; no-op without a key.
    gigachat_auth_key: str = ""
    gigachat_scope: str = "GIGACHAT_API_PERS"
    gigachat_model: str = "GigaChat"
    # Sber's endpoints use a Russian root CA most systems don't trust out of
    # the box; off by default, flip once that CA is in the container's trust store.
    gigachat_verify_ssl: bool = False

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
