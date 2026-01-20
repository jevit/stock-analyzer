"""
Backtesting engine - Test strategies on historical data.
"""
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import pandas as pd
from loguru import logger

from src.indicators.technical import calculate_indicators
from src.strategies.trend_pullback import TrendPullbackStrategy
from src.strategies.breakout import BreakoutStrategy
from src.strategies.mean_reversion import MeanReversionStrategy
from src.strategies.macd_crossover import MACDCrossoverStrategy
from src.strategies.golden_cross import GoldenCrossStrategy
from src.strategies.volume_breakout import VolumeBreakoutStrategy
from src.backtest.trade import Trade
from config.settings import get_settings


class BacktestEngine:
    """Backtest trading strategies on historical data."""

    def __init__(
        self,
        lookback_days: int = 365,
        max_holding_days: int = 30,
        slippage_pct: float = 0.1
    ):
        """
        Initialize backtesting engine.

        Args:
            lookback_days: Days of history to test (365 = 1 year)
            max_holding_days: Max days to hold a position before forced exit
            slippage_pct: Slippage on entry/exit (0.1 = 0.1%)
        """
        self.lookback_days = lookback_days
        self.max_holding_days = max_holding_days
        self.slippage_pct = slippage_pct / 100

        # Initialize strategies
        settings = get_settings()
        self.strategies = {
            "Trend Pullback": TrendPullbackStrategy(),
            "Breakout": BreakoutStrategy(),
            "Mean Reversion": MeanReversionStrategy(),
            "MACD Crossover": MACDCrossoverStrategy(),
            "Golden Cross": GoldenCrossStrategy(),
            "Volume Breakout": VolumeBreakoutStrategy(),
        }

    def backtest_ticker(
        self,
        ticker: str,
        df: pd.DataFrame,
        strategy_name: str = None
    ) -> List[Trade]:
        """
        Backtest a single ticker.

        Args:
            ticker: Stock ticker
            df: Price DataFrame with indicators
            strategy_name: Specific strategy to test (None = all)

        Returns:
            List of trades
        """
        # Get recent data for backtesting
        cutoff_date = df.index[-1] - timedelta(days=self.lookback_days)
        df_test = df[df.index >= cutoff_date].copy()

        if len(df_test) < 60:
            logger.warning(f"{ticker}: Not enough data for backtesting")
            return []

        # Recalculate indicators on test data
        df_test = calculate_indicators(df_test)

        all_trades = []

        # Test each strategy
        strategies_to_test = {strategy_name: self.strategies[strategy_name]} if strategy_name else self.strategies

        for strat_name, strategy in strategies_to_test.items():
            trades = self._backtest_strategy(ticker, df_test, strat_name, strategy)
            all_trades.extend(trades)

        return all_trades

    def _backtest_strategy(
        self,
        ticker: str,
        df: pd.DataFrame,
        strategy_name: str,
        strategy
    ) -> List[Trade]:
        """
        Backtest a specific strategy on a ticker.

        Args:
            ticker: Stock ticker
            df: Price DataFrame
            strategy_name: Strategy name
            strategy: Strategy instance

        Returns:
            List of trades
        """
        trades = []
        open_trades = []

        # Iterate through each day
        for i in range(60, len(df)):  # Need 60 days for indicators
            current_date = df.index[i]
            current_row = df.iloc[:i+1]  # Data up to current day

            # Update open trades
            for trade in open_trades:
                if trade.is_closed:
                    continue

                high = df['High'].iloc[i]
                low = df['Low'].iloc[i]
                close = df['Close'].iloc[i]

                # Update extremes
                trade.update_extremes(low)
                trade.update_extremes(high)

                # Check stop loss
                if low <= trade.stop_loss:
                    exit_price = trade.stop_loss * (1 - self.slippage_pct)
                    trade.close_trade(current_date, exit_price, "stop_loss")
                    continue

                # Check take profit
                if high >= trade.take_profit:
                    exit_price = trade.take_profit * (1 - self.slippage_pct)
                    trade.close_trade(current_date, exit_price, "take_profit")
                    continue

                # Check timeout
                if trade.duration_days >= self.max_holding_days:
                    trade.close_trade(current_date, close, "timeout")
                    continue

                # Update duration
                trade.duration_days = (current_date - trade.entry_date).days

            # Check for new signal
            result = strategy.analyze(current_row)

            if result.signal_detected and result.entry_level and result.invalidation_level and result.target_level:
                # Apply slippage to entry
                entry_price = result.entry_level * (1 + self.slippage_pct)

                # Verify entry is still valid (price didn't blow past it)
                next_open = df['Open'].iloc[i+1] if i+1 < len(df) else df['Close'].iloc[i]

                # Only enter if next day's open is within reasonable range of entry
                if abs(next_open - entry_price) / entry_price < 0.05:  # 5% max gap
                    trade = Trade(
                        ticker=ticker,
                        strategy=strategy_name,
                        entry_date=df.index[i+1] if i+1 < len(df) else current_date,
                        entry_price=entry_price,
                        stop_loss=result.invalidation_level,
                        take_profit=result.target_level,
                    )

                    open_trades.append(trade)
                    trades.append(trade)

        # Close any remaining open trades at last price
        last_date = df.index[-1]
        last_price = df['Close'].iloc[-1]

        for trade in open_trades:
            if not trade.is_closed:
                trade.close_trade(last_date, last_price, "end_of_data")

        return trades

    def backtest_all(
        self,
        data: Dict[str, pd.DataFrame],
        strategy_name: str = None
    ) -> Dict[str, List[Trade]]:
        """
        Backtest all tickers.

        Args:
            data: Dict of ticker -> DataFrame
            strategy_name: Specific strategy to test (None = all)

        Returns:
            Dict of ticker -> list of trades
        """
        all_results = {}

        for ticker, df in data.items():
            logger.info(f"Backtesting {ticker}...")
            trades = self.backtest_ticker(ticker, df, strategy_name)
            if trades:
                all_results[ticker] = trades

        return all_results
