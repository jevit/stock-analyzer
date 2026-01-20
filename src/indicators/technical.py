"""
Technical indicators calculation.
"""
import pandas as pd
import numpy as np
from loguru import logger

from config.settings import get_settings


def calculate_sma(series: pd.Series, period: int) -> pd.Series:
    """Calculate Simple Moving Average."""
    return series.rolling(window=period, min_periods=period).mean()


def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index.

    Args:
        series: Price series (typically Close)
        period: RSI period (default 14)

    Returns:
        RSI values (0-100)
    """
    delta = series.diff()

    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    # Use Wilder's smoothing after initial SMA
    for i in range(period, len(series)):
        avg_gain.iloc[i] = (avg_gain.iloc[i - 1] * (period - 1) + gain.iloc[i]) / period
        avg_loss.iloc[i] = (avg_loss.iloc[i - 1] * (period - 1) + loss.iloc[i]) / period

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Average True Range.

    Args:
        high: High prices
        low: Low prices
        close: Close prices
        period: ATR period (default 14)

    Returns:
        ATR values
    """
    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = true_range.rolling(window=period, min_periods=period).mean()

    return atr


def calculate_macd(
    series: pd.Series,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate MACD (Moving Average Convergence Divergence).

    Args:
        series: Price series (typically Close)
        fast_period: Fast EMA period (default 12)
        slow_period: Slow EMA period (default 26)
        signal_period: Signal line period (default 9)

    Returns:
        Tuple of (MACD line, Signal line, Histogram)
    """
    ema_fast = series.ewm(span=fast_period, adjust=False).mean()
    ema_slow = series.ewm(span=slow_period, adjust=False).mean()

    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram


def calculate_bollinger_bands(
    series: pd.Series,
    period: int = 20,
    num_std: int = 2
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate Bollinger Bands.

    Args:
        series: Price series (typically Close)
        period: Moving average period (default 20)
        num_std: Number of standard deviations (default 2)

    Returns:
        Tuple of (middle_band, upper_band, lower_band)
    """
    middle = calculate_sma(series, period)
    std = series.rolling(window=period, min_periods=period).std()

    upper = middle + (std * num_std)
    lower = middle - (std * num_std)

    return middle, upper, lower


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate all technical indicators for a price DataFrame.

    Args:
        df: DataFrame with OHLCV data (Open, High, Low, Close, Volume)

    Returns:
        DataFrame with additional indicator columns
    """
    settings = get_settings()

    if df is None or df.empty:
        logger.warning("Empty DataFrame provided to calculate_indicators")
        return df

    # Make a copy to avoid modifying original
    df = df.copy()

    # Ensure we have required columns
    required = ["Open", "High", "Low", "Close", "Volume"]
    if not all(col in df.columns for col in required):
        raise ValueError(f"DataFrame must contain columns: {required}")

    logger.debug(f"Calculating indicators for {len(df)} rows")

    # Simple Moving Averages
    df["SMA20"] = calculate_sma(df["Close"], settings.sma_short)
    df["SMA50"] = calculate_sma(df["Close"], settings.sma_medium)
    df["SMA200"] = calculate_sma(df["Close"], settings.sma_long)

    # RSI
    df["RSI"] = calculate_rsi(df["Close"], settings.rsi_period)

    # ATR
    df["ATR"] = calculate_atr(df["High"], df["Low"], df["Close"], settings.atr_period)

    # ATR as percentage of close (volatility measure)
    df["ATR_pct"] = (df["ATR"] / df["Close"]) * 100

    # Bollinger Bands
    df["BB_middle"], df["BB_upper"], df["BB_lower"] = calculate_bollinger_bands(
        df["Close"], settings.bb_period, settings.bb_std
    )

    # MACD
    df["MACD"], df["MACD_signal"], df["MACD_hist"] = calculate_macd(df["Close"])

    # Volume Average
    df["Volume_avg20"] = calculate_sma(df["Volume"], settings.volume_avg_period)

    # Volume ratio (current volume vs average)
    df["Volume_ratio"] = df["Volume"] / df["Volume_avg20"]

    # Distance from SMAs (in percentage)
    df["Dist_SMA20_pct"] = ((df["Close"] - df["SMA20"]) / df["SMA20"]) * 100
    df["Dist_SMA50_pct"] = ((df["Close"] - df["SMA50"]) / df["SMA50"]) * 100
    df["Dist_SMA200_pct"] = ((df["Close"] - df["SMA200"]) / df["SMA200"]) * 100

    # Highest high over lookback period (for breakout)
    df["High_55d"] = df["High"].rolling(window=settings.breakout_lookback_days).max()

    # RSI crossing 50 (for trend pullback)
    df["RSI_prev1"] = df["RSI"].shift(1)
    df["RSI_prev2"] = df["RSI"].shift(2)
    df["RSI_crossed_50_up"] = (
        (df["RSI"] > 50) &
        ((df["RSI_prev1"] <= 50) | (df["RSI_prev2"] <= 50))
    )

    # Daily returns for additional analysis
    df["Return_1d"] = df["Close"].pct_change() * 100

    logger.debug("Indicators calculated successfully")

    return df


def get_latest_indicators(df: pd.DataFrame) -> dict:
    """
    Extract latest indicator values as a dictionary.

    Args:
        df: DataFrame with calculated indicators

    Returns:
        Dictionary with latest values for each indicator
    """
    if df is None or df.empty:
        return {}

    latest = df.iloc[-1]

    return {
        "date": df.index[-1],
        "close": latest["Close"],
        "open": latest["Open"],
        "high": latest["High"],
        "low": latest["Low"],
        "volume": latest["Volume"],
        "sma20": latest.get("SMA20"),
        "sma50": latest.get("SMA50"),
        "sma200": latest.get("SMA200"),
        "rsi": latest.get("RSI"),
        "atr": latest.get("ATR"),
        "atr_pct": latest.get("ATR_pct"),
        "bb_upper": latest.get("BB_upper"),
        "bb_lower": latest.get("BB_lower"),
        "bb_middle": latest.get("BB_middle"),
        "volume_avg20": latest.get("Volume_avg20"),
        "volume_ratio": latest.get("Volume_ratio"),
        "dist_sma50_pct": latest.get("Dist_SMA50_pct"),
        "dist_sma200_pct": latest.get("Dist_SMA200_pct"),
        "high_55d": latest.get("High_55d"),
        "rsi_crossed_50": latest.get("RSI_crossed_50_up"),
    }
