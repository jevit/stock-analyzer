"""
Fundamental analysis module - Extract key metrics.
"""
from dataclasses import dataclass
from typing import Dict, Optional
import pandas as pd
from loguru import logger

from src.data.downloader import get_ticker_info


@dataclass
class FundamentalMetrics:
    """Fundamental metrics for a ticker."""
    ticker: str
    name: str = ""

    # Valuation
    pe_ratio: Optional[float] = None  # Price/Earnings
    peg_ratio: Optional[float] = None  # P/E to Growth
    pb_ratio: Optional[float] = None  # Price/Book
    ps_ratio: Optional[float] = None  # Price/Sales

    # Growth
    revenue_growth: Optional[float] = None  # Revenue growth %
    earnings_growth: Optional[float] = None  # Earnings growth %

    # Profitability
    profit_margin: Optional[float] = None  # Net margin %
    roe: Optional[float] = None  # Return on Equity %

    # Dividends
    dividend_yield: Optional[float] = None  # Dividend yield %
    payout_ratio: Optional[float] = None  # Payout ratio %

    # Size & Sector
    market_cap: Optional[float] = None  # Market cap
    sector: str = "N/A"
    industry: str = "N/A"

    # Scores
    value_score: int = 0  # 0-100
    growth_score: int = 0  # 0-100
    quality_score: int = 0  # 0-100
    dividend_score: int = 0  # 0-100


def get_fundamental_metrics(ticker: str, df: Optional[pd.DataFrame] = None) -> FundamentalMetrics:
    """
    Get fundamental metrics for a ticker.

    Args:
        ticker: Stock ticker
        df: Price DataFrame (for calculating returns)

    Returns:
        FundamentalMetrics object
    """
    ticker = ticker.upper()

    # Get info from yfinance
    info = get_ticker_info(ticker, use_cache=True)

    if not info:
        return FundamentalMetrics(ticker=ticker)

    # Extract metrics
    metrics = FundamentalMetrics(
        ticker=ticker,
        name=info.get("name", ticker),

        # Valuation
        pe_ratio=info.get("trailingPE") or info.get("forwardPE"),
        peg_ratio=info.get("pegRatio"),
        pb_ratio=info.get("priceToBook"),
        ps_ratio=info.get("priceToSalesTrailing12Months"),

        # Growth
        revenue_growth=info.get("revenueGrowth"),
        earnings_growth=info.get("earningsGrowth"),

        # Profitability
        profit_margin=info.get("profitMargins"),
        roe=info.get("returnOnEquity"),

        # Dividends
        dividend_yield=info.get("dividendYield"),
        payout_ratio=info.get("payoutRatio"),

        # Size & Sector
        market_cap=info.get("marketCap"),
        sector=info.get("sector", "N/A"),
        industry=info.get("industry", "N/A"),
    )

    # Convert percentages
    if metrics.revenue_growth:
        metrics.revenue_growth *= 100
    if metrics.earnings_growth:
        metrics.earnings_growth *= 100
    if metrics.profit_margin:
        metrics.profit_margin *= 100
    if metrics.roe:
        metrics.roe *= 100
    if metrics.dividend_yield:
        metrics.dividend_yield *= 100
    if metrics.payout_ratio:
        metrics.payout_ratio *= 100

    # Calculate scores
    metrics.value_score = _calculate_value_score(metrics)
    metrics.growth_score = _calculate_growth_score(metrics)
    metrics.quality_score = _calculate_quality_score(metrics)
    metrics.dividend_score = _calculate_dividend_score(metrics)

    return metrics


def _calculate_value_score(m: FundamentalMetrics) -> int:
    """Calculate value investing score (0-100)."""
    score = 0
    count = 0

    # Low P/E is good
    if m.pe_ratio is not None and m.pe_ratio > 0:
        if m.pe_ratio < 15:
            score += 30
        elif m.pe_ratio < 20:
            score += 20
        elif m.pe_ratio < 25:
            score += 10
        count += 1

    # Low P/B is good
    if m.pb_ratio is not None and m.pb_ratio > 0:
        if m.pb_ratio < 1.5:
            score += 25
        elif m.pb_ratio < 3:
            score += 15
        elif m.pb_ratio < 5:
            score += 5
        count += 1

    # Low PEG is good
    if m.peg_ratio is not None and m.peg_ratio > 0:
        if m.peg_ratio < 1:
            score += 25
        elif m.peg_ratio < 1.5:
            score += 15
        elif m.peg_ratio < 2:
            score += 5
        count += 1

    # Good profit margin
    if m.profit_margin is not None and m.profit_margin > 0:
        if m.profit_margin > 20:
            score += 20
        elif m.profit_margin > 10:
            score += 10
        count += 1

    return min(100, score) if count > 0 else 0


def _calculate_growth_score(m: FundamentalMetrics) -> int:
    """Calculate growth investing score (0-100)."""
    score = 0
    count = 0

    # Revenue growth
    if m.revenue_growth is not None:
        if m.revenue_growth > 30:
            score += 40
        elif m.revenue_growth > 20:
            score += 30
        elif m.revenue_growth > 10:
            score += 20
        elif m.revenue_growth > 5:
            score += 10
        count += 1

    # Earnings growth
    if m.earnings_growth is not None:
        if m.earnings_growth > 30:
            score += 40
        elif m.earnings_growth > 20:
            score += 30
        elif m.earnings_growth > 10:
            score += 20
        elif m.earnings_growth > 5:
            score += 10
        count += 1

    # Good margins enable growth
    if m.profit_margin is not None and m.profit_margin > 0:
        if m.profit_margin > 15:
            score += 20
        elif m.profit_margin > 10:
            score += 10
        count += 1

    return min(100, score) if count > 0 else 0


def _calculate_quality_score(m: FundamentalMetrics) -> int:
    """Calculate quality score (0-100)."""
    score = 0
    count = 0

    # High ROE
    if m.roe is not None and m.roe > 0:
        if m.roe > 20:
            score += 30
        elif m.roe > 15:
            score += 20
        elif m.roe > 10:
            score += 10
        count += 1

    # Good profit margin
    if m.profit_margin is not None and m.profit_margin > 0:
        if m.profit_margin > 20:
            score += 30
        elif m.profit_margin > 15:
            score += 20
        elif m.profit_margin > 10:
            score += 10
        count += 1

    # Reasonable valuation (not too high)
    if m.pe_ratio is not None and m.pe_ratio > 0:
        if m.pe_ratio < 30:
            score += 20
        elif m.pe_ratio < 40:
            score += 10
        count += 1

    # Good PEG
    if m.peg_ratio is not None and m.peg_ratio > 0:
        if m.peg_ratio < 1.5:
            score += 20
        elif m.peg_ratio < 2:
            score += 10
        count += 1

    return min(100, score) if count > 0 else 0


def _calculate_dividend_score(m: FundamentalMetrics) -> int:
    """Calculate dividend investing score (0-100)."""
    score = 0
    count = 0

    # Dividend yield
    if m.dividend_yield is not None and m.dividend_yield > 0:
        if m.dividend_yield > 4:
            score += 50
        elif m.dividend_yield > 3:
            score += 40
        elif m.dividend_yield > 2:
            score += 30
        elif m.dividend_yield > 1:
            score += 20
        count += 1
    else:
        # No dividend = 0 score
        return 0

    # Sustainable payout ratio
    if m.payout_ratio is not None and m.payout_ratio > 0:
        if 30 <= m.payout_ratio <= 60:
            score += 30  # Sweet spot
        elif 20 <= m.payout_ratio < 30 or 60 < m.payout_ratio <= 75:
            score += 20  # OK
        elif m.payout_ratio < 20 or m.payout_ratio > 75:
            score += 10  # Too low or too high
        count += 1

    # Quality: good profit margin
    if m.profit_margin is not None and m.profit_margin > 0:
        if m.profit_margin > 15:
            score += 20
        elif m.profit_margin > 10:
            score += 10
        count += 1

    return min(100, score) if count > 0 else 0


def get_all_fundamentals(data: Dict[str, pd.DataFrame]) -> Dict[str, FundamentalMetrics]:
    """
    Get fundamentals for all tickers.

    Args:
        data: Dict of ticker -> DataFrame

    Returns:
        Dict of ticker -> FundamentalMetrics
    """
    fundamentals = {}

    for ticker, df in data.items():
        try:
            metrics = get_fundamental_metrics(ticker, df)
            fundamentals[ticker] = metrics
        except Exception as e:
            logger.warning(f"Failed to get fundamentals for {ticker}: {e}")
            fundamentals[ticker] = FundamentalMetrics(ticker=ticker)

    return fundamentals
