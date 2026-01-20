"""
Data downloader using yfinance.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import yfinance as yf
from loguru import logger

from config.settings import get_settings
from src.data.cache import CacheManager


def download_ticker_data(
    ticker: str,
    use_cache: bool = True,
    force_refresh: bool = False
) -> Optional[pd.DataFrame]:
    """
    Download historical price data for a ticker.

    Args:
        ticker: Stock ticker symbol
        use_cache: Whether to use cached data if available
        force_refresh: Force download even if cache is valid

    Returns:
        DataFrame with OHLCV data or None if download fails
    """
    settings = get_settings()
    cache = CacheManager()
    ticker = ticker.upper()

    # Try to get from cache first
    if use_cache and not force_refresh:
        cached_data = cache.get_cached_data(ticker)
        if cached_data is not None:
            return cached_data

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=settings.history_years * 365)

    logger.info(f"Downloading {ticker} data from {start_date.date()} to {end_date.date()}")

    try:
        # Download from yfinance
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date, auto_adjust=True)

        if df.empty:
            logger.warning(f"No data returned for {ticker}")
            return None

        # Ensure we have required columns
        required_cols = ["Open", "High", "Low", "Close", "Volume"]
        if not all(col in df.columns for col in required_cols):
            logger.error(f"Missing required columns for {ticker}")
            return None

        # Keep only required columns
        df = df[required_cols].copy()

        # Remove timezone info from index if present
        if df.index.tz is not None:
            df.index = df.index.tz_localize(None)

        # Add ticker column
        df["Ticker"] = ticker

        logger.info(f"Downloaded {len(df)} rows for {ticker}")

        # Save to cache
        if use_cache:
            cache.save_to_cache(ticker, df)

        return df

    except Exception as e:
        logger.error(f"Error downloading {ticker}: {e}")
        return None


def download_all_tickers(
    tickers: List[str],
    use_cache: bool = True,
    force_refresh: bool = False,
    progress_callback: Optional[callable] = None
) -> Tuple[Dict[str, pd.DataFrame], List[str]]:
    """
    Download data for multiple tickers.

    Args:
        tickers: List of ticker symbols
        use_cache: Whether to use cached data
        force_refresh: Force refresh all data
        progress_callback: Optional callback for progress updates (ticker, current, total)

    Returns:
        Tuple of (dict mapping ticker to DataFrame, list of failed tickers)
    """
    results = {}
    failed = []

    total = len(tickers)
    for i, ticker in enumerate(tickers):
        if progress_callback:
            progress_callback(ticker, i + 1, total)

        data = download_ticker_data(ticker, use_cache=use_cache, force_refresh=force_refresh)

        if data is not None:
            results[ticker] = data
        else:
            failed.append(ticker)

    logger.info(f"Downloaded {len(results)}/{total} tickers successfully")
    if failed:
        logger.warning(f"Failed tickers: {failed}")

    return results, failed


# Cache for ticker info to avoid repeated API calls
_ticker_info_cache: Dict[str, dict] = {}


def get_ticker_info(ticker: str, use_cache: bool = True) -> Optional[dict]:
    """
    Get basic info about a ticker.

    Args:
        ticker: Stock ticker symbol
        use_cache: Use cached info if available

    Returns:
        Dictionary with ticker info or None
    """
    ticker = ticker.upper()

    # Check cache first
    if use_cache and ticker in _ticker_info_cache:
        return _ticker_info_cache[ticker]

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        result = {
            "name": info.get("shortName") or info.get("longName") or ticker,
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": info.get("marketCap", 0),
            "currency": info.get("currency", "USD"),

            # Valuation metrics
            "trailingPE": info.get("trailingPE"),
            "forwardPE": info.get("forwardPE"),
            "pegRatio": info.get("pegRatio"),
            "priceToBook": info.get("priceToBook"),
            "priceToSalesTrailing12Months": info.get("priceToSalesTrailing12Months"),

            # Growth metrics
            "revenueGrowth": info.get("revenueGrowth"),
            "earningsGrowth": info.get("earningsGrowth"),

            # Profitability
            "profitMargins": info.get("profitMargins"),
            "returnOnEquity": info.get("returnOnEquity"),

            # Dividends
            "dividendYield": info.get("dividendYield"),
            "payoutRatio": info.get("payoutRatio"),
        }

        # Cache the result
        _ticker_info_cache[ticker] = result
        return result

    except Exception as e:
        logger.debug(f"Could not get info for {ticker}: {e}")
        # Cache failure to avoid repeated calls
        _ticker_info_cache[ticker] = {"name": ticker}
        return {"name": ticker}


def preload_ticker_info(tickers: List[str]) -> None:
    """
    Preload info for multiple tickers (for performance).

    Args:
        tickers: List of ticker symbols
    """
    for ticker in tickers:
        if ticker.upper() not in _ticker_info_cache:
            get_ticker_info(ticker)
