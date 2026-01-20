"""
Trade representation for backtesting.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Trade:
    """Represents a single trade in backtesting."""

    # Entry
    ticker: str
    strategy: str
    entry_date: datetime
    entry_price: float

    # Levels
    stop_loss: float
    take_profit: float

    # Exit
    exit_date: Optional[datetime] = None
    exit_price: Optional[float] = None
    exit_reason: str = ""  # "stop_loss", "take_profit", "timeout"

    # Performance
    pnl_pct: Optional[float] = None
    duration_days: int = 0
    max_adverse_pct: float = 0.0  # Max drawdown during trade
    max_favorable_pct: float = 0.0  # Max gain during trade

    # Status
    is_closed: bool = False
    is_winner: bool = False

    def close_trade(self, exit_date: datetime, exit_price: float, exit_reason: str) -> None:
        """
        Close the trade.

        Args:
            exit_date: Exit date
            exit_price: Exit price
            exit_reason: Reason for exit
        """
        self.exit_date = exit_date
        self.exit_price = exit_price
        self.exit_reason = exit_reason
        self.is_closed = True

        # Calculate P&L
        self.pnl_pct = ((exit_price - self.entry_price) / self.entry_price) * 100
        self.is_winner = self.pnl_pct > 0

        # Duration
        self.duration_days = (exit_date - self.entry_date).days

    def update_extremes(self, price: float) -> None:
        """
        Update max adverse and favorable moves.

        Args:
            price: Current price
        """
        pnl_pct = ((price - self.entry_price) / self.entry_price) * 100

        if pnl_pct < 0:
            self.max_adverse_pct = min(self.max_adverse_pct, pnl_pct)
        else:
            self.max_favorable_pct = max(self.max_favorable_pct, pnl_pct)

    @property
    def risk_reward_realized(self) -> float:
        """Calculate realized risk/reward ratio."""
        if not self.is_closed:
            return 0.0

        risk = abs((self.stop_loss - self.entry_price) / self.entry_price * 100)
        if risk == 0:
            return 0.0

        return abs(self.pnl_pct) / risk

    def __repr__(self) -> str:
        status = "CLOSED" if self.is_closed else "OPEN"
        result = "WIN" if self.is_winner else "LOSS"
        return (
            f"Trade({self.ticker}, {self.strategy}, "
            f"{self.entry_date.date()}, {status}, "
            f"{result if self.is_closed else ''}, "
            f"PnL: {self.pnl_pct:.2f}% if self.is_closed else 'N/A')"
        )
