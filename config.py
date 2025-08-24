from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Infra
    POSTGRES_DSN: str = "postgresql+asyncpg://solai:solai@localhost:5432/solai"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Providers
    HELIUS_WS: str = "wss://mainnet.helius-rpc.com/?api-key=YOUR_KEY"
    HELIUS_HTTP: str = "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY"
    TRITON_WS: str | None = None  # optionnel

    # Jupiter
    JUPITER_BASE: str = "https://quote-api.jup.ag"
    JUPITER_SWAP: str = "https://quote-api.jup.ag/v6/swap"

    # Telegram
    TG_TOKEN: str | None = None
    TG_CHAT_ID: str | None = None

    # Runtime
    NETWORK: str = "mainnet"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

from connectors.providers import RpcProvider
PROVIDERS = [
    RpcProvider("helius", "wss://mainnet.helius-rpc.com/?api-key=YOUR_KEY", "https://mainnet.helius-rpc.com/?api-key=YOUR_KEY"),
    # Add Triton/Custom
    # RpcProvider("triton", "wss://...", "https://..."),
]

settings = Settings()

# Update providers with actual keys
for p in PROVIDERS:
    p.ws_url = p.ws_url.replace("YOUR_KEY", settings.HELIUS_WS.split("=")[-1])
    p.http_url = p.http_url.replace("YOUR_KEY", settings.HELIUS_HTTP.split("=")[-1])
