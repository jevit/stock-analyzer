"""
Utility functions for the stock analyzer.
"""
import sys
from pathlib import Path
from typing import List
from loguru import logger


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure logging with loguru.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Remove default handler
    logger.remove()

    # Add console handler with formatting
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
    )

    # Add file handler for errors
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    logger.add(
        log_dir / "errors.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
        rotation="1 MB",
        retention="7 days",
    )


def load_tickers(filepath: Path) -> List[str]:
    """
    Load ticker symbols from a text file.

    Args:
        filepath: Path to the tickers file (one ticker per line)

    Returns:
        List of ticker symbols (uppercase, trimmed)

    Raises:
        FileNotFoundError: If the tickers file doesn't exist
    """
    if not filepath.exists():
        raise FileNotFoundError(f"Tickers file not found: {filepath}")

    tickers = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            ticker = line.strip().upper()
            # Skip empty lines and comments
            if ticker and not ticker.startswith("#"):
                tickers.append(ticker)

    logger.info(f"Loaded {len(tickers)} tickers from {filepath}")
    return tickers


def format_number(value: float, decimals: int = 2) -> str:
    """Format a number with thousands separator."""
    if abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:.{decimals}f}B"
    elif abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.{decimals}f}M"
    elif abs(value) >= 1_000:
        return f"{value / 1_000:.{decimals}f}K"
    return f"{value:.{decimals}f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format a value as percentage."""
    return f"{value:.{decimals}f}%"
