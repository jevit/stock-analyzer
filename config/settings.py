"""
Application settings and configuration.
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Settings:
    """Application configuration settings."""

    # Paths
    base_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    data_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "data")
    cache_dir: Path = field(default_factory=lambda: Path(__file__).parent.parent / "data" / "cache")
    tickers_file: Path = field(default_factory=lambda: Path(__file__).parent.parent / "tickers.txt")

    # Data settings
    history_years: int = 5
    cache_expiry_hours: int = 12  # Cache expires after 12 hours

    # Indicator settings
    sma_short: int = 20
    sma_medium: int = 50
    sma_long: int = 200
    rsi_period: int = 14
    atr_period: int = 14
    bb_period: int = 20
    bb_std: int = 2
    volume_avg_period: int = 20

    # Strategy thresholds
    pullback_sma_distance_pct: float = 2.0  # Max distance from SMA50 in %
    breakout_lookback_days: int = 55
    breakout_volume_multiplier: float = 1.5
    breakout_min_atr_pct: float = 1.0  # Minimum ATR% to avoid flat stocks

    # Scoring
    alert_score_threshold: int = 75

    # Telegram settings
    telegram_token: Optional[str] = field(
        default_factory=lambda: os.getenv("TELEGRAM_TOKEN")
    )
    telegram_chat_id: Optional[str] = field(
        default_factory=lambda: os.getenv("TELEGRAM_CHAT_ID")
    )

    # Email settings
    smtp_server: Optional[str] = field(
        default_factory=lambda: os.getenv("SMTP_SERVER")
    )
    smtp_port: int = field(
        default_factory=lambda: int(os.getenv("SMTP_PORT", "587"))
    )
    email_from: Optional[str] = field(
        default_factory=lambda: os.getenv("EMAIL_FROM")
    )
    email_password: Optional[str] = field(
        default_factory=lambda: os.getenv("EMAIL_PASSWORD")
    )
    email_to: Optional[str] = field(
        default_factory=lambda: os.getenv("EMAIL_TO")
    )

    def __post_init__(self):
        """Ensure directories exist."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)


# Singleton instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
