"""
Alert history management - Avoid duplicate notifications.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, asdict
from loguru import logger

from config.settings import get_settings


@dataclass
class AlertRecord:
    """Record of a sent alert."""
    ticker: str
    strategy: str
    score: int
    timestamp: str
    price: float


class AlertHistory:
    """
    Manage alert history to avoid sending duplicate notifications.

    Alerts are considered duplicates if:
    - Same ticker + same strategy within cooldown period
    """

    def __init__(self, cooldown_hours: int = 24):
        """
        Initialize alert history.

        Args:
            cooldown_hours: Hours before same ticker/strategy can alert again
        """
        settings = get_settings()
        self.history_file = settings.data_dir / "alert_history.json"
        self.cooldown_hours = cooldown_hours
        self._history: Dict[str, AlertRecord] = {}
        self._load_history()

    def _load_history(self) -> None:
        """Load history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._history = {
                        k: AlertRecord(**v) for k, v in data.items()
                    }
                logger.debug(f"Loaded {len(self._history)} alert records")
            except Exception as e:
                logger.error(f"Error loading alert history: {e}")
                self._history = {}
        else:
            self._history = {}

    def _save_history(self) -> None:
        """Save history to file."""
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, "w", encoding="utf-8") as f:
                data = {k: asdict(v) for k, v in self._history.items()}
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving alert history: {e}")

    def _make_key(self, ticker: str, strategy: str) -> str:
        """Create unique key for ticker+strategy combination."""
        return f"{ticker.upper()}:{strategy}"

    def is_duplicate(self, ticker: str, strategy: str) -> bool:
        """
        Check if this alert was already sent recently.

        Args:
            ticker: Stock ticker
            strategy: Strategy name

        Returns:
            True if duplicate (within cooldown period)
        """
        key = self._make_key(ticker, strategy)

        if key not in self._history:
            return False

        record = self._history[key]
        record_time = datetime.fromisoformat(record.timestamp)
        cutoff = datetime.now() - timedelta(hours=self.cooldown_hours)

        return record_time > cutoff

    def record_alert(self, ticker: str, strategy: str, score: int, price: float) -> None:
        """
        Record that an alert was sent.

        Args:
            ticker: Stock ticker
            strategy: Strategy name
            score: Alert score
            price: Current price
        """
        key = self._make_key(ticker, strategy)
        self._history[key] = AlertRecord(
            ticker=ticker.upper(),
            strategy=strategy,
            score=score,
            timestamp=datetime.now().isoformat(),
            price=price
        )
        self._save_history()
        logger.info(f"Recorded alert: {ticker} - {strategy}")

    def get_new_alerts(self, analyses: List) -> List:
        """
        Filter analyses to only include new (non-duplicate) alerts.

        Args:
            analyses: List of TickerAnalysis objects

        Returns:
            Filtered list with only new alerts
        """
        new_alerts = []

        for a in analyses:
            if not a.has_signal or not a.best_strategy:
                continue

            if not self.is_duplicate(a.ticker, a.best_strategy):
                new_alerts.append(a)
            else:
                logger.debug(f"Skipping duplicate alert: {a.ticker} - {a.best_strategy}")

        return new_alerts

    def cleanup_old_records(self, days: int = 30) -> int:
        """
        Remove records older than specified days.

        Args:
            days: Remove records older than this

        Returns:
            Number of records removed
        """
        cutoff = datetime.now() - timedelta(days=days)
        old_keys = []

        for key, record in self._history.items():
            record_time = datetime.fromisoformat(record.timestamp)
            if record_time < cutoff:
                old_keys.append(key)

        for key in old_keys:
            del self._history[key]

        if old_keys:
            self._save_history()
            logger.info(f"Cleaned up {len(old_keys)} old alert records")

        return len(old_keys)

    def get_recent_alerts(self, hours: int = 24) -> List[AlertRecord]:
        """
        Get alerts sent in the last N hours.

        Args:
            hours: Look back period

        Returns:
            List of recent AlertRecords
        """
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = []

        for record in self._history.values():
            record_time = datetime.fromisoformat(record.timestamp)
            if record_time > cutoff:
                recent.append(record)

        # Sort by timestamp descending
        recent.sort(key=lambda x: x.timestamp, reverse=True)
        return recent

    def clear_history(self) -> None:
        """Clear all alert history."""
        self._history = {}
        self._save_history()
        logger.info("Alert history cleared")
