"""
Telegram notification system.
"""
from typing import List, Optional
import requests
from loguru import logger

from config.settings import get_settings
from src.scoring.scorer import TickerAnalysis


class TelegramNotifier:
    """Send alerts via Telegram bot."""

    def __init__(self, token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        Initialize Telegram notifier.

        Args:
            token: Bot token (or use env TELEGRAM_TOKEN)
            chat_id: Chat ID to send to (or use env TELEGRAM_CHAT_ID)
        """
        settings = get_settings()
        self.token = token or settings.telegram_token
        self.chat_id = chat_id or settings.telegram_chat_id
        self.base_url = f"https://api.telegram.org/bot{self.token}" if self.token else None

    def is_configured(self) -> bool:
        """Check if Telegram is properly configured."""
        return bool(self.token and self.chat_id)

    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        """
        Send a message via Telegram.

        Args:
            text: Message text
            parse_mode: Parse mode (HTML or Markdown)

        Returns:
            True if sent successfully
        """
        if not self.is_configured():
            logger.warning("Telegram not configured - skipping notification")
            return False

        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": parse_mode,
                "disable_web_page_preview": True,
            }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            logger.info("Telegram message sent successfully")
            return True

        except requests.RequestException as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False

    def format_alert_message(self, analyses: List[TickerAnalysis], min_score: int = 75) -> str:
        """
        Format analysis results into a Telegram alert message.

        Args:
            analyses: List of TickerAnalysis
            min_score: Minimum score to include

        Returns:
            Formatted message string
        """
        # Filter by score
        alerts = [a for a in analyses if a.global_score >= min_score and a.has_signal]

        if not alerts:
            return ""

        # Build message
        lines = [
            "📊 <b>Stock Analyzer - Alertes du jour</b>",
            f"<i>{len(alerts)} signal(s) détecté(s) (score ≥ {min_score})</i>",
            "",
        ]

        for a in alerts[:10]:  # Limit to top 10
            # Emoji based on strategy
            emoji = "📈"
            if "Breakout" in a.best_strategy:
                emoji = "🚀"
            elif "Mean Reversion" in a.best_strategy:
                emoji = "🔄"

            lines.append(
                f"{emoji} <b>{a.ticker}</b> - Score: {a.global_score}/100"
            )
            lines.append(
                f"   Stratégie: {a.best_strategy}"
            )
            lines.append(
                f"   Prix: {a.close:.2f} | RSI: {a.rsi:.1f}" if a.rsi else f"   Prix: {a.close:.2f}"
            )

            # Main reason (first one that's informative)
            if a.reasons:
                main_reason = next(
                    (r for r in a.reasons if not r.startswith("⭐")),
                    a.reasons[0]
                )
                lines.append(f"   → {main_reason[:60]}...")
            lines.append("")

        # Footer disclaimer
        lines.append("─" * 30)
        lines.append("<i>⚠️ Analyse technique uniquement - Pas de conseil financier</i>")

        return "\n".join(lines)

    def send_daily_alert(self, analyses: List[TickerAnalysis], min_score: int = 75) -> bool:
        """
        Send daily alert with top opportunities.

        Args:
            analyses: List of TickerAnalysis
            min_score: Minimum score threshold

        Returns:
            True if sent successfully (or no alerts to send)
        """
        message = self.format_alert_message(analyses, min_score)

        if not message:
            logger.info(f"No signals with score >= {min_score} - no alert sent")
            return True

        return self.send_message(message)

    def test_connection(self) -> bool:
        """Test Telegram connection by sending a test message."""
        if not self.is_configured():
            return False

        return self.send_message("🔔 Stock Analyzer - Test de connexion réussi!")
