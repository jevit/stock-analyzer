"""
Backtesting results analysis and statistics.
"""
from dataclasses import dataclass
from typing import List, Dict
import pandas as pd

from src.backtest.trade import Trade


@dataclass
class BacktestResults:
    """Aggregated backtesting results."""

    strategy_name: str
    period: str

    # Trade counts
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0

    # Win rate
    win_rate_pct: float = 0.0

    # Returns
    avg_win_pct: float = 0.0
    avg_loss_pct: float = 0.0
    avg_return_pct: float = 0.0
    total_return_pct: float = 0.0

    # Best/Worst
    best_trade_pct: float = 0.0
    worst_trade_pct: float = 0.0

    # Risk metrics
    profit_factor: float = 0.0  # Total wins / Total losses
    avg_rr_realized: float = 0.0  # Average realized R/R
    max_consecutive_losses: int = 0

    # Duration
    avg_duration_days: float = 0.0
    avg_win_duration_days: float = 0.0
    avg_loss_duration_days: float = 0.0

    # Exit reasons
    stop_loss_exits: int = 0
    take_profit_exits: int = 0
    timeout_exits: int = 0

    # Drawdown
    max_drawdown_pct: float = 0.0


def analyze_trades(trades: List[Trade], strategy_name: str = "All", period: str = "1Y") -> BacktestResults:
    """
    Analyze a list of trades and compute statistics.

    Args:
        trades: List of closed trades
        strategy_name: Strategy name
        period: Time period

    Returns:
        BacktestResults with statistics
    """
    if not trades:
        return BacktestResults(strategy_name=strategy_name, period=period)

    # Filter closed trades only
    closed_trades = [t for t in trades if t.is_closed]

    if not closed_trades:
        return BacktestResults(strategy_name=strategy_name, period=period)

    results = BacktestResults(strategy_name=strategy_name, period=period)

    # Counts
    results.total_trades = len(closed_trades)
    results.winning_trades = sum(1 for t in closed_trades if t.is_winner)
    results.losing_trades = results.total_trades - results.winning_trades

    # Win rate
    results.win_rate_pct = (results.winning_trades / results.total_trades) * 100 if results.total_trades > 0 else 0

    # Returns
    winners = [t for t in closed_trades if t.is_winner]
    losers = [t for t in closed_trades if not t.is_winner]

    if winners:
        results.avg_win_pct = sum(t.pnl_pct for t in winners) / len(winners)
        results.best_trade_pct = max(t.pnl_pct for t in winners)

    if losers:
        results.avg_loss_pct = sum(t.pnl_pct for t in losers) / len(losers)
        results.worst_trade_pct = min(t.pnl_pct for t in losers)

    results.avg_return_pct = sum(t.pnl_pct for t in closed_trades) / len(closed_trades)
    results.total_return_pct = sum(t.pnl_pct for t in closed_trades)

    # Profit factor
    total_wins = sum(abs(t.pnl_pct) for t in winners) if winners else 0
    total_losses = sum(abs(t.pnl_pct) for t in losers) if losers else 0

    results.profit_factor = (total_wins / total_losses) if total_losses > 0 else 0

    # Average R/R realized
    rr_ratios = [t.risk_reward_realized for t in closed_trades if t.risk_reward_realized > 0]
    results.avg_rr_realized = sum(rr_ratios) / len(rr_ratios) if rr_ratios else 0

    # Max consecutive losses
    max_consec = 0
    current_consec = 0

    for t in closed_trades:
        if not t.is_winner:
            current_consec += 1
            max_consec = max(max_consec, current_consec)
        else:
            current_consec = 0

    results.max_consecutive_losses = max_consec

    # Duration
    durations = [t.duration_days for t in closed_trades]
    results.avg_duration_days = sum(durations) / len(durations) if durations else 0

    if winners:
        results.avg_win_duration_days = sum(t.duration_days for t in winners) / len(winners)

    if losers:
        results.avg_loss_duration_days = sum(t.duration_days for t in losers) / len(losers)

    # Exit reasons
    results.stop_loss_exits = sum(1 for t in closed_trades if t.exit_reason == "stop_loss")
    results.take_profit_exits = sum(1 for t in closed_trades if t.exit_reason == "take_profit")
    results.timeout_exits = sum(1 for t in closed_trades if t.exit_reason == "timeout")

    # Max drawdown (cumulative)
    cumulative_returns = []
    cumulative = 0
    for t in closed_trades:
        cumulative += t.pnl_pct
        cumulative_returns.append(cumulative)

    if cumulative_returns:
        peak = cumulative_returns[0]
        max_dd = 0

        for ret in cumulative_returns:
            if ret > peak:
                peak = ret
            dd = peak - ret
            max_dd = max(max_dd, dd)

        results.max_drawdown_pct = max_dd

    return results


def analyze_by_strategy(all_trades: Dict[str, List[Trade]]) -> Dict[str, BacktestResults]:
    """
    Analyze trades grouped by strategy.

    Args:
        all_trades: Dict of ticker -> list of trades

    Returns:
        Dict of strategy name -> BacktestResults
    """
    # Flatten all trades
    flat_trades = []
    for trades in all_trades.values():
        flat_trades.extend(trades)

    # Group by strategy
    by_strategy = {}

    for trade in flat_trades:
        if trade.strategy not in by_strategy:
            by_strategy[trade.strategy] = []
        by_strategy[trade.strategy].append(trade)

    # Analyze each strategy
    results = {}

    for strategy_name, trades in by_strategy.items():
        results[strategy_name] = analyze_trades(trades, strategy_name=strategy_name)

    # Also add "All Strategies" combined
    results["All Strategies"] = analyze_trades(flat_trades, strategy_name="All Strategies")

    return results


def create_equity_curve(trades: List[Trade]) -> pd.DataFrame:
    """
    Create an equity curve from trades.

    Args:
        trades: List of closed trades

    Returns:
        DataFrame with date and cumulative return
    """
    if not trades:
        return pd.DataFrame(columns=['Date', 'Cumulative_Return'])

    # Sort by exit date
    sorted_trades = sorted([t for t in trades if t.is_closed], key=lambda x: x.exit_date)

    dates = []
    cumulative = []
    cum_return = 0

    for trade in sorted_trades:
        cum_return += trade.pnl_pct
        dates.append(trade.exit_date)
        cumulative.append(cum_return)

    df = pd.DataFrame({
        'Date': dates,
        'Cumulative_Return': cumulative
    })

    return df
